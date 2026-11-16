"""Synthetic, clearly labelled test images; never retailer/price evidence."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def barcode_image(code="4006381333931"):
    left = [
        "0001101",
        "0011001",
        "0010011",
        "0111101",
        "0100011",
        "0110001",
        "0101111",
        "0111011",
        "0110111",
        "0001011",
    ]
    parity = [
        "LLLLLL",
        "LLGLGG",
        "LLGGLG",
        "LLGGGL",
        "LGLLGG",
        "LGGLLG",
        "LGGGLL",
        "LGLGLG",
        "LGLGGL",
        "LGGLGL",
    ]
    invert = lambda s: "".join("1" if c == "0" else "0" for c in s)
    bits = (
        "101"
        + "".join(
            left[int(d)] if p == "L" else invert(left[int(d)])[::-1]
            for d, p in zip(code[1:7], parity[int(code[0])])
        )
        + "01010"
        + "".join(invert(left[int(d)]) for d in code[7:])
        + "101"
    )
    image = Image.new("RGB", (1280, 720), "white")
    draw = ImageDraw.Draw(image)
    # Use wide, integer-aligned modules and generous quiet zones. This makes
    # the synthetic EAN-13 reliably detectable after Android photo decoding.
    module_width = 9
    left_edge = (image.width - len(bits) * module_width) // 2
    for i, bit in enumerate(bits):
        if bit == "1":
            x = left_edge + i * module_width
            draw.rectangle((x, 110, x + module_width - 1, 530), fill="black")
    draw.text(
        (left_edge, 590), "SIMULATION " + code, font=ImageFont.truetype(FONT, 23), fill="black"
    )
    return image


def receipt_image():
    image = Image.new("RGB", (900, 680), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 34)
    for i, line in enumerate(
        [
            "СИМУЛАЦИЯ - НЕ Е ИСТИНСКА БЕЛЕЖКА",
            "Тестов магазин A",
            "МЛЯКО 2 x 1.10",
            "МЛЯКО 2.20 EUR",
            "ОЛИО 3.00 EUR",
            "ОБЩО 5.20 EUR",
            "В БРОЙ 6.00 EUR",
            "РЕСТО 0.80 EUR",
        ]
    ):
        draw.text((25, 25 + i * 75), line, font=font, fill="black")
    return image


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "backend/tests/fixtures")
    parser.add_argument("--video", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    barcode_image().save(args.output / "simulation-ean13.png")
    receipt_image().save(args.output / "simulation-receipt.png")
    if args.video:
        image = barcode_image().convert("YCbCr")
        y, cb, cr = image.split()
        frame = (
            y.tobytes()
            + cb.resize((320, 240)).tobytes()
            + cr.resize((320, 240)).tobytes()
        )
        with (args.output / "simulation-camera.y4m").open("wb") as f:
            f.write(b"YUV4MPEG2 W640 H480 F5:1 Ip A1:1 C420jpeg\n")
            for _ in range(10):
                f.write(b"FRAME\n" + frame)
    print("Synthetic barcode/receipt fixtures prepared; no live data")
