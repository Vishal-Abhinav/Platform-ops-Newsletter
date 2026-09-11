#!/usr/bin/env python3
"""Template + diagram engine for deep-dive topic pages.

Same design language as the rest of the site, same section rhythm as the
existing issues: one architecture diagram, a CORE reference, an ADVANCED
reference, worked terminal examples, a decision table, a cheatsheet.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import html

from siteconf import BASE           # canonical origin, one source of truth

ACCENT = {  # diagram node roles
    "core":  ("rgba(0,194,212,.14)",  "#00c2d4",              "#066c77"),
    "warm":  ("rgba(245,158,11,.14)", "rgba(245,158,11,.6)",  "#8a5806"),
    "hot":   ("rgba(229,57,53,.13)",  "rgba(229,57,53,.55)",  "#a32b28"),
    "go":    ("rgba(132,204,22,.16)", "#84cc16",              "#3f6f0c"),
    "calm":  ("rgba(124,58,237,.12)", "rgba(124,58,237,.45)", "#5b21b6"),
    "plain": ("transparent",          "rgba(0,0,0,.2)",       "#6b6860"),
}
DARK_TEXT = {"core": "#4dd6e4", "warm": "#f5b544", "hot": "#f07570",
             "go": "#a7e137", "calm": "#b596f5", "plain": "#8a877f"}


def esc(s):
    return html.escape(str(s), quote=True)


# ── layered diagram ──────────────────────────────────────────────────────────
W, LABEL_W, PAD_R = 1000, 168, 20
NODE_H, GAP_X, GAP_Y, LAYER_GAP = 46, 10, 10, 28
AREA = W - LABEL_W - PAD_R
CHAR = 6.35


def _wrap(text, width_px, max_lines=2):
    limit = max(6, int((width_px - 14) / CHAR))
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if len(t) <= limit:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if not lines:
        lines = [text[:limit]]
    if len(lines) == max_lines and sum(len(x) for x in lines) + len(lines) - 1 < len(text):
        lines[-1] = lines[-1][:max(3, limit - 1)] + "…"
    return lines


def diagram(layers, label=""):
    """layers: [(layer_label, [(node_text, role), ...]), ...]"""
    parts, y = [], 14
    for lab, nodes in layers:
        per_row = len(nodes)
        while per_row > 1 and (AREA - GAP_X * (per_row - 1)) / per_row < 104:
            per_row -= 1
        rows = [nodes[i:i + per_row] for i in range(0, len(nodes), per_row)]
        rows_h = len(rows) * NODE_H + (len(rows) - 1) * GAP_Y
        mid = y + rows_h / 2
        parts.append(f'<text class="dg-layer" x="{LABEL_W - 22}" y="{mid + 4:.1f}">{esc(lab.upper())}</text>')
        parts.append(f'<circle class="dg-tick" cx="{LABEL_W - 8}" cy="{mid:.1f}" r="3"/>')
        for ri, row in enumerate(rows):
            n = len(row)
            w = (AREA - GAP_X * (n - 1)) / n
            ry = y + ri * (NODE_H + GAP_Y)
            for i, (text, role) in enumerate(row):
                fill, line, fg = ACCENT.get(role, ACCENT["plain"])
                x = LABEL_W + i * (w + GAP_X)
                ls = _wrap(text, w)
                ty = ry + NODE_H / 2 + (4 if len(ls) == 1 else -2)
                dash = ' stroke-dasharray="3 3"' if role == "plain" else ''
                parts.append(f'<rect x="{x:.1f}" y="{ry}" width="{w:.1f}" height="{NODE_H}" rx="4" '
                             f'fill="{fill}" stroke="{line}"{dash} stroke-width="1"/>')
                for li, ln in enumerate(ls):
                    parts.append(f'<text class="dg-node n-{role}" x="{x + w / 2:.1f}" '
                                 f'y="{ty + li * 12:.1f}" fill="{fg}">{esc(ln)}</text>')
        y += rows_h + LAYER_GAP
    h = y - LAYER_GAP + 14
    return (f'<svg class="dg" viewBox="0 0 {W} {h:.0f}" role="img" aria-label="{esc(label)}">'
            f'<line class="dg-spine" x1="{LABEL_W - 8}" y1="14" x2="{LABEL_W - 8}" y2="{h - 14:.1f}"/>'
            + "".join(parts) + '</svg>')


# ── blocks ───────────────────────────────────────────────────────────────────
def card(n, name, desc, tags, body):
    """Expandable reference card — the ec-* pattern used across the site."""
    tag_html = "".join(f'<span class="tg">{esc(t)}</span>' for t in tags)
    return f"""<div class="rc" data-rc>
  <button class="rc-head" type="button" aria-expanded="false">
    <span class="rc-n">{n:02d}</span>
    <span class="rc-main"><span class="rc-name">{esc(name)}</span>
      <span class="rc-desc">{desc}</span>
      <span class="rc-tags">{tag_html}</span></span>
    <span class="rc-chev" aria-hidden="true">⌄</span>
  </button>
  <div class="rc-body"><div class="rc-inner">{body}</div></div>
