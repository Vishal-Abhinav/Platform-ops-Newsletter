#!/usr/bin/env python3
"""Fold the reader's 46-group Kubernetes + OpenShift list directly INTO the
Kubernetes and OpenShift hub pages themselves, not only onto the standalone
categories/kubernetes-openshift-map/ page.

Why both exist: the standalone page (build_topicmap.py) is the clean,
cross-referenced version — one URL, all 46 groups, easy to link and to
re-verify. This script additionally appends the Kubernetes-only groups
(1-24 of the reader's list) onto categories/kubernetes/index.html, and the
OpenShift-only groups (25-46) onto categories/openshift/index.html, because
that's where a reader actually looks first (Categories -> Kubernetes), and a
link out to a separate page isn't the same as the content being there.

Runs AFTER build_hubs.py (needs the hub pages to already exist on disk) and
AFTER build_topicmap.py is irrelevant to run order, but the CLASSIFICATION
must stay identical to that page, so it's imported from there rather than
re-implemented — one status per item, not two different opinions depending
on which page you're looking at.
"""
import os
import pathlib as _pl
import sys

TOOLS = _pl.Path(__file__).resolve().parent
ROOT = _pl.Path(os.environ.get("PO_ROOT") or TOOLS.parent)
sys.path.insert(0, str(TOOLS))

from build_topicmap import classify, zone_block, esc, slug, GROUPS  # noqa: E402

SPLIT_TITLE = "OpenShift Fundamentals"   # group 25 — everything before this is Kubernetes
_titles = [t for t, _ in GROUPS]
SPLIT_AT = _titles.index(SPLIT_TITLE)

TOPICS_ANCHOR = '<!-- topic-checklist-anchor -->'   # right after the "ALL n TOPICS" chips section

# Both hubs anchor the checklist immediately after their own "ALL n TOPICS"
# chips, so the curated set and the full list read as one thought instead of
# being split by the sibling-pillar nav and the pager.
#
# OpenShift used to anchor on the request pill — last thing before the footer — with a
# comment saying only the Kubernetes page had been asked for. That is how a
# one-page fix becomes an inconsistency: two hubs carrying the same kind of
# content in two different places, and a reader who learns the Kubernetes page
# then cannot find the same thing on OpenShift. The layout belongs to the
# content type, not to whichever page prompted the request.
HUBS = [
    ("kubernetes", ROOT / "categories" / "kubernetes" / "index.html",
     "KUBERNETES", 0, SPLIT_AT, TOPICS_ANCHOR),
    ("openshift", ROOT / "categories" / "openshift" / "index.html",
     "OPENSHIFT", SPLIT_AT, len(GROUPS), TOPICS_ANCHOR),
]


def section_for(name_upper, groups_slice, other_slug, other_label):
    total = live = pipe = plan = 0
    blocks = []
    for n, (title, rows) in enumerate(groups_slice, 1):
        g_live = sum(1 for _, s, _ in rows if s == "L")
        g_pipe = sum(1 for _, s, _ in rows if s == "P")
        g_plan = len(rows) - g_live - g_pipe
        total += len(rows); live += g_live; pipe += g_pipe; plan += g_plan
        zones = (zone_block("L", "Live now", rows)
                 + zone_block("P", "In pipeline", rows)
                 + zone_block("-", "Planned", rows))
        blocks.append(
            f'<div class="topicmap-group" id="{slug(title)}">'
            f'<h3>{n:02d} · {esc(title)}</h3>'
            f'<p class="lede">{len(rows)} items — {g_live} live · {g_pipe} pipeline · {g_plan} planned</p>'
            f'{zones}</div>'
        )
    lede = (f'Every {name_upper.title()} concept and error state from the reader’s own '
            f'checklist, grouped exactly as given — {total} items across {len(groups_slice)} '
            f'groups, honestly marked live only where a published page actually covers it. '
            f'<a href="../{other_slug}/index.html">See the {other_label} half</a> or '
            f'<a href="../kubernetes-openshift-map/index.html">the full cross-referenced map, both '
            f'halves in one place →</a>')
    return (
        '<section id="complete-topic-list"><div class="wrap">'
        f'<h2>COMPLETE {name_upper} TOPIC &amp; ERROR LIST</h2>'
        f'<p class="lede">{lede}</p>'
        f'<div class="stats"><div class="stat"><b>{total}</b><i>Items</i></div>'
        f'<div class="stat"><b class="live">{live}</b><i>Live</i></div>'
        f'<div class="stat"><b class="pipe">{pipe}</b><i>In pipeline</i></div>'
        f'<div class="stat"><b class="plan">{plan}</b><i>Planned</i></div></div>'
        f'<div class="progress"><i class="live" style="flex:{live}"></i>'
        f'<i class="pipe" style="flex:{pipe}"></i><i class="plan" style="flex:{plan}"></i></div>'
        + "".join(blocks) +
        '</div></section>\n'
    )


def build():
    groups, _live, _pipe, _plan = classify()

    for slug_name, path, upper, lo, hi, anchor in HUBS:
        if not path.exists():
            print(f"  !! {path.relative_to(ROOT)} does not exist — run build_hubs.py first")
            continue
        other = [h for h in HUBS if h[0] != slug_name][0]
        section = section_for(upper, groups[lo:hi], other[0], other[2].title())

        src = path.read_text(encoding="utf-8")
        marker = "<!-- complete-topic-list:start -->"
        marker_end = "<!-- complete-topic-list:end -->"
        block = f"\n{marker}\n{section}{marker_end}\n"

        # Always strip any previously-inserted block first, then re-insert
        # fresh at the current anchor. Replacing in place (instead of always
        # re-anchoring) would leave the block stuck at whatever position an
        # earlier run used, even after build_hubs.py moves the anchor —
        # exactly the bug that would've kept this stuck at the bottom of the
        # Kubernetes page after the reorder below.
        if marker in src:
            start = src.index(marker)
            end = src.index(marker_end) + len(marker_end)
            src = src[:start] + src[end:]

        if anchor not in src:
            print(f"  !! anchor not found in {path.relative_to(ROOT)} — page structure changed")
            continue
        at = src.index(anchor)
        at += len(anchor) if anchor == TOPICS_ANCHOR else 0
        src = src[:at] + block + "\n" + src[at:]

        path.write_text(src, encoding="utf-8")
        n_items = hi - lo
        print(f"  {path.relative_to(ROOT)}: {n_items} groups folded in")


if __name__ == "__main__":
    build()
