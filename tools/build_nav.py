#!/usr/bin/env python3
"""Generate the site-wide mega-menu: assets/nav-data.json + megamenu.css + .js

One shared component rather than markup baked into 65 pages. Each page gets two
lines in its head; the script reads data-root for the relative depth and builds
the panel from the JSON, so a new category needs no page edits at all.
"""
import os
import json
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import sys                                    # noqa: E402
sys.path.insert(0, str(TOOLS))
from taxonomy import PILLARS, cat_stats       # noqa: E402
from hubs_spec import SPEC                    # noqa: E402

ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# ── data ─────────────────────────────────────────────────────────────────────
data = {"pillars": [], "quick": [
    {"label": "All Categories", "href": "categories/index.html"},
    {"label": "Reference Library", "href": "index.html#library"},
    {"label": "Knowledge Map", "href": "index.html#topics"},
    {"label": "Latest Issues", "href": "index.html#issues"},
    {"label": "Subscribe", "href": "index.html#subscribe"},
]}
for pname, cats in PILLARS:
    entry = {"name": pname, "cats": []}
    pl = pp = 0
    for cname, icon, topics in cats:
        l, p, n = cat_stats(topics)
        pl += l
        pp += p
        entry["cats"].append({
            "name": cname, "icon": icon,
            "href": f"categories/{SPEC[cname][0]}/index.html",
            "live": l, "pipe": p, "plan": n,
        })
    entry["live"], entry["pipe"] = pl, pp
    data["pillars"].append(entry)

NAV_JSON = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
# Inlined into megamenu.js rather than fetched: the README tells people they can
# open the pages straight off disk, and fetch() is blocked on file:// by CORS.
(ASSETS / "nav-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1),
                                      encoding="utf-8")