</div>"""


def term(title, lines):
    """Terminal block. lines: [('$'|'#'|'>'|'', text)] — '#' is a comment."""
    out = ""
    for kind, text in lines:
        if kind == '#':
            out += f'<div class="tl"><span class="tc">{esc(text)}</span></div>'
        elif kind == '':
            out += f'<div class="tl"><span class="to">{esc(text)}</span></div>'
        else:
            out += (f'<div class="tl"><span class="tp">{esc(kind)}</span> '
                    f'<span class="tx">{esc(text)}</span></div>')
    return (f'<div class="tb"><div class="tb-bar"><i class="d r"></i><i class="d y"></i>'
            f'<i class="d g"></i><span class="tb-t">{esc(title)}</span></div>'
            f'<div class="tb-body">{out}</div></div>')


def table(headers, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in headers)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="tw"><table class="tbl {cls}"><thead><tr>{h}</tr></thead>'
            f'<tbody>{b}</tbody></table></div>')


def note(kind, title, body):
    return f'<div class="note {kind}"><b>{esc(title)}</b>{body}</div>'


# ── stylesheet (one file, shared by every topic page) ────────────────────────
CSS = """
:root{--ink:#08090c;--paper:#f2f0eb;--smoke:#e4e0d8;--ash:#b8b2a7;--coal:#1c1f26;
 --cyan:#00c2d4;--amber:#f59e0b;--crimson:#e53935;--lime:#84cc16;--purple:#7c3aed;
 --page-bg:#f2f0eb;--panel-bg:#e4e0d8;--card-bg:#f8f7f4;--page-fg:#1c1f26;--heading-fg:#1c1f26;
 --muted:#6b6860;--line-1:rgba(0,0,0,.06);--line-2:rgba(0,0,0,.1);--line-3:rgba(0,0,0,.16);
 --wash:rgba(0,0,0,.04);--nav-bg:rgba(242,240,235,.9);--code-bg:#0d0f14;}
html[data-theme="dark"]{--page-bg:#0c0e12;--panel-bg:#14161c;--card-bg:#181b22;--page-fg:#e7e5df;
 --heading-fg:#eeece6;--muted:#9a978e;--line-1:rgba(255,255,255,.07);--line-2:rgba(255,255,255,.11);
 --line-3:rgba(255,255,255,.18);--wash:rgba(255,255,255,.05);--nav-bg:rgba(12,14,18,.9);}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--page-bg);color:var(--page-fg);font-family:'Manrope',system-ui,sans-serif;
 -webkit-font-smoothing:antialiased;line-height:1.65;}
a{color:inherit;}
.wrap{max-width:1000px;margin:0 auto;padding:0 40px;}
@media(max-width:700px){.wrap{padding:0 20px;}}

nav{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:18px;padding:14px 40px;
 background:var(--nav-bg);backdrop-filter:blur(14px);border-bottom:1px solid var(--line-1);}
