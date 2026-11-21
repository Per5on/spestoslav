"""Verify transient read recovery and bounded location failures without shared writes."""

import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base-url", default="http://127.0.0.1:8775")
parser.add_argument("--api-url", default="http://127.0.0.1:8774")
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=False)
proof = {}
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.on("pageerror", lambda e: errors.append(str(e)))
    rows = page.request.get(args.api_url + "/api/v1/localities?q=Sofia").json()
    calls = [0]

    def recover(route):
        calls[0] += 1
        if calls[0] == 1:
            route.abort("timedout")
        else:
            route.fulfill(
                status=200, content_type="application/json", body=json.dumps(rows)
            )

    page.route(re.compile(r"/api/v1/localities\?"), recover)
    page.goto(args.base_url, wait_until="domcontentloaded")
    location = page.get_by_role("textbox", name="Търси населено място…", exact=True)
    expect(location).to_have_count(1)
    location.fill("S", timeout=60000)
    page.wait_for_timeout(450)
    assert calls[0] == 0
    location.fill("So")
    expect(page.get_by_text("София", exact=True)).to_be_visible(timeout=15000)
    assert calls[0] == 2, calls
    page.get_by_text("София", exact=True).click()
    expect(location).to_have_value("София")
    for tab in ("Техника", "Горива", "Сравни цените", "Храни"):
        page.get_by_role("tab", name=tab, exact=True).click()
        expect(location).to_have_value("София")
    expect(location).to_have_count(1)
    proof["one_shared_location_field_searches_after_two_characters"] = True
    proof["transient_location_failure_recovers_without_manual_retry"] = True
    page.close()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.on("pageerror", lambda e: errors.append(str(e)))
    calls[0] = 0

    def unavailable(route):
        calls[0] += 1
        route.fulfill(status=503, content_type="application/json", body="{}")

    page.route(re.compile(r"/api/v1/localities\?"), unavailable)
    page.goto(args.base_url, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Търси населено място…", exact=True).fill(
        "So", timeout=60000
    )
    expect(
        page.get_by_text("Търсенето временно не е достъпно.", exact=True)
    ).to_be_visible(timeout=10000)
    assert calls[0] == 3, calls
    expect(page.get_by_text("София", exact=True)).to_have_count(0)
    page.get_by_role("button", name="Опитайте отново", exact=True).click()
    expect(
        page.get_by_text("Търсенето временно не е достъпно.", exact=True)
    ).not_to_be_visible()
    expect(
        page.get_by_text("Търсенето временно не е достъпно.", exact=True)
    ).to_be_visible(timeout=10000)
    assert calls[0] == 6, calls
    page.screenshot(path=str(args.output_dir / "bounded-network-failure.png"))
    proof["permanent_failure_stops_after_three_reads_and_manual_retry_works"] = True
    assert not errors, errors
    proof["javascript_errors"] = errors
    browser.close()
(args.output_dir / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
print(json.dumps(proof))
