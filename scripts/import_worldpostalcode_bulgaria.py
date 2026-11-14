#!/usr/bin/env python3
"""Import Bulgarian settlement/postal-code rows from WorldPostalCode.

Usage:
  python scripts/import_worldpostalcode_bulgaria.py

Writes UTF-8 CSV to data/bulgaria_postal_codes.csv. This is a source-derived
reference dataset, not an official Bulgarian postal register.
"""
from __future__ import annotations

import csv
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://worldpostalcode.com/bulgaria/"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "bulgaria_postal_codes.csv"
USER_AGENT = "SpestoslavDataImporter/1.0 (postal-code reference import; contact: project maintainers)"
REQUEST_DELAY_SECONDS = 0.8
TIMEOUT_SECONDS = 25
POSTAL_CODE = re.compile(r"^\d{4}$")
SKIP_LABELS = {"all", "codes", "regions", "search by map", "how to find a postal code"}

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch(url: str) -> BeautifulSoup:
    response = session.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    time.sleep(REQUEST_DELAY_SECONDS)
    return BeautifulSoup(response.text, "html.parser")


def in_bulgaria(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.lower() == "worldpostalcode.com" and parsed.path.startswith("/bulgaria/")


def section_links(soup: BeautifulSoup) -> list[str]:
    """Get links in the page's Regions section (region/municipality navigation)."""
    heading = next(
        (h for h in soup.find_all(["h2", "h3"]) if clean(h.get_text(" ", strip=True)).lower() == "regions"),
        None,
    )
    if not heading:
        return []
    links: list[str] = []
    for sibling in heading.next_siblings:
        if getattr(sibling, "name", None) in {"h1", "h2", "h3"}:
            break
        if hasattr(sibling, "find_all"):
            for anchor in sibling.find_all("a", href=True):
                target = urljoin(BASE_URL, anchor["href"])
                if in_bulgaria(target):
                    links.append(target)
    # Some layouts wrap the links in a parent between heading and next heading.
    if not links:
        parent = heading.parent
        for anchor in parent.find_all("a", href=True):
            target = urljoin(BASE_URL, anchor["href"])
            if in_bulgaria(target):
                links.append(target)
    return list(dict.fromkeys(links))


def extract_rows(soup: BeautifulSoup, page_url: str) -> list[dict[str, str]]:
    text = soup.get_text("\n", strip=True)
    lines = [clean(line) for line in text.splitlines() if clean(line)]
    start = next((i for i, line in enumerate(lines) if re.search(r"\bCodes\s*$", line, re.I)), None)
    if start is None:
        return []
    end = next((i for i in range(start + 1, len(lines)) if lines[i].lower() == "search by map"), len(lines))
    region_or_municipality = clean(lines[start][:-5]).strip(" :-")
    rows = []
    for index in range(start + 1, end):
        if not POSTAL_CODE.fullmatch(lines[index]):
            continue
        # The source presents each locality followed by its four-digit code;
        # preceding one-letter lines are alphabetical index headings.
        if index == start + 1:
            continue
        locality = lines[index - 1]
        if len(locality) == 1 or locality.lower() in SKIP_LABELS or re.search(r"\bCodes\s*$", locality, re.I):
            continue
        if POSTAL_CODE.fullmatch(locality):
            continue
        rows.append({
            "settlement_name": locality,
            "postal_code": lines[index],
            "municipality_or_region": region_or_municipality,
            "source_url": page_url,
        })
    return rows


def main() -> int:
    queue = deque([BASE_URL])
    visited: set[str] = set()
    records: dict[tuple[str, str, str], dict[str, str]] = {}
    errors: list[tuple[str, str]] = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            soup = fetch(url)
            for row in extract_rows(soup, url):
                key = (
                    row["settlement_name"].casefold(),
                    row["postal_code"],
                    row["municipality_or_region"].casefold(),
                )
                records[key] = row
            for child in section_links(soup):
                if child not in visited:
                    queue.append(child)
            print(f"[ok] {url} ({len(extract_rows(soup, url))} rows; {len(visited)} pages visited)")
        except requests.RequestException as exc:
            errors.append((url, str(exc)))
            print(f"[error] {url}: {exc}", file=sys.stderr)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["settlement_name", "postal_code", "municipality_or_region", "source_url"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(records.values(), key=lambda r: (r["settlement_name"].casefold(), r["postal_code"])))

    print(f"\nVisited {len(visited)} pages; wrote {len(records)} unique rows to {OUTPUT}")
    if errors:
        error_path = OUTPUT.with_name("worldpostalcode_import_errors.txt")
        error_path.write_text("\n".join(f"{url}\t{error}" for url, error in errors) + "\n", encoding="utf-8")
        print(f"{len(errors)} page errors recorded in {error_path}", file=sys.stderr)
        return 2
    if not records:
        print("No postal-code rows were extracted. Review the source markup before using the output.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
