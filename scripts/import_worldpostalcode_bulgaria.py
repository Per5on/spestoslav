#!/usr/bin/env python3
"""Download and normalize GeoNames' Bulgaria postal-code export.

Source: https://download.geonames.org/export/zip/BG.zip
Licence: Creative Commons Attribution 3.0 (CC BY 3.0), per the GeoNames postal-code archive readme.
The source is not an official Bulgarian postal register; values are preserved
without inventing missing municipality/settlement relationships.
"""
from __future__ import annotations

import csv
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

SOURCE_URL = "https://download.geonames.org/export/zip/BG.zip"
USER_AGENT = "Spestoslav/1.0 (open postal reference data import)"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "bulgaria_postal_codes.csv"

SOURCE_FIELDS = (
    "country_code", "postal_code", "place_name", "admin_name1", "admin_code1",
    "admin_name2", "admin_code2", "admin_name3", "admin_code3",
    "latitude", "longitude", "accuracy",
)
OUTPUT_FIELDS = (
    "country_code", "postal_code", "place_name_source",
    "settlement_name_bg", "settlement_name_latin",
    "oblast_name_source", "oblast_code",
    "municipality_name_source", "municipality_code",
    "settlement_admin_name_source", "settlement_admin_code",
    "latitude", "longitude", "coordinate_accuracy", "source_url",
)


def split_bilingual(value: str) -> tuple[str, str]:
    """Split only the explicit 'Bulgarian / Latin' convention; otherwise preserve."""
    value = value.strip()
    if " / " in value:
        left, right = value.split(" / ", 1)
        return left.strip(), right.strip()
    return value, ""


def main() -> int:
    request = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            archive_bytes = response.read()
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members = [n for n in archive.namelist() if n.lower().endswith(".txt")]
            member = next((n for n in members if Path(n).name.lower() == "bg.txt"), None)
            if member is None:
                member = next((n for n in members if Path(n).name.lower() != "readme.txt"), None)
            if member is None:
                raise ValueError("GeoNames archive contains no .txt data file")
            raw = archive.read(member).decode("utf-8")
    except Exception as exc:
        print(f"Download/read failed: {exc}", file=sys.stderr)
        return 2

    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        values = line.split("\t")
        if len(values) != len(SOURCE_FIELDS):
            print(f"Skipping malformed line {line_number}: {len(values)} columns", file=sys.stderr)
            continue
        item = dict(zip(SOURCE_FIELDS, values))
        if item["country_code"] != "BG":
            continue
        # Prefer GeoNames admin_name3 for the settlement name because
        # place_name is sometimes Latin-only. Fall back when admin_name3
        # is absent, preserving the source rather than inventing a value.
        settlement_name_source = item["admin_name3"].strip() or item["place_name"].strip()
        bg_name, latin_name = split_bilingual(settlement_name_source)
        rows.append({
            "country_code": item["country_code"],
            "postal_code": item["postal_code"],
            "place_name_source": item["place_name"],
            "settlement_name_bg": bg_name,
            "settlement_name_latin": latin_name,
            "oblast_name_source": item["admin_name1"],
            "oblast_code": item["admin_code1"],
            "municipality_name_source": item["admin_name2"],
            "municipality_code": item["admin_code2"],
            "settlement_admin_name_source": item["admin_name3"],
            "settlement_admin_code": item["admin_code3"],
            "latitude": item["latitude"],
            "longitude": item["longitude"],
            "coordinate_accuracy": item["accuracy"],
            "source_url": SOURCE_URL,
        })

    if not rows:
        print("No Bulgaria records found; output was not replaced.", file=sys.stderr)
        return 1

    rows.sort(key=lambda r: (
        r["settlement_name_bg"].casefold(),
        r["oblast_name_source"].casefold(),
        r["municipality_name_source"].casefold(),
        r["postal_code"],
    ))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    missing_municipality = sum(not r["municipality_name_source"] for r in rows)
    missing_settlement_admin = sum(not r["settlement_admin_name_source"] for r in rows)
    print(f"Wrote {len(rows)} GeoNames Bulgaria rows to {OUTPUT}")
    print(f"Rows missing municipality label: {missing_municipality}")
    print(f"Rows missing settlement-level admin label: {missing_settlement_admin}")
    print("No missing administrative values were inferred or filled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
