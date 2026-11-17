"""Inventory safety checks, including generated SQL against disposable PostgreSQL."""

import json
import os
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_branch_batch import load_batch, render_sql
from reconcile_inventory import read_csv, reconcile

BASELINE = ROOT / "data/evidence/2026-11-17-preview-baseline.json"


def test_reviewed_seed_diff_preserves_inactive_and_is_not_count_subtraction():
    snapshot = json.loads(BASELINE.read_text())
    result = reconcile(
        read_csv(ROOT / "data/store_branches_seed.csv"),
        snapshot,
        read_csv(ROOT / "data/store_branch_closures.csv"),
        read_csv(ROOT / "data/store_branch_pending_review.csv"),
    )
    assert result["baseline_total"] == 139
    assert result["actions"] == {"unchanged": 138, "insert_candidate": 5}
    assert result["confirmed_closure_matches"] == []
    assert len(result["retained_outside_seed"]) == 1
    assert result["retained_outside_seed"][0]["active"] is False
    assert {r["city"] for r in result["rows"] if r["action"] == "insert_candidate"} == {
        "Банско",
        "Тетевен",
        "Благоевград",
    }


def test_reconciliation_blocks_reactivation_and_duplicate_db_identity():
    snapshot = json.loads(BASELINE.read_text())
    seed = read_csv(ROOT / "data/store_branches_seed.csv")
    target = snapshot["branches"][0]
    target["active"] = False
    result = reconcile(seed, snapshot, [], [])
    assert result["actions"]["blocked_inactive"] == 1
    snapshot["branches"].append(dict(target, id=str(uuid.uuid4())))
    with pytest.raises(ValueError, match="Duplicate"):
        reconcile(seed, snapshot, [], [])


@pytest.mark.parametrize("schema_kind", ["current", "legacy-preview"])
@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"), reason="Disposable PostgreSQL required"
)
def test_generated_import_atomic_idempotent_and_fail_closed(schema_kind):
    import psycopg

    # These fixtures intentionally model the two different branch schemas. Never public.
    schema = "inventory_test_" + uuid.uuid4().hex
    row = load_batch(ROOT / "data/batches/2026-11-14-groceries.csv")[0]
    sql = render_sql([row], schema=schema_kind)
    locality = uuid.uuid4()
    with psycopg.connect(os.environ["TEST_DATABASE_URL"], autocommit=True) as db:
        db.execute(f'CREATE SCHEMA "{schema}"')
        try:
            db.execute(f'SET search_path TO "{schema}"')
            db.execute(
                "CREATE TABLE inhabited_localities (id uuid PRIMARY KEY, name_bg text, municipality text, region text)"
            )
            db.execute(
                "CREATE TABLE catalog_retailers (code text PRIMARY KEY, category_code text, active boolean)"
            )
            extras = ""
            if schema_kind == "legacy-preview":
                extras = ", retailer_name text NOT NULL, city text NOT NULL, settlement text, municipality text, region text, last_seen_at timestamptz, UNIQUE(source,source_id)"
            db.execute(
                "CREATE TABLE store_branches (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), retailer_code text NOT NULL, branch_name text, address text NOT NULL, source text, source_id text, locality_id uuid, active boolean NOT NULL"
                + extras
                + ")"
            )
            db.execute(
                "INSERT INTO inhabited_localities VALUES (%s,%s,%s,%s)",
                (locality, row["city"], row["municipality"], row["region"]),
            )
            db.execute(
                "INSERT INTO catalog_retailers VALUES (%s,%s,true)",
                (row["retailer_code"], row["category_code"]),
            )
            db.execute(sql)
            before = db.execute("SELECT * FROM store_branches").fetchall()
            db.execute(sql)
            assert db.execute("SELECT * FROM store_branches").fetchall() == before
            assert len(before) == 1
            db.execute("UPDATE store_branches SET active=false")
            with pytest.raises(psycopg.errors.RaiseException, match="inactive"):
                db.execute(sql)
            assert db.execute("SELECT active FROM store_branches").fetchone() == (
                False,
            )
            db.execute(
                "UPDATE store_branches SET active=true,source_id='other-source-id',address=%s",
                ("УЛ. „Ярослав Вешин“ 41",),
            )
            with pytest.raises(psycopg.errors.RaiseException, match="another identity"):
                db.execute(sql)
            # Fail late in a multi-row batch: first insert must roll back with second.
            db.execute("TRUNCATE store_branches")
            bad = dict(row, address="Missing locality 2", city="Not in reference")
            with pytest.raises(
                psycopg.errors.RaiseException, match="Expected one locality"
            ):
                db.execute(render_sql([row, bad], schema=schema_kind))
            assert db.execute("SELECT count(*) FROM store_branches").fetchone() == (0,)
            # Replay the complete observed preview inventory in this isolated schema.
            snapshot = json.loads(BASELINE.read_text())
            db.execute("TRUNCATE inhabited_localities, catalog_retailers")
            for loc in snapshot["localities"]:
                db.execute(
                    "INSERT INTO inhabited_localities VALUES (%s,%s,%s,%s)",
                    tuple(loc[k] for k in ("id", "name_bg", "municipality", "region")),
                )
            seed = read_csv(ROOT / "data/store_branches_seed.csv")
            categories = {r["retailer_code"]: r["category_code"] for r in seed}
            for code, category in categories.items():
                db.execute(
                    "INSERT INTO catalog_retailers VALUES (%s,%s,true)",
                    (code, category),
                )
            columns = [
                "id",
                "retailer_code",
                "branch_name",
                "address",
                "source",
                "source_id",
                "locality_id",
                "active",
            ]
            if schema_kind == "legacy-preview":
                columns += [
                    "retailer_name",
                    "city",
                    "settlement",
                    "municipality",
                    "region",
                ]
            for branch in snapshot["branches"]:
                db.execute(
                    "INSERT INTO store_branches ("
                    + ",".join(columns)
                    + ") VALUES ("
                    + ",".join(["%s"] * len(columns))
                    + ")",
                    tuple(branch[k] for k in columns),
                )
            before = db.execute("SELECT * FROM store_branches ORDER BY id").fetchall()
            additions = load_batch(
                ROOT / "data/batches/2026-11-17-reconciled-additions.csv",
                ROOT / "data/store_branches_seed.csv",
            )
            reviewed_sql = render_sql(additions, schema=schema_kind)
            db.execute(reviewed_sql)
            after = db.execute("SELECT * FROM store_branches ORDER BY id").fetchall()
            assert db.execute(
                "SELECT count(*),count(*) FILTER (WHERE active) FROM store_branches"
            ).fetchone() == (144, 143)
            assert all(record in after for record in before)
            db.execute(reviewed_sql)
            assert (
                db.execute("SELECT * FROM store_branches ORDER BY id").fetchall()
                == after
            )
        finally:
            db.execute("SET search_path TO public")
            db.execute(f'DROP SCHEMA "{schema}" CASCADE')
