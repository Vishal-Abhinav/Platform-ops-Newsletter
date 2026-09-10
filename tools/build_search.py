#!/usr/bin/env python3
"""Global search: assets/search.js — one index, one box, every page.

Indexes every category, every topic, every published page and every command,
so one box answers "where is X" from anywhere on the site. Inlined rather than
fetched, same reason as the mega-menu: these pages are meant to open off disk.
"""
import html
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from taxonomy import PILLARS          # noqa: E402
from hubs_spec import SPEC            # noqa: E402
from cmd_data import ALL as COMMANDS  # noqa: E402

ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# kind: 0 category · 1 topic · 2 page · 3 command
rows = []
seen_pages = {}

for pname, cats in PILLARS:
    for cname, icon, topics in cats:
        slug = SPEC[cname][0]
        rows.append([0, cname, f"categories/{slug}/index.html", pname, icon])
        for tname, st, href in topics:
            rows.append([1, tname, href or f"categories/{slug}/index.html",
                         cname, {"L": "live", "P": "pipe", "-": "plan"}[st]])
            if st == "L" and href:
                seen_pages.setdefault(href, cname)

# published pages, titled from their own <title>
for href in sorted(seen_pages):
    f = ROOT / href
    if not f.exists():
        continue
    m = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8"), re.S)
    title = html.unescape(re.sub(r"\s+", " ", m.group(1))).split(" · ")[0].strip() if m else href
    rows.append([2, title, href, seen_pages[href], ""])

for spec in COMMANDS:
    page = f"Commands/{spec['slug'].upper()}/{spec['slug']}.html"
    for gid, heading, desc, cmds in spec["groups"]:
        for cmd, what, example in cmds:
            name = html.unescape(re.sub(r"<[^>]+>", "", cmd)).strip()
            rows.append([3, name, page, spec["title"], html.unescape(re.sub(r"<[^>]+>", "", what))[:90]])

INDEX = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))

CSS = """/* Global search — centred in the nav on every page. */
.gs-wrap{position:relative;flex:0 1 380px;min-width:0;margin:0 auto;}
.gs-in{display:flex;align-items:center;gap:8px;background:rgba(128,128,128,.12);
  border:1px solid rgba(128,128,128,.28);border-radius:4px;padding:0 10px;
  transition:border-color .18s,background .18s;}
.gs-in:focus-within{border-color:#e53935;background:rgba(128,128,128,.06);}
.gs-in svg{width:14px;height:14px;flex-shrink:0;stroke:currentColor;fill:none;stroke-width:2;
  opacity:.5;}
.gs-in input{flex:1;min-width:0;background:none;border:0;outline:none;color:inherit;
  font-family:'DM Mono',monospace;font-size:11.5px;letter-spacing:.4px;padding:9px 0;
  -webkit-appearance:none;appearance:none;}
.gs-in input::placeholder{opacity:.45;}
.gs-k{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;opacity:.4;
  border:1px solid currentColor;border-radius:3px;padding:1px 5px;flex-shrink:0;}

.gs-pop{position:fixed;z-index:999;display:none;background:#16181d;
  border:1px solid rgba(255,255,255,.1);box-shadow:0 30px 80px rgba(0,0,0,.5);
  max-height:min(70vh,560px);overflow-y:auto;scrollbar-width:thin;
  scrollbar-color:rgba(255,255,255,.25) transparent;}
.gs-pop.on{display:block;}
.gs-pop::-webkit-scrollbar{width:8px;}
.gs-pop::-webkit-scrollbar-thumb{background:rgba(255,255,255,.22);border-radius:4px;}
.gs-head{padding:10px 16px;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;
  text-transform:uppercase;color:rgba(255,255,255,.35);
  border-bottom:1px solid rgba(255,255,255,.07);position:sticky;top:0;background:#16181d;}
.gs-r{display:flex;align-items:center;gap:11px;padding:9px 16px;text-decoration:none;
  border-left:2px solid transparent;}
.gs-r:hover,.gs-r.sel{background:rgba(255,255,255,.06);border-left-color:#e53935;}
.gs-t{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;
  padding:2px 6px;border-radius:3px;flex-shrink:0;width:66px;text-align:center;}
.gs-t.k0{background:rgba(0,194,212,.18);color:#4dd6e4;}
.gs-t.k1{background:rgba(132,204,22,.16);color:#a7e137;}
.gs-t.k2{background:rgba(229,57,53,.18);color:#f07570;}
.gs-t.k3{background:rgba(245,158,11,.16);color:#f5b544;}
.gs-n{flex:1;min-width:0;}
.gs-n b{display:block;font-size:13px;font-weight:500;color:rgba(255,255,255,.9);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.gs-n span{display:block;font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:.8px;
  text-transform:uppercase;color:rgba(255,255,255,.35);margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.gs-n mark{background:rgba(245,158,11,.35);color:#fff;padding:0 1px;border-radius:2px;}
.gs-none{padding:26px 16px;text-align:center;font-family:'DM Mono',monospace;font-size:10px;
  letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,.35);}
@media(max-width:900px){.gs-wrap{display:none;}}
"""

