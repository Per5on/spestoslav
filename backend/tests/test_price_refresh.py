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
import collect_storefront_offers as storefront
import verify_price_coverage as coverage
from verify_price_coverage import verify_category
from refresh_live_prices import Batch, cache_batches, check_published_feed, collect_batches, combine_fuel_sources


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


def test_grocery_refresh_uses_direct_online_sku_and_skips_unavailable_products(monkeypatch):
    import json

    delays = []
    monkeypatch.setattr(storefront.time, "sleep", delays.append)
    base, delay, products = storefront.STOREFRONTS["t_market"]
    monkeypatch.setitem(storefront.STOREFRONTS, "t_market", (base, delay, products[:2]))
    monkeypatch.setitem(storefront.STOREFRONTS, "bulmag", (base, delay, ()))
    good_code, good_sku, good_slug, good_name, _ = products[0]
    _, failed_sku, second_slug, *_ = products[1]

    def response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nCrawl-delay: 3", headers={"Set-Cookie": "store_location=1; Path=/"})
        assert request.url.host == "tmarketonline.bg"
        assert not request.url.query
        assert "cookie" not in request.headers
        if request.url.path.endswith(second_slug):
            return httpx.Response(503)
        assert request.url.path.endswith(good_slug)
        data = {
            "@type": "Product", "name": good_name, "sku": good_sku,
            "offers": [{"@type": "Offer", "url": str(request.url), "price": 1.32,
                        "priceCurrency": "EUR", "availability": "https://schema.org/InStock"}],
        }
        return httpx.Response(200, text=f'<script type="application/ld+json">{json.dumps(data)}</script>')

    failed = []
    with httpx.Client(transport=httpx.MockTransport(response)) as client:
        batch, = collect_batches("groceries", client, failed.append)
    assert delays == [3, 3]
    assert failed == [failed_sku]
    row, = batch.rows
    assert row[2:7] == ("t_market", "", "", good_code, "1.32")
    assert row[9] == "NATIONAL_ONLINE"
    assert "INSERT INTO national_offers" in batch.statement
    assert "store_branches" not in batch.statement


def test_public_readback_retries_transient_errors_and_rejects_old_offers(monkeypatch):
    now = datetime.now(timezone.utc)
    stamp = now.isoformat()
    source = "https://tmarketonline.bg/product/zahar-sladeya-1kg"
    batch = Batch("groceries", [
        ("groceries", source, "t_market", "", "", "404031", "1.32", stamp, stamp, "NATIONAL_ONLINE"),
    ], "")
    result = {"retailer_code": "t_market", "source_reference": source,
              "price_eur": "1.3200", "observed_at": stamp, "price_scope": "NATIONAL_ONLINE"}

    requests = []

    delays = []
    monkeypatch.setattr(coverage, "sleep", delays.append)

    def respond(request):
        assert request.url.params["category_code"] == "groceries"
        requests.append(request)
        if len(requests) == 1:
            raise httpx.ReadTimeout("First read timed out", request=request)
        if len(requests) == 2:
            return httpx.Response(503)
        return httpx.Response(200, json=[result])

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert check_published_feed(client, "https://api.example", "groceries", [batch]) == {"expected": 1, "served": 1}
        assert [request.url for request in requests] == [requests[0].url] * 3
        assert all(request.method == "GET" for request in requests)
        assert delays == [1, 2]
        result["observed_at"] = (now - timedelta(hours=4)).isoformat()
        assert check_published_feed(client, "https://api.example", "groceries", [batch]) == {
            "ok": False, "expected": 1, "served": 0,
        }


@pytest.mark.parametrize("status, expected_calls", [(503, 3), (404, 1)])
def test_public_readback_fails_after_bounded_retries(monkeypatch, status, expected_calls):
    calls = []
    monkeypatch.setattr(coverage, "sleep", lambda delay: None)

    def respond(request):
        calls.append(request)
        return httpx.Response(status)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client, pytest.raises(httpx.HTTPStatusError):
        coverage.read(client, "https://api.example")
    assert len(calls) == expected_calls


