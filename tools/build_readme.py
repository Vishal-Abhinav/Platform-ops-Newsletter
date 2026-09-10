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
