#!/usr/bin/env python3
"""One honest, stable page for every Kubernetes/OpenShift checklist item that
isn't Live yet — built on content_page.py's real component system (the same
hero/nav/footer/note/pager vocabulary every deep-dive issue uses), not a
bespoke stub stylesheet.

WHY
---
The reader's 942-item checklist marks each item Live, Pipeline, or Planned.
A Live item already has a real page — that page is *why* it's Live — so it
keeps linking straight there. A Pipeline or Planned item used to render as a
plain <span>: no link, a dead end. That's 786 items right now (up or down a
little as pages change) with nowhere to click through to.

This script gives each of those items a real, stable URL instead. It is NOT
a shortcut around writing the real thing — the page says plainly that the
topic isn't covered yet, same as the chip already did, just at a URL a
reader (or a search result, or a bookmark) can actually land on. The moment
a real page covers that item, classify() in build_topicmap.py stops routing
it here — the item's own href becomes the real page, this script never
writes a stub for it again, and if a stale one is still on disk from an
earlier build, cleanup() below removes it. One classification, everywhere:
this script never re-decides Live/Pipeline/Planned, only build_topicmap.py's
classify() does that.

First cut of this script (16 Sep) shipped its own minimal one-off CSS
(.ph-wrap/.ph-badge/.ph-note) to get 786 dead ends off the site fast. That
was correct triage, but it meant these pages didn't look like the rest of
the site — no hero, no themed note callouts, no pager, a different footer
copy. This version renders through content_page.render() instead: same
nav/hero/footer/typography as the 15 written deep-dives, `note()` for the
status callout, and a `.pager` + "more in this series" siblings list built
from the item's own group — so a reader who lands here from search cannot
tell it apart from a page that was written by hand, except for what it
plainly says: this one isn't, yet.

`robots=noindex,follow` stays — these are thin placeholder pages by design,
and no volume of them should look, to a search engine, like 786 new articles.

Runs AFTER build_topicmap.py. Both build_search.py's index and verify.py's
sitemap crawl pick these pages up for free — they're just files under
categories/, not a separate registry to keep in sync.
"""
import os
import pathlib as _pl
import sys

TOOLS = _pl.Path(__file__).resolve().parent
ROOT = _pl.Path(os.environ.get("PO_ROOT") or TOOLS.parent)
sys.path.insert(0, str(TOOLS))

from build_topicmap import classify, esc, slug, topic_href, TOPICS_REL  # noqa: E402
from content_page import CSS, render, section, note                     # noqa: E402

OUT_ROOT = ROOT / TOPICS_REL
CSS_REL = f"{TOPICS_REL}/topic.css"          # one shared copy, siblings of the topics/ dir
UP = "../../../../"   # categories/kubernetes-openshift-map/topics/<slug>/ -> ROOT
MAP_REL = "categories/kubernetes-openshift-map/index.html"
MAP_HREF = UP + MAP_REL

# (note() kind, status label, explanatory sentence). "warn" (amber) for work
# already in flight, the neutral "plan" kind (added to content_page.py's CSS
# alongside this) for nothing having started — tip/trap both read as
# good/dangerous, which is wrong for "not written yet".
STATUS = {
    "P": ("warn", "In pipeline",
          "This term already turns up on the page that covers its group, but "
          "nothing on the site documents it in its own right yet."),
    "-": ("plan", "Planned",
          "Nothing on the site covers this yet — it's on the list because a "
          "reader asked for the complete checklist, not because it's been "
          "written."),
}

SIBLING_CAP = 8   # a group can run past 20 items; keep the related list scannable


def _page(group_title, gslug, name, status, siblings):
    kind, label, explain = STATUS[status]
    folder = topic_href(group_title, name)
    rel = f"{TOPICS_REL}/{folder}/index.html"
    canon = f"{rel[:-len('index.html')]}"   # trailing-slash directory form

    tagline = ("Part of the Kubernetes & OpenShift reader checklist — "
               f"{label.lower()}, not written as its own page yet.")

    body = (
        note(kind, label, f"<p>{esc(explain)}</p>")
        + f'<p>See what already <em>is</em> live in '
          f'<a href="{MAP_HREF}#{gslug}">{esc(group_title)}</a>, or browse '
          f'<a href="{MAP_HREF}">the complete 942-item checklist</a>.</p>'
    )
    sections = section("Coverage status", "Where this stands", "", body)

    pager = ('<div class="pager">'
             f'<a href="{MAP_HREF}#{gslug}">← Back<b>{esc(group_title)}</b></a>'
             f'<a class="next" href="{MAP_HREF}">Full map →<b>Topic Map</b></a>'
             '</div>')

    related = [(n2, f"../{topic_href(group_title, n2)}/index.html")
               for n2 in siblings][:SIBLING_CAP]

    return render(
        slug=folder, title=name, tagline=tagline, eyebrow=group_title,
        crumbs=[("Home", UP + "index.html"), ("Categories", UP + "categories/index.html"),
                ("Topic Map", MAP_HREF), (name, None)],
        meta=[f"<b>{label}</b> status", f"<b>{esc(group_title)}</b> group"],
        sections=sections, pager=pager, related=related, up=UP,
        css=UP + CSS_REL, canon=canon, robots="noindex,follow")


def build():
    groups, live, pipe, plan = classify()

    (ROOT / CSS_REL).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / CSS_REL).write_text(CSS.strip() + "\n", encoding="utf-8")

    wanted = {}
    written = 0
    for title, rows in groups:
        gslug = slug(title)
        pending = [(name, status) for name, status, _href in rows if status != "L"]
        names = [n for n, _s in pending]
        for name, status in pending:
            rel = f"{TOPICS_REL}/{topic_href(title, name)}/index.html"
            wanted[rel] = True
            siblings = [n2 for n2 in names if n2 != name]
            out = ROOT / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(_page(title, gslug, name, status, siblings), encoding="utf-8")
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
