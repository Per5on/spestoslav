#!/usr/bin/env python3
"""Read-only branch reconciliation; never infer closure from an absent seed row."""

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


def normalize(value):
    return re.sub(
        r"[\W_]+",
        " ",
        unicodedata.normalize("NFKC", (value or "").replace("№", " ")).casefold(),
    ).strip()


def physical_key(row):
    return tuple(
        normalize(row.get(k, ""))
        for k in ("retailer_code", "city", "municipality", "region", "address")
    )


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def reconcile(seed, snapshot, closures, pending):
    existing = snapshot["branches"]
    localities = snapshot["localities"]
    by_id = {r["id"]: r for r in localities}
    by_locality = {}
    for row in localities:
        key = tuple(normalize(row[k]) for k in ("name_bg", "municipality", "region"))
        by_locality.setdefault(key, []).append(row["id"])
    physical, identities = {}, {}
    for row in existing:
        # Canonical linked locality is authoritative, not legacy denormalized columns.
        if row.get("locality_id") not in by_id:
            raise ValueError("Existing branch has missing/unknown locality link")
        loc = by_id[row["locality_id"]]
        canonical = dict(
            row,
            city=loc["name_bg"],
            municipality=loc["municipality"],
            region=loc["region"],
        )
        key = physical_key(canonical)
        identity = (row["source"], row["source_id"])
        if key in physical or (identity[1] is not None and identity in identities):
            raise ValueError("Duplicate physical branch or source identity in database")
        physical[key] = row
        if identity[1] is not None:
            identities[identity] = row
    closed_keys = {physical_key(r) for r in closures}
    pending_keys = {physical_key(r) for r in pending}
    seen, result = set(), []
    for row in seed:
        key = physical_key(row)
        if key in seen:
            raise ValueError("Duplicate normalized seed branch")
        seen.add(key)
        loc_key = key[1:4]
        if len(by_locality.get(loc_key, [])) != 1:
            raise ValueError(f"Expected one canonical locality: {loc_key}")
        digest = hashlib.sha256(
            "|".join(
                row[k].strip()
                for k in ("retailer_code", "city", "municipality", "region", "address")
            ).encode()
        ).hexdigest()[:32]
        source_id = f"inventory:{row['retailer_code']}:{digest}"
        match = physical.get(key)
        collision = identities.get((row["source"], source_id))
        if key in closed_keys or key in pending_keys:
            action = "blocked_closed_or_pending"
        elif collision and (not match or collision["id"] != match["id"]):
            action = "blocked_source_identity_collision"
        elif match and not match["active"]:
            action = "blocked_inactive"
        elif match:
            action = "unchanged"
        else:
            action = "insert_candidate"
        result.append(
            {
                "retailer_code": row["retailer_code"],
                "city": row["city"],
                "address": row["address"],
                "source_url": row["source_url"],
                "source_checked_at": row["source_checked_at"],
                "proposed_source_id": source_id,
                "locality_id": by_locality[loc_key][0],
                "existing_id": match["id"] if match else None,
                "action": action,
            }
        )
    retained = [
        {
            "id": row["id"],
            "retailer_code": row["retailer_code"],
            "address": row["address"],
            "active": row["active"],
            "action": "retain_history_no_change",
        }
        for key, row in physical.items()
        if key not in seen
    ]
    closed_existing = [
        {"id": row["id"], "active": row["active"], "action": "review_closure"}
        for key, row in physical.items()
        if key in closed_keys
    ]
    return {
        "read_only": True,
        "baseline_total": len(existing),
        "baseline_active": sum(r["active"] for r in existing),
        "baseline_linked": len(existing),
        "seed_rows": len(seed),
        "actions": dict(Counter(r["action"] for r in result)),
        "rows": result,
        "retained_outside_seed": retained,
        "confirmed_closure_matches": closed_existing,
        "warning": "Candidates require current official evidence and reviewed import; no writes performed.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument(
        "--seed", type=Path, default=Path("data/store_branches_seed.csv")
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = reconcile(
        read_csv(args.seed),
        json.loads(args.snapshot.read_text()),
        read_csv(root / "data/store_branch_closures.csv"),
        read_csv(root / "data/store_branch_pending_review.csv"),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