# ── styles ───────────────────────────────────────────────────────────────────
CSS = """/* Site-wide mega-menu. Deliberately dark in both themes — it reads as
   chrome rather than page content, the way the terminal blocks do. */
.mm-btn{display:inline-flex;align-items:center;gap:8px;background:none;border:0;cursor:pointer;
  font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.6px;text-transform:uppercase;
  color:inherit;padding:8px 10px;border-radius:3px;transition:background .18s,color .18s;
  flex-shrink:0;}
.mm-btn:hover,.mm-btn[aria-expanded="true"]{background:rgba(229,57,53,.12);color:#e53935;}
.mm-btn i{display:block;width:14px;height:10px;position:relative;flex-shrink:0;}
.mm-btn i::before,.mm-btn i::after,.mm-btn i span{content:'';position:absolute;left:0;right:0;
  height:1.5px;background:currentColor;transition:transform .25s,opacity .2s;}
.mm-btn i::before{top:0;} .mm-btn i span{top:4.2px;} .mm-btn i::after{bottom:0;}
.mm-btn[aria-expanded="true"] i::before{transform:translateY(4.2px) rotate(45deg);}
.mm-btn[aria-expanded="true"] i span{opacity:0;}
.mm-btn[aria-expanded="true"] i::after{transform:translateY(-4.2px) rotate(-45deg);}

.mm-scrim{position:fixed;inset:0;z-index:998;background:rgba(8,9,12,.45);opacity:0;
  pointer-events:none;transition:opacity .22s;}
.mm-scrim.on{opacity:1;pointer-events:auto;}

.mm{position:fixed;z-index:999;top:0;left:0;display:none;grid-template-columns:262px 1fr;
  background:#16181d;box-shadow:0 32px 90px rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.09);
  max-height:min(78vh,660px);overflow:hidden;}
.mm.on{display:grid;}
.mm-l{background:#111318;border-right:1px solid rgba(255,255,255,.07);overflow-y:auto;
  padding:10px 0;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.25) transparent;}
.mm-r{overflow-y:auto;padding:14px 0;scrollbar-width:thin;
  scrollbar-color:rgba(255,255,255,.25) transparent;}
.mm-l::-webkit-scrollbar,.mm-r::-webkit-scrollbar{width:8px;}
.mm-l::-webkit-scrollbar-thumb,.mm-r::-webkit-scrollbar-thumb{
  background:rgba(255,255,255,.22);border-radius:4px;}

.mm-p{display:flex;align-items:center;gap:10px;width:100%;padding:10px 16px;background:none;
  border:0;cursor:pointer;text-align:left;color:rgba(255,255,255,.72);
  font-family:'Manrope',system-ui,sans-serif;font-size:13.5px;font-weight:500;
  transition:background .15s,color .15s;}
.mm-p:hover{background:rgba(255,255,255,.05);color:#fff;}
.mm-p[aria-selected="true"]{background:#16181d;color:#fff;box-shadow:inset 3px 0 0 #e53935;}
.mm-p .n{font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,.3);flex-shrink:0;}
.mm-p .t{flex:1;min-width:0;}
.mm-p .c{font-family:'DM Mono',monospace;font-size:8.5px;color:#84cc16;flex-shrink:0;}
.mm-p .a{color:rgba(255,255,255,.3);font-size:12px;flex-shrink:0;}

.mm-head{padding:0 22px 10px;margin:0 0 6px;border-bottom:1px solid rgba(255,255,255,.07);
  font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2.2px;text-transform:uppercase;
  color:rgba(255,255,255,.35);}
.mm-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:1px 0;
  padding:0 12px;}
.mm-c{display:flex;align-items:flex-start;gap:10px;padding:9px 10px;text-decoration:none;
  border-radius:3px;transition:background .15s;}
.mm-c:hover{background:rgba(255,255,255,.06);}
.mm-c .ico{font-size:13px;line-height:1.35;flex-shrink:0;}
.mm-c .nm{display:block;font-size:13px;color:rgba(255,255,255,.85);line-height:1.35;}
.mm-c:hover .nm{color:#fff;}
.mm-c .sub{display:block;font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:1px;
  text-transform:uppercase;color:rgba(255,255,255,.32);margin-top:3px;}
.mm-c .sub b{color:#84cc16;font-weight:400;}

.mm-foot{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:2px;padding:12px 16px;
  background:#111318;border-top:1px solid rgba(255,255,255,.07);}
.mm-foot a{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.4px;
  text-transform:uppercase;color:rgba(255,255,255,.55);text-decoration:none;padding:7px 12px;
  border-radius:3px;transition:background .15s,color .15s;}
.mm-foot a:hover{background:rgba(229,57,53,.16);color:#fff;}

@media(max-width:820px){
  .mm{grid-template-columns:1fr;left:0!important;right:0;width:auto!important;
    max-height:calc(100vh - 56px);}
  .mm-l{display:flex;gap:2px;overflow-x:auto;overflow-y:hidden;padding:8px;
    border-right:0;border-bottom:1px solid rgba(255,255,255,.07);}
  .mm-p{width:auto;white-space:nowrap;padding:8px 12px;font-size:12px;}
  .mm-p .n,.mm-p .a,.mm-p .c{display:none;}
  .mm-p[aria-selected="true"]{box-shadow:inset 0 -2px 0 #e53935;}
  .mm-grid{grid-template-columns:1fr;}
}
"""
(ASSETS / "megamenu.css").write_text(CSS, encoding="utf-8")

