#!/usr/bin/env python3
"""Render the README's Mermaid data-flow diagram to SVG, light and dark.

    python3 tools/make_arch_svg.py

NOT part of build.sh, for the same reason make_og_card.py is not: this needs
Playwright and a copy of Mermaid, and the output is a committed asset rather
than build output. Run it when the diagram in tools/README.base.md changes.

WHY IT IS DONE THIS WAY
-----------------------
GitHub renders Mermaid itself, so the README diagram needs nothing. The site
has no renderer, and shipping one is not an option — mermaid.min.js is about
3.3 MB, larger than the entire site, and it would have to come off a CDN,
which is the one thing the site's own architecture page says it never does.

So Mermaid runs once, here, and the site gets a plain inline SVG: same source
of truth as the README, zero JavaScript for the reader.

Two files come out because Mermaid bakes literal colours into the SVG and
cannot be re-themed with CSS variables afterwards. The page shows one and
hides the other, which is explicit and correct in both themes.

build_colophon.py refuses to build if the committed SVG does not match the
Mermaid source it came from, so an edited diagram cannot ship stale — the
build stops and tells you to run this.

REQUIREMENTS
------------
    pip install playwright && playwright install chromium
    npm pack mermaid        # extract the tarball into tools/.mermaid/

Point PO_MERMAID at the extracted package, or let it find it next to this
script under .mermaid/.
"""
import base64
import hashlib
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

SRC_MD = TOOLS / "README.base.md"
OUT = ROOT / "assets" / "arch"
LIB_DIR = pathlib.Path(os.environ.get("PO_MERMAID") or (TOOLS / ".mermaid"))
FONT_DIR = pathlib.Path(os.environ.get("PO_FONTS") or (TOOLS / ".fontcache"))
FONT_FILE = "dm-mono-latin-400-normal.woff2"
FONT_FAMILY = "DM Mono"

# Straight off the site's own palette, so the diagram sits in the page rather
# than on top of it. Keys are Mermaid's, values are topic.css's.
THEMES = {
    "light": {
        "background": "#f2f0eb", "primaryColor": "#f8f7f4",
        "primaryBorderColor": "rgba(0,0,0,.22)", "primaryTextColor": "#1c1f26",
        "lineColor": "rgba(0,0,0,.34)", "secondaryColor": "#e4e0d8",
        "tertiaryColor": "#e4e0d8", "clusterBkg": "rgba(0,0,0,.03)",
        "clusterBorder": "rgba(0,0,0,.12)", "textColor": "#1c1f26",
        "titleColor": "#1c1f26", "edgeLabelBackground": "#f2f0eb",
    },
    "dark": {
        "background": "#0c0e12", "primaryColor": "#181b22",
        "primaryBorderColor": "rgba(255,255,255,.24)", "primaryTextColor": "#e7e5df",
        "lineColor": "rgba(255,255,255,.34)", "secondaryColor": "#14161c",
        "tertiaryColor": "#14161c", "clusterBkg": "rgba(255,255,255,.03)",
        "clusterBorder": "rgba(255,255,255,.12)", "textColor": "#e7e5df",
        "titleColor": "#eeece6", "edgeLabelBackground": "#0c0e12",
    },
}


def mermaid_source():
    md = SRC_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```mermaid\n(.*?)\n```", md, re.S)
    assert len(blocks) == 1, (
        f"{SRC_MD.name}: expected exactly one mermaid block, found {len(blocks)}. "
        "This script and build_colophon.py both assume the architecture diagram "
        "is the only one.")
    return blocks[0].strip()


def find_lib():
    for p in LIB_DIR.rglob("mermaid.min.js"):
        return p
    raise SystemExit(
        f"mermaid.min.js not found under {LIB_DIR}.\n"
        f"Run:  npm pack mermaid      (extract the tarball into {LIB_DIR})\n"
        f"      or set PO_MERMAID to wherever it already is.\n"
        f"This is only needed when the diagram changes — the rendered SVGs are "
        f"committed, so a normal build does not need Mermaid at all.")


