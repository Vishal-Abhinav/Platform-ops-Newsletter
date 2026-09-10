#!/usr/bin/env python3
"""Regenerate the README's Knowledge Map section from the same taxonomy."""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import pathlib
import sys

sys.path.insert(0, str(TOOLS))
from taxonomy import PILLARS, cat_stats  # noqa: E402

R = ROOT / 'README.md'
MARK = {"L": "✅", "P": "🔸", "-": "·"}

rows, blocks = [], []
TL = TP = TN = 0
for i, (pname, cats) in enumerate(PILLARS):
    pl = pp = pn = 0
    lines = []
    for cname, icon, topics in cats:
        l, p, n = cat_stats(topics)
        pl += l; pp += p; pn += n
        lines.append(f"**{icon} {cname}** — {l} live · {p} pipeline · {n} planned  ")
        for tname, st, href in topics:
            if st == "L" and href:
                lines.append(f"{MARK[st]} [{tname}](./{href}) &nbsp;")
            else:
                lines.append(f"{MARK[st]} {tname} &nbsp;")
        lines.append("")
    TL += pl; TP += pp; TN += pn
    rows.append(f"| `{i + 1:02d}` | **{pname}** | {len(cats)} | {pl} | {pp} | {pn} | {pl + pp + pn} |")
    blocks.append(
        f"<details>\n<summary><b>{i + 1:02d} · {pname}</b> — {len(cats)} categor{'y' if len(cats)==1 else 'ies'} · "
        f"{pl} live · {pp} pipeline · {pn} planned</summary>\n\n"
        + "\n".join(lines) + "\n</details>\n")

n_pages = len({t[2] for _, cats in PILLARS for _, _, ts in cats
                for t in ts if t[1] == "L" and t[2]})
N_CATS = sum(len(c) for _, c in PILLARS)
rows.append(f"| | **Total** | **{N_CATS}** | **{TL}** | **{TP}** | **{TN}** | **{TL + TP + TN}** |")

SECTION = f"""## 🗺️ Knowledge Map

The **2026 master map** — every subject this newsletter intends to cover, in one place.
{TL + TP + TN} topics, grouped into {N_CATS} categories and {len(PILLARS)} pillars. The homepage renders
this same map with search and status filters; both are generated from one source
of truth, so the numbers here and there can never disagree.

| | Pillar | Categories | ✅ Live | 🔸 Pipeline | · Planned | Total |
|:--|:--|--:|--:|--:|--:|--:|
{chr(10).join(rows)}

**Status meanings**

| | Meaning |
|:--|:--|
| ✅ **Live** | A published issue covers it, and the topic links straight to that page. |
| 🔸 **Pipeline** | Next up — adjacent to a series already running, so it's queued rather than hypothetical. |
| · **Planned** | On the backlog. No date attached; it moves to pipeline when the series in front of it lands. |

Live topics point at the {n_pages} deep-dives already in this repo — 11 monthly issues plus the
Foundation reference pages — so one page can light up several topics at once. Issue #051 alone
covers Prometheus, Grafana, Loki, Jaeger and distributed tracing.

<br>

{chr(10).join(blocks)}
"""


src = R.read_text(encoding='utf-8')
a = src.index('## 🗺️ Knowledge Map')
b = src.index('## 📚 Published Issues')
src = src[:a] + SECTION + "\n---\n\n" + src[b:]
R.write_text(src, encoding='utf-8')
print(f"README -> {len(src)} bytes | {len(PILLARS)} pillars, {N_CATS} categories, "
      f"{TL + TP + TN} topics ({TL} live / {TP} pipeline / {TN} planned)")


# ════════════════════════════════════════════════════════════════════════════
# Everything below keeps the REST of the README honest. The map section above
# was already derived, but the badge, the inventory sentence, the feature table
# and the repository tree were hand-written and had drifted badly — the README
# still claimed 521 topics in 33 categories under 10 pillars, and a structure
# tree with no Foundation, Commands, categories, assets or tools in it.
#
# Each rewrite asserts it matched exactly once, so a reworded README fails the
# build instead of quietly going stale again.
# ════════════════════════════════════════════════════════════════════════════
import json                                      # noqa: E402
import re                                        # noqa: E402
from build_feed import ISSUES                    # noqa: E402
from cmd_data import ALL as CMD_SPECS            # noqa: E402

src = R.read_text(encoding="utf-8")


