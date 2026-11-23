"""Offline regression checks for the price publication cache and source validators."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import sys

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import check_daily_prices as checks
import collect_burlex_branch_prices as burlex
import collect_karai_fuel_offers as karai
from refresh_live_prices import Batch, cache_batches


def test_tarnovo_prices_match_catalogue_names_and_keep_the_branch_scope():
    store = "БУРЛЕКС МАГРО"
    pages = []

    def response(request):
        if str(request.url) == burlex.SOURCE:
            return httpx.Response(200, text='<div class="burlex-wrap" data-nonce="test"></div> BGN_EUR_RATE = 1.95583')
        page = int(request.url.params["page"])
        pages.append(page)
        assert request.url.params["settlement"] == "Велико Търново"
        assert request.url.params["store"] == store
        return httpx.Response(200, json={
            "ok": True, "page": page, "total": 2,
            "rows": [{
                "store": store, "settlement": "Велико Търново",
                "product_name": "БАНАНИ" if page == 1 else "Different product",
                "product_code": "81590", "price": "2.15",
            }],
        })

    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        observations, observed = burlex.collect(store, client)
    assert pages == [1, 2]
    assert list(observations) == [{"code": "81590", "price": "1.10"}]
    statement = burlex.render(store, observations, observed)
    assert "name_bg='Велико Търново'" in statement
    assert "b.address='ул. Васил Левски 15'" in statement


def test_invalid_fuel_source_is_reported():
    now = datetime.now(timezone.utc)
    payload = {
        "date": now.astimezone(karai.ZoneInfo("Europe/Sofia")).date().isoformat(),
        "fetchedAt": now.replace(tzinfo=None).isoformat(), "source": "live",
        "providers": [{"logoKey": "eko", "a95": "1.45", "diesel": None, "lpg": None}],
    }
    assert checks.attempt(lambda: karai.offers(payload, now)) == {"ok": False, "error": "ValueError"}
    payload["fetchedAt"] = now.isoformat()
    payload["providers"][0]["a95"] = "wrong"
    assert checks.attempt(lambda: karai.offers(payload, now)) == {"ok": False, "error": "ValueError"}
    payload["providers"][0]["a95"] = "1.45"
    rows, observed = karai.offers(payload, now)
    assert rows == [{"retailer": "eko", "fuel": "petrol", "price": "1.45"}] and observed == now


def test_cache_preserves_history_without_returning_expired_prices(tmp_path):
    now = datetime.now(timezone.utc)
    expired, future = now - timedelta(hours=2), now + timedelta(hours=1)
    static = ("fuel", "https://example.invalid", "eko", "", "", "petrol", "1.45")
    path = tmp_path / "prices.sqlite"
    batch = Batch("fuel", [
        (*static, expired.isoformat(), now.isoformat(), "NATIONAL_ONLINE"),
        (*static, now.isoformat(), future.isoformat(), "NATIONAL_ONLINE"),
    ], "")
    for _ in range(2):
        cache_batches(path, [batch])
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT count(*) FROM price_observations").fetchone() == (2,)
        assert connection.execute("SELECT count(*) FROM unexpired_observations").fetchone() == (1,)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)


def test_fuel_sql_rejects_unsafe_delimiter():
    with pytest.raises(ValueError, match="delimiter"):
        karai.render([{"retailer": "$karai$"}], datetime.now(timezone.utc))
