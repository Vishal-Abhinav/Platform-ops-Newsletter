#!/usr/bin/env python3
"""One honest, stable page for every Kubernetes/OpenShift checklist item that
isn't Live yet.

WHY
---
The reader's 942-item checklist marks each item Live, Pipeline, or Planned.
A Live item already has a real page — that page is *why* it's Live — so it
keeps linking straight there. A Pipeline or Planned item used to render as a
plain <span>: no link, a dead end. That's 786 items right now (up or down a
little as pages change) with nowhere to click through to.

This script gives each of those 786 items a real, stable URL instead. It is
NOT a shortcut around writing the real thing — the page says plainly that
the topic isn't covered yet, same as the chip already did, just at a URL a
reader (or a search result, or a bookmark) can actually land on. The moment
a real page covers that item, classify() in build_topicmap.py stops routing
it here — the item's own href becomes the real page, this script never
writes a stub for it again, and if a stale one is still on disk from an
earlier build, cleanup() below removes it. One classification, everywhere:
this script never re-decides Live/Pipeline/Planned, only build_topicmap.py's
classify() does that.

Runs AFTER build_topicmap.py. Both build_search.py's index and verify.py's
sitemap crawl pick these pages up for free — they're just files under
categories/, not a separate registry to keep in sync.
"""
import html
import os
import pathlib as _pl
import sys

TOOLS = _pl.Path(__file__).resolve().parent
ROOT = _pl.Path(os.environ.get("PO_ROOT") or TOOLS.parent)
sys.path.insert(0, str(TOOLS))

from siteconf import BASE                                          # noqa: E402
from build_topicmap import classify, esc, slug, topic_href, TOPICS_REL, GC  # noqa: E402
import chrome                                                        # noqa: E402

OUT_ROOT = ROOT / TOPICS_REL
UP = "../../../../"   # categories/kubernetes-openshift-map/topics/<slug>/ -> ROOT
MAP_HREF = "categories/kubernetes-openshift-map/index.html"

STATUS = {
    "P": ("pipe", "In pipeline",
          "This term already turns up on the page that covers its group, but "
          "nothing on the site documents it in its own right yet."),
    "-": ("plan", "Planned",
          "Nothing on the site covers this yet."),
}


def render(group_title, gslug, name, status):
    cls, label, note = STATUS[status]
    rel = f"{TOPICS_REL}/{topic_href(group_title, name)}/index.html"
    canonical = BASE + rel[:-len("index.html")]
    title_tag = f"{name} · {group_title} · Kubernetes & OpenShift Topic Map"
    desc = (f"{name} — {label.lower()}, part of the {group_title} group in the reader-requested "
            f"Kubernetes & OpenShift checklist on Platform Ops.")

    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title_tag)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex,follow">
<meta name="author" content="Vishal Abhinav">
<meta name="copyright" content="© 2026 Vishal Abhinav. Text and diagrams CC BY-NC-ND 4.0.">
<link rel="canonical" href="{canonical}">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="alternate" type="application/rss+xml" title="Platform Ops — new issues" href="{UP}feed.xml">
<script>
(function(){{try{{var t=localStorage.getItem('po-theme');
 if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}}catch(e){{}}}})();
</script>
<link rel="stylesheet" href="{UP}categories/hub.css">
<style>
.ph-wrap{{max-width:720px;margin:0 auto;padding:72px 24px 100px;}}
.ph-badge{{display:inline-block;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.6px;
  text-transform:uppercase;padding:4px 10px;border-radius:3px;margin-bottom:20px;border:1px solid;}}
.ph-badge.pipe{{background:var(--n-pipe-bg);color:var(--n-pipe-fg);border-color:var(--n-pipe-br);}}
.ph-badge.plan{{background:var(--n-plan-bg);color:var(--n-plan-fg);border-color:var(--n-plan-br);}}
.ph-wrap h1{{font-size:clamp(28px,4vw,40px);line-height:1.15;margin-bottom:10px;}}
.ph-group{{color:var(--muted);font-family:'DM Mono',monospace;font-size:12px;letter-spacing:.6px;
  text-transform:uppercase;margin-bottom:30px;}}
.ph-note{{font-size:15.5px;line-height:1.75;color:var(--page-fg);margin-bottom:36px;max-width:56ch;}}
.ph-note a{{color:inherit;}}
.ph-back{{font-family:'DM Mono',monospace;font-size:12px;letter-spacing:.6px;text-decoration:none;
  color:var(--page-fg);border-bottom:1px solid var(--line-3);padding-bottom:2px;}}
</style>
{GC}
</head>
"""

    body = f"""<body>
<nav>
  <a href="{UP}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>
  <div class="crumb"><a href="{UP}index.html">Home</a><span>/</span><a href="{UP}categories/index.html">Categories</a><span>/</span><a href="{UP}{MAP_HREF}">Topic Map</a><span>/</span><span class="cur">{esc(name)}</span></div>
  <div class="nav-right">{chrome.TOGGLE}<a href="{UP}index.html#subscribe" class="nav-logo nav-sub" style="font-size:11px;letter-spacing:1.6px;font-family:'DM Mono',monospace">SUBSCRIBE</a></div>
</nav>

<div class="ph-wrap">
  <span class="ph-badge {cls}">{esc(label)}</span>
  <h1>{esc(name)}</h1>
  <div class="ph-group">{esc(group_title)} · Kubernetes &amp; OpenShift Topic Map</div>
  <p class="ph-note">{esc(note)} See everything that <em>is</em> live today on
    <a href="{UP}{MAP_HREF}">the complete topic map</a>, or jump straight to this item's group
    below.</p>
  <a class="ph-back" href="{UP}{MAP_HREF}#{gslug}">&larr; Back to {esc(group_title)}</a>
</div>
{chrome.footer(UP)}
{chrome.TOGGLE_JS}
</body>
</html>"""

    return head + body


def build():
    groups, live, pipe, plan = classify()

    wanted = {}
    for title, rows in groups:
        gslug = slug(title)
        for name, status, href in rows:
            if status == "L":
                continue
            rel = f"{TOPICS_REL}/{topic_href(title, name)}/index.html"
            wanted[rel] = (title, gslug, name, status)

    written = 0
    for rel, (title, gslug, name, status) in wanted.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(title, gslug, name, status), encoding="utf-8")
        written += 1

    # Stale cleanup: a Pipeline/Planned item that became Live (or was renamed)
    # no longer appears in `wanted` — its old placeholder page is dead weight
    # and, worse, a page the sitemap and the link-checker still see even
    # though nothing points to it any more. Remove any page under topics/
    # that classify() didn't just ask for.
    removed = 0
    if OUT_ROOT.exists():
        existing = {str(p.relative_to(ROOT)).replace("\\", "/")
                    for p in OUT_ROOT.glob("*/index.html")}
        for rel in existing - set(wanted):
            (ROOT / rel).unlink()
            (ROOT / rel).parent.rmdir()
            removed += 1

    print(f"topic placeholder pages: {written} written, {removed} stale removed "
          f"({pipe} pipeline, {plan} planned)")


if __name__ == "__main__":
    build()