# ── behaviour ────────────────────────────────────────────────────────────────
JS = """var PO_NAV = __NAV_JSON__;
/* Site-wide mega-menu. Injected into whatever <nav> the page already has,
   so no page needs its own markup. Depth comes from data-root on this tag. */
(function () {
  var me = document.currentScript ||
           document.querySelector('script[src$="megamenu.js"]');
  var ROOT = (me && me.getAttribute('data-root')) || '';

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  try { build(PO_NAV); } catch (e) { /* nav is an enhancement, not load-bearing */ }

  function build(data) {
    var nav = document.querySelector('nav');
    if (!nav) return;

    var btn = el('button', 'mm-btn');
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-haspopup', 'true');
    btn.innerHTML = '<i><span></span></i>Browse';

    var scrim = el('div', 'mm-scrim');
    var panel = el('div', 'mm');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Browse all categories');

    var left = el('div', 'mm-l');
    var right = el('div', 'mm-r');
    var foot = el('div', 'mm-foot');

    data.pillars.forEach(function (p, i) {
      var b = el('button', 'mm-p');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      b.innerHTML = '<span class="n">' + String(i + 1).padStart(2, '0') + '</span>' +
                    '<span class="t">' + p.name + '</span>' +
                    (p.live ? '<span class="c">' + p.live + '</span>' : '') +
                    '<span class="a">›</span>';
      var show = function () {
        left.querySelectorAll('.mm-p').forEach(function (x) {
          x.setAttribute('aria-selected', 'false');
        });
        b.setAttribute('aria-selected', 'true');
        paint(p);
      };
      b.addEventListener('mouseenter', show);
      b.addEventListener('focus', show);
      b.addEventListener('click', show);
      left.appendChild(b);
    });

    function paint(p) {
      right.innerHTML = '';
      right.appendChild(el('div', 'mm-head',
        p.name + ' — ' + p.cats.length + ' categor' + (p.cats.length === 1 ? 'y' : 'ies') +
        ' · ' + p.live + ' live · ' + p.pipe + ' in pipeline'));
      var grid = el('div', 'mm-grid');
      p.cats.forEach(function (c) {
        var a = el('a', 'mm-c');
        a.href = ROOT + c.href;
        a.innerHTML = '<span class="ico">' + c.icon + '</span><span>' +
          '<span class="nm">' + c.name + '</span>' +
          '<span class="sub">' + (c.live ? '<b>' + c.live + ' live</b> · ' : '') +
          c.pipe + ' pipe · ' + c.plan + ' planned</span></span>';
        grid.appendChild(a);
      });
      right.appendChild(grid);
    }
    paint(data.pillars[0]);

    data.quick.forEach(function (q) {
      var a = el('a', null, q.label);
      a.href = ROOT + q.href;
      foot.appendChild(a);
    });

    panel.appendChild(left);
    panel.appendChild(right);
    panel.appendChild(foot);
    document.body.appendChild(scrim);
    document.body.appendChild(panel);

    /* Anchor under the nav, clamped to the viewport. Fixed positioning, so it
       is measured from the button rather than nested inside a nav that may be
       backdrop-filtered — a filter creates a containing block and would trap
       an absolutely positioned panel inside it. */
    function place() {
      var r = btn.getBoundingClientRect();
      var w = Math.min(900, window.innerWidth - 24);
      panel.style.width = w + 'px';
      panel.style.top = Math.round(r.bottom + 8) + 'px';
      panel.style.left = Math.round(
        Math.max(12, Math.min(r.left, window.innerWidth - w - 12))) + 'px';
    }

    function open(on) {
      btn.setAttribute('aria-expanded', on ? 'true' : 'false');
      panel.classList.toggle('on', on);
      scrim.classList.toggle('on', on);
      if (on) place();
    }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      open(btn.getAttribute('aria-expanded') !== 'true');
    });
    scrim.addEventListener('click', function () { open(false); });
    panel.addEventListener('click', function (e) { e.stopPropagation(); });
    document.addEventListener('click', function () { open(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { open(false); btn.focus(); }
    });
    window.addEventListener('resize', function () {
      if (panel.classList.contains('on')) place();
    });
    window.addEventListener('scroll', function () {
      if (panel.classList.contains('on')) place();
    }, { passive: true });

    /* Next to the logo where there's room, else at the end of the nav.
       search.js may later move both into a .nav-side group; insert relative to
       the logo rather than to the nav so the order survives either way. */
    var logo = nav.querySelector('.nav-logo');
    if (logo) logo.insertAdjacentElement('afterend', btn);
    else nav.appendChild(btn);
  }
})();
"""
(ASSETS / "megamenu.js").write_text(JS.replace("__NAV_JSON__", NAV_JSON),
                                    encoding="utf-8")


# ── inject the two lines into every published page ───────────────────────────
def depth_prefix(rel):
    return "../" * (len(pathlib.PurePosixPath(rel).parts) - 1)


added, already = 0, 0
for f in sorted(ROOT.rglob("*.html")):
    if ".git" in f.parts or "tools" in f.parts or f.name == "kit-template.html":
        continue
    rel = str(f.relative_to(ROOT)).replace("\\", "/")
    s = f.read_text(encoding="utf-8")
    if "megamenu.js" in s:
        already += 1
        continue
    up = depth_prefix(rel)
    tag = (f'<link rel="stylesheet" href="{up}assets/megamenu.css">\n'
           f'<script defer src="{up}assets/megamenu.js" data-root="{up}"></script>\n')
    s = s.replace("</head>", tag + "</head>", 1)
    f.write_text(s, encoding="utf-8")
    added += 1

n_cats = sum(len(p["cats"]) for p in data["pillars"])
print(f"nav-data.json: {len(data['pillars'])} pillars, {n_cats} categories")
print(f"megamenu wired into {added} pages ({already} already had it)")