def sub(pattern, repl, why):
    global src
    new, n = re.subn(pattern, repl.replace("\\", "\\\\"), src, count=1)
    assert n == 1, f"README: {why} — pattern matched {n} times, expected 1:\n  {pattern}"
    src = new


# ── the facts, counted rather than remembered ───────────────────────────────
N_TOPICS = TL + TP + TN
N_PILLARS = len(PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])
N_CMD_PAGES = len(CMD_SPECS)

pages = sorted(p for p in ROOT.rglob("*.html")
               if "tools" not in p.parts and p.name != "kit-template.html")
N_PAGES = len(pages)
by_dir = {}
for p in pages:
    by_dir[p.relative_to(ROOT).parts[0] if len(p.relative_to(ROOT).parts) > 1
           else "."] = by_dir.get(p.relative_to(ROOT).parts[0]
                                  if len(p.relative_to(ROOT).parts) > 1 else ".", 0) + 1
N_HUBS = by_dir.get("categories", 0)
N_FOUND = by_dir.get("Foundation", 0)
N_TERMS = len(list((ROOT / "Infrastructure/OS/LINUX/GLOSSARY/TERMS/fundamentals").glob("*.html")))
_sjs = ROOT / "assets/search.js"
if _sjs.exists():
    # The index is one long line of JSON, so count the rows rather than lines.
    _txt = _sjs.read_text(encoding="utf-8")
    _a = _txt.index("var PO_SEARCH")
    N_SEARCH = len(json.loads(_txt[_txt.index("[", _a):_txt.index("];", _a) + 1]))
else:
    N_SEARCH = 0

# ── 1. the badge ────────────────────────────────────────────────────────────
sub(r"Live%20Issues-\d+-", f"Live%20Issues-{N_ISSUES}-", "live-issues badge")

# ── 2. the inventory sentence ───────────────────────────────────────────────
sub(r"\*\*Currently in this repo:\*\*[^\n]*",
    f"**Currently in this repo:** {N_ISSUES} monthly issue pages, {N_FOUND} Foundation "
    f"reference deep-dives, {N_CMD_PAGES} command references covering {N_CMDS} commands, "
    f"a 190-term Linux & Unix glossary with {N_TERMS} standalone term pages, "
    f"{N_HUBS} category pages, 2 section hubs and a homepage index — "
    f"{N_PAGES} pages in total.",
    "inventory sentence")

# ── 3. the feature table ────────────────────────────────────────────────────
sub(r"\| 🗺️ \*\*Knowledge map\*\* \|[^\n]*",
    f"| 🗺️ **Knowledge map** | All {N_TOPICS} topics, grouped into {N_CATS} categories under "
    f"{N_PILLARS} pillars — search by name, filter by status, open a pillar to see what's "
    f"shipped and what's queued |", "knowledge-map feature row")

sub(r"\| 🖥️ \*\*Coverage terminal\*\* \|[^\n]*",
    f"| 🖥️ **Coverage terminal** | Terminal-style `tree` view of the {N_PILLARS} pillars with "
    f"live-vs-total counts, and a `ls published/` listing that links straight into every issue |",
    "coverage-terminal feature row")

sub(r"\| 📡 \*\*RSS\*\* \|[^\n]*",
    f"| 📡 **RSS** | `feed.xml` carries all {N_ISSUES} issues, and every page advertises it in "
    f"its `<head>` |", "RSS feature row")

sub(r"\| 📌 \*\*Pinned archive\*\* \|[^\n]*",
    "| 📌 **Pinned archive** | On desktop Latest Issues is pinned beside the map and scrolls "
    "inside itself, so the issues stay one glance away however far down the map you are |",
    "archive feature row")

sub(r"\| 🧭 \*\*Mega-menu\*\* \|[^\n]*",
    f"| 🧭 **Mega-menu** | Cascading browse panel on every page — {N_PILLARS} pillars, "
    f"{N_CATS} categories, with live counts |", "mega-menu feature row")

sub(r"\| ⌨️ \*\*Command references\*\* \|[^\n]*",
    f"| ⌨️ **Command references** | Searchable, group-filtered command tables — {N_CMDS} "
    f"commands so far |", "command-references feature row")

sub(r"\| 🔍 \*\*Global search\*\* \|[^\n]*",
    f"| 🔍 **Global search** | Centred in the nav of all {N_PAGES} pages — {N_SEARCH} entries "
    f"covering every category, topic, page and command; `/` to focus, arrows to move, "
    f"Enter to open |", "global-search feature row")

