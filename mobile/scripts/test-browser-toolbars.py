"""Check responsive catalog controls using the local preview fixture server."""
import argparse
import re
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
        expect(toolbar.get_by_role("button")).to_have_count(1)
        field = toolbar.get_by_role("radio").first if fuel else toolbar.get_by_role("textbox")
        if fuel:
            expect(page.get_by_test_id("fuel-first-row").get_by_role("radio")).to_have_count(2)
            expect(page.get_by_test_id("fuel-second-row").get_by_role("radio")).to_have_count(3)
            assert toolbar.get_by_role("radio").nth(2).bounding_box()["y"] > field.bounding_box()["y"]
        refresh = toolbar.get_by_role("button").last
        first, last = field.bounding_box(), refresh.bounding_box()
        assert abs(first["y"] - last["y"]) < 2, (first, last)
        assert first["x"] + first["width"] < last["x"], (first, last)
        assert min(first["height"], last["height"]) >= 44, (first, last)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    geometry()
    location = page.get_by_test_id("location-search").bounding_box()
    assert location["y"] + location["height"] < tabs.first.bounding_box()["y"]
    assert tabs.first.bounding_box()["height"] <= 40
    for index in range(4):
        icon = tabs.nth(index).get_by_test_id(re.compile("^tab-icon-"))
        expect(icon).to_be_visible()
        label = tabs.nth(index).get_by_text(tabs.nth(index).get_attribute("aria-label"), exact=True)
        icon_box, label_box = icon.bounding_box(), label.bounding_box()
        assert icon_box["y"] + icon_box["height"] <= label_box["y"] + 1
    assert page.get_by_test_id("app-header").bounding_box()["height"] <= 60
    assert toolbar.get_by_role("textbox").evaluate("(el) => getComputedStyle(el).backgroundColor") == "rgb(237, 243, 229)"
    expect(page.get_by_test_id("category-groups")).to_be_visible(timeout=20000)
    food_overflow = page.get_by_role("button", name="Още групи")
    food_overflow.click()
    expect(page.get_by_role("menu").get_by_role("menuitem").first).to_be_visible()
    page.get_by_role("button", name="Отказ", exact=True).click(position={"x": 5, "y": 5})
    expect(page.get_by_role("menu")).to_have_count(0)
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
    menu = page.get_by_role("menu")
    expect(menu.get_by_role("menuitem").first).to_be_visible()
    menu.get_by_role("menuitem").first.click()
    expect(menu).to_have_count(0)
    expect(overflow).to_have_attribute("aria-expanded", "false")
    page.screenshot(path=args.output_dir / "technology.png")
    tabs.nth(2).click()
    geometry(fuel=True)
    assert [radio.get_attribute("aria-label") for radio in toolbar.get_by_role("radio").all()] == [
        "Бензин 95", "Бензин 98+", "Дизел", "Дизел +", "Автогаз",
    ]
    selected_fuel = toolbar.get_by_role("radio", name="Бензин 98+")
    selected_fuel.click()
    expect(selected_fuel).to_have_attribute("aria-checked", "true")
    expect(toolbar.get_by_role("radio")).to_have_count(5)
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
        settings = page.get_by_test_id("settings-columns")
        columns = [
            ("Език", "Тема", "Размер на шрифта"),
            ("Общи условия", "Политика за поверителност", "Изтрий данни"),
        ]
        boxes = [[settings.get_by_role("button", name=name, exact=True).bounding_box()
                  for name in column] for column in columns]
        for column in boxes:
            assert all(abs(box["x"] - column[0]["x"]) < 2 for box in column)
            assert [box["y"] for box in column] == sorted(box["y"] for box in column)
        assert boxes[0][0]["x"] < boxes[1][0]["x"]
        page.screenshot(path=args.output_dir / "settings.png")
        page.get_by_role("button", name="Тема", exact=True).click()
        return page.get_by_test_id("appearance-screen").get_by_role("radio")

    options = open_appearance()
    dark = page.get_by_test_id("appearance-screen").get_by_role("switch")
    expect(dark).to_have_count(1)
    expect(dark).to_have_accessible_name("Тъмен режим")
    dark.click()
    expect(dark).to_have_attribute("aria-checked", "true")
    dark.click()
    expect(dark).to_have_attribute("aria-checked", "false")
    retained = (1, 6, 9, 11, 12, 13, 15, 16)
    expect(options).to_have_count(len(retained))
    for number in retained:
        option = page.get_by_role("radio", name=f"Цветова комбинация {number}", exact=True)
        option.click()
        expect(option).to_have_attribute("aria-checked", "true")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=args.output_dir / "appearance.png")
    page.reload()
    open_appearance()
    expect(page.get_by_role("radio", name="Цветова комбинация 16", exact=True)).to_have_attribute("aria-checked", "true")
    page.evaluate("""localStorage.setItem("spestovnik-preferences",
        JSON.stringify({language: "bg", palette: 16}))""")
    page.reload()
    open_appearance()
    expect(page.get_by_role("radio", name="Цветова комбинация 1", exact=True)).to_have_attribute("aria-checked", "true")
    assert not errors, errors
    browser.close()
print("Catalogue toolbar dry run passed at standard and narrow widths in six languages.")
