#!/usr/bin/env python3
"""Rebuild the Knowledge Map section of index.html from taxonomy.py.

Everything visible — counts, bars, the terminal tree, the summary line — is
derived here. Nothing in index.html is hand-maintained any more, so the numbers
cannot drift away from the list again.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
# TOOLS is the real tools/ directory — derived from this file's own
# location, never from ROOT. ROOT is the OUTPUT root (dist/) and source
# must never be looked up underneath it.
TOOLS = _pl.Path(__file__).resolve().parent

import html
import pathlib
import re
import sys

sys.path.insert(0, str(TOOLS))
from taxonomy import PILLARS, cat_stats  # noqa: E402
from build_feed import ISSUES            # noqa: E402  the issue register

SRC = ROOT / 'index.html'

def _slug(name):
    return name.lower().replace(" & ", "-and-").replace(" ", "-")


SLUG = {p: _slug(p) for p, _ in PILLARS}
SLUG["Data & Applications"] = "data-and-apps"   # keeps the existing anchor

# ── the "published/" listing, newest first ───────────────────────────────────
# This was a hand-kept copy of the issue register and it stopped at #057 while
# the register ran on to #067 — so the terminal announced "11 deep-dives online"
# under a feed carrying 21. It is now the register itself, sorted newest first
# the way `ls -1t` would.
#
# Two pages sit at a filename that isn't the one a reader would expect. The old
# list papered over that by hand; the map keeps that, and asserts each entry
# still exists so a rename can't leave a silent mislabel behind.
LABEL = {
    "DevOps/K8/ERROR/K8-error.html":   "k8-error-runbook.html",
    "DevOps/CICD/cicd-pipelines.html": "cicd-gitops.html",
}
_paths = {path for _n, path, *_ in ISSUES}
for _p in LABEL:
    assert _p in _paths, f"build_kmap LABEL: {_p} is no longer an issue path"

PUBLISHED = [(path, LABEL.get(path, path.rsplit("/", 1)[-1]), f"#{num:03d}")
             for num, path, *_ in sorted(ISSUES, key=lambda i: -i[0])]

# The newest issue drives the hero: the counter and the "New — Issue #NNN" pill.
LATEST_NUM, LATEST_PATH = PUBLISHED[0][2].lstrip("#"), PUBLISHED[0][0]

KEY = {"L": "live", "P": "pipe", "-": "plan"}
ZONE = {"live": "Live now", "pipe": "In pipeline", "plan": "Planned"}


def esc(s):
    return html.escape(s, quote=True)


# ── aggregate ────────────────────────────────────────────────────────────────
pillar_stats, cat_index = [], []
for pname, cats in PILLARS:
    pl = pp = pn = 0
    for cname, icon, topics in cats:
        l, p, n = cat_stats(topics)
        pl += l; pp += p; pn += n
        cat_index.append((pname, cname, l, p, n, len(topics)))
    pillar_stats.append((pname, pl, pp, pn, pl + pp + pn, cats))

T_LIVE = sum(s[1] for s in pillar_stats)
T_PIPE = sum(s[2] for s in pillar_stats)
T_PLAN = sum(s[3] for s in pillar_stats)
T_ALL = T_LIVE + T_PIPE + T_PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_PILL = len(PILLARS)


# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """/* ─── KNOWLEDGE MAP: STATS, FILTERS, PILLARS, CATEGORIES, TOPICS ─── */
.km-stats{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--hairline-2);
  border:1px solid var(--hairline-2);margin:-32px 0 14px;}
.km-stat{background:var(--page-bg);padding:16px 8px 14px;text-align:center;}
.km-stat-n{font-family:'Bebas Neue',sans-serif;font-size:30px;line-height:1;color:var(--heading-fg);letter-spacing:0.5px;}
.km-stat-n.live{color:#5a9c1a;}
.km-stat-n.pipe{color:#b97309;}
.km-stat-n.plan{color:var(--ash);}
.km-stat-l{font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:1.6px;
  text-transform:uppercase;color:var(--muted);margin-top:6px;}
html[data-theme="dark"] .km-stat-n.live{color:var(--lime);}
html[data-theme="dark"] .km-stat-n.pipe{color:var(--amber);}

.km-bar{display:flex;height:5px;overflow:hidden;margin-bottom:26px;background:var(--hairline-1);}
.km-bar i{display:block;height:100%;}
.km-bar i.live{background:var(--lime);}
.km-bar i.pipe{background:var(--amber);}
.km-bar i.plan{background:var(--hairline-4);}

.km-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px;}
.km-search{position:relative;flex:1 1 200px;min-width:0;display:flex;align-items:center;}
.km-search svg{position:absolute;left:12px;width:14px;height:14px;stroke:var(--muted);fill:none;
  stroke-width:2;pointer-events:none;}
.km-search input{width:100%;min-width:0;background:var(--wash-1);border:1px solid var(--hairline-3);
  border-radius:3px;padding:11px 12px 11px 34px;font-family:'DM Mono',monospace;font-size:11.5px;
  letter-spacing:0.6px;color:var(--page-fg);outline:none;transition:border-color .2s,background .2s;
  -webkit-appearance:none;appearance:none;}
.km-search input::placeholder{color:var(--ash);}
.km-search input:focus{border-color:var(--crimson);background:var(--page-bg);}
.km-filters{display:flex;gap:2px;flex-shrink:0;}
.km-f{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.4px;text-transform:uppercase;
  padding:10px 13px;border:1px solid var(--hairline-3);background:transparent;color:var(--muted);
  cursor:pointer;transition:background .2s,color .2s,border-color .2s;}
.km-f:hover{color:var(--heading-fg);border-color:var(--hairline-5);}
.km-f.on{background:var(--cta-bg);border-color:var(--cta-bg);color:var(--cta-fg);}
.km-result{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;
  color:var(--muted);min-height:15px;margin-bottom:22px;}
.km-result b{color:var(--crimson);font-weight:400;}

.km-pillars{display:flex;flex-direction:column;gap:2px;}
.km-pillar{background:var(--panel-bg);position:relative;}
.km-pillar::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;
  background:transparent;transition:background .25s;}
