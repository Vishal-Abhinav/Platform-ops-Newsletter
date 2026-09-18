#!/usr/bin/env python3
"""Draw brand/banner.svg — the animated masthead at the top of the README.

    python3 tools/make_banner.py

WHY IT IS GENERATED
-------------------
Same reason as everything else here: it carries numbers, and a number typed by
hand is a number that goes stale. The coverage bar at the bottom of the banner
is the real live/pipeline/planned split from taxonomy.py, so the picture on the
repo's front page cannot disagree with the site.

WHY IT IS AN SVG WITH CSS INSIDE IT
-----------------------------------
GitHub renders a README image through its own proxy, and an SVG referenced with
`![](brand/banner.svg)` is loaded as an IMAGE, not as part of the page. That has
two consequences that shape everything below:

  * Nothing outside the file exists. No webfonts — the four families this site
    self-hosts are unavailable here, so the type uses generic stacks and is
    laid out to survive whichever face the reader's machine picks. No external
    stylesheet, no script.
  * CSS animation inside the file still runs. `<style>` in the SVG root
    animates normally in an <img> context, which is why this moves at all.

WHERE IT LIVES, AND WHY NOT IN static/
--------------------------------------
`brand/` at the repo root, deliberately outside `static/`. Anything in
`static/` is copied into `dist/` and published to the website; this image is
for GitHub, and the website has no use for it. Keeping it out of `static/` is
the difference between an asset and a stray file on the live site.
"""
import os
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from taxonomy import PILLARS, cat_stats      # noqa: E402
from build_feed import ISSUES                # noqa: E402
from cmd_data import ALL as CMD_SPECS        # noqa: E402

OUT = REPO / "brand"

INK, PAPER, CRIMSON, CYAN = "#08090c", "#f2f0eb", "#e53935", "#00c2d4"
MUTED, LINE = "#8b8780", "rgba(255,255,255,.07)"

# ── the numbers, from the same place every page gets them ───────────────────
LIVE = PIPE = PLAN = 0
for _n, _cats in PILLARS:
    for _c, _i, _t in _cats:
        l, p, n = cat_stats(_t)
        LIVE += l; PIPE += p; PLAN += n
TOTAL = LIVE + PIPE + PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])

W, H = 1200, 320

# The mark: three ascending bars, the same shape as the site's favicon, on the
# same 32-unit grid it is drawn on there.
BARS = [(0, 20, 14), (0, 13, 21), (0, 6, 28)]


def bars(x, y, scale, delay_step=0.18):
    out = []
    for i, (_bx, by, bw) in enumerate(BARS):
        out.append(
            f'<rect class="bar" x="{x}" y="{y + by * scale}" '
            f'width="{bw * scale}" height="{4 * scale}" rx="{1 * scale}" '
            f'fill="{CRIMSON}" style="animation-delay:{i * delay_step}s"/>')
    return "".join(out)


def coverage_bar(x, y, w, h):
    """live / pipeline / planned, to scale. The widths are the real ratio."""
    segs, cur = [], x
    for val, colour, cls in ((LIVE, CRIMSON, "s-live"),
                             (PIPE, "#f59e0b", "s-pipe"),
                             (PLAN, "#3a3f4a", "s-plan")):
        seg_w = w * val / TOTAL
        segs.append(f'<rect class="seg {cls}" x="{cur}" y="{y}" width="{seg_w:.1f}" '
                    f'height="{h}" fill="{colour}"/>')
        cur += seg_w
    return "".join(segs)


SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}" role="img"
     aria-label="Platform Ops — field notes from production, not slideware.
                 Written by Vishal Abhinav, published by Srivan Technologies.
                 {N_ISSUES} issues, {TOTAL} topics across {N_CATS} categories,
                 {N_CMDS} commands documented.">
<style>
  .wm   {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
           font-weight: 700; letter-spacing: 6px; }}
  .mono {{ font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; }}

  /* The bars rise once, then breathe. A masthead that loops aggressively is a
     distraction on a page someone is trying to read. */
  .bar    {{ transform-origin: left center; animation: grow .9s cubic-bezier(.2,.7,.3,1) backwards; }}
  @keyframes grow {{ from {{ transform: scaleX(0); opacity: 0; }} }}

  .seg    {{ transform-origin: left center; animation: grow 1.1s cubic-bezier(.2,.7,.3,1) .5s backwards; }}

  .fade   {{ animation: fade .8s ease-out backwards; }}
  @keyframes fade {{ from {{ opacity: 0; transform: translateY(10px); }} }}

  /* One pulse crossing the rule, echoing the two-paths diagram on the site. */
  .pulse  {{ animation: run 5.6s cubic-bezier(.45,0,.55,1) infinite; }}
  @keyframes run {{
    0%   {{ transform: translateX(0);    opacity: 0; }}
    6%   {{ opacity: 1; }}
    80%  {{ opacity: 1; }}
    92%, 100% {{ transform: translateX(1080px); opacity: 0; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    .bar, .seg, .fade, .pulse {{ animation: none; }}
    .pulse {{ opacity: 0; }}
  }}
</style>

<rect width="{W}" height="{H}" fill="{INK}"/>

<!-- a faint grid, the same one the site's hero uses -->
<g stroke="{LINE}" stroke-width="1">
  {"".join(f'<line x1="{i*60}" y1="0" x2="{i*60}" y2="{H}"/>' for i in range(1, 20))}
  {"".join(f'<line x1="0" y1="{j*60}" x2="{W}" y2="{j*60}"/>' for j in range(1, 6))}
</g>

{bars(60, 58, 1.35)}

<text class="wm fade" x="60" y="152" font-size="62" fill="{PAPER}"
      style="animation-delay:.15s">PLATFORM OPS</text>

<text class="mono fade" x="63" y="186" font-size="15" fill="{MUTED}"
      letter-spacing="2.4" style="animation-delay:.28s">
  FIELD NOTES FROM PRODUCTION, NOT SLIDEWARE
</text>

<text class="mono fade" x="63" y="216" font-size="13" fill="{CYAN}"
      letter-spacing="1.6" style="animation-delay:.38s">
  VISHAL ABHINAV  ·  SRIVAN TECHNOLOGIES
</text>

<!-- the rule, and the pulse that crosses it -->
<line x1="60" y1="244" x2="1140" y2="244" stroke="rgba(255,255,255,.13)" stroke-width="1"/>
<circle class="pulse" cx="60" cy="244" r="3.5" fill="{CRIMSON}"/>

<!-- coverage, to scale, from taxonomy.py -->
{coverage_bar(60, 262, 1080, 7)}

<text class="mono" x="60" y="292" font-size="11.5" fill="{MUTED}" letter-spacing="1.3">
  {LIVE} LIVE
</text>
<text class="mono" x="160" y="292" font-size="11.5" fill="#f59e0b" letter-spacing="1.3">
  {PIPE} IN PIPELINE
</text>
<text class="mono" x="300" y="292" font-size="11.5" fill="#6b6860" letter-spacing="1.3">
  {PLAN} PLANNED
</text>
<text class="mono" x="1140" y="292" font-size="11.5" fill="{MUTED}"
      letter-spacing="1.3" text-anchor="end">
  {N_ISSUES} ISSUES  ·  {N_CATS} CATEGORIES  ·  {N_CMDS} COMMANDS
</text>
</svg>
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "banner.svg"
    f.write_text(SVG.lstrip(), encoding="utf-8")
    print(f"  {len(SVG) // 1024 + 1} KB  brand/banner.svg  "
          f"({LIVE} live / {PIPE} pipeline / {PLAN} planned of {TOTAL})")
