#!/usr/bin/env python3
"""Render the Commands reference pages."""
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from cmd_page import CSS, render, esc      # noqa: E402
from cmd_data import ALL                   # noqa: E402

OUT = ROOT / "Commands"
OUT.mkdir(exist_ok=True)
(OUT / "commands.css").write_text(CSS.strip() + "\n", encoding="utf-8")

# Which category hub each page belongs under
CAT_SLUG = {
    "linux-commands": "linux-commands",
    "kubernetes-commands": "kubernetes-commands",
    "docker-commands": "docker-commands",
}

built = []
for i, spec in enumerate(ALL):
    prev_s = ALL[i - 1] if i else None
    next_s = ALL[i + 1] if i + 1 < len(ALL) else None
    pager = '<div class="pager">'
    pager += (f'<a href="../{prev_s["slug"].upper()}/{prev_s["slug"]}.html">← Previous'
              f'<b>{esc(prev_s["title"])}</b></a>' if prev_s else
              '<a href="../../categories/index.html">← Categories<b>Index</b></a>')
    pager += (f'<a class="next" href="../{next_s["slug"].upper()}/{next_s["slug"]}.html">Next →'
              f'<b>{esc(next_s["title"])}</b></a>' if next_s else
              '<a class="next" href="../../categories/index.html">Categories →<b>Index</b></a>')
    pager += '</div>'

    html_out = render(slug=spec["slug"], title=spec["title"], icon=spec["icon"],
                      tagline=spec["tagline"], groups=spec["groups"],
                      category_slug=CAT_SLUG[spec["slug"]], pager=pager)
    d = OUT / spec["slug"].upper()
    d.mkdir(exist_ok=True)
    (d / f'{spec["slug"]}.html').write_text(html_out, encoding="utf-8")
    n = sum(len(g[3]) for g in spec["groups"])
    built.append((spec["title"], n, len(spec["groups"]), len(html_out)))

for title, n, g, size in built:
    print(f"  {size // 1024:3d} KB  {title:24} {n:3d} commands in {g} groups")
print(f"built {len(built)} command references, "
      f"{sum(b[1] for b in built)} commands total")
