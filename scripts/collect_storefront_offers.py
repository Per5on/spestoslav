"""Read reviewed online offers for exact catalogue products from retailer pages."""

from datetime import datetime, timedelta, timezone
import time
from urllib.robotparser import RobotFileParser

import httpx

from collect_techmart_offers import AGENT, offer_price

# catalogue code, shop SKU, product path, exact name, GTIN when supplied
STOREFRONTS = {
    "t_market": ("https://tmarketonline.bg", 3, (
        ("404031", "764988", "/product/zahar-sladeya-1kg", "Захар СЛАДЕЯ 1 кг", None),
        ("620257", "1371275", "/product/zahar-klio-1-kg", "Захар КЛИО 1 кг", None),
        ("102132", "390138", "/product/brashno-sofiya-mel-ekstra-1-kg", "Брашно СОФИЯ МЕЛ eкстра 1 кг", None),
    )),
    "bulmag": ("https://bulmag.org", 2, (
        ("102132", "19963", "/product/brashno-ekstra-sofiya-mel-1kg", "Брашно Екстра София Мел 1кг", None),
    )),
    "ardes": ("https://ardes.bg", 2, (
        ("46637", "MZB0N5UEU", "/product/xiaomi-redmi-a7-pro-4gb-64gb-black-mzb0n5ueu-529552", None, "6932554493271"),
    )),
}


def collect(retailer, client, failed_sku):
    base, delay, products = STOREFRONTS[retailer]
    try:
        response = client.get(base + "/robots.txt")
        response.raise_for_status()
    except httpx.HTTPError:
        for _, sku, *_ in products:
            failed_sku(sku)
        return
    robots = RobotFileParser()
    robots.parse(response.text.splitlines())
    delay = max(delay, robots.crawl_delay(AGENT) or 0)
    for code, sku, path, name, gtin in products:
        url = base + path
        if not robots.can_fetch(AGENT, url):
            failed_sku(sku)
            continue
        time.sleep(delay)
        try:
            # Avoid carrying a previously selected branch across public offers.
            client.cookies.clear()
            response = client.get(url)
            response.raise_for_status()
            amount = offer_price(response.text, sku, source_url=url, product_name=name, gtin=gtin)
        except (httpx.HTTPError, ValueError):
            failed_sku(sku)
            continue
        if not amount:
            failed_sku(sku)
            continue
        observed = datetime.now(timezone.utc)
        yield {
            "code": code, "retailer": retailer, "url": url, "price": amount,
            "observed": observed.isoformat(), "expires": (observed + timedelta(hours=12)).isoformat(),
        }
