#!/usr/bin/env python3
"""Generate the site icons. Manual step, like make_og_card.py — not in build.sh.

WHY THESE EXIST
---------------
The site shipped with no favicon at all: zero <link rel="icon"> across 878
pages, and /favicon.ico returned 404. Google therefore drew its generic globe
next to every result, which is what "the logo shows small" looks like in a
search listing.

WHY THESE SIZES
---------------
Google's favicon requirement is a square whose side is a MULTIPLE OF 48
(48, 96, 144, 192 …), served at a crawlable URL. That last part matters more
than it sounds: srivantechnologies.com already carries this exact mark, but
declares it as a `data:` URI with 32px and 512px PNG fallbacks — a data URI is
inline rather than fetchable, and neither 32 nor 512 is a multiple of 48, so
Google has nothing it can use and falls back to the globe there too. Same mark,
same outcome, different cause than "no icon".

THE MARK
--------
Taken from srivantechnologies.com so the two properties are visibly one brand:
an ink rounded square with three ascending crimson bars. Platform Ops is a
subdomain of Srivan Technologies and Google already groups them under one site
name, so a different mark here would read as a different organisation.

Geometry is expressed on a 32-unit grid and scaled, so every size is the same
drawing rather than a resample of one bitmap.

    python3 tools/make_favicon.py
"""
import pathlib
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install --break-system-packages Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

INK = (8, 9, 12, 255)          # --ink    #08090c
CRIMSON = (229, 57, 53, 255)   # --crimson #e53935

# (x, y, w, h) on a 32x32 grid, matching srivantechnologies.com exactly.
BARS = [(0.96, 22.72, 30.08, 4.16),
        (4.16, 15.36, 23.68, 4.16),
        (7.36, 8.00, 17.28, 4.16)]
BAR_R = 1.75
CARD_R = 7.04

SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" aria-label="Platform Ops">
  <rect width="32" height="32" rx="{CARD_R}" fill="#08090c"/>
''' + "".join(
    f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{BAR_R}" fill="#e53935"/>\n'
    for x, y, w, h in BARS) + '</svg>\n'


def render(size, ss=8):
    """Draw at `ss`x and downsample — the bars are thin, so aliasing shows."""
    s, k = size * ss, (size * ss) / 32.0
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=CARD_R * k, fill=INK)
    for x, y, w, h in BARS:
        d.rounded_rectangle([x * k, y * k, (x + w) * k, (y + h) * k],
                            radius=BAR_R * k, fill=CRIMSON)
    return img.resize((size, size), Image.LANCZOS)


def main():
    ASSETS.mkdir(exist_ok=True)
    made = []

    # Multiples of 48 are what Google will accept; 192 doubles as the Android
    # icon. 180 is Apple's, and is not required to follow Google's rule.
    for size, name in [(96, "assets/favicon-96.png"),
                       (192, "assets/favicon-192.png"),
                       (180, "assets/apple-touch-icon.png")]:
        p = ROOT / name
        render(size).save(p, "PNG", optimize=True)
        made.append((name, p.stat().st_size))

    # /favicon.ico at the root: browsers request it whether or not it is
    # declared, and it was 404ing on every page load.
    ico = ROOT / "favicon.ico"
    render(64).save(ico, "ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    made.append(("favicon.ico", ico.stat().st_size))

    # An SVG for crisp rendering, as a real file rather than a data: URI so a
    # crawler can actually fetch it.
    svg = ASSETS / "favicon.svg"
    svg.write_text(SVG, encoding="utf-8")
    made.append(("assets/favicon.svg", svg.stat().st_size))

    for name, n in made:
        print(f"  {n:>7,} B  {name}")
    print(f"wrote {len(made)} icon file(s)")


if __name__ == "__main__":
    main()
