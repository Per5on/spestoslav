"""Rasterize Ionicons sources and export an additive thumbnail database seed."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/symbolic-thumbnails"
VENDOR = ROOT / "mobile/node_modules/@expo/vector-icons/build/vendor/react-native-vector-icons"
ICONS = {
    "groceries": "basket-outline", "dairy-eggs": "egg-outline",
    "bakery-breakfast": "cafe-outline", "produce": "leaf-outline",
    "meat-fish": "fish-outline", "pantry": "nutrition-outline", "spices-drinks": "wine-outline",
    "technology": "laptop-outline", "mobile": "phone-portrait-outline",
    "major-appliances": "snow-outline", "small-appliances": "cafe-outline",
    "tv-computing": "tv-outline", "smart-home-mobility": "home-outline", "fuel": "car-outline",
}

DDL = """CREATE TABLE IF NOT EXISTS symbolic_thumbnails (
    code text PRIMARY KEY CHECK (code ~ '^[a-z0-9-]+$'),
    width smallint NOT NULL CHECK (width BETWEEN 1 AND 320),
    height smallint NOT NULL CHECK (height BETWEEN 1 AND 280),
    data bytea NOT NULL CHECK (octet_length(data) BETWEEN 1 AND 65536),
    sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    source_url text NOT NULL,
    license text NOT NULL CHECK (license = 'MIT')
)"""


def rasterize():
    from PIL import Image, ImageDraw, ImageFont

    glyphs = json.loads((VENDOR / "glyphmaps/Ionicons.json").read_text())
    font = ImageFont.truetype(str(VENDOR / "Fonts/Ionicons.ttf"), 88)
    for code, icon in ICONS.items():
        image = Image.new("RGB", (160, 140), "#edf3e5")
        ImageDraw.Draw(image).text((80, 70), chr(glyphs[icon]), fill="#19562a", font=font, anchor="mm")
        image.save(DATA / f"{code}.webp", format="WEBP", lossless=True)


def seed():
    from PIL import Image

    statements = [DDL]
    for code, icon in ICONS.items():
        path = DATA / f"{code}.webp"
        data = path.read_bytes()
        with Image.open(path) as image:
            image.load()
            assert image.format == "WEBP" and image.width <= 320 and image.height <= 280
            width, height = image.size
        assert 0 < len(data) <= 65536
        digest = hashlib.sha256(data).hexdigest()
        source = f"https://ionic.io/ionicons?search={icon}"
        statements.append(
            "INSERT INTO symbolic_thumbnails (code, width, height, data, sha256, source_url, license) "
            f"VALUES ('{code}', {width}, {height}, decode('{data.hex()}', 'hex'), '{digest}', '{source}', 'MIT') "
            "ON CONFLICT (code) DO UPDATE SET width = excluded.width, height = excluded.height, "
            "data = excluded.data, sha256 = excluded.sha256, source_url = excluded.source_url, license = excluded.license"
        )
    return statements


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rasterize", action="store_true")
    args = parser.parse_args()
    if args.rasterize:
        rasterize()
    print(json.dumps(seed()))
