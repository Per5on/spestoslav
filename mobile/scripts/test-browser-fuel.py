"""Measure first fuel price and check locality isolation and older-host fallback."""

import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from urllib.request import urlopen

from playwright.async_api import async_playwright, expect

API = "http://127.0.0.1:8774"
WEB = "http://127.0.0.1:8775"
PRICE = "1.45 €/L"
NOTICE = "Няма налични цени за това гориво."


async def trial(browser, locality, delay, legacy=False):
    context = await browser.new_context(viewport={"width": 390, "height": 844})
    await context.add_init_script(
        f"localStorage.setItem('spestovnik-preview-001', {json.dumps(json.dumps({'locality': locality, 'basket': []}))})"
    )
    page = await context.new_page()
    requests = []

    async def intercept(route):
        path = route.request.url.split("/api/v1/")[1]
        if path.startswith("fuel-snapshot?") or "category_code=fuel" in path:
            requests.append(path.split("?")[0])
            if legacy and path.startswith("fuel-snapshot?"):
                await route.fulfill(status=404, json={"detail": "Older fixture API"})
                return
            await asyncio.sleep(delay / 1000)
        await route.continue_()

    try:
        await page.route(API + "/api/v1/**", intercept)
        await page.goto(WEB, wait_until="domcontentloaded")
        tab = page.get_by_role("tab", name="Горива", exact=True)
        await tab.evaluate(
            """(el, price) => {
                const start = performance.now();
                function inspect() {
                    if (document.body.innerText.includes(price)) {
                        window.fuelResult = {
                            fromTab: Math.round(performance.now() - start),
                            fromNavigation: Math.round(performance.now())
                        };
                    } else requestAnimationFrame(inspect);
                }
                el.click();
                requestAnimationFrame(inspect);
            }""",
            PRICE,
        )
        if delay:
            await expect(page.get_by_test_id("fuel-loading")).to_be_visible()
            await expect(page.get_by_text(NOTICE, exact=True)).to_have_count(0)
        await page.wait_for_function("window.fuelResult", timeout=10000)
        result = await page.evaluate("window.fuelResult")
        expected = (
            ["fuel-snapshot", "national-offers", "prices/current", "products", "stores"]
            if legacy else ["fuel-snapshot"]
        )
        assert sorted(requests) == expected, requests
        if legacy:
            await page.get_by_test_id("location-search").fill("Пловдив")
            await page.get_by_role("button", name="Пловдив", exact=False).first.click()
            await expect(page.get_by_text(PRICE, exact=True)).to_have_count(0)
        return result
    finally:
        await context.close()


async def check_online_and_empty_states(browser, locality):
    context = await browser.new_context(viewport={"width": 390, "height": 844})
    await context.add_init_script(
        f"localStorage.setItem('spestovnik-preview-001', {json.dumps(json.dumps({'locality': locality, 'basket': []}))})"
    )
    page = await context.new_page()

    async def online_only(route):
        response = await route.fetch()
        payload = await response.json()
        payload["prices"] = []
        product = next(row for row in payload["products"] if row["fuel_type"] == "petrol")
        store = payload["stores"][0]
        payload["online"] = [{
            "product_id": product["id"],
            "retailer_code": store["retailer_code"],
            "price_eur": "1.87",
            "price_scope": "NATIONAL_ONLINE",
            "valid_until": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        }]
        await route.fulfill(response=response, json=payload)

    try:
        await page.route(API + "/api/v1/fuel-snapshot?*", online_only)
        await page.goto(WEB, wait_until="domcontentloaded")
        await page.get_by_role("tab", name="Горива", exact=True).click()
        await expect(page.get_by_text("1.87 €/L", exact=True)).to_be_visible()
        await expect(page.get_by_text("1 клон", exact=True)).to_be_visible()
        await expect(page.get_by_text(NOTICE, exact=True)).to_have_count(0)
        await page.get_by_role("radio", name="Дизел", exact=True).click()
        await expect(page.get_by_text(NOTICE, exact=True)).to_be_visible()
        await expect(page.get_by_text("Няма налична цена", exact=True).first).to_be_visible()
    finally:
        await context.close()


async def main(output):
    with urlopen(API + "/api/v1/localities?q=Sofija", timeout=5) as response:
        sofia = json.load(response)[0]
    output.mkdir(parents=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(args=["--no-sandbox"])
        await check_online_and_empty_states(browser, sofia)
        results = {}
        for label, delay, legacy, count in [
            ("loopback", 0, False, 5), ("100-ms", 100, False, 5),
            ("300-ms", 300, False, 5), ("legacy-100-ms", 100, True, 1),
        ]:
            trials = [await trial(browser, sofia, delay, legacy) for _ in range(count)]
            results[label] = {
                "trials": trials,
                "medianFromTabMs": median(entry["fromTab"] for entry in trials),
                "medianFromNavigationMs": median(entry["fromNavigation"] for entry in trials),
            }
        (output / "timings.json").write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(results))
        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.output_dir))
