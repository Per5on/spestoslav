"""Verify the release's revised navigation and name-only locality on Android 10."""

import os, re, subprocess, time, xml.etree.ElementTree as ET
from pathlib import Path


def adb(*args):
    return subprocess.check_output(["adb", *args], text=True)


def nodes():
    adb("shell", "uiautomator", "dump", "/sdcard/window.xml")
    return list(ET.fromstring(adb("shell", "cat", "/sdcard/window.xml")).iter("node"))


def label(n):
    return n.get("text") or n.get("content-desc", "")


def bounds(n):
    return list(map(int, re.findall(r"\d+", n.get("bounds", ""))))


def tap_node(n):
    x1, y1, x2, y2 = bounds(n)
    adb("shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))
    time.sleep(0.7)


def tap(text):
    matches = [n for n in nodes() if label(n) == text]
    assert matches, f"Missing control: {text}"
    tap_node(matches[0])


def wait_text(text, timeout=75):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        matches = [n for n in nodes() if label(n) == text]
        if matches:
            return matches[0]
        time.sleep(1)
    raise AssertionError(f"Missing text after {timeout}s: {text}")


adb("logcat", "-c")
adb("shell", "am", "start", "-W", "-n", "bg.spestoslav.preview/.MainActivity")
wait_text("Спестовник", 20)
initial = nodes()
order = ["Храни", "ТЕХНИКА", "Горива", "Моят списък"]
positions = [bounds(next(n for n in initial if label(n) == name))[0] for name in order]
assert positions == sorted(positions)
assert not any(label(n) == "Дом" or label(n) == "МЕСТОПОЛОЖЕНИЕ" for n in initial)
tap("Изберете населено място")
tap_node(next(n for n in nodes() if n.get("class") == "android.widget.EditText"))
adb("shell", "input", "text", "Sofia")
tap_node(wait_text("София"))
toolbar = nodes()
products = next(n for n in toolbar if label(n) == "Продукти")
stores = next(n for n in toolbar if label(n).startswith("Магазини ("))
refresh = next(n for n in toolbar if label(n) == "Обнови")
assert (
    max(bounds(n)[1] for n in [products, stores, refresh])
    - min(bounds(n)[1] for n in [products, stores, refresh])
    < 4
)
assert bounds(products)[0] < bounds(stores)[0] < bounds(refresh)[0]
for tab in ["ТЕХНИКА", "Горива", "Моят списък"]:
    tap(tab)
    assert any(label(n) == "София" for n in nodes())
assert any("Списъкът е празен" in label(n) for n in nodes())
tap("Настройки")
tap("Сканирай")
assert any("Камерата" in label(n) for n in nodes())
tap("Настройки")
tap("Език")
names = {"English", "Deutsch", "Español", "Français", "Русский"}
seen = {label(n) for n in nodes()}
width, height = map(int, re.findall(r"\d+", adb("shell", "wm", "size"))[:2])
for _ in range(3):
    if names.issubset(seen):
        break
    adb(
        "shell",
        "input",
        "swipe",
        str(width // 2),
        str(int(height * 0.78)),
        str(width // 2),
        str(int(height * 0.35)),
        "300",
    )
    time.sleep(0.5)
    seen.update(label(n) for n in nodes())
assert names.issubset(seen), names - seen
tap("Храни")
assert adb("shell", "pidof", "bg.spestoslav.preview").strip()
logs = adb("logcat", "-d")
assert "FATAL EXCEPTION" not in logs, logs
Path("android-smoke.log").write_text(logs)
with open(
    "android-preview-" + os.environ.get("PREVIEW_SEQUENCE", "003") + ".png", "wb"
) as f:
    f.write(subprocess.check_output(["adb", "exec-out", "screencap", "-p"]))
print(
    "Android 10 smoke passed: ordered tabs, no lower ribbon/Home, name-only locality, shared selection, list, three-dot menu and language choices."
)
