"""Safety regressions for reviewed inventory batch preparation."""

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location(
    "batch", ROOT / "scripts/prepare_branch_batch.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
PATH = ROOT / "data/batches/2026-11-14-groceries.csv"


def write_batch(tmp_path, rows):
    path = tmp_path / "batch.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_reviewed_batch_matches_seed_and_has_unique_bounded_ids():
    rows = batch.load_batch(PATH, ROOT / "data/store_branches_seed.csv")
    assert len(rows) == 22
    assert len({batch.source_id(r) for r in rows}) == 22
    assert all(len(batch.source_id(r)) <= 100 for r in rows)


def test_identity_distinguishes_same_name_localities():
    row = batch.load_batch(PATH)[0]
    other = dict(row, municipality="Друга община", region="Друга област")
    assert batch.source_id(row) != batch.source_id(other)
    assert batch.source_id(row) == batch.source_id(
        dict(row, branch_name="Renamed display name")
    )


def test_duplicate_physical_branch_rejected_despite_different_name(tmp_path):
    row = batch.load_batch(PATH)[0]
    with pytest.raises(ValueError, match="Duplicate physical"):
        batch.load_batch(
            write_batch(tmp_path, [row, dict(row, branch_name="Other name")])
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("municipality", ""),
        ("region", ""),
        ("source_url", "javascript:alert(1)"),
        ("source_checked_at", "2999-01-01"),
        ("source", "SEARCH_SNIPPET"),
        ("latitude", "42"),
    ],
)
def test_unreviewable_rows_rejected(tmp_path, field, value):
    row = dict(batch.load_batch(PATH)[0], **{field: value})
    with pytest.raises(ValueError):
        batch.load_batch(write_batch(tmp_path, [row]))


def test_seed_mismatch_rejected(tmp_path):
    row = dict(batch.load_batch(PATH)[0], address="Unreviewed address")
    with pytest.raises(ValueError, match="exactly once"):
        batch.load_batch(
            write_batch(tmp_path, [row]), ROOT / "data/store_branches_seed.csv"
        )


def test_sql_quotes_data_and_rejects_delimiter():
    row = dict(batch.load_batch(PATH)[0], branch_name="O'Brien \\ test")
    sql = batch.render_sql([row], schema="legacy-preview")
    assert "O''Brien" in sql
    assert "ON CONFLICT (source,source_id) DO NOTHING" in sql
    with pytest.raises(ValueError, match="delimiter"):
        batch.render_sql([dict(row, branch_name="$inventory_batch$")])


def test_pending_and_closed_branches_are_outside_verified_batch():
    rows = batch.load_batch(PATH)
    identities = {batch.source_id(r) for r in rows}
    with (ROOT / "data/store_branch_pending_review.csv").open() as handle:
        pending = list(csv.DictReader(handle))
    assert len(pending) == 1
    assert pending[0]["active"] == "false"
    assert pending[0]["source_id"] not in identities
    with (ROOT / "data/store_branch_closures.csv").open() as handle:
        closed = list(csv.DictReader(handle))
    assert len(closed) == 4
    assert all(batch.source_id(r) not in identities for r in closed)


def test_case_punctuation_and_number_marker_duplicates_rejected(tmp_path):
    row = batch.load_batch(PATH)[0]
    other = dict(row, address="УЛ. Ярослав Вешин 41", branch_name="Different label")
    with pytest.raises(ValueError, match="Duplicate physical"):
        batch.load_batch(write_batch(tmp_path, [row, other]))


def test_closed_and_pending_cannot_be_submitted_as_active(tmp_path):
    row = batch.load_batch(PATH)[0]
    for filename in ("store_branch_closures.csv", "store_branch_pending_review.csv"):
        with (ROOT / "data" / filename).open() as handle:
            rejected = next(iter(csv.DictReader(handle)))
        candidate = dict(
            row, **{key: value for key, value in rejected.items() if key in row}
        )
        with pytest.raises(ValueError, match="Closed or pending"):
            batch.load_batch(write_batch(tmp_path, [candidate]))


def test_current_and_legacy_sql_are_explicit_and_do_not_restore_postal():
    rows = batch.load_batch(
        ROOT / "data/batches/2026-11-17-reconciled-additions.csv",
        ROOT / "data/store_branches_seed.csv",
    )
    assert len(rows) == 5
    current = batch.render_sql(rows)
    assert "gen_random_uuid()" in current
    assert "last_seen_at" not in current
    assert "last_seen_at" in batch.render_sql(rows, "legacy-preview")
    assert "postal_code" not in current
    assert "UPDATE store_branches" not in current
    with pytest.raises(ValueError, match="schema"):
        batch.render_sql(rows, "auto-guess")
