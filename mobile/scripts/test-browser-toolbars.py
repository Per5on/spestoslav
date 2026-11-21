"""Check responsive catalog controls using the local preview fixture server."""
import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:8775")
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=False)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.base_url)
    tabs = page.get_by_role("tab")
    toolbar = page.get_by_test_id("catalog-toolbar")
    expect(tabs).to_have_count(4, timeout=30000)
    assert [tab.get_attribute("aria-label") for tab in tabs.all()] == [
        "Храни", "Техника", "Горива", "Сравни цените",
    ]

    def geometry(fuel=False):
        expect(toolbar.get_by_role("button")).to_have_count(2 if fuel else 1)
        field = toolbar.get_by_role("button").first if fuel else toolbar.get_by_role("textbox")
        refresh = toolbar.get_by_role("button").last
        first, last = field.bounding_box(), refresh.bounding_box()
        assert abs(first["y"] - last["y"]) < 2, (first, last)
        assert first["x"] + first["width"] < last["x"], (first, last)
        assert min(first["height"], last["height"]) >= 44, (first, last)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    geometry()
    assert toolbar.get_by_role("textbox").evaluate("(el) => getComputedStyle(el).backgroundColor") == "rgb(237, 243, 229)"
    expect(page.get_by_test_id("category-groups")).to_be_visible(timeout=20000)
    page.screenshot(path=args.output_dir / "food.png")
    tabs.nth(1).click()
    geometry()
    expect(page.get_by_test_id("thumbnail-loaded-demo-laptop")).to_be_visible(timeout=20000)
    groups = page.get_by_test_id("category-groups")
    expect(groups.get_by_role("button", name="Телевизори и компютри")).to_be_visible(timeout=20000)
    top = [groups.get_by_role("button", name=label, exact=True).bounding_box()
           for label in ("Всички продукти", "Телевизори и компютри")]
    bottom = [groups.get_by_role("button", name=label, exact=True).bounding_box()
              for label in ("Умен дом", "Малки уреди", "Големи уреди")]
    assert abs(top[0]["y"] - top[1]["y"]) < 2
    assert max(box["y"] for box in bottom) - min(box["y"] for box in bottom) < 2
    assert bottom[0]["y"] > top[0]["y"]
    overflow = groups.get_by_role("button", name="Още групи")
    expect(overflow).to_have_attribute("aria-expanded", "false")
    overflow.click()
    expect(overflow).to_have_attribute("aria-expanded", "true")
    overflow.click()
    expect(overflow).to_have_attribute("aria-expanded", "false")
    page.screenshot(path=args.output_dir / "technology.png")
    tabs.nth(2).click()
    geometry(fuel=True)
    selector = toolbar.get_by_role("button").first
    selector.click()
    panel = page.get_by_test_id("fuel-type-menu")
    assert [radio.get_attribute("aria-label") for radio in panel.get_by_role("radio").all()] == [
        "Бензин 95", "Бензин 98+", "Дизел", "Дизел +", "Автогаз",
    ]
    panel.get_by_role("radio", name="Бензин 98+").click()
    expect(selector).to_have_accessible_name("Избрано гориво: Бензин 98+")
    expect(panel).to_have_count(0)
    page.screenshot(path=args.output_dir / "fuel.png")
    tabs.nth(3).click()
    page.screenshot(path=args.output_dir / "compare.png")
    page.set_viewport_size({"width": 320, "height": 844})
    for language in ("bg", "en", "de", "es", "fr", "ru"):
        page.evaluate("""language => localStorage.setItem(
            "spestovnik-preferences", JSON.stringify({language, fontScale: 1.3}))""", language)
        page.reload()
        for index in range(3):
            tabs.nth(index).click()
            geometry(fuel=index == 2)
    page.evaluate("""localStorage.setItem("spestovnik-preferences",
        JSON.stringify({language: "bg", fontScale: 1.3}))""")
    page.reload()

    def open_appearance():
        page.get_by_role("button", name="Отвори менюто").click()
        page.get_by_role("menuitem", name="Настройки").click()
        page.get_by_role("button", name="Облик", exact=True).click()
        return page.get_by_test_id("appearance-screen").get_by_role("radio")

    options = open_appearance()
    expect(options).to_have_count(17)
    for index in range(8, 17):
        options.nth(index).click()
        expect(options.nth(index)).to_have_attribute("aria-checked", "true")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=args.output_dir / "appearance.png")
    page.reload()
    expect(open_appearance().nth(16)).to_have_attribute("aria-checked", "true")
    assert not errors, errors
    browser.close()
print("Catalogue toolbar dry run passed at standard and narrow widths in six languages.")
