"""Public collector stops on access/schema conflicts and stages metadata only."""

import importlib.util
from pathlib import Path
import httpx
import pytest

spec = importlib.util.spec_from_file_location(
    "catalog_collector",
    Path(__file__).resolve().parents[2] / "scripts/collect_burlex_catalog.py",
)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


def response_handler(kind="normal"):
    def handle(request):
        if request.url.path == "/kolkostruva/":
            if kind == "forbidden":
                return httpx.Response(403)
            return httpx.Response(
                200, text='<div class="burlex-wrap" data-nonce="public-table-token">'
            )
        row = {
            "product_code": "123",
            "product_name": "МЛЯКО 1Л",
            "category": "Прясно мляко",
            "price": "999.99",
            "promo_price": "0.01",
            "store": "TEST ONLY",
        }
        page = int(request.url.params["page"])
        if kind == "conflict" and page == 2:
            row["product_name"] = "DIFFERENT PRODUCT"
        return httpx.Response(
            200,
            json={
                "ok": True,
                "page": page,
                "per_page": 500,
                "total": 501 if kind == "conflict" else 1,
                "rows": [] if kind == "empty" else [row],
            },
        )

    return handle


def test_metadata_staged_without_prices_or_fake_gtins():
    with httpx.Client(transport=httpx.MockTransport(response_handler())) as client:
        data = collector.collect(["TEST ONLY"], 3, client, pause=lambda _: None)
    assert data["requires_review"] and not data["prices_imported"]
    assert data["products"] == [
        {
            "source_product_code": "123",
            "name": "МЛЯКО 1Л",
            "source_category": "Прясно мляко",
        }
    ]
    assert data["truncated_stores"] == []


@pytest.mark.parametrize("kind", ["forbidden", "conflict", "empty"])
def test_bad_source_is_not_an_empty_or_accepted_update(kind):
    with httpx.Client(transport=httpx.MockTransport(response_handler(kind))) as client:
        with pytest.raises((ValueError, httpx.HTTPStatusError)):
            collector.collect(["TEST ONLY"], 3, client, pause=lambda _: None)
