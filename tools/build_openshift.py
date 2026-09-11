#!/usr/bin/env python3
"""Render the OpenShift deep-dive pages.

Same shape as build_foundation.py: a module supplies TOPICS, this renders them
with the shared content_page template and wires the prev/next pager from ORDER.

ORDER is the reading sequence, and it is also what the pager walks — so a
topic that is not written yet simply drops out of the chain rather than
producing a dead link.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import importlib
import sys

sys.path.insert(0, str(TOOLS))
from content_page import CSS, render, esc            # noqa: E402

OUT = ROOT / 'OpenShift'

# Reading order. (display name, slug or None, external href or None)
ORDER = [
    ("OpenShift Architecture & Fundamentals", "openshift-architecture", None),
    ("OpenShift Networking & Storage", "openshift-networking-storage", None),
    ("OpenShift Operations", "openshift-operations", None),
]

MODULES = [m for m in sys.argv[1:]] or ["ocp_a"]
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
            return (n, ext)
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
    pager += (f'<a href="{prev_l[1]}">← Previous<b>{esc(prev_l[0])}</b></a>' if prev_l else
              '<a href="../../categories/openshift/index.html">← OpenShift<b>Category hub</b></a>')
    pager += (f'<a class="next" href="{next_l[1]}">Next →<b>{esc(next_l[0])}</b></a>' if next_l else
              '<a class="next" href="../../categories/openshift/index.html">OpenShift →<b>Category hub</b></a>')
    pager += '</div>'

    html_out = render(
        slug=t["slug"], title=t["title"], tagline=t["tagline"], eyebrow=t["eyebrow"],
        crumbs=[("Home", "../../index.html"), ("Categories", "../../categories/index.html"),
                ("OpenShift", "../../categories/openshift/index.html"), (t["title"], None)],
        meta=t["meta"], sections=t["sections"], pager=pager, up="../../",
        css="../topic.css")     # OpenShift/topic.css, written above

    d = OUT / t["slug"].upper()
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{t["slug"]}.html').write_text(html_out, encoding='utf-8')
    built.append((t["title"], f'OpenShift/{t["slug"].upper()}/{t["slug"]}.html', len(html_out)))

for title, path, size in built:
    print(f"  {size // 1024:3d} KB  {path}   ({title})")
print(f"built {len(built)} OpenShift page(s) + topic.css")
