#!/usr/bin/env python3
"""Render the Kubernetes and Service Mesh deep-dive pages.

Same shape as build_openshift.py. ORDER is the reading sequence and also what
the pager walks, so a topic not written yet drops out of the chain rather than
producing a dead link.

Two sections share this builder because they share a category hub parent in
the crumb trail only at the Categories level — each page names its own
category, which is why CATEGORY is part of ORDER rather than a constant.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import importlib
import sys

sys.path.insert(0, str(TOOLS))
from content_page import CSS, render, esc            # noqa: E402

OUT = ROOT / 'Kubernetes'

# (display name, slug, category display, category hub slug)
ORDER = [
    ("Kubernetes Workloads",        "kubernetes-workloads",          "Kubernetes",   "kubernetes"),
    ("Kubernetes Config & Access",  "kubernetes-config-and-access",  "Kubernetes",   "kubernetes"),
    ("Kubernetes Scheduling",       "kubernetes-scheduling",         "Kubernetes",   "kubernetes"),
    ("Kubernetes Autoscaling",      "kubernetes-autoscaling",        "Kubernetes",   "kubernetes"),
    ("Kubernetes Cluster Operations", "kubernetes-cluster-operations", "Kubernetes", "kubernetes"),
    ("Service Mesh Fundamentals",   "service-mesh-fundamentals",     "Service Mesh", "service-mesh"),
    ("Service Mesh Operations",     "service-mesh-operations",       "Service Mesh", "service-mesh"),
]

MODULES = [m for m in sys.argv[1:]] or ["k8s_a"]
topics = {}
for mod in MODULES:
    for t in importlib.import_module(mod).TOPICS:
        topics[t["slug"]] = t

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n", encoding='utf-8')

built = []
for i, (name, slug, cat, cat_slug) in enumerate(ORDER):
    if slug not in topics:
        continue
    t = topics[slug]

    def link(j):
        if j < 0 or j >= len(ORDER):
            return None
        n, s, _c, _cs = ORDER[j]
        return (n, f"../{s.upper()}/{s}.html") if s in topics else None

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
              f'<a href="../../categories/{cat_slug}/index.html">← {esc(cat)}<b>Category hub</b></a>')
    pager += (f'<a class="next" href="{next_l[1]}">Next →<b>{esc(next_l[0])}</b></a>' if next_l else
              f'<a class="next" href="../../categories/{cat_slug}/index.html">{esc(cat)} →<b>Category hub</b></a>')
    pager += '</div>'

    html_out = render(
        slug=t["slug"], title=t["title"], tagline=t["tagline"], eyebrow=t["eyebrow"],
        crumbs=[("Home", "../../index.html"), ("Categories", "../../categories/index.html"),
                (cat, f"../../categories/{cat_slug}/index.html"), (t["title"], None)],
        meta=t["meta"], sections=t["sections"], pager=pager, up="../../",
        css="../topic.css")

    d = OUT / t["slug"].upper()
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{t["slug"]}.html').write_text(html_out, encoding='utf-8')
    built.append((t["title"], f'Kubernetes/{t["slug"].upper()}/{t["slug"]}.html', len(html_out)))

for title, path, size in built:
    print(f"  {size // 1024:3d} KB  {path}   ({title})")
print(f"built {len(built)} page(s) + topic.css")