.nav-logo{display:flex;align-items:center;gap:9px;font-family:'Bebas Neue',sans-serif;font-size:19px;
 letter-spacing:2.5px;text-decoration:none;color:var(--heading-fg);flex-shrink:0;}
.nav-logo span{width:8px;height:8px;border-radius:50%;background:var(--crimson);}
.crumb{flex:1;min-width:0;display:flex;align-items:center;gap:8px;flex-wrap:wrap;
 font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
.crumb a{text-decoration:none;color:var(--muted);}
.crumb a:hover{color:var(--crimson);}
.crumb .cur{color:var(--heading-fg);}
.nav-right{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.tt{width:32px;height:32px;border:1px solid var(--line-2);background:transparent;border-radius:50%;
 cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);}
.tt:hover{color:var(--crimson);border-color:var(--crimson);}
.tt svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;}
html:not([data-theme="dark"]) .tt .moon,html[data-theme="dark"] .tt .sun{display:none;}
@media(max-width:760px){nav{padding:12px 18px;gap:12px;}.crumb{display:none;}}

header.hero{padding:60px 0 40px;border-bottom:1px solid var(--line-1);}
.eyebrow{display:inline-flex;align-items:center;gap:10px;font-family:'DM Mono',monospace;font-size:10.5px;
 letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;}
.eyebrow::before{content:'';width:22px;height:1px;background:var(--crimson);}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(42px,7vw,74px);line-height:.95;letter-spacing:-.5px;
 color:var(--heading-fg);}
.sub{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:20px;color:var(--muted);
 max-width:700px;margin-top:14px;}
.meta{display:flex;flex-wrap:wrap;gap:18px;margin-top:26px;font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);}
.meta b{color:var(--heading-fg);font-weight:400;}

section{padding:52px 0;border-bottom:1px solid var(--line-1);}
.sec-tag{display:inline-flex;align-items:center;gap:9px;font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:2.6px;text-transform:uppercase;color:var(--crimson);margin-bottom:12px;}
.sec-tag::before{content:'';width:16px;height:1px;background:var(--crimson);}
h2{font-family:'Bebas Neue',sans-serif;font-size:34px;letter-spacing:1px;color:var(--heading-fg);margin-bottom:10px;}
h3{font-family:'Manrope',sans-serif;font-size:14.5px;font-weight:700;color:var(--heading-fg);
 margin:22px 0 8px;letter-spacing:.1px;}
.lede{font-size:15px;color:var(--muted);max-width:720px;margin-bottom:26px;}
p{font-size:14.5px;margin-bottom:12px;}
p.tight{margin-bottom:8px;}
ul,ol{margin:10px 0 14px 20px;}
li{font-size:14px;margin-bottom:7px;}
code{font-family:'DM Mono',monospace;font-size:.88em;background:var(--wash);padding:2px 5px;
 border-radius:3px;border:1px solid var(--line-1);}
strong{font-weight:700;color:var(--heading-fg);}