sub(r"\| 🧩 \*\*Category hubs\*\* \|[^\n]*",
    f"| 🧩 **Category hubs** | Every one of the {N_CATS} categories has its own page with a "
    f"generated architecture diagram and its full topic list |", "category-hubs feature row")

# ── 4. the repository tree, walked rather than remembered ──────────────────
# It listed neither Foundation, Commands, categories, assets nor tools, and
# called the LICENSE MIT. Generated from what is actually on disk now, with
# the issue directories itemised and the bulk ones counted.
ISSUE_OF = {path: num for num, path, *_ in ISSUES}
DETAIL = ("DevOps", "Infrastructure", "SRE")          # itemise these
NOTE = {
    "categories": f"{N_HUBS - 1} category hubs + index",
    "Foundation": "reference deep-dives",
    "Commands":   f"{N_CMDS} commands",
}


def walk(d, prefix, out, depth=0):
    kids = sorted([k for k in d.iterdir()
                   if (k.is_dir() and any(k.rglob("*.html"))) or k.suffix == ".html"],
                  key=lambda k: (k.is_dir(), k.name.lower()))
    for i, k in enumerate(kids):
        last = i == len(kids) - 1
        arm = "└── " if last else "├── "
        rel = k.relative_to(ROOT).as_posix()
        if k.is_dir():
            n = len(list(k.rglob("*.html")))
            # Collapse bulk directories, but never one holding an issue page —
            # those numbers are the point of this tree.
            has_issue = any(x.relative_to(ROOT).as_posix() in ISSUE_OF
                            for x in k.rglob("*.html"))
            if depth >= 2 and n > 4 and not has_issue:
                out.append(f"{prefix}{arm}{k.name}/{' ' * max(1, 46 - len(prefix) - len(k.name))}"
                           f"← {n} pages")
                continue
            out.append(f"{prefix}{arm}{k.name}/")
            walk(k, prefix + ("    " if last else "│   "), out, depth + 1)
        else:
            num = ISSUE_OF.get(rel)
            pad = " " * max(1, 46 - len(prefix) - len(k.name))
            out.append(f"{prefix}{arm}{k.name}{pad}#{num:03d}" if num
                       else f"{prefix}{arm}{k.name}")


detail = []
for name in DETAIL:
    d = ROOT / name
    if d.exists():
        detail.append(f"├── {name}/")
        walk(d, "│   ", detail, 1)
        detail.append("│")

bulk = []
for name in ("categories", "Foundation", "Commands"):
    n = by_dir.get(name, 0)
    if n:
        bulk.append(f"├── {name}/{' ' * max(1, 33 - len(name))}← {n} pages · {NOTE[name]}")

TREE_TEXT = "\n".join([
    "Platform-ops-Newsletter/",
    "│",
    "├── index.html                       ← Homepage: hero, knowledge map, archive, author",
    "├── README.md                        ← You are here (generated — edit tools/README.base.md)",
    "├── LICENSE                          ← MIT for the code, CC BY-NC-ND 4.0 for the writing",
    "├── NOTICE                           ← what that dual licence means, in one page",
    "├── feed.xml   sitemap.xml           ← generated by build_feed.py and verify.py",
    "│",
    "├── tools/                           ← THE SOURCE. Everything else here is generated.",
    f"│   ├── taxonomy.py                  ← {N_PILLARS} pillars, {N_CATS} categories, "
    f"{N_TOPICS} topics — single source of truth",
    "│   ├── build.sh                     ← one command rebuilds the whole site",
    "│   └── verify.py                    ← gates the build; refuses a broken link or a wrong count",
    "│",
    "├── assets/                          ← shared components injected into every page",
    "│   ├── megamenu.css  megamenu.js    ← cascading Browse panel",
    f"│   └── search.css    search.js      ← global search, {N_SEARCH}-entry index",
    "│",
    *bulk,
    "│",
    *detail,
]).rstrip("│\n ").rstrip()

a = src.index("## 🗂️ Repository Structure")
o = src.index("```", a)
c = src.index("```", o + 3) + 3
src = src[:o] + "```\n" + TREE_TEXT + "\n```" + src[c:]

# ── 5. the topic-request count ──────────────────────────────────────────────
sub(r"\d+ of the \d+ topics have no page yet",
    f"{TP + TN} of the {N_TOPICS} topics have no page yet", "topic-request count")

R.write_text(src, encoding="utf-8")
print(f"README -> {len(src)} bytes | {N_PAGES} pages, {N_ISSUES} issues, "
      f"{N_CMDS} commands, {N_SEARCH} search entries")
