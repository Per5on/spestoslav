#!/usr/bin/env python3
"""Bounded review-only Techmart public catalogue collector. Never imports prices."""

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

GROUPS = {
    "mobile": [
        "smartfoni",
        "mobilni-telefoni",
        "smart-chasovnici",
        "fitnes-grivni",
        "aksesoari-za-smartfon",
        "vynshni-baterii",
        "tableti",
        "audio-slushalki",
        "elektronni-knigi",
    ],
    "major-appliances": [
        "peralni",
        "sushilni",
        "hladilnici",
        "sydo-miyalni",
        "myqlni",
        "pechki",
        "gotvarski-pechki",
        "klimatici",
        "invertorni-klimatici",
        "kombinirani-hladilnici-s-frizer",
        "hladilnici-side-by-side",
        "bojleri",
        "freezeri",
    ],
    "small-appliances": [
        "kafemashini",
        "prahosmukachki",
        "mikrovylnovi",
        "elektricheski-kani",
        "blenderi",
        "mikseri",
        "pasatori",
        "tosteri",
        "frityurnici",
        "seshoari",
        "mashinki-za-podstrigvane",
        "el.-chetki-i-zybni-dushove",
        "masazhori",
        "za-gladene",
    ],
    "tv-computing": [
        "televizori",
        "laptopi",
        "monitori",
        "nastolni-kompyutri",
        "printeri",
        "periferiq",
        "flash-pameti",
        "hard-diskove",
        "slushalki",
        "mikrofoni",
        "mrezhovi-adaptori",
    ],
    "smart-home-mobility": [
        "smart-dom",
        "smart-kontakti",
        "smart-krushki",
        "elektricheski-trotinetki",
        "videonablyudenie",
    ],
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.limit = None
        self.rejected = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "select" and "limitSwitcher" in d.get("class", ""):
            self.limit = d.get("data-href")
        if tag == "a" and d.get("data-tm-item"):
            try:
                item = json.loads(d["data-tm-item"])
            except json.JSONDecodeError:
                self.rejected += 1
                return
            if item.get("item_id") and item.get("item_name"):
                self.rows.append(
                    {
                        "source_product_code": str(item["item_id"]),
                        "name": item["item_name"].strip(),
                        "brand": item.get("item_brand") or None,
                        "source_category": item.get("item_category2")
                        or item.get("item_category", ""),
                        "source_url": urljoin(
                            "https://techmart.bg/", d.get("href", "")
                        ),
                    }
                )


def collect(cache, limit=1000):
    cache.mkdir(parents=True, exist_ok=True)

    def read(url):
        if urlsplit(url).hostname != "techmart.bg":
            raise ValueError("Unexpected source host")
        target = cache / (hashlib.sha256(url.encode()).hexdigest() + ".html")
        if target.exists():
            return target.read_text()
        time.sleep(0.5)
        with urlopen(
            Request(
                url,
                headers={
                    "User-Agent": "Spestovnik catalogue source review (https://github.com/Per5on/spestoslav)"
                },
            ),
            timeout=25,
        ) as response:
            if urlsplit(response.url).hostname != "techmart.bg":
                raise ValueError("Unexpected redirect")
            raw = response.read(4000001)
            if len(raw) > 4000000:
                raise ValueError("Source exceeds bounded page size")
        text = raw.decode("utf-8")
        target.write_text(text)
        return text

    robots = RobotFileParser()
    robots.parse(
        read("https://techmart.bg/robots.txt").replace("\\r\\n", "\n").splitlines()
    )
    import xml.etree.ElementTree as ET

    tree = ET.fromstring(read("https://techmart.bg/sitemaps/sitemap-categories.xml"))
    published = {
        e.text
        for e in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    records = {}
    pages = []
    # Round-robin groups avoids a single appliance group consuming the full sample.
    for index in range(max(map(len, GROUPS.values()))):
        for group, slugs in GROUPS.items():
            if index >= len(slugs):
                continue
            url = "https://techmart.bg/" + slugs[index]
            if url not in published or not robots.can_fetch("*", url):
                continue
            page = Page()
            page.feed(read(url))
            used = url
            if page.limit:
                larger = urljoin(url, page.limit + "limit/48")
                if robots.can_fetch("*", larger):
                    page = Page()
                    page.feed(read(larger))
                    used = larger
            pages.append({"url": used, "items": len(page.rows)})
            for row in page.rows:
                if urlsplit(row["source_url"]).hostname != "techmart.bg":
                    raise ValueError("Unexpected product URL")
                row["group_code"] = group
                previous = records.get(row["source_product_code"])
                if previous and previous["name"] != row["name"]:
                    raise ValueError("Conflicting source identity")
                records.setdefault(row["source_product_code"], row)
            print(
                json.dumps(
                    {
                        "category": slugs[index],
                        "items": len(page.rows),
                        "unique": len(records),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            by_name = {}
            for record in records.values():
                by_name.setdefault(" ".join(record["name"].casefold().split()), record)
            if len(by_name) >= limit:
                return {
                    "schema_version": 1,
                    "source": "TECHMART_PUBLIC_CATALOG",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "selection": "Representative source-backed sample, not verified national bestseller ranking",
                    "prices_imported": False,
                    "verified_gtins": False,
                    "pages": pages,
                    "products": list(by_name.values())[:limit],
                }
    raise ValueError(
        f"Only {len(records)} distinct products observed; do not pad to {limit}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = collect(args.cache)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
