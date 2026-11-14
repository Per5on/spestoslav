"""Fuelo v2 station prices. All rows have UNKNOWN certainty: the public schema
has no reliable reported-versus-estimated flag. Country/brand averages are never
converted into physical-station prices. API access must be supplied by the owner.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os
import time
from urllib.parse import urlsplit
import httpx


class FueloError(RuntimeError):
    pass


class FueloClient:
    ORIGIN = "https://api.fuelo.net"

    def __init__(self, api_key=None, transport=None, throttle_seconds=13):
        key = api_key or os.getenv("FUELO_API_KEY")
        if not key:
            raise FueloError(
                "FUELO_API_KEY is required; station prices need an eligible plan"
            )
        self.client = httpx.Client(
            base_url=self.ORIGIN,
            headers={"Authorization": "Bearer " + key},
            timeout=20,
            transport=transport,
            follow_redirects=False,
        )
        self.throttle_seconds = throttle_seconds
        self.previous = 0

    def close(self):
        self.client.close()

    def get(self, path, params=None):
        url = httpx.URL(path if path.startswith("https://") else self.ORIGIN + path)
        if (
            url.scheme != "https"
            or url.host != "api.fuelo.net"
            or url.port not in (None, 443)
            or url.userinfo
            or not url.path.startswith("/v2/")
        ):
            raise FueloError("Untrusted Fuelo pagination URL")
        delay = self.previous + self.throttle_seconds - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self.previous = time.monotonic()
        try:
            with self.client.stream("GET", str(url), params=params) as response:
                if response.status_code in (401, 403):
                    raise FueloError("Fuelo key or plan does not permit this endpoint")
                if response.status_code == 429:
                    raise FueloError(
                        "Fuelo rate limit reached; retry in a later scheduled run"
                    )
                response.raise_for_status()
                body = bytearray()
                for part in response.iter_bytes():
                    body.extend(part)
                    if len(body) > 4 * 1024 * 1024:
                        raise FueloError("Fuelo response exceeds size limit")
                import json

                return json.loads(body)
        except httpx.HTTPError:
            raise FueloError("Fuelo request failed; no prices imported") from None

    def stations(self, max_pages=50):
        path = "/v2/gasstations"
        params = {"country": "bg", "limit": 50}
        seen = set()
        for page in range(max_pages):
            payload = self.get(path, params)
            for station in payload["data"]:
                if station.get("country") != "bg":
                    raise FueloError("Unexpected station country")
                yield station
            next_page = payload.get("links", {}).get("next")
            if not next_page:
                return
            if next_page in seen:
                raise FueloError("Repeated pagination cursor")
            seen.add(next_page)
            path = next_page
            params = {"country": "bg"}
        raise FueloError(
            "Station pagination limit reached; incomplete inventory must not be imported"
        )

    def station_prices(self, station_id):
        if not isinstance(station_id, int) or station_id <= 0:
            raise FueloError("Invalid Fuelo station id")
        payload = self.get(f"/v2/gasstations/{station_id}/prices")["data"]
        if (
            payload.get("gasstation_id") != station_id
            or payload.get("country") != "bg"
            or payload.get("currency") != "EUR"
        ):
            raise FueloError("Unexpected station identity, country or currency")
        if payload.get("active") is not True:
            return []
        now = datetime.now(timezone.utc)
        rows = []
        units = {
            "gasoline": "L",
            "diesel": "L",
            "lpg": "L",
            "methane": "kg",
            "gasoline95plus": "L",
            "gasoline98": "L",
            "gasoline98plus": "L",
            "dieselplus": "L",
            "electricity": "kWh",
        }
        for item in payload["prices"]:
            if item.get("price") is None or not item.get("updated_at"):
                continue
            fuel = item.get("fuel")
            unit = item.get("unit")
            if fuel not in units or unit != units[fuel]:
                raise FueloError("Unsupported fuel or unit")
            value = Decimal(str(item["price"]))
            if not value.is_finite() or value <= 0:
                raise FueloError("Invalid fuel price")
            updated = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            if updated.tzinfo is None:
                raise FueloError("Fuelo update timestamp must include timezone")
            if not now - timedelta(hours=48) < updated <= now:
                continue
            rows.append(
                {
                    "station_id": station_id,
                    "fuel": fuel,
                    "unit": unit,
                    "price_eur": str(value),
                    "observed_at": updated.isoformat(),
                    "expires_at": (updated + timedelta(hours=48)).isoformat(),
                    "certainty": "UNKNOWN",
                    "source_reference": f"{self.ORIGIN}/v2/gasstations/{station_id}/prices",
                }
            )
        return rows