.km-pillar.open::before{background:var(--crimson);}
.km-p-head{display:flex;align-items:center;gap:12px;width:100%;padding:16px 22px;background:none;
  border:0;cursor:pointer;text-align:left;font:inherit;color:inherit;transition:background .2s;}
.km-p-head:hover{background:var(--wash-2);}
.km-p-idx{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1px;color:var(--ash);flex-shrink:0;}
.km-p-name{font-family:'Bebas Neue',sans-serif;font-size:23px;letter-spacing:1.2px;
  color:var(--heading-fg);line-height:1;flex:1;min-width:0;}
.km-p-counts{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1px;color:var(--muted);
  white-space:nowrap;flex-shrink:0;}
.km-p-counts em{font-style:normal;color:#5a9c1a;}
html[data-theme="dark"] .km-p-counts em{color:var(--lime);}
.km-p-mini{display:flex;width:52px;height:4px;flex-shrink:0;background:var(--hairline-1);overflow:hidden;}
.km-p-mini i.live{background:var(--lime);}
.km-p-mini i.pipe{background:var(--amber);}
.km-p-mini i.plan{background:var(--hairline-4);}
.km-p-arrow{font-family:'DM Mono',monospace;font-size:13px;color:var(--muted);flex-shrink:0;
  transition:transform .3s,color .2s;}
.km-pillar.open .km-p-arrow{transform:rotate(-180deg);color:var(--crimson);}
.km-p-body{display:grid;grid-template-rows:0fr;transition:grid-template-rows .4s cubic-bezier(.25,.46,.45,.94);}
.km-pillar.open .km-p-body{grid-template-rows:1fr;}
.km-p-inner{overflow:hidden;min-height:0;}
.km-cats{padding:0 12px 12px;display:flex;flex-direction:column;gap:1px;}

/* Same card language as the old domain cards — icon tile, Bebas title, status
   line with a live dot — just at the tighter scale 33 of them demand. */
.km-cat{background:var(--card-bg);position:relative;}
.km-cat::before{content:'';position:absolute;top:0;left:0;width:2px;height:100%;
  background:transparent;transition:background .25s;}
.km-cat.open::before{background:var(--crimson);}
.km-c-head{display:flex;align-items:center;gap:13px;width:100%;padding:13px 16px;background:none;
  border:0;cursor:pointer;text-align:left;font:inherit;color:inherit;transition:background .2s;}
.km-c-head:hover{background:var(--wash-1);}
.km-c-icon{width:34px;height:34px;display:flex;align-items:center;justify-content:center;
  font-size:17px;line-height:1;background:var(--wash-2);border-radius:4px;flex-shrink:0;}
.km-c-meta{flex:1;min-width:0;}
.km-c-name{display:block;font-family:'Bebas Neue',sans-serif;font-size:21px;letter-spacing:1px;
  line-height:1;color:var(--heading-fg);}
.km-c-counts{display:flex;align-items:center;gap:6px;margin-top:4px;
  font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;text-transform:uppercase;
  color:var(--muted);}
.km-c-counts em{font-style:normal;color:#5a9c1a;font-weight:700;}
.km-c-counts .dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;background:var(--lime);
  animation:legend-pulse 2s ease-in-out infinite;}
.km-c-counts .dot.none{background:transparent;border:1.5px dashed var(--ash);animation:none;box-shadow:none;}
html[data-theme="dark"] .km-c-counts em{color:var(--lime);}
.km-c-arrow{font-family:'DM Mono',monospace;font-size:12px;color:var(--ash);flex-shrink:0;
  transition:transform .3s;}
.km-cat.open .km-c-arrow{transform:rotate(-180deg);color:var(--crimson);}
.km-c-body{display:grid;grid-template-rows:0fr;transition:grid-template-rows .35s cubic-bezier(.25,.46,.45,.94);}
.km-cat.open .km-c-body{grid-template-rows:1fr;}
.km-c-inner{overflow:hidden;min-height:0;}
.km-topics{display:flex;flex-wrap:wrap;gap:5px;padding:4px 14px 18px;
  border-top:1px solid var(--hairline-1);margin:0 0 0 0;}

.km-zone{width:100%;display:flex;align-items:center;gap:8px;font-family:'DM Mono',monospace;
  font-size:8.5px;letter-spacing:2px;text-transform:uppercase;margin:12px 0 5px;}
.km-zone::after{content:'';flex:1;height:1px;background:var(--hairline-2);}
.km-zone:first-child{margin-top:14px;}
.km-zone.live{color:#5a9c1a;}
.km-zone.pipe{color:#b97309;}
.km-zone.plan{color:var(--ash);}
html[data-theme="dark"] .km-zone.live{color:var(--lime);}
html[data-theme="dark"] .km-zone.pipe{color:var(--amber);}

.km-t{display:inline-block;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:0.7px;
  padding:4px 10px;border-radius:20px;text-transform:uppercase;text-decoration:none;
  border:1px solid transparent;transition:background .2s,color .2s,border-color .2s;}
button.km-t{font-family:'DM Mono',monospace;cursor:pointer;line-height:1.5;}
.km-t.live{background:rgba(132,204,22,0.14);border-color:rgba(132,204,22,0.4);color:#4c840f;}
.km-t.live:hover{background:var(--lime);color:#0c0e12;border-color:var(--lime);}
.km-t.live::before{content:'●';font-size:7px;vertical-align:middle;margin-right:5px;color:var(--lime);}
.km-t.live::after{content:' ↗';letter-spacing:0;}
.km-t.pipe{background:rgba(245,158,11,0.12);border-color:rgba(245,158,11,0.35);color:#a06508;}
.km-t.plan{background:transparent;border:1px dashed var(--hairline-4);color:var(--ash);}
html[data-theme="dark"] .km-t.live{color:#a7e137;}
html[data-theme="dark"] .km-t.pipe{color:#f5b544;}
html[data-theme="dark"] .km-t.plan{color:#7d7a72;}
.km-t[hidden],.km-zone[hidden],.km-cat[hidden],.km-pillar[hidden]{display:none!important;}

/* A pillar that isn't subdivided (Foundation, Networking, Cloud) would otherwise
   show a category row repeating its own name — drop the row, keep the topics. */
.km-cat.solo{background:transparent;}
.km-cat.solo > .km-c-head{display:none;}
.km-cat.solo > .km-c-body{grid-template-rows:1fr;}
.km-cat.solo .km-topics{border-top:0;padding-top:0;}
.km-cat.solo .km-zone:first-child{margin-top:4px;}

.km-empty{font-family:'DM Mono',monospace;font-size:10.5px;letter-spacing:1px;color:var(--muted);
  padding:26px 4px;text-align:center;}
/* --ash is a light-theme value and stays bright in dark mode, so the "planned"
   greys have to be restated here or the backlog shouts louder than what's live. */
html[data-theme="dark"] .km-stat-n.plan,
html[data-theme="dark"] .km-zone.plan,
html[data-theme="dark"] .km-p-idx,
html[data-theme="dark"] .km-c-arrow,
html[data-theme="dark"] .km-search input::placeholder{color:#6e6b64;}

/* The knowledge row is a grid; without min-width:0 the column is sized by its
   widest min-content child (the search input's default size) and pushes the
   whole page sideways on a phone. */
.knowledge-row > .kr-col{min-width:0;}
@media(max-width:600px){
  /* 5 cells over 3 columns leaves a hole; 6 tracks lets the last two split a row. */
  .km-stats{grid-template-columns:repeat(6,1fr);}
  .km-stat{grid-column:span 2;}
  .km-stat:nth-child(4),.km-stat:nth-child(5){grid-column:span 3;}
  .km-stat-n{font-size:26px;}
  .km-p-mini{display:none;}
  .km-p-counts,.km-c-counts{font-size:8.5px;}
  .km-p-counts .u,.km-c-counts .u{display:none;}
  .km-p-head{padding:14px 16px;gap:9px;}
  .km-c-head{padding:10px 11px;gap:9px;}
  .km-cats{padding:0 8px 8px;}
  .km-topics{padding:4px 11px 16px;}
}

/* ─── LEGEND + KNOWLEDGE-MAP TERMINAL ─── */
.legend-row{display:flex;align-items:center;gap:20px;margin:0 0 26px;flex-wrap:wrap;}
.legend-item{display:flex;align-items:center;gap:8px;font-family:'DM Mono',monospace;font-size:10px;
  letter-spacing:1px;text-transform:uppercase;color:var(--muted);}
.legend-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.legend-dot.live{background:var(--lime);box-shadow:0 0 0 3px rgba(132,204,22,0.18);animation:legend-pulse 2s ease-in-out infinite;}
.legend-dot.pipe{background:var(--amber);box-shadow:0 0 0 3px rgba(245,158,11,0.16);}
.legend-dot.soon{background:transparent;border:1.5px dashed var(--muted);}
@keyframes legend-pulse{0%,100%{box-shadow:0 0 0 3px rgba(132,204,22,0.18);}50%{box-shadow:0 0 0 5px rgba(132,204,22,0.08);}}

.kmap-terminal{background:#0d0f14;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-shadow:0 32px 80px rgba(0,0,0,.45);overflow:hidden;margin-bottom:40px;position:relative;}
.kmap-terminal::before{content:'';position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%22160%22%20height%3D%22160%22%20viewBox%3D%220%200%20160%20160%22%3E%3Cg%20fill%3D%22none%22%20stroke%3D%22%23ffffff%22%20stroke-width%3D%221%22%20opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M0%2C40%20H60%20V0%22/%3E%3Cpath%20d%3D%22M160%2C120%20H100%20V160%22/%3E%3Cpath%20d%3D%22M0%2C160%20V140%20H40%22/%3E%3Cpath%20d%3D%22M160%2C0%20V60%20H120%22/%3E%3Ccircle%20cx%3D%2260%22%20cy%3D%2240%22%20r%3D%223%22/%3E%3Ccircle%20cx%3D%22100%22%20cy%3D%22120%22%20r%3D%223%22/%3E%3Ccircle%20cx%3D%2240%22%20cy%3D%22140%22%20r%3D%223%22/%3E%3Ccircle%20cx%3D%22120%22%20cy%3D%2260%22%20r%3D%223%22/%3E%3Cpath%20d%3D%22M0%2C90%20H160%22%20stroke-dasharray%3D%222%206%22/%3E%3Cpath%20d%3D%22M80%2C0%20V160%22%20stroke-dasharray%3D%222%206%22/%3E%3C/g%3E%3C/svg%3E");background-size:160px 160px;animation:bg-drift 60s linear infinite;pointer-events:none;z-index:0;}
.kmap-terminal .terminal-bar{position:relative;z-index:1;}
/* The terminal is dark in both themes, so it has to state its own foreground —
   inheriting the page colour left bare rows black-on-black in light mode. */
.kmap-body{position:relative;z-index:1;padding:24px 28px;font-family:'DM Mono',monospace;
  font-size:11.5px;line-height:1.8;overflow-x:auto;color:rgba(255,255,255,.55);}
.kt-row{display:block;white-space:pre;opacity:0;transform:translateX(-10px);transition:opacity .45s ease,transform .45s ease;}
.kt-row-split{display:flex!important;align-items:baseline;justify-content:space-between;gap:14px;white-space:normal;}
.kt-row-split .kt-left{white-space:pre;}
.kt-row.visible{opacity:1;transform:translateX(0);}
.tl-branch{color:rgba(255,255,255,.16);}
.tl-dir{color:rgba(255,255,255,.55);}
.tl-live{color:#fff;text-decoration:none;border-bottom:1px dashed rgba(132,204,22,.55);transition:color .2s,border-color .2s;white-space:normal;}
.tl-live:hover{color:var(--lime);border-color:var(--lime);}
.tl-live::before{content:'● ';color:var(--lime);font-size:8px;}
.tl-soon{color:rgba(255,255,255,.25);white-space:normal;}
.tl-out{color:rgba(255,255,255,.3);}
.tl-count-live{color:var(--lime);white-space:pre;}
.tl-count-soon{color:rgba(255,255,255,.32);white-space:pre;}
.tl-ok{color:var(--lime);}
@media(max-width:900px){ .kmap-body{font-size:10px;padding:20px 14px;} }
"""


# ── terminal tree ────────────────────────────────────────────────────────────
def row(inner):
    return f'        <span class="tl kt-row">{inner}</span>'


def row_split(left, right, cls="tl-count-live"):
    return (f'        <span class="tl kt-row kt-row-split"><span class="kt-left">{left}</span>'
            f'<span class="{cls}">{right}</span></span>')


tree = [
    row('<span class="tl-prompt">❯</span> <span class="tl-cmd">tree platform-ops/ --master-map-2026</span>'),
    row('platform-ops/'),
]
for i, (pname, pl, pp, pn, tot, _cats) in enumerate(pillar_stats):
    last = (i == len(pillar_stats) - 1)
    branch = '└── ' if last else '├── '
    left = (f'<span class="tl-branch">{branch}</span>'
            f'<span class="tl-dir">{SLUG[pname]}/</span>')
    cls = "tl-count-live" if pl else "tl-count-soon"
    tree.append(row_split(left, f'[ {pl} live / {tot} ]', cls))

tree.append(row(' '))
tree.append(row('<span class="tl-prompt">❯</span> <span class="tl-cmd">ls -1t published/</span>'))
for j, (href, label, issue) in enumerate(PUBLISHED):
    b = '└── ' if j == len(PUBLISHED) - 1 else '├── '
    tree.append(row(f'<span class="tl-branch">{b}</span>'
                    f'<a href="{href}" class="tl-live">{label}</a> '
                    f'<span class="tl-out">· issue {issue}</span>'))
tree.append(row(' '))
tree.append(row(f'<span class="tl-ok">✓</span> <span class="tl-out">{N_PILL} pillars, {N_CATS} categories, '
                f'{T_ALL} topics — {len(PUBLISHED)} deep-dives online</span>'))
tree.append(row(f'<span class="tl-ok">✓</span> <span class="tl-out">{T_LIVE} topics live · {T_PIPE} in pipeline · '
                f'{T_PLAN} planned</span>'))
tree.append(row('<span class="tl-prompt">❯</span> <span class="cursor-blink"></span>'))
TREE = "\n".join(tree)


# ── pillars / categories / topics ────────────────────────────────────────────
def flexes(l, p, n):
    """Zero-count segments must not render, or flex:0 still shows a hairline."""
    out = []
    for cls, v in (("live", l), ("pipe", p), ("plan", n)):
        if v:
            out.append(f'<i class="{cls}" style="flex:{v}"></i>')
    return "".join(out)


blocks = []
for i, (pname, pl, pp, pn, tot, cats) in enumerate(pillar_stats):
    # Pillars start CLOSED. With all 621 chips rendered the column ran to
    # ~15,500px and the page read as endless; collapsed it is 11 tidy rows you
    # can take in at once. The categories inside stay open, so opening a
    # pillar shows its whole contents in one click rather than two.
    open_cls = ""
    cat_html = []
    solo = len(cats) == 1 and cats[0][0] == pname
    for cname, icon, topics in cats:
        l, p, n = cat_stats(topics)
        chips = []
        for status in ("L", "P", "-"):
            group = [t for t in topics if t[1] == status]
            if not group:
                continue
            k = KEY[status]
            chips.append(f'          <div class="km-zone {k}" data-zone="{k}">{ZONE[k]}</div>')
            for tname, _st, href in group:
                lbl = esc(tname)
                if k == "live" and href:
                    chips.append(f'          <a class="km-t live" data-s="live" href="{href}">{lbl}</a>')
                else:
                    chips.append(f'          <button type="button" class="km-t {k}" '
                                 f'data-s="{k}">{lbl}</button>')
        cat_html.append(f"""        <div class="km-cat open{' solo' if solo else ''}" data-cat>
          <button class="km-c-head" type="button" aria-expanded="true">
            <span class="km-c-icon" aria-hidden="true">{icon}</span>
            <span class="km-c-meta">
              <span class="km-c-name">{esc(cname)}</span>
              <span class="km-c-counts"><i class="dot{'' if l else ' none'}"></i><em>{l}</em><span class="u"> live</span> · {p}<span class="u"> pipe</span> · {n}<span class="u"> planned</span></span>
            </span>
            <span class="km-c-arrow" aria-hidden="true">⌄</span>
          </button>
          <div class="km-c-body"><div class="km-c-inner"><div class="km-topics">
{chr(10).join(chips)}
          </div></div></div>
        </div>""")

    blocks.append(f"""      <section class="km-pillar{open_cls}" data-pillar>
        <button class="km-p-head" type="button" aria-expanded="{'true' if open_cls else 'false'}">
          <span class="km-p-idx">{i + 1:02d}</span>
          <span class="km-p-name">{esc(pname)}</span>
          <span class="km-p-counts"><em>{pl}</em><span class="u"> live</span> · {pp}<span class="u"> pipe</span> · {pn}<span class="u"> planned</span></span>
          <span class="km-p-mini" aria-hidden="true">{flexes(pl, pp, pn)}</span>
          <span class="km-p-arrow" aria-hidden="true">⌄</span>
        </button>
        <div class="km-p-body"><div class="km-p-inner"><div class="km-cats">
{chr(10).join(cat_html)}
        </div></div></div>
      </section>""")

PILLAR_HTML = "\n".join(blocks)

SECTION = f"""    <div class="section-tag">Knowledge Map</div>
    <h2 class="section-title">WHAT WE COVER</h2>
    <p class="section-lead">The 2026 master map — {T_ALL} topics, {N_CATS} categories, {N_PILL} pillars. Search it, filter it, or open a pillar to see exactly what's shipped and what's queued.</p>

    <div class="km-stats">
      <div class="km-stat"><div class="km-stat-n">{T_ALL}</div><div class="km-stat-l">Topics</div></div>
      <div class="km-stat"><div class="km-stat-n">{N_CATS}</div><div class="km-stat-l">Categories</div></div>
      <div class="km-stat"><div class="km-stat-n live">{T_LIVE}</div><div class="km-stat-l">Live</div></div>
      <div class="km-stat"><div class="km-stat-n pipe">{T_PIPE}</div><div class="km-stat-l">In pipeline</div></div>
      <div class="km-stat"><div class="km-stat-n plan">{T_PLAN}</div><div class="km-stat-l">Planned</div></div>
    </div>
    <div class="km-bar" aria-hidden="true">{flexes(T_LIVE, T_PIPE, T_PLAN)}</div>

    <div class="legend-row">
      <div class="legend-item"><span class="legend-dot live"></span> Live — published &amp; linked</div>
      <div class="legend-item"><span class="legend-dot pipe"></span> In pipeline — next up</div>
      <div class="legend-item"><span class="legend-dot soon"></span> Planned — on the backlog</div>
    </div>

    <div class="km-controls">
      <label class="km-search">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <input type="search" id="kmSearch" autocomplete="off" spellcheck="false"
               placeholder="Search {T_ALL} topics — kubernetes, bgp, terraform, slo…"
               aria-label="Search the knowledge map">
      </label>
      <div class="km-filters" role="group" aria-label="Filter by status">
        <button type="button" class="km-f on" data-f="all">All</button>
        <button type="button" class="km-f" data-f="live">Live</button>
        <button type="button" class="km-f" data-f="pipe">Pipeline</button>
        <button type="button" class="km-f" data-f="plan">Planned</button>
      </div>
    </div>
    <div class="km-result" id="kmResult" aria-live="polite"></div>

    <div class="kmap-terminal">
      <div class="terminal-bar">
        <div class="t-dot r"></div><div class="t-dot y"></div><div class="t-dot g"></div>
        <div class="t-title">platform-ops ~ knowledge-map</div>
      </div>
      <div class="terminal-body kmap-body">
{TREE}
      </div>
    </div>

    <div class="km-pillars" id="kmPillars">
{PILLAR_HTML}
    </div>
    <div class="km-empty" id="kmEmpty" hidden>No topic matches that search.</div>
  </div>"""


# ── JS ───────────────────────────────────────────────────────────────────────
JS = """/* ── Knowledge map: two-level accordion + search + status filter ── */
(function(){
  const root = document.getElementById('kmPillars');
  if (!root) return;
  const search  = document.getElementById('kmSearch');
  const result  = document.getElementById('kmResult');
  const empty   = document.getElementById('kmEmpty');
  const pillars = Array.from(root.querySelectorAll('[data-pillar]'));
  const cats    = Array.from(root.querySelectorAll('[data-cat]'));
  const topics  = Array.from(root.querySelectorAll('.km-t'));
  const TOTAL   = topics.length;
  let filter = 'all';

  topics.forEach(t => { t.dataset.q = t.textContent.trim().toLowerCase(); });

  const setOpen = (el, on) => {
    if (el.classList.contains('solo')) return;   /* header hidden; stays open */
    el.classList.toggle('open', on);
    const head = el.querySelector('button');
    if (head) head.setAttribute('aria-expanded', on ? 'true' : 'false');
  };

  /* Accordion — one pillar open at a time, one category open per pillar. */
  root.addEventListener('click', e => {
    const pHead = e.target.closest('.km-p-head');
    if (pHead) {
      const p = pHead.closest('[data-pillar]');
      setOpen(p, !p.classList.contains('open'));   /* toggle this one only */
      setTimeout(syncIssuesScrollHeight, 460);
      return;
    }
    const cHead = e.target.closest('.km-c-head');
    if (cHead) {
      const c = cHead.closest('[data-cat]');
      setOpen(c, !c.classList.contains('open'));   /* toggle this one only */
      setTimeout(syncIssuesScrollHeight, 400);
    }
  });

  function apply(){
    const q = (search.value || '').trim().toLowerCase();
    const active = q.length > 0 || filter !== 'all';
    let shown = 0;

    cats.forEach(c => {
      let hits = 0;
      c.querySelectorAll('.km-t').forEach(t => {
        const ok = (!q || t.dataset.q.indexOf(q) !== -1) &&
                   (filter === 'all' || t.dataset.s === filter);
        t.hidden = !ok;
        if (ok) hits++;
      });
      /* A zone heading only earns its place if something under it survived. */
      c.querySelectorAll('.km-zone').forEach(z => {
        let n = 0, el = z.nextElementSibling;
        while (el && !el.classList.contains('km-zone')) {
          if (el.classList.contains('km-t') && !el.hidden) n++;
          el = el.nextElementSibling;
        }
        z.hidden = n === 0;
      });
      c.hidden = active && hits === 0;
      if (active && hits > 0) setOpen(c, true);
      if (!active) setOpen(c, true);
      shown += hits;
      c.dataset.hits = hits;
    });

    pillars.forEach(p => {
      const hits = Array.from(p.querySelectorAll('[data-cat]'))
                        .reduce((n, c) => n + Number(c.dataset.hits || 0), 0);
      p.hidden = active && hits === 0;
      if (active) setOpen(p, hits > 0);
    });

    if (!active) {
      /* Back to the default shape, not to everything-open: a search that
         matched three pillars must not leave all eleven expanded behind it. */
      pillars.forEach(p => setOpen(p, false));
      result.textContent = '';
    } else {
      result.innerHTML = '<b>' + shown + '</b> of ' + TOTAL + ' topics' +
        (q ? ' matching “' + q.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '”' : '');
    }
    if (empty) empty.hidden = shown !== 0;
    setTimeout(syncIssuesScrollHeight, 60);
  }

  let t;
  search.addEventListener('input', () => { clearTimeout(t); t = setTimeout(apply, 120); });
  search.addEventListener('search', apply);
  document.querySelectorAll('.km-f').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.km-f').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
      filter = btn.dataset.f;
      apply();
    });
  });
})();"""


# ── splice ───────────────────────────────────────────────────────────────────
src = SRC.read_text(encoding='utf-8')

# 1. CSS
start = src.index('/* ─── TOPIC CARDS ─── */')
end = src.index('/* ─── TOOLCHAIN DIAGRAM ─── */')
src = src[:start] + CSS + "\n" + src[end:]

# 2. HTML section
h0 = src.index('    <div class="section-tag">Knowledge Map</div>')
h1 = src.index('  <!-- ═══════════ LATEST ISSUES ═══════════ -->')
src = src[:h0] + SECTION + "\n\n" + src[h1:]

# 3. JS accordion
j0 = src.index('/* ── Accordion ── */')
j1 = src.index('/* ── Keep the Latest Issues scroll panel flush')
src = src[:j0] + JS + "\n\n" + src[j1:]

# 4. cursor-ring hover targets
src = src.replace("'a,button,.topic-card,.issue-card",
                  "'a,button,.km-p-head,.km-c-head,.issue-card")

# 5. drop rules for the grid that no longer exists
src = src.replace(".kr-topics .topics-grid { grid-template-columns: 1fr; }\n", "")
src = src.replace("  .topics-grid{grid-template-columns:1fr;}\n", "")

# 6. the knowledge constellation ──────────────────────────────────────────────
#
# Thirteen pillars around a centre, sized by how much each one actually holds.
# Drawn here rather than written into index.base.html for the usual reason: the
# names, the counts and the anchors all come off the taxonomy, so a pillar
# added there appears here, correctly sized and correctly linked, without
# anyone remembering to update a hand-drawn diagram.
#
# The anchors are the ones build_hubs.py already writes onto the category
# index — `<section id="kubernetes-openshift">` and friends — so these links
# point into a page that exists today. No new route is invented, and no
# existing page is modified to make this work.
import math  # noqa: E402

_PILL = []
for _name, _cats in PILLARS:
    _l = _p = _n = 0
    for _c, _i, _topics in _cats:
        a, b, c = cat_stats(_topics)
        _l += a; _p += b; _n += c
    _PILL.append({
        "name": _name,
        "cats": len(_cats),
        "live": _l, "pipe": _p, "plan": _n,
        "total": _l + _p + _n,
        # build_hubs.py: pname.lower().replace(" & ", "-").replace(" ", "-")
        "anchor": _name.lower().replace(" & ", "-").replace(" ", "-"),
    })

_MAXT = max(p["total"] for p in _PILL)
_CX, _CY, _RING = 500.0, 430.0, 248.0
_nodes, _edges, _dots, _items = [], [], [], []
# Track what the drawing actually occupies so the viewBox can be fitted to it
# rather than guessed. A guessed box is how a diagram ends up centred in a
# screenful of empty dark: the shape is fine, the frame is wrong.
_ext = []   # (x0, y0, x1, y1) boxes in user units
_CHW = 7.0  # DM Mono advance at 11.5px — close enough to fit a label box

for _i, _p in enumerate(sorted(_PILL, key=lambda d: -d["total"])):
    # Start at the top and go clockwise. The largest pillar leads, so the eye
    # lands on the substantial part of the map first rather than on whatever
    # happens to sort first alphabetically.
    _ang = -math.pi / 2 + (2 * math.pi * _i / len(_PILL))
    _x = _CX + _RING * math.cos(_ang)
    _y = _CY + _RING * math.sin(_ang)
    # Area, not radius, tracks the count — a pillar holding four times as much
    # should look four times as big, and radius alone would make it sixteen.
    _r = 15 + 23 * math.sqrt(_p["total"] / _MAXT)
    _lx = _CX + (_RING + _r + 14) * math.cos(_ang)
    _ly = _CY + (_RING + _r + 14) * math.sin(_ang)
    _anchor_attr = ("middle" if abs(_x - _CX) < 40
                    else ("start" if _x > _CX else "end"))
    _lw = len(_p["name"]) * _CHW
    _lx0 = _lx if _anchor_attr == "start" else (
        _lx - _lw if _anchor_attr == "end" else _lx - _lw / 2)
    _ext.append((_x - _r, _y - _r, _x + _r, _y + _r))          # the disc
    _ext.append((_lx0, _ly - 9, _lx0 + _lw, _ly + 9))          # its label
    _href = f"categories/index.html#{_p['anchor']}"
    _label = html.escape(_p["name"])
    _tot, _live = _p["total"], _p["live"]

    _edges.append(
        f'<path class="kc-edge" id="kc-e{_i}" d="M{_CX:.0f},{_CY:.0f} '
        f'L{_x:.1f},{_y:.1f}"/>')
    _dots.append(
        f'<circle class="kc-dot" r="2.5" style="offset-path:path(\'M{_CX:.0f},'
        f'{_CY:.0f} L{_x:.1f},{_y:.1f}\'); animation-delay:{_i * 0.31:.2f}s"/>')
    _nodes.append(
        f'<a class="kc-node" href="{_href}" data-edge="kc-e{_i}" '
        f'data-t="{_label}" '
        f'data-d="{_tot} topics in {_p["cats"]} categor'
        f'{"y" if _p["cats"] == 1 else "ies"} · {_live} live">'
        f'<circle class="kc-halo" cx="{_x:.1f}" cy="{_y:.1f}" r="{_r + 9:.1f}"/>'
        f'<circle class="kc-disc" cx="{_x:.1f}" cy="{_y:.1f}" r="{_r:.1f}"/>'
        f'<text class="kc-n" x="{_x:.1f}" y="{_y:.1f}">{_tot}</text>'
        f'<text class="kc-l" x="{_lx:.1f}" y="{_ly:.1f}" '
        f'text-anchor="{_anchor_attr}">{_label}</text>'
        f'</a>')
    # The same thirteen, as a list. This is what a phone shows and what a
    # screen reader reads; the circle is the desktop presentation of it.
    _items.append(
        f'<li><a href="{_href}"><b>{_label}</b>'
        f'<span>{_tot} topics · {_live} live · {_p["cats"]} categor'
        f'{"y" if _p["cats"] == 1 else "ies"}</span></a></li>')

_ext.append((_CX - 74, _CY - 74, _CX + 74, _CY + 74))          # the core ring
_PAD = 14.0
_vx0 = min(e[0] for e in _ext) - _PAD
_vy0 = min(e[1] for e in _ext) - _PAD
_vw  = max(e[2] for e in _ext) + _PAD - _vx0
_vh  = max(e[3] for e in _ext) + _PAD - _vy0

KC = f"""<section class="kc" id="constellation" aria-labelledby="kc-head">
  <div class="kc-inner">
    <h2 class="kc-head" id="kc-head">The knowledge constellation</h2>
    <p class="kc-lede">{len(_PILL)} pillars, sized by how much each one holds.
      Follow one into its categories.</p>

    <div class="kc-stage">
      <svg viewBox="{_vx0:.0f} {_vy0:.0f} {_vw:.0f} {_vh:.0f}" role="img" aria-label="The {len(_PILL)} knowledge pillars arranged around Platform Ops, sized by topic count. The same list follows in text.">
        <g class="kc-edges">{''.join(_edges)}</g>
        <g class="kc-flow" aria-hidden="true">{''.join(_dots)}</g>
        <g class="kc-core" aria-hidden="true">
          <circle class="kc-core-ring" cx="{_CX:.0f}" cy="{_CY:.0f}" r="74"/>
          <circle class="kc-core-disc" cx="{_CX:.0f}" cy="{_CY:.0f}" r="58"/>
          <text class="kc-core-t" x="{_CX:.0f}" y="{_CY - 8:.0f}">PLATFORM</text>
          <text class="kc-core-t" x="{_CX:.0f}" y="{_CY + 12:.0f}">OPS</text>
        </g>
        <g class="kc-nodes">{''.join(_nodes)}</g>
      </svg>
      <div class="kc-tip" id="kcTip" role="status" aria-live="polite"><b></b><span></span></div>
    </div>

    <ul class="kc-list">{''.join(_items)}</ul>
  </div>
</section>"""

_k0 = src.index("<!-- KC:START -->")
_k1 = src.index("<!-- KC:END -->") + len("<!-- KC:END -->")
src = src[:_k0] + KC + src[_k1:]

# 7. the notice board ─────────────────────────────────────────────────────────
#
# A departure board for the archive: what is newest, in the format a board at
# a station would use. Generated from the same issue register the feed and the
# footer read, so the newest row cannot be the issue before last — which is
# exactly what the old hand-typed hero pill was, three issues running.
#
# ON THE WORD "FLASHING": this board does not flash, and that is deliberate
# rather than a liberty. WCAG 2.3.1 draws the line at three flashes a second
# because anything faster is a seizure risk, and a page that strobes is a page
# people close. What it does instead is what a real board does — a lamp that
# breathes at 2.4s, and characters that flap into place once on arrival and
# then hold still. It reads as live; it does not blink at anyone.
_ISS = sorted(ISSUES, key=lambda r: -r[0])[:4]
_NB_ROWS = []
for _n, _path, _title, _desc, _dt in _ISS:
    _cat = _path.split("/")[0].replace("-", " ")
    _new = ' data-new="1"' if _n == _ISS[0][0] else ""
    _NB_ROWS.append(
        f'<a class="nb-row" href="{_path}"{_new}>'
        f'<span class="nb-no">#{_n:03d}</span>'
        f'<span class="nb-ti">{html.escape(_title)}</span>'
        f'<span class="nb-ca">{html.escape(_cat)}</span>'
        f'<span class="nb-st">{"NEW" if _n == _ISS[0][0] else "&#183;"}</span>'
        f'</a>')

# One <span> per character so each can settle on its own beat. Spaces get a
# non-breaking space or the inline-block collapses them and the title closes
# up into one word as it lands.
_HEAD = _ISS[0][2].upper()
_FLAP = "".join(
    f'<span style="animation-delay:{i * 0.035:.3f}s">'
    f'{"&#160;" if ch == " " else html.escape(ch)}</span>'
    for i, ch in enumerate(_HEAD))

_STAMP = _ISS[0][4].strftime("%d %b %Y").upper()

NB = f"""<section class="nb" aria-labelledby="nb-head">
  <div class="nb-inner">
    <div class="nb-frame">
      <div class="nb-top">
        <span class="nb-lamp" aria-hidden="true"></span>
        <span class="nb-live">Live</span>
        <h2 class="nb-title" id="nb-head">Platform Ops &#183; notice board</h2>
        <span class="nb-stamp">{_STAMP}</span>
      </div>

      <div class="nb-hero">
        <div class="nb-hero-meta">Now published &#183; Issue #{_ISS[0][0]:03d}</div>
        <p class="nb-flap" aria-label="{html.escape(_ISS[0][2])}">{_FLAP}</p>
        <a class="nb-cta" href="{_ISS[0][1]}">Read issue #{_ISS[0][0]:03d}
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
      </div>

      <div class="nb-list" role="list">
        <div class="nb-head" aria-hidden="true">
          <span class="nb-no">Issue</span><span class="nb-ti">Title</span>
          <span class="nb-ca">Series</span><span class="nb-st">Status</span>
        </div>
        {''.join(_NB_ROWS)}
      </div>

      <div class="nb-foot">{len(ISSUES)} issues in the archive &#183;
        <a href="#issues">browse them all</a></div>
    </div>
  </div>
</section>"""

_n0 = src.index("<!-- NB:START -->")
_n1 = src.index("<!-- NB:END -->") + len("<!-- NB:END -->")
src = src[:_n0] + NB + src[_n1:]


# 6. hero: the issue counter and the "New" pill ───────────────────────────────
# Both were typed into index.base.html and both were still on #057 three issues
# after #060 shipped. They now come off the register like everything else.
def _one(pattern, repl, why):
    """repl is a callable, never a template — a \\g<1> in a string replacement
    is silently eaten by the backslash-escaping these helpers elsewhere do, and
    lands "\\g<1>67" in the page instead of the number."""
    global src
    new, n = re.subn(pattern, repl, src, count=1)
    assert n == 1, f"index.html: {why} — matched {n} times, expected 1:\n  {pattern}"
    src = new


# The knowledge band under the hero. Every cell is filled from the register
# rather than typed, and each is substituted BY NAME rather than by position,
# so adding a seventh cell can never quietly hand one cell another's number —
# which is exactly what a single `data-target="\d+"` pattern would do the
# moment a second counter appeared on the page.
_KS = {
    "topics":     T_ALL,
    "categories": N_CATS,
    "pillars":    N_PILL,
    "live":       T_LIVE,
    "pipe":       T_PIPE,
    "plan":       T_PLAN,
}
for _key, _value in _KS.items():
    _one(rf'(data-ks="{_key}" data-target=")\d+(")',
         lambda m, v=_value: f"{m.group(1)}{v}{m.group(2)}",
         f"knowledge band: {_key}")

_one(r'(<span data-ks-issues>)\d+(</span>)',
     lambda m: f"{m.group(1)}{len(PUBLISHED)}{m.group(2)}",
     "knowledge band: issues published")

# The footer's Newsletter column carries the same "newest" claim, and it had
# drifted with the other two.
_one(r'<a href="[^"]*">Newest — Issue #\d+</a>',
     lambda m: f'<a href="{LATEST_PATH}">Newest — Issue #{LATEST_NUM}</a>',
     "footer newest-issue link")

SRC.write_text(src, encoding='utf-8')
print(f"pillars={N_PILL} categories={N_CATS} topics={T_ALL} "
      f"live={T_LIVE} pipe={T_PIPE} plan={T_PLAN}")
print(f"published={len(PUBLISHED)} newest=#{LATEST_NUM} -> {LATEST_PATH}")
print(f"index.html -> {len(src)} bytes")