def test_public_release_check_requires_two_eligible_retailers_for_the_same_product():
    now = datetime.now(timezone.utc)
    branches = [
        {"category_code": "groceries", "locality_id": "town", "locality_name": "Варна", "retailer_code": code}
        for code in ("t_market", "bulmag")
    ]
    results = [
        {"product_id": "flour", "retailer_code": code, "price_eur": price,
         "valid_until": (now + timedelta(hours=1)).isoformat(), "price_scope": "NATIONAL_ONLINE"}
        for code, price in (("t_market", "1.15"), ("bulmag", "1.23"))
    ]
    scoped = list(results)

    def respond(request):
        if request.url.params.get("locality_id"):
            assert request.url.params["locality_id"] == "town"
            assert request.url.params["product_id"] == "flour"
            return httpx.Response(200, json=scoped)
        return httpx.Response(200, json=results)

    with httpx.Client(base_url="https://api.example", transport=httpx.MockTransport(respond)) as client:
        result = verify_category(client, "groceries", branches, now)
        assert result["ok"]
        assert result["sample"]["retailer_prices"] == {"bulmag": "1.23", "t_market": "1.15"}
        assert not verify_category(client, "groceries", branches[:1], now)["ok"]
        scoped.pop()
        assert not verify_category(client, "groceries", branches, now)["ok"]
        results[1]["product_id"] = "different"
        assert not verify_category(client, "groceries", branches, now)["ok"]


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
    payload["currency"] = "BGN"
    assert checks.attempt(lambda: karai.offers(payload, now)) == {"ok": False, "error": "ValueError"}


def test_cross_check_keeps_fuelo_amount_with_missing_or_different_secondary():
    now = datetime.now(timezone.utc)
    feed = {
        "observed_at": (now - timedelta(hours=1)).isoformat(), "currency": "EUR", "unit": "L",
        "prices": [
            {"retailer": "eko", "fuel": "petrol", "price": "1.46"},
            {"retailer": "eko", "fuel": "diesel", "price": "1.75"},
            {"retailer": "eko", "fuel": "dieselPlus", "price": "1.80"},
        ],
    }
    secondary = [
        {"retailer": "eko", "fuel": "petrol", "price": "1.46"},
        {"retailer": "eko", "fuel": "diesel", "price": "1.69"},
        {"retailer": "omv", "fuel": "lpg", "price": "0.80"},
    ]
    prices, checks = combine_fuel_sources(feed, secondary, now)
    assert checks == {"matched": 1, "different": 1, "no_secondary": 1}
    assert {(row["retailer"], row["fuel"]): row["price"] for row in prices} == {
        ("eko", "petrol"): "1.46", ("eko", "diesel"): "1.75",
        ("eko", "dieselPlus"): "1.80", ("omv", "lpg"): "0.80",
    }
    assert all(row["source"].startswith("https://bg.fuelo.net/prices/date/") for row in prices[:3])
    assert prices[3] == secondary[2]
    with pytest.raises(ValueError, match="expired"):
        combine_fuel_sources(feed, secondary, now + timedelta(days=1))


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

def test_cache_migrates_legacy_rows_and_retains_overlapping_source_observations(tmp_path):
    from refresh_live_prices import TABLE

    path = tmp_path / "legacy.sqlite"
    now = datetime.now(timezone.utc)
    stamp, expiry = now.isoformat(), (now + timedelta(hours=1)).isoformat()
    base = ("groceries", "https://direct.example.invalid", "test", "София", "address", "1")
    first = (*base, "2.19", stamp, expiry, "BRANCH")
    second = (base[0], "https://archive.example.invalid", *base[2:], "2.20", stamp, expiry, "BRANCH")
    with sqlite3.connect(path) as db:
        db.execute(TABLE.replace("observed_at, source_url, price_scope)", "observed_at)"))
        db.execute("INSERT INTO price_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", first)
        db.execute("CREATE INDEX price_validity ON price_observations(category, valid_until)")
        db.execute("CREATE VIEW unexpired_observations AS SELECT * FROM price_observations")
    for _ in range(2):
        cache_batches(path, [Batch("groceries", [first, second], "")])
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT price_eur FROM unexpired_observations ORDER BY price_eur").fetchall() == [
            ("2.19",), ("2.20",),
        ]
