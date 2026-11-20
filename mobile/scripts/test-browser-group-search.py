"""Regression: switching product groups must clear stale search filters.

Run against the local web preview and fixture API; no Android build or writes.
"""
import argparse
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:8775")
args = parser.parse_args()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.base_url, wait_until="domcontentloaded")
    page.get_by_role("tab", name="Техника", exact=True).click()
    groups = page.get_by_test_id("category-group-choices")
    expect(groups).to_be_visible(timeout=30000)
    search = page.get_by_label("Търси продукт…", exact=True)
    search.fill("unlikely-no-product-0000")
    page.get_by_role("button", name="Приложи (0)", exact=True).click()
    expect(page.get_by_role("button", name="Добави", exact=False)).to_have_count(0)
    # Selecting a product group clears the old query, pending selections and
    # open suggestion panel instead of applying both incompatible filters.
    groups.get_by_role("button").nth(1).click()
    expect(search).to_have_value("")
    expect(page.get_by_role("button", name="Добави", exact=False).first).to_be_visible(timeout=30000)
    search.fill("unlikely-no-product-0000")
    page.get_by_role("button", name="Приложи (0)", exact=True).click()
    groups.get_by_role("button").first.click()
    expect(search).to_have_value("")
    assert not errors, errors
    browser.close()
print("PASS: category group switches clear stale product searches")
