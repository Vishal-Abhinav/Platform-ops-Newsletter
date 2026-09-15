#!/usr/bin/env python3
"""Generate the 1200x630 social cards under assets/og/.

    python3 tools/make_og_card.py            # any issue missing a card
    python3 tools/make_og_card.py --all      # regenerate every card
    python3 tools/make_og_card.py 58 59 60   # just these

NOT part of build.sh. Cards are committed binary assets, not build output —
regenerating them every build would churn ~200 KB per card in git history for
no reason. Run this when you add an issue, or when the footer URL changes.

REQUIREMENTS
------------
Playwright with Chromium, and the three webfonts. The fonts are the fiddly
part: they are not installed on most systems, and if they are missing the
render silently falls back to a default face and bakes the WRONG typography
into the PNG — with no error. So this script fetches them, embeds them as
base64, and then ASSERTS that the rendered text actually used them.

    pip install playwright && playwright install chromium
    npm pack @fontsource/bebas-neue @fontsource/dm-mono @fontsource/manrope

Point FONT_DIR at the extracted packages, or let it find them next to this
script under .fontcache/.
"""
import argparse
import base64
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT / "tools"))

from siteconf import BASE                      # noqa: E402
from build_feed import ISSUES                  # noqa: E402

OUT = ROOT / "assets" / "og"
FONT_DIR = pathlib.Path(os.environ.get("PO_FONTS") or (ROOT / "tools" / ".fontcache"))

FONTS = {
    "Bebas Neue": "bebas-neue-latin-400-normal.woff2",
    "DM Mono": "dm-mono-latin-400-normal.woff2",
    "Manrope": "manrope-latin-400-normal.woff2",
}

# The footer is the canonical host, without the scheme.
FOOTER = BASE.split("//", 1)[1].rstrip("/")


def font_face(name, filename):
    for p in FONT_DIR.rglob(filename):
        b64 = base64.b64encode(p.read_bytes()).decode()
        return (f"@font-face{{font-family:'{name}';font-style:normal;font-weight:400;"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    raise SystemExit(
        f"font {filename} not found under {FONT_DIR}.\n"
        f"Run:  npm pack @fontsource/bebas-neue @fontsource/dm-mono @fontsource/manrope\n"
        f"      (extract the tarballs into {FONT_DIR})\n"
        f"Without the real fonts the card renders in a fallback face and looks wrong.")


def card_html(num, title, blurb, month_year):
    faces = "".join(font_face(n, f) for n, f in FONTS.items())
    # The card has a fixed height, so the blurb budget depends on how many
    # lines the title already took. A long title wraps to two, which leaves
    # room for two lines of blurb rather than three.
    two_line_title = len(title) > 30
    budget = 108 if two_line_title else 152
    blurb = blurb.strip()
    if len(blurb) > budget:
        cut = blurb[:budget].rsplit(" ", 1)[0]
        blurb = cut.rstrip(" ,;:—-") + "…"
    esc = lambda s: (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1200px;height:630px;overflow:hidden;}}
body{{background:#0c0e12;position:relative;font-family:'Manrope',sans-serif;}}

/* circuit grid — the same motif as the knowledge map's terminal backdrop */
.grid{{position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px);
  background-size:64px 64px;}}
.trace{{position:absolute;background:rgba(255,255,255,.05);}}
.node{{position:absolute;width:7px;height:7px;border-radius:50%;
  border:1px solid rgba(255,255,255,.10);}}

/* the two glows that give the card depth */
.glow-r{{position:absolute;width:760px;height:760px;right:-230px;top:-330px;border-radius:50%;
  background:radial-gradient(circle,rgba(229,57,53,.20),transparent 62%);}}
.glow-c{{position:absolute;width:640px;height:640px;right:-150px;bottom:-290px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,194,212,.13),transparent 62%);}}

.num{{position:absolute;right:52px;bottom:-40px;font-family:'Bebas Neue',sans-serif;
  font-size:300px;line-height:1;color:rgba(255,255,255,.035);letter-spacing:-4px;}}

.wrap{{position:absolute;inset:0;padding:62px 72px;display:flex;flex-direction:column;}}
.brand{{display:flex;align-items:center;gap:17px;}}
.dot{{width:15px;height:15px;border-radius:50%;background:#e53935;
  box-shadow:0 0 22px rgba(229,57,53,.85);}}
