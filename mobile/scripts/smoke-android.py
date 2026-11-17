"""Verify the release's revised navigation and name-only locality on Android 10."""

import os, re, subprocess, time, xml.etree.ElementTree as ET
import json
import atexit
from pathlib import Path


def adb(*args):
    return subprocess.check_output(["adb", *args], text=True)


def nodes():
    adb("shell", "uiautomator", "dump", "/sdcard/window.xml")
    return list(ET.fromstring(adb("shell", "cat", "/sdcard/window.xml")).iter("node"))


def label(n):
    return n.get("text") or n.get("content-desc", "")


def wait_resource(resource, timeout=45):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        matches = [n for n in nodes() if n.get("resource-id", "").endswith(resource)]
        if matches:
            return matches[0]
        time.sleep(1)
    raise AssertionError(f"Resource did not load after {timeout}s: {resource}")


def bounds(n):
    return list(map(int, re.findall(r"\d+", n.get("bounds", ""))))


def tap_node(n):
    x1, y1, x2, y2 = bounds(n)
    adb("shell", "input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))
    time.sleep(0.7)


def tap(text):
    matches = [n for n in nodes() if text in (n.get("text"), n.get("content-desc"))]
    assert matches, f"Missing control: {text}"
    tap_node(matches[0])


def wait_text(text, timeout=75):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        matches = [n for n in nodes() if text in (n.get("text"), n.get("content-desc"))]
        if matches:
            return matches[0]
        time.sleep(1)
    raise AssertionError(f"Missing text after {timeout}s: {text}")


sequence = os.environ.get("PREVIEW_SEQUENCE")
if not sequence or not re.fullmatch(r"[0-9]{3}", sequence):
    raise RuntimeError("PREVIEW_SEQUENCE must be supplied from mobile/preview.json")

def save_diagnostics():
    # Capture evidence even when an assertion fails, before the emulator exits.
    try:
        Path("android-smoke.log").write_text(adb("logcat", "-d"))
        Path("android-preview-" + sequence + ".png").write_bytes(
            subprocess.check_output(["adb", "exec-out", "screencap", "-p"])
        )
        adb("shell", "uiautomator", "dump", "/sdcard/window.xml")
        Path("android-smoke-window.xml").write_text(adb("shell", "cat", "/sdcard/window.xml"))
    except (subprocess.SubprocessError, OSError) as error:
        print("Could not save Android diagnostics:", error)


atexit.register(save_diagnostics)
adb("logcat", "-c")
adb("shell", "am", "start", "-W", "-n", "bg.spestoslav.preview/.MainActivity")
wait_text("Спестовник", 20)
initial = nodes()
order = ["Храни", "Техника", "Горива", "Моят списък"]
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
assert bounds(stores)[0] < bounds(products)[0] < bounds(refresh)[0]
# Check actual decoded remote images, not merely an Image view or an icon fallback.
photos = next(n for n in nodes() if "Примерни снимки" in label(n))
tap_node(photos)
wait_resource("thumbnail-loaded-demo-milk")
assert not any(n.get("resource-id", "").endswith("thumbnail-fallback-demo-milk") for n in nodes())
tap("Техника")
wait_resource("thumbnail-loaded-demo-laptop")
assert not any(n.get("resource-id", "").endswith("thumbnail-fallback-demo-laptop") for n in nodes())
tap("Храни")
tap_node(next(n for n in nodes() if "Примерни снимки" in label(n)))
for tab in ["Техника", "Горива", "Моят списък"]:
    tap(tab)
    assert any(label(n) == "София" for n in nodes())
assert any("Списъкът е празен" in label(n) for n in nodes())
tap("Горива");tap("Гориво")
for grade in ("Бензин 95", "Бензин 98+", "Дизел", "Дизел +", "Автогаз"):
    assert any(label(n) == grade for n in nodes()), grade
tap("Бензин 95")
tap("Отвори менюто")
tap("Сканирай")
wait_text("Търсене по баркод", 20)
# Exercise actual Android permission denial and a camera preview, not just its menu.
adb("shell", "pm", "revoke", "bg.spestoslav.preview", "android.permission.CAMERA")
tap("Отвори камерата")
deadline=time.monotonic()+15
while time.monotonic()<deadline:
    options=nodes()
    deny=[n for n in options if label(n).casefold() in ("deny", "don't allow") or n.get("resource-id", "").endswith("id/permission_deny_button")]
    if deny:
        tap_node(deny[0]);break
    time.sleep(.5)
else:
    raise AssertionError("Android camera permission dialog did not appear")
wait_text("Камерата е забранена. Разрешете достъп в настройките или въведете кода.", 15)
wait_text("Търсене по баркод", 15)
adb("shell", "pm", "grant", "bg.spestoslav.preview", "android.permission.CAMERA")
tap("Отвори камерата")
wait_text("Отказ", 15)
time.sleep(2)
assert not any("Камерата или снимката не е достъпна" in label(n) for n in nodes())
tap("Отказ")
# The only fixture in Downloads contains a synthetic valid EAN. Decode through ML Kit.
tap("Баркод от снимка")
deadline=time.monotonic()+45
opened_downloads = False
while time.monotonic()<deadline:
    options=nodes()
    if not opened_downloads and any(label(n) == "No items" for n in options):
        # AOSP Recent can omit adb-seeded media. Browse its real Downloads file.
        tap("Show roots")
        tap_node(wait_text("Downloads", 10))
        opened_downloads = True
        continue
    names=[n for n in options if "spestovnik-simulation-ean13" in label(n)]
    thumbs=[n for n in options if n.get("resource-id", "").endswith("id/icon_thumb")]
    if names or thumbs:
        tap_node((names or thumbs)[0])
        break
    time.sleep(1)
else:
    raise AssertionError("Synthetic barcode image missing in Android picker: "+str([label(n) for n in options]))
wait_text("4006381333931",40)
tap("Отвори менюто")
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
# About must show installed metadata, not a hardcoded config label.
tap("Отвори менюто")
tap("За приложението")
wait_text("© 2026 Vimp. All rights reserved.")
package=adb("shell","dumpsys","package","bg.spestoslav.preview")
installed_version=re.search(r"versionName=(\S+)",package).group(1)
installed_code=re.search(r"versionCode=(\d+)",package).group(1)
metadata=json.loads(Path("preview.json").read_text())
assert installed_version==metadata["version"] and int(installed_code)==int(metadata["sequence"])
wait_text(f"Версия {installed_version} ({installed_code})")
tap("Отвори менюто");tap("Настройки");tap("Език");tap("English")
tap("Open menu");tap("About")
wait_text(f"Version {installed_version} ({installed_code})")
wait_text("© 2026 Vimp. All rights reserved.")
tap("Open menu");tap("Settings");tap("Language");tap("Български")
tap("Храни")
assert adb("shell", "pidof", "bg.spestoslav.preview").strip()
logs = adb("logcat", "-d")
assert "FATAL EXCEPTION" not in logs, logs
Path("android-smoke.log").write_text(logs)
with open(
    "android-preview-" + sequence + ".png", "wb"
) as f:
    f.write(subprocess.check_output(["adb", "exec-out", "screencap", "-p"]))
print(
    "Android 10 smoke passed: ordered tabs, no lower ribbon/Home, name-only locality, shared selection, decoded food/technology images, five fuel grades, list, three-dot menu and language choices."
)