def font_face():
    """DM Mono, embedded, because Mermaid measures text to size its boxes.

    This is the make_og_card.py trap in a different costume. Mermaid lays every
    node out against the font the RENDERING browser has. Headless Chromium has
    no DM Mono, so it silently measured a fallback, sized the boxes to that,
    and the site — which does load DM Mono — drew wider text into boxes built
    for a narrower face. Every second line was clipped. Embedding the real font
    and asserting it loaded is the only way to know the measurements are the
    ones the reader will see.
    """
    for p in FONT_DIR.rglob(FONT_FILE):
        b64 = base64.b64encode(p.read_bytes()).decode()
        return (f"@font-face{{font-family:'{FONT_FAMILY}';font-style:normal;"
                f"font-weight:400;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    raise SystemExit(
        f"{FONT_FILE} not found under {FONT_DIR}.\n"
        f"Run:  npm pack @fontsource/dm-mono   (extract the tarball into {FONT_DIR})\n"
        f"Without the real font Mermaid sizes every box to a fallback face and the "
        f"labels are clipped on the site.")


def render(src):
    from playwright.sync_api import sync_playwright

    lib = find_lib().read_text(encoding="utf-8")
    face = font_face()
    exe = os.environ.get("PO_CHROMIUM", "/opt/pw-browsers/chromium")
    out = {}
    with sync_playwright() as p:
        browser = (p.chromium.launch(executable_path=exe)
                   if pathlib.Path(exe).exists() else p.chromium.launch())
        for name, variables in THEMES.items():
            page = browser.new_page(viewport={"width": 1100, "height": 900})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.set_content(
                f"<!doctype html><meta charset='utf-8'><style>{face}</style>"
                f"<div id='o' style=\"font-family:'{FONT_FAMILY}',monospace\">.</div>"
                f"<script>{lib}</script><script>\n"
                f"document.fonts.load(\"12px '{FONT_FAMILY}'\").then(function(){{\n"
                f"  return document.fonts.ready;\n"
                f"}}).then(function(){{\n"
                f"  window.__loaded = [...document.fonts].filter(f=>f.status==='loaded')"
                f".map(f=>f.family);\n"
                f"  return mermaid.render('a', {json.dumps(src)});\n"
                f"}}).then(function(r){{window.__svg=r.svg;window.__ok=true;}})"
                ".catch(function(e){window.__err=String(e&&e.message||e);window.__ok=true;});"
                # htmlLabels:false matters more than it looks. By default Mermaid
                # puts label text in a <foreignObject>, which is real HTML living
                # in the host document — so the page's own stylesheet applies to
                # it. Mermaid sized every box against ITS line-height; the
                # colophon page then restyled the text inside those boxes and the
                # second line of every two-line label was clipped. SVG <text> is
                # out of reach of the page's CSS, so the measurement holds.
                f"\nmermaid.initialize({{startOnLoad:false,securityLevel:'strict',"
                f"theme:'base',themeVariables:{json.dumps(variables)},"
                f"flowchart:{{htmlLabels:false,useMaxWidth:false}},"
                f"fontFamily:\"'{FONT_FAMILY}',ui-monospace,monospace\"}});"
                "</script>")
            page.wait_for_function("window.__ok === true", timeout=60000)
            err = page.evaluate("window.__err || null")
            assert not err, f"mermaid failed to render the {name} diagram: {err}"
            assert not errors, f"page errors while rendering {name}: {errors[:2]}"

            loaded = page.evaluate("window.__loaded || []")
            assert FONT_FAMILY in loaded, (
                f"{name}: '{FONT_FAMILY}' did not load, so Mermaid measured a fallback "
                f"face and the boxes would be the wrong size. Loaded: {sorted(set(loaded))}")

            out[name] = clean(page.evaluate("window.__svg"), name)
            page.close()
        browser.close()
    return out


def clean(svg, theme):
    """Make the SVG safe to inline and let the page's CSS size it.

    Mermaid stamps an id and an inline max-width on the root element. Two of
    these end up in one document, so the ids have to differ, and the inline
    max-width would beat any stylesheet rule.
    """
    svg = re.sub(r'\sid="a"', f' id="arch-{theme}"', svg, count=1)
    svg = re.sub(r'\sstyle="[^"]*max-width[^"]*"', "", svg, count=1)
    svg = svg.replace("<svg ", f'<svg class="arch-svg arch-{theme}" ', 1)
    # Mermaid scopes its internal CSS by that root id, so it has to follow.
    svg = svg.replace("#a ", f"#arch-{theme} ")
    assert "viewBox" in svg, f"{theme}: rendered SVG has no viewBox, it would not scale"
    return svg


if __name__ == "__main__":
    src = mermaid_source()
    svgs = render(src)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in svgs.items():
        (OUT / f"dataflow-{name}.svg").write_text(svg, encoding="utf-8")
        print(f"  {len(svg) // 1024:3d} KB  assets/arch/dataflow-{name}.svg")
    digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
    (OUT / "dataflow.sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"source sha256 {digest[:16]}… — build_colophon.py checks this")