.brand span{{font-family:'Bebas Neue',sans-serif;font-size:43px;letter-spacing:7px;color:#f2f0eb;}}
.kicker{{font-family:'DM Mono',monospace;font-size:14px;letter-spacing:5.5px;color:#84cc16;
  margin:11px 0 0 32px;}}
.meta{{font-family:'DM Mono',monospace;font-size:16px;letter-spacing:4px;
  color:rgba(255,255,255,.42);margin-top:29px;}}
h1{{font-family:'Bebas Neue',sans-serif;font-size:{74 if two_line_title else 86}px;
  line-height:.96;letter-spacing:.5px;color:#fff;margin-top:14px;max-width:960px;}}
.blurb{{font-size:23px;line-height:1.52;color:rgba(255,255,255,.60);
  margin-top:26px;max-width:800px;}}
.foot{{margin-top:auto;}}
.rule{{display:flex;height:5px;width:264px;border-radius:3px;overflow:hidden;}}
.rule i{{flex:1;}}
.url{{font-family:'DM Mono',monospace;font-size:16px;letter-spacing:1.4px;
  color:rgba(255,255,255,.34);margin-top:24px;}}
</style></head><body>
<div class="grid"></div>
<div class="trace" style="left:330px;top:0;width:1px;height:196px;"></div>
<div class="trace" style="left:330px;top:196px;width:216px;height:1px;"></div>
<div class="trace" style="left:546px;top:196px;width:1px;height:132px;"></div>
<div class="trace" style="left:840px;top:392px;width:1px;height:238px;"></div>
<div class="trace" style="left:648px;top:392px;width:192px;height:1px;"></div>
<div class="trace" style="left:72px;top:456px;width:150px;height:1px;"></div>
<div class="node" style="left:327px;top:193px;"></div>
<div class="node" style="left:543px;top:325px;"></div>
<div class="node" style="left:837px;top:389px;"></div>
<div class="node" style="left:219px;top:453px;"></div>
<div class="glow-r"></div><div class="glow-c"></div>
<div class="num">{num}</div>
<div class="wrap">
  <div class="brand"><i class="dot"></i><span>PLATFORM OPS</span></div>
  <div class="kicker">MONTHLY TECHNICAL NEWSLETTER</div>
  <div class="meta">ISSUE #{num:03d} &nbsp;·&nbsp; {month_year.upper()}</div>
  <h1>{esc(title.upper())}</h1>
  <div class="blurb">{esc(blurb)}</div>
  <div class="foot">
    <div class="rule"><i style="background:#e53935"></i><i style="background:#f59e0b"></i
      ><i style="background:#00c2d4"></i><i style="background:#84cc16"></i></div>
    <div class="url">{esc(FOOTER)}</div>
  </div>
</div></body></html>"""


def render(cards):
    """One browser, all cards. Asserts the real fonts actually loaded."""
    from playwright.sync_api import sync_playwright

    exe = os.environ.get("PO_CHROMIUM", "/opt/pw-browsers/chromium")
    made = []
    with sync_playwright() as p:
        browser = (p.chromium.launch(executable_path=exe)
                   if pathlib.Path(exe).exists() else p.chromium.launch())
        page = browser.new_page(viewport={"width": 1200, "height": 630},
                                device_scale_factor=1)
        for num, title, blurb, month_year in cards:
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                             encoding="utf-8") as fh:
                fh.write(card_html(num, title, blurb, month_year))
                tmp = fh.name
            page.goto(f"file://{tmp}")
            page.wait_for_timeout(450)

            # A missing webfont does not error — it silently substitutes and
            # bakes the wrong face into a PNG nobody re-checks. Verify.
            loaded = page.evaluate(
                "() => [...document.fonts].filter(f=>f.status==='loaded')"
                ".map(f=>f.family)")
            for fam in FONTS:
                assert fam in loaded, (
                    f"issue #{num}: '{fam}' did not load — the card would render "
                    f"in a fallback face. Loaded: {sorted(set(loaded))}")

            OUT.mkdir(parents=True, exist_ok=True)
            dest = OUT / f"i{num:03d}.png"
            page.screenshot(path=str(dest))
            os.unlink(tmp)
            made.append((dest, dest.stat().st_size))
        browser.close()
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("issues", nargs="*", type=int)
    ap.add_argument("--all", action="store_true",
                    help="regenerate every card, not just missing ones")
    args = ap.parse_args()

    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    todo = []
    for num, _path, title, blurb, when in ISSUES:
        if args.issues and num not in args.issues:
            continue
        if not args.issues and not args.all and (OUT / f"i{num:03d}.png").exists():
            continue
        todo.append((num, title, blurb, f"{MONTHS[when.month - 1]} {when.year}"))

    if not todo:
        print("every issue already has a card (use --all to regenerate)")
        return 0

    print(f"rendering {len(todo)} card(s), footer: {FOOTER}")
    for dest, size in render(sorted(todo)):
        print(f"  {size // 1024:4d} KB  {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