.dg-scroll{overflow-x:auto;padding-bottom:6px;}
.dg{width:100%;min-width:660px;height:auto;display:block;}
.dg-layer{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.6px;fill:var(--muted);text-anchor:end;}
.dg-node{font-family:'DM Mono',monospace;font-size:10.5px;text-anchor:middle;}
.dg-spine,.dg-tick{stroke:var(--line-3);fill:var(--line-3);stroke-width:1;}
html[data-theme="dark"] .dg-node.n-core{fill:#4dd6e4!important;}
html[data-theme="dark"] .dg-node.n-warm{fill:#f5b544!important;}
html[data-theme="dark"] .dg-node.n-hot{fill:#f07570!important;}
html[data-theme="dark"] .dg-node.n-go{fill:#a7e137!important;}
html[data-theme="dark"] .dg-node.n-calm{fill:#b596f5!important;}
html[data-theme="dark"] .dg-node.n-plain{fill:#8a877f!important;}
.dg-cap{font-size:13px;color:var(--muted);margin-top:16px;max-width:760px;font-style:italic;
 font-family:'Instrument Serif',Georgia,serif;}

.rc{background:var(--card-bg);border:1px solid var(--line-1);margin-bottom:2px;position:relative;}
.rc::before{content:'';position:absolute;top:0;left:0;width:2px;height:100%;background:transparent;
 transition:background .25s;}
.rc.open::before{background:var(--crimson);}
.rc-head{display:flex;align-items:flex-start;gap:14px;width:100%;padding:16px 18px;background:none;
 border:0;cursor:pointer;text-align:left;font:inherit;color:inherit;transition:background .2s;}
.rc-head:hover{background:var(--wash);}
.rc-n{font-family:'DM Mono',monospace;font-size:10px;color:var(--ash);flex-shrink:0;padding-top:3px;}
.rc-main{flex:1;min-width:0;}
.rc-name{display:block;font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:.6px;
 line-height:1.1;color:var(--heading-fg);}
.rc-desc{display:block;font-size:13px;color:var(--muted);margin-top:5px;line-height:1.55;}
.rc-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px;}
.tg{font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:1.1px;text-transform:uppercase;
 padding:3px 8px;border-radius:20px;background:var(--wash);border:1px solid var(--line-2);color:var(--muted);}
.rc-chev{font-family:'DM Mono',monospace;font-size:13px;color:var(--ash);flex-shrink:0;
 transition:transform .3s;padding-top:3px;}
.rc.open .rc-chev{transform:rotate(-180deg);color:var(--crimson);}
.rc-body{display:grid;grid-template-rows:0fr;transition:grid-template-rows .4s cubic-bezier(.25,.46,.45,.94);}
.rc.open .rc-body{grid-template-rows:1fr;}
.rc-inner{overflow:hidden;min-height:0;}
.rc-inner > div:last-child,.rc-inner > p:last-child{margin-bottom:0;}
.rc-inner{padding:0 18px 0 46px;}
.rc.open .rc-inner{padding-bottom:22px;}
@media(max-width:700px){.rc-inner{padding-left:18px;}}

.tb{background:var(--code-bg);border-radius:6px;overflow:hidden;margin:14px 0;
 border:1px solid rgba(255,255,255,.08);}
.tb-bar{display:flex;align-items:center;gap:6px;padding:9px 13px;background:rgba(255,255,255,.04);
 border-bottom:1px solid rgba(255,255,255,.07);}
.tb-bar .d{width:8px;height:8px;border-radius:50%;display:block;}
.tb-bar .d.r{background:#ff5f57;}.tb-bar .d.y{background:#febc2e;}.tb-bar .d.g{background:#28c840;}
.tb-t{margin-left:9px;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.4px;
 text-transform:uppercase;color:rgba(255,255,255,.35);}
.tb-body{padding:15px 16px;font-family:'DM Mono',monospace;font-size:12px;line-height:1.85;
 overflow-x:auto;}
.tl{white-space:pre;}
.tp{color:var(--cyan);}
/* .tx, not .tt — .tt is the theme-toggle button defined above (32px circle,
   display:flex, border-radius:50%). Sharing the class name laid every command
   line out inside that box and clipped it on both sides. */
.tx{color:#e8e6e1;}
.tc{color:rgba(255,255,255,.32);}
.to{color:rgba(255,255,255,.6);}

.tw{overflow-x:auto;margin:16px 0;}
.tbl{width:100%;border-collapse:collapse;font-size:13px;min-width:520px;}
.tbl th{text-align:left;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.6px;
 text-transform:uppercase;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line-3);
 white-space:nowrap;}
.tbl td{padding:11px 12px;border-bottom:1px solid var(--line-1);vertical-align:top;}
.tbl tr:hover td{background:var(--wash);}
.tbl code{white-space:nowrap;}
.tbl.mono td:first-child{font-family:'DM Mono',monospace;font-size:11.5px;white-space:nowrap;
 color:var(--heading-fg);}

.note{padding:14px 16px;border-left:3px solid;background:var(--wash);margin:16px 0;font-size:13.5px;}
.note b{display:block;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.8px;
 text-transform:uppercase;margin-bottom:7px;}
.note.tip{border-color:var(--lime);}.note.tip b{color:#4c840f;}
.note.warn{border-color:var(--amber);}.note.warn b{color:#8a5806;}
.note.trap{border-color:var(--crimson);}.note.trap b{color:var(--crimson);}
html[data-theme="dark"] .note.tip b{color:var(--lime);}
html[data-theme="dark"] .note.warn b{color:var(--amber);}

.pager{display:flex;gap:2px;margin-top:26px;}
.pager a{flex:1;background:var(--card-bg);border:1px solid var(--line-1);padding:16px 18px;
 text-decoration:none;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;
 text-transform:uppercase;color:var(--muted);transition:background .2s,color .2s;}
.pager a:hover{background:var(--panel-bg);color:var(--crimson);}
.pager a.next{text-align:right;}
.pager a b{display:block;font-family:'Bebas Neue',sans-serif;font-size:19px;letter-spacing:.5px;
 color:var(--heading-fg);font-weight:400;margin-top:5px;}

footer{background:var(--coal);color:var(--paper);padding:52px 40px 26px;}
.f-in{max-width:1000px;margin:0 auto;}
.f-top{display:grid;grid-template-columns:1.3fr 2fr;gap:48px;}
.f-logo{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:3px;color:#fff;text-decoration:none;}
.f-tag{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:14px;
 color:rgba(255,255,255,.5);margin-top:12px;line-height:1.6;}
.f-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;}
.f-col-t{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:2.2px;text-transform:uppercase;
 color:rgba(255,255,255,.35);margin-bottom:12px;}
.f-cols a{display:block;font-size:12.5px;color:rgba(255,255,255,.72);text-decoration:none;padding:4px 0;}
.f-cols a:hover{color:var(--cyan);}
.f-bot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-top:38px;padding-top:18px;
 border-top:1px solid rgba(255,255,255,.1);font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:1.2px;color:rgba(255,255,255,.35);}
.f-bot a{color:rgba(255,255,255,.5);}
@media(max-width:820px){.f-top{grid-template-columns:1fr;gap:30px;}footer{padding:44px 20px 22px;}}
@media(max-width:560px){.f-cols{grid-template-columns:1fr 1fr;}}
"""

GC = """<!-- Privacy-friendly analytics (GoatCounter). Put your site code between the
     quotes on the PO_GC line below; left empty, nothing loads and nothing is
     sent. The README has a one-liner that sets it across every page at once. -->
<script>
(function(){var PO_GC='';
 if(!PO_GC) return;
 var s=document.createElement('script');
 s.async=true; s.src='https://gc.zgo.at/count.js';
 s.setAttribute('data-goatcounter','https://'+PO_GC+'.goatcounter.com/count');
 document.head.appendChild(s);})();
</script>"""

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&'
         'family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&'
         'family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">')

TOGGLE = ('<button class="tt" id="tt" type="button" aria-label="Toggle dark mode">'
          '<svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/>'
          '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2'
          'M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
          '<svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/>'
          '</svg></button>')

JS = """<script>
document.getElementById('tt').addEventListener('click',function(){
  var d=document.documentElement.getAttribute('data-theme')==='dark';
  if(d){document.documentElement.removeAttribute('data-theme');}
  else{document.documentElement.setAttribute('data-theme','dark');}
  try{localStorage.setItem('po-theme',d?'light':'dark');}catch(e){}
});
document.addEventListener('click',function(e){
  var h=e.target.closest('.rc-head'); if(!h) return;
  var c=h.parentElement, open=c.classList.contains('open');
  c.classList.toggle('open',!open);
  h.setAttribute('aria-expanded', !open?'true':'false');
});
</script>"""


def render(*, slug, title, tagline, eyebrow, crumbs, meta, sections, pager, up="../../",
           css=None):
    # The stylesheet used to be hardcoded to Foundation's copy. That still RESOLVED
    # from other sections — so verify.py passed — but it meant every deep-dive
    # outside Foundation silently depended on Foundation existing, and its own
    # topic.css was written and never loaded. Pass the path that belongs to the
    # section; Foundation stays the default so nothing there changes.
    css = css or f"{up}Foundation/topic.css"
    crumb = ""
    for i, (label, href) in enumerate(crumbs):
        if i:
            crumb += '<span>/</span>'
        crumb += (f'<a href="{esc(href)}">{esc(label)}</a>' if href
                  else f'<span class="cur">{esc(label)}</span>')
    meta_html = " ".join(f'<span>{m}</span>' for m in meta)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} · Platform Ops · Vishal Abhinav</title>
<meta name="description" content="{esc(tagline)}">
<meta name="author" content="Vishal Abhinav">
<meta name="copyright" content="© 2026 Vishal Abhinav. Text and diagrams CC BY-NC-ND 4.0.">
<link rel="canonical" href="{BASE}Foundation/{slug.upper()}/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Platform Ops · Tech with Vishal Abhinav">
<meta property="og:title" content="{esc(title)} · Platform Ops">
<meta property="og:description" content="{esc(tagline)}">
<meta property="og:url" content="{BASE}Foundation/{slug.upper()}/{slug}.html">
<meta property="og:image" content="{BASE}assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)} · Platform Ops">
<meta name="twitter:description" content="{esc(tagline)}">
<meta name="twitter:image" content="{BASE}assets/og/home.png">
{FONTS}
<link rel="alternate" type="application/rss+xml" title="Platform Ops — new issues" href="{up}feed.xml">
<script>
(function(){{try{{var t=localStorage.getItem('po-theme');
 if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}}catch(e){{}}}})();
</script>
{GC}
<link rel="stylesheet" href="{css}">
</head>
<body>
<nav>
  <a href="{up}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>
  <div class="crumb">{crumb}</div>
  <div class="nav-right">{TOGGLE}<a href="{up}index.html#subscribe" class="nav-logo"
    style="font-size:11px;letter-spacing:1.6px;font-family:'DM Mono',monospace">SUBSCRIBE</a></div>
</nav>

<header class="hero"><div class="wrap">
  <div class="eyebrow">{esc(eyebrow)}</div>
  <h1>{esc(title)}</h1>
  <p class="sub">{esc(tagline)}</p>
  <div class="meta">{meta_html}</div>
</div></header>

{sections}

<section style="border-bottom:0"><div class="wrap">{pager}</div></section>

<footer>
  <div class="f-in">
    <div class="f-top">
      <div>
        <a class="f-logo" href="{up}index.html">PLATFORM OPS</a>
        <p class="f-tag">Field notes on Kubernetes, SRE, and Platform Engineering —
          written from production, not slideware.</p>
      </div>
      <div class="f-cols">
        <div><div class="f-col-t">Newsletter</div>
          <a href="{up}index.html#issues">Latest Issues</a>
          <a href="{up}index.html#subscribe">Subscribe</a>
          <a href="{up}feed.xml">RSS Feed</a></div>
        <div><div class="f-col-t">Explore</div>
          <a href="{up}categories/index.html">All Categories</a>
          <a href="{up}categories/foundation/index.html">Foundation Hub</a>
          <a href="{up}index.html#topics">Knowledge Map</a></div>
        <div><div class="f-col-t">Connect</div>
          <a href="https://github.com/Vishal-Abhinav/Platform-ops-Newsletter" target="_blank">GitHub Repo ↗</a>
          <a href="{up}index.html#authors">About the Author</a>
          <a href="#">Back to Top ↑</a></div>
      </div>
    </div>
    <div class="f-bot">
      <div>© 2026 Vishal Abhinav · Platform Ops — code MIT,
        <a href="{up}LICENSE">text &amp; diagrams CC BY-NC-ND 4.0</a></div>
      <div>Built for engineers, by an engineer.</div>
    </div>
  </div>
</footer>
{JS}
</body>
</html>
"""


def section(tag, heading, lede, body):
    return (f'<section><div class="wrap"><div class="sec-tag">{esc(tag)}</div>'
            f'<h2>{esc(heading)}</h2>'
            + (f'<p class="lede">{lede}</p>' if lede else '')
            + body + '</div></section>')
