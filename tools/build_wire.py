#!/usr/bin/env python3
"""Third build stage: wire the category hubs into index.html, and add the
licence line the dual MIT / CC BY-NC-ND split needs."""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import pathlib
import sys

sys.path.insert(0, str(TOOLS))
from hubs_spec import SPEC   # noqa: E402
from taxonomy import PILLARS  # noqa: E402

N_CATS = sum(len(c) for _, c in PILLARS)

SRC = ROOT / 'index.html'
src = SRC.read_text(encoding='utf-8')

# ── nav: a Categories entry ──────────────────────────────────────────────────
src = src.replace('    <li><a href="#topics">Topics</a></li>\n',
                  '    <li><a href="#topics">Topics</a></li>\n'
                  '    <li><a href="categories/index.html">Categories</a></li>\n', 1)

# ── knowledge map: link every category row to its hub ────────────────────────
n = 0
for cname, (slug, _tag, _layers) in SPEC.items():
    esc = cname.replace('&', '&amp;')
    needle = f'<span class="km-c-name">{esc}</span>'
    if needle not in src:
        print('  !! category not found in index.html:', cname)
        continue
    # the hub link is the first row inside the category's expanded topic area
    body_at = src.index('<div class="km-topics">', src.index(needle))
    ins = body_at + len('<div class="km-topics">')
    link = (f'\n          <a class="km-hublink" href="categories/{slug}/index.html">'
            f'Open the {esc} hub — architecture, issues, full topic list →</a>')
    src = src[:ins] + link + src[ins:]
    n += 1
print(f'hub links added to {n} categories')

# ── the "all categories" entry above the pillar list ─────────────────────────
src = src.replace('    <div class="km-pillars" id="kmPillars">',
                  '    <a class="km-allcats" href="categories/index.html">'
                  '<b>Every category has its own page</b> — architecture diagram, the issues that '
                  f'cover it, and the full topic list. Browse all {N_CATS} →</a>\n'
                  '    <div class="km-pillars" id="kmPillars">', 1)

# ── styles for both ──────────────────────────────────────────────────────────
CSS = """
.km-hublink{display:block;width:100%;margin:0 0 4px;padding:9px 12px;border-radius:4px;
  background:var(--wash-2);border:1px solid var(--hairline-3);text-decoration:none;
  font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.1px;text-transform:uppercase;
  color:var(--muted);transition:background .2s,color .2s,border-color .2s;}
.km-hublink:hover{background:var(--crimson);border-color:var(--crimson);color:#fff;}
.km-allcats{display:block;margin-bottom:14px;padding:15px 18px;text-decoration:none;
  background:var(--panel-bg);border-left:3px solid var(--crimson);
  font-family:'DM Mono',monospace;font-size:10.5px;letter-spacing:1.1px;line-height:1.7;
  text-transform:uppercase;color:var(--muted);transition:background .2s;}
.km-allcats:hover{background:var(--wash-2);color:var(--heading-fg);}
.km-allcats b{color:var(--heading-fg);font-weight:400;}
"""
src = src.replace('/* ─── TOOLCHAIN DIAGRAM ─── */', CSS.strip() + '\n\n/* ─── TOOLCHAIN DIAGRAM ─── */', 1)

# ── footer: categories + the licence split ───────────────────────────────────
src = src.replace('          <a href="#topics">Knowledge Map</a>',
                  '          <a href="categories/index.html">All Categories</a>\n'
                  '          <a href="#topics">Knowledge Map</a>', 1)
src = src.replace(
    '<div class="footer-note">© 2026 Tech with Vishal Abhinav · Platform Ops Engineer</div>',
    '<div class="footer-note">© 2026 Vishal Abhinav · Platform Ops Engineer — code MIT, '
    '<a href="LICENSE" style="color:inherit">text &amp; diagrams CC BY-NC-ND 4.0</a></div>', 1)
src = src.replace('<meta name="author" content="Vishal Abhinav">',
                  '<meta name="author" content="Vishal Abhinav">\n'
                  '<meta name="copyright" content="© 2026 Vishal Abhinav. '
                  'Text and diagrams CC BY-NC-ND 4.0.">', 1)

old_sync = """  const topicsH = topics.getBoundingClientRect().height;
  const innerH = issuesInner.getBoundingClientRect().height;
  const wrapH = scrollWrap.getBoundingClientRect().height;
  const target = Math.max(320, Math.round(topicsH - (innerH - wrapH)));
  scrollBox.style.maxHeight = target + 'px';"""
new_sync = """  // Measure the non-scrolling chrome from the gaps around the wrap, not from
  // the inner's own height — the latter already reflects whatever maxHeight we
  // set last time, so it feeds back and collapses the panel to its floor.
  const innerRect = issuesInner.getBoundingClientRect();
  const wrapRect  = scrollWrap.getBoundingClientRect();
  const chrome    = (wrapRect.top - innerRect.top)
                  + (innerRect.bottom - wrapRect.bottom);
  const byColumn  = topics.getBoundingClientRect().height - chrome;
  // Never taller than the screen. The topics column is ~2300px now, and a panel
  // matched to it put its own scrollbar mostly off-screen — the scroll still
  // worked, you just couldn't reach the bar, which reads as it being disabled.
  const byScreen  = window.innerHeight - 120;
  scrollBox.style.maxHeight =
    Math.max(360, Math.round(Math.min(byColumn, byScreen))) + 'px';"""
assert old_sync in src, "scroll-sync block not found"
src = src.replace(old_sync, new_sync, 1)

SRC.write_text(src, encoding='utf-8')
print(f'index.html -> {len(src)} chars')
for probe in ('km-hublink', 'km-allcats', 'categories/index.html', 'CC BY-NC-ND'):
    print(f'  {probe:24} x{src.count(probe)}')
