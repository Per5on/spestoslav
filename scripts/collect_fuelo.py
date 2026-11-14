#!/usr/bin/env python3
"""Collect only explicitly reviewed station/product mappings into pending review.

python scripts/collect_fuelo.py --mapping /secure/reviewed-fuelo-mappings.json
Requires FUELO_API_KEY, API_BASE_URL and COLLECTOR_API_KEY. Mapping rows contain
station_id, branch_id and a products map keyed by Fuelo fuel code. Station-to-branch
mappings must be reviewed by address + canonical locality, never city name alone.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.collectors.fuelo import FueloClient, FueloError


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", required=True)
    args = parser.parse_args()
    mappings = json.loads(Path(args.mapping).read_text())
    if not mappings:
        print("No reviewed station mappings configured; nothing collected.")
        return
    base = os.environ["API_BASE_URL"].rstrip("/")
    if not base.startswith("https://"):
        raise SystemExit("API_BASE_URL must use HTTPS")
    client = FueloClient()
    count = 0
    try:
        with httpx.Client(
            timeout=30,
            headers={"X-Collector-Key": os.environ["COLLECTOR_API_KEY"]},
            follow_redirects=False,
        ) as api:
            for mapping in mappings:
                observations = []
                for row in client.station_prices(mapping["station_id"]):
                    product = mapping["products"].get(row["fuel"])
                    if not product:
                        continue
                    observations.append(
                        {
                            "product_id": product,
                            "branch_id": mapping["branch_id"],
                            "price_eur": row["price_eur"],
                            "source_reference": row["source_reference"],
                            "observed_at": row["observed_at"],
                            "expires_at": row["expires_at"],
                            "source_code": "fuelo",
                            "external_id": f"{row['station_id']}:{row['fuel']}:{row['observed_at']}",
                        }
                    )
                if observations:
                    response = api.post(
                        base + "/api/v1/collector/observations",
                        json={"observations": observations},
                    )
                    response.raise_for_status()
                    count += len(observations)
    finally:
        client.close()
    print(
        f"Queued {count} Fuelo observations with UNKNOWN certainty for review; no prices auto-verified."
    )


if __name__ == "__main__":
    main()
