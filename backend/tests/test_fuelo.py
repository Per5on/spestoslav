from datetime import datetime, timedelta, timezone
import httpx
import pytest

from app.collectors.fuelo import FueloClient, FueloError


def client(payload, status=200):
    def handler(request):
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.url.host == "api.fuelo.net"
        return httpx.Response(status, json=payload)

    return FueloClient(
        "test-key", transport=httpx.MockTransport(handler), throttle_seconds=0
    )


def snapshot(**fields):
    return dict(
        gasstation_id=123,
        country="bg",
        active=True,
        currency="EUR",
        prices=[
            {
                "fuel": "diesel",
                "unit": "L",
                "price": 1.83,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        **fields,
    )


def test_station_price_keeps_unknown_certainty_and_freshness():
    c = client({"data": snapshot()})
    try:
        rows = c.station_prices(123)
        assert rows[0]["certainty"] == "UNKNOWN"
        assert rows[0]["price_eur"] == "1.83"
        assert datetime.fromisoformat(rows[0]["expires_at"]) - datetime.fromisoformat(
            rows[0]["observed_at"]
        ) == timedelta(hours=48)
    finally:
        c.close()


@pytest.mark.parametrize("status", [401, 403, 429])
def test_missing_plan_or_quota_fails_without_fallback_scraping(status):
    c = client({"code": "plan_required"}, status)
    try:
        with pytest.raises(FueloError):
            c.station_prices(123)
    finally:
        c.close()


@pytest.mark.parametrize(
    "change", [{"currency": "BGN"}, {"country": "de"}, {"gasstation_id": 999}]
)
def test_country_currency_and_station_identity_must_match(change):
    value = snapshot()
    value.update(change)
    c = client({"data": value})
    try:
        with pytest.raises(FueloError):
            c.station_prices(123)
    finally:
        c.close()


def test_stale_missing_closed_and_unit_mismatches():
    value = snapshot()
    value["prices"][0]["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(days=4)
    ).isoformat()
    c = client({"data": value})
    try:
        assert c.station_prices(123) == []
    finally:
        c.close()
    value["active"] = False
    c = client({"data": value})
    try:
        assert c.station_prices(123) == []
    finally:
        c.close()
    value = snapshot()
    value["prices"][0]["unit"] = "kg"
    c = client({"data": value})
    try:
        with pytest.raises(FueloError):
            c.station_prices(123)
    finally:
        c.close()


def test_pagination_never_leaks_key_to_another_host():
    c = client(
        {"data": [], "links": {"next": "https://attacker.example/v2/gasstations"}}
    )
    try:
        with pytest.raises(FueloError, match="Untrusted"):
            list(c.stations())
    finally:
        c.close()


def test_api_key_is_required(monkeypatch):
    monkeypatch.delenv("FUELO_API_KEY", raising=False)
    with pytest.raises(FueloError, match="required"):
        FueloClient()