JS = """var PO_SEARCH = __INDEX__;
/* Global search. Injected into whatever <nav> the page has, like the mega-menu.
   ROOT comes from data-root so the same file works at every depth. */
(function () {
  var me = document.currentScript || document.querySelector('script[src$="search.js"]');
  var ROOT = (me && me.getAttribute('data-root')) || '';
  var KIND = ['Category', 'Topic', 'Page', 'Command'];
  var LIMIT = 40;

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function hi(text, q) {
    var i = text.toLowerCase().indexOf(q);
    if (i < 0 || !q) return esc(text);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) +
           '</mark>' + esc(text.slice(i + q.length));
  }

  function build() {
    var nav = document.querySelector('nav');
    if (!nav || nav.querySelector('.gs-wrap')) return;

    var wrap = document.createElement('div');
    wrap.className = 'gs-wrap';
    wrap.innerHTML =
      '<div class="gs-in">' +
      '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>' +
      '<input type="search" id="gsq" autocomplete="off" spellcheck="false" ' +
      'placeholder="Search topics, commands, pages…" aria-label="Search the site">' +
      '<span class="gs-k">/</span></div>';

    var pop = document.createElement('div');
    pop.className = 'gs-pop';
    document.body.appendChild(pop);

    /* Centre it: after the logo when the nav is a flex row, else appended. */
    var logo = nav.querySelector('.nav-logo');
    var mm = nav.querySelector('.mm-btn');
    if (mm) mm.insertAdjacentElement('afterend', wrap);
    else if (logo && logo.parentNode === nav) logo.insertAdjacentElement('afterend', wrap);
    else nav.appendChild(wrap);

    var input = wrap.querySelector('input'), sel = -1, hits = [];

    function place() {
      var r = wrap.getBoundingClientRect();
      var w = Math.max(r.width, Math.min(520, window.innerWidth - 24));
      pop.style.width = w + 'px';
      pop.style.top = Math.round(r.bottom + 6) + 'px';
      pop.style.left = Math.round(
        Math.max(12, Math.min(r.left, window.innerWidth - w - 12))) + 'px';
    }

    function render(q) {
      if (!q) { pop.classList.remove('on'); return; }
      var starts = [], contains = [];
      for (var i = 0; i < PO_SEARCH.length; i++) {
        var r = PO_SEARCH[i], n = r[1].toLowerCase(), at = n.indexOf(q);
        if (at === 0) starts.push(r);
        else if (at > 0) contains.push(r);
        if (starts.length >= LIMIT) break;
      }
      hits = starts.concat(contains).slice(0, LIMIT);
      if (!hits.length) {
        pop.innerHTML = '<div class="gs-none">Nothing matches “' + esc(q) + '”</div>';
      } else {
        var html = '<div class="gs-head">' + hits.length +
                   (hits.length === LIMIT ? '+' : '') + ' results · ↑↓ to move · ↵ to open</div>';
        hits.forEach(function (r, i) {
          html += '<a class="gs-r' + (i === sel ? ' sel' : '') + '" href="' + ROOT + r[2] + '">' +
                  '<span class="gs-t k' + r[0] + '">' + KIND[r[0]] + '</span>' +
                  '<span class="gs-n"><b>' + hi(r[1], q) + '</b><span>' +
                  esc(r[3]) + (r[4] ? ' · ' + esc(r[4]) : '') + '</span></span></a>';
        });
        pop.innerHTML = html;
      }
      place();
      pop.classList.add('on');
    }

    var t;
    input.addEventListener('input', function () {
      sel = -1;
      clearTimeout(t);
      t = setTimeout(function () { render(input.value.trim().toLowerCase()); }, 90);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { pop.classList.remove('on'); input.blur(); return; }
      if (!hits.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length;
        render(input.value.trim().toLowerCase());
        var el = pop.querySelectorAll('.gs-r')[sel];
        if (el) el.scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && sel >= 0) {
        e.preventDefault();
        window.location.href = ROOT + hits[sel][2];
      }
    });
    input.addEventListener('focus', function () {
      if (input.value.trim()) render(input.value.trim().toLowerCase());
    });
    document.addEventListener('click', function (e) {
      if (!pop.contains(e.target) && !wrap.contains(e.target)) pop.classList.remove('on');
    });
    /* "/" focuses search, the way every docs site does it */
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault(); input.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (pop.classList.contains('on')) place();
    });
    window.addEventListener('scroll', function () {
      if (pop.classList.contains('on')) place();
    }, { passive: true });
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', build);
  else build();
})();
"""

(ASSETS / "search.css").write_text(CSS, encoding="utf-8")
(ASSETS / "search.js").write_text(JS.replace("__INDEX__", INDEX), encoding="utf-8")

added, already = 0, 0
for f in sorted(ROOT.rglob("*.html")):
    if ".git" in f.parts or "tools" in f.parts or f.name == "kit-template.html":
        continue
    rel = str(f.relative_to(ROOT)).replace("\\", "/")
    s = f.read_text(encoding="utf-8")
    if "assets/search.js" in s:
        already += 1
        continue
    up = "../" * (len(pathlib.PurePosixPath(rel).parts) - 1)
    tag = (f'<link rel="stylesheet" href="{up}assets/search.css">\n'
           f'<script defer src="{up}assets/search.js" data-root="{up}"></script>\n')
    f.write_text(s.replace("</head>", tag + "</head>", 1), encoding="utf-8")
    added += 1

kinds = {}
for r in rows:
    kinds[r[0]] = kinds.get(r[0], 0) + 1
print(f"search index: {len(rows)} entries "
      f"({kinds.get(0,0)} categories, {kinds.get(1,0)} topics, "
      f"{kinds.get(2,0)} pages, {kinds.get(3,0)} commands), "
      f"{len(INDEX)//1024} KB")
print(f"search wired into {added} pages ({already} already had it)")
