#!/usr/bin/env python3
"""Generate the site icons from the checked-in favicon source image.

The production build copies static/ into dist/, so the generated favicon files
live under static/ rather than at the repository root. The source image is a
square Srivan-style mark supplied by the site owner.

    python3 tools/make_favicon.py
"""
import base64
import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install --break-system-packages Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
ASSETS = STATIC / "assets"
SOURCE = ASSETS / "favicon-source.png"


def source_image():
    if not SOURCE.exists():
        sys.exit(f"favicon source missing: {SOURCE}")
    img = Image.open(SOURCE).convert("RGBA")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    return img.crop((left, top, left + side, top + side))


def render(img, size):
    return img.resize((size, size), Image.LANCZOS)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    STATIC.mkdir(parents=True, exist_ok=True)
    img = source_image()
    made = []

    for size, name in [(96, "assets/favicon-96.png"),
                       (192, "assets/favicon-192.png"),
                       (180, "assets/apple-touch-icon.png")]:
        p = STATIC / name
        render(img, size).save(p, "PNG", optimize=True)
        made.append((name, p.stat().st_size))

    ico = STATIC / "favicon.ico"
    render(img, 64).save(ico, "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    made.append(("favicon.ico", ico.stat().st_size))

    png = (ASSETS / "favicon-192.png").read_bytes()
    encoded = base64.b64encode(png).decode("ascii")
    svg = ASSETS / "favicon.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192" role="img" aria-label="Platform Ops">\n'
        f'  <image href="data:image/png;base64,{encoded}" width="192" height="192"/>\n'
        '</svg>\n',
        encoding="utf-8",
    )
    made.append(("assets/favicon.svg", svg.stat().st_size))

    for name, n in made:
        print(f"  {n:>7,} B  static/{name}")
    print(f"wrote {len(made)} icon file(s) from static/assets/favicon-source.png")


if __name__ == "__main__":
    main()
