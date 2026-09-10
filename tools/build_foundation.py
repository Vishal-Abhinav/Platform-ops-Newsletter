#!/usr/bin/env python3
"""Render the Foundation topic pages."""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import importlib
import pathlib
import sys

sys.path.insert(0, str(TOOLS))
import content_page                                  # noqa: E402
from content_page import CSS, render, esc            # noqa: E402

OUT = ROOT / 'Foundation'

# Foundation's running order, matching the taxonomy. Entries without a module
# are the ones already covered by an existing issue.
ORDER = [
    ("Computer Fundamentals", "computer-fundamentals", None),
    ("Operating Systems", "operating-systems", None),
    ("Linux", None, "../../Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html"),
    ("Unix", "unix", None),
    ("Windows Server", "windows-server", None),
    ("Shell & Bash", "shell-and-bash", None),
    ("Python", "python", None),
    ("Programming Fundamentals", "programming-fundamentals", None),
    ("Data Structures & Algorithms", "data-structures-algorithms", None),
    ("Git & Version Control", "git-version-control", None),
]

MODULES = [m for m in sys.argv[1:]] or ["fnd_a"]
topics = {}
for mod in MODULES:
    for t in importlib.import_module(mod).TOPICS:
        topics[t["slug"]] = t

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n", encoding='utf-8')

built = []
for i, (name, slug, external) in enumerate(ORDER):
    if not slug or slug not in topics:
        continue
    t = topics[slug]

    def link(j):
        if j < 0 or j >= len(ORDER):
            return None
        n, s, ext = ORDER[j]
        if ext:
            return (n, ext)   # already written relative to Foundation/<TOPIC>/
        if s and s in topics:
            return (n, f"../{s.upper()}/{s}.html")
        return None

    prev_l, next_l = None, None
    for j in range(i - 1, -1, -1):
        prev_l = link(j)
        if prev_l:
            break
    for j in range(i + 1, len(ORDER)):
        next_l = link(j)
        if next_l:
            break

    pager = '<div class="pager">'
    pager += (f'<a href="{esc(prev_l[1])}">← Previous<b>{esc(prev_l[0])}</b></a>' if prev_l
              else '<a href="../../categories/foundation/index.html">← Foundation<b>Hub</b></a>')
    pager += (f'<a class="next" href="{esc(next_l[1])}">Next →<b>{esc(next_l[0])}</b></a>' if next_l
              else '<a class="next" href="../../categories/foundation/index.html">Foundation →<b>Hub</b></a>')
    pager += '</div>'

    html_out = render(
        slug=slug, title=t["title"], tagline=t["tagline"], eyebrow=t["eyebrow"],
        crumbs=[("Home", "../../index.html"), ("Categories", "../../categories/index.html"),
                ("Foundation", "../../categories/foundation/index.html"), (t["title"], None)],
        meta=t["meta"], sections=t["sections"], pager=pager)

    d = OUT / slug.upper()
    d.mkdir(exist_ok=True)
    (d / f"{slug}.html").write_text(html_out, encoding='utf-8')
    built.append((t["title"], f"Foundation/{slug.upper()}/{slug}.html", len(html_out)))

for name, path, n in built:
    print(f"  {n // 1024:3d} KB  {path}   ({name})")
print(f"built {len(built)} topic pages + topic.css")
