#!/usr/bin/env python3
"""Command-reference pages: a filterable table of commands, grouped by task.

A different shape from the topic deep-dives — you arrive knowing what you want
to do and needing the exact invocation, so the page is search-first.
"""
import html
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
from siteconf import BASE           # canonical origin, one source of truth


def esc(s):
    return html.escape(str(s), quote=True)


CSS = """
:root{--paper:#f2f0eb;--coal:#1c1f26;--cyan:#00c2d4;--amber:#f59e0b;--crimson:#e53935;
 --lime:#84cc16;--ash:#b8b2a7;--page-bg:#f2f0eb;--panel-bg:#e4e0d8;--card-bg:#f8f7f4;
 --page-fg:#1c1f26;--heading-fg:#1c1f26;--muted:#6b6860;--line-1:rgba(0,0,0,.06);
 --line-2:rgba(0,0,0,.1);--line-3:rgba(0,0,0,.16);--wash:rgba(0,0,0,.04);
 --nav-bg:rgba(242,240,235,.9);--code-bg:#0d0f14;}
html[data-theme="dark"]{--page-bg:#0c0e12;--panel-bg:#14161c;--card-bg:#181b22;--page-fg:#e7e5df;
 --heading-fg:#eeece6;--muted:#9a978e;--line-1:rgba(255,255,255,.07);--line-2:rgba(255,255,255,.11);
 --line-3:rgba(255,255,255,.18);--wash:rgba(255,255,255,.05);--nav-bg:rgba(12,14,18,.9);}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--page-bg);color:var(--page-fg);font-family:'Manrope',system-ui,sans-serif;
 -webkit-font-smoothing:antialiased;line-height:1.6;}
a{color:inherit;}
.wrap{max-width:1120px;margin:0 auto;padding:0 40px;}
@media(max-width:700px){.wrap{padding:0 18px;}}

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
.tt{width:32px;height:32px;border:1px solid var(--line-2);background:transparent;border-radius:50%;
 cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);flex-shrink:0;}
.tt:hover{color:var(--crimson);border-color:var(--crimson);}
.tt svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;}
html:not([data-theme="dark"]) .tt .moon,html[data-theme="dark"] .tt .sun{display:none;}
@media(max-width:760px){nav{padding:12px 16px;gap:10px;}.crumb{display:none;}}

header.hero{padding:56px 0 34px;border-bottom:1px solid var(--line-1);}
.eyebrow{display:inline-flex;align-items:center;gap:10px;font-family:'DM Mono',monospace;font-size:10.5px;
 letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:14px;}
.eyebrow::before{content:'';width:22px;height:1px;background:var(--crimson);}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(40px,7vw,70px);line-height:.95;
 letter-spacing:-.5px;color:var(--heading-fg);display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
h1 .ico{font-size:.58em;line-height:1;}
.sub{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:19px;color:var(--muted);
 max-width:720px;margin-top:12px;}

.ctl{position:sticky;top:59px;z-index:40;background:var(--page-bg);
 border-bottom:1px solid var(--line-1);padding:14px 0;}
.ctl-in{max-width:1120px;margin:0 auto;padding:0 40px;display:flex;flex-wrap:wrap;gap:10px;
 align-items:center;}
@media(max-width:700px){.ctl-in{padding:0 18px;}}
.cs{position:relative;flex:1 1 220px;min-width:0;display:flex;align-items:center;}
.cs svg{position:absolute;left:12px;width:14px;height:14px;stroke:var(--muted);fill:none;
 stroke-width:2;pointer-events:none;}
.cs input{width:100%;min-width:0;background:var(--wash);border:1px solid var(--line-2);border-radius:3px;
 padding:11px 12px 11px 34px;font-family:'DM Mono',monospace;font-size:12px;color:var(--page-fg);
 outline:none;-webkit-appearance:none;appearance:none;transition:border-color .2s;}
.cs input::placeholder{color:var(--ash);}
.cs input:focus{border-color:var(--crimson);}
.gfilters{display:flex;flex-wrap:wrap;gap:2px;}
.gf{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;text-transform:uppercase;
 padding:9px 11px;border:1px solid var(--line-2);background:transparent;color:var(--muted);
 cursor:pointer;transition:background .2s,color .2s,border-color .2s;}
.gf:hover{color:var(--heading-fg);border-color:var(--line-3);}
.gf.on{background:var(--coal);border-color:var(--coal);color:var(--paper);}
html[data-theme="dark"] .gf.on{background:var(--paper);color:var(--coal);border-color:var(--paper);}
.cres{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.3px;text-transform:uppercase;
 color:var(--muted);flex-basis:100%;}
.cres b{color:var(--crimson);font-weight:400;}

.grp{padding:40px 0 0;}
.grp-h{display:flex;align-items:baseline;gap:12px;margin-bottom:4px;}
.grp-h h2{font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:.8px;color:var(--heading-fg);}
.grp-h .cnt{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.4px;color:var(--muted);
 text-transform:uppercase;}
.grp-d{font-size:13.5px;color:var(--muted);max-width:720px;margin-bottom:16px;}
.grp[hidden]{display:none;}

.tw{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:640px;}
th{text-align:left;font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:1.6px;
 text-transform:uppercase;color:var(--muted);padding:9px 12px;border-bottom:1px solid var(--line-3);
 white-space:nowrap;}
td{padding:11px 12px;border-bottom:1px solid var(--line-1);vertical-align:top;}
tr:hover td{background:var(--wash);}
tr[hidden]{display:none;}
td.c{font-family:'DM Mono',monospace;font-size:12px;color:var(--heading-fg);white-space:nowrap;
 width:1%;}
td.c b{font-weight:400;color:var(--crimson);}
td.w{font-size:13px;color:var(--page-fg);}
td.e{font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);white-space:nowrap;}
mark{background:rgba(245,158,11,.35);color:inherit;padding:0 1px;border-radius:2px;}

.empty{padding:50px 0;text-align:center;font-family:'DM Mono',monospace;font-size:11px;
 letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
.note{padding:14px 16px;border-left:3px solid var(--amber);background:var(--wash);margin:18px 0 0;
 font-size:13.5px;}
.note b{display:block;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.8px;
 text-transform:uppercase;margin-bottom:6px;color:#8a5806;}
html[data-theme="dark"] .note b{color:var(--amber);}

.pager{display:flex;gap:2px;margin:44px 0 0;}
.pager a{flex:1;background:var(--card-bg);border:1px solid var(--line-1);padding:15px 18px;
 text-decoration:none;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;
 text-transform:uppercase;color:var(--muted);transition:background .2s,color .2s;}
.pager a:hover{background:var(--panel-bg);color:var(--crimson);}
.pager a.next{text-align:right;}
.pager a b{display:block;font-family:'Bebas Neue',sans-serif;font-size:18px;letter-spacing:.5px;
 color:var(--heading-fg);font-weight:400;margin-top:4px;}

footer{background:var(--coal);color:var(--paper);padding:48px 40px 24px;margin-top:56px;}
.f-in{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;gap:24px;
 justify-content:space-between;align-items:flex-end;}
.f-logo{font-family:'Bebas Neue',sans-serif;font-size:21px;letter-spacing:3px;color:#fff;
 text-decoration:none;}
.f-links{display:flex;flex-wrap:wrap;gap:18px;font-family:'DM Mono',monospace;font-size:10px;
 letter-spacing:1.3px;text-transform:uppercase;}
.f-links a{color:rgba(255,255,255,.65);text-decoration:none;}
.f-links a:hover{color:var(--cyan);}
.f-bot{max-width:1120px;margin:26px auto 0;padding-top:16px;
 border-top:1px solid rgba(255,255,255,.1);font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:1.2px;color:rgba(255,255,255,.35);}
.f-bot a{color:rgba(255,255,255,.5);}
"""

JS = """<script>
document.getElementById('tt').addEventListener('click',function(){
  var d=document.documentElement.getAttribute('data-theme')==='dark';
  if(d){document.documentElement.removeAttribute('data-theme');}
  else{document.documentElement.setAttribute('data-theme','dark');}
  try{localStorage.setItem('po-theme',d?'light':'dark');}catch(e){}
});
(function(){
  var q=document.getElementById('q'), res=document.getElementById('res'),
      empty=document.getElementById('empty'),
      rows=[].slice.call(document.querySelectorAll('tbody tr')),
      groups=[].slice.call(document.querySelectorAll('.grp')),
      TOTAL=rows.length, group='all';
  rows.forEach(function(r){ r.dataset.q=r.textContent.toLowerCase(); });

  function apply(){
    var term=(q.value||'').trim().toLowerCase(), shown=0;
    rows.forEach(function(r){
      var ok=(!term||r.dataset.q.indexOf(term)!==-1) &&
             (group==='all'||r.closest('.grp').dataset.g===group);
      r.hidden=!ok; if(ok) shown++;
    });
    groups.forEach(function(g){
      g.hidden=!g.querySelector('tbody tr:not([hidden])');
    });
    res.innerHTML = (term||group!=='all')
      ? '<b>'+shown+'</b> of '+TOTAL+' commands'
      : TOTAL+' commands across '+groups.length+' groups';
    empty.hidden = shown!==0;
  }
  var t; q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(apply,110);});
  q.addEventListener('search',apply);
  document.querySelectorAll('.gf').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('.gf').forEach(function(x){x.classList.remove('on');});
      b.classList.add('on'); group=b.dataset.g; apply();
    });
  });
  apply();
})();
</script>"""

TOGGLE = ('<button class="tt" id="tt" type="button" aria-label="Toggle dark mode">'
          '<svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/>'
          '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2'
          'M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
          '<svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/>'
          '</svg></button>')

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&'
         'family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&'
         'family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">')

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


def render(*, slug, title, icon, tagline, groups, category_slug, pager, up="../../"):
    """groups: [(id, heading, description, [(command, what, example|''), ...]), ...]"""
    total = sum(len(g[3]) for g in groups)

    filters = '<button type="button" class="gf on" data-g="all">All</button>'
    filters += "".join(f'<button type="button" class="gf" data-g="{esc(g[0])}">{esc(g[1])}</button>'
                       for g in groups)

    body = ""
    for gid, heading, desc, rows in groups:
        trs = ""
        for cmd, what, example in rows:
            trs += (f'<tr><td class="c">{cmd}</td><td class="w">{what}</td>'
                    f'<td class="e">{example}</td></tr>')
        body += f"""
  <section class="grp" data-g="{esc(gid)}"><div class="wrap">
    <div class="grp-h"><h2>{esc(heading)}</h2><span class="cnt">{len(rows)} commands</span></div>
    <p class="grp-d">{desc}</p>
    <div class="tw"><table><thead><tr><th>Command</th><th>What it does</th>
      <th>Typical use</th></tr></thead><tbody>{trs}</tbody></table></div>
  </div></section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} · Platform Ops · Vishal Abhinav</title>
<meta name="description" content="{esc(tagline)}">
<meta name="author" content="Vishal Abhinav">
<meta name="copyright" content="© 2026 Vishal Abhinav. Text and diagrams CC BY-NC-ND 4.0.">
<link rel="canonical" href="{BASE}Commands/{slug.upper()}/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Platform Ops · Tech with Vishal Abhinav">
<meta property="og:title" content="{esc(title)} · Platform Ops">
<meta property="og:description" content="{esc(tagline)}">
<meta property="og:url" content="{BASE}Commands/{slug.upper()}/{slug}.html">
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
<link rel="stylesheet" href="{up}Commands/commands.css">
</head>
<body>
<nav>
  <a href="{up}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>
  <div class="crumb">
    <a href="{up}index.html">Home</a><span>/</span>
    <a href="{up}categories/index.html">Categories</a><span>/</span>
    <a href="{up}categories/{esc(category_slug)}/index.html">Commands</a><span>/</span>
    <span class="cur">{esc(title)}</span>
  </div>
  {TOGGLE}
</nav>

<header class="hero"><div class="wrap">
  <div class="eyebrow">Commands · Reference</div>
  <h1><span class="ico">{icon}</span>{esc(title)}</h1>
  <p class="sub">{esc(tagline)}</p>
</div></header>

<div class="ctl"><div class="ctl-in">
  <label class="cs">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/>
      <path d="M20 20l-3.5-3.5"/></svg>
    <input type="search" id="q" autocomplete="off" spellcheck="false"
           placeholder="Search {total} commands — try a flag, a task, or part of a name"
           aria-label="Search commands">
  </label>
  <div class="gfilters">{filters}</div>
  <div class="cres" id="res" aria-live="polite"></div>
</div></div>

{body}
<div class="empty" id="empty" hidden>No command matches that search.</div>

<div class="wrap">{pager}</div>

<footer>
  <div class="f-in">
    <a class="f-logo" href="{up}index.html">PLATFORM OPS</a>
    <div class="f-links">
      <a href="{up}categories/{esc(category_slug)}/index.html">Commands Hub</a>
      <a href="{up}categories/index.html">All Categories</a>
      <a href="{up}index.html#library">Reference Library</a>
      <a href="{up}index.html#subscribe">Subscribe</a>
      <a href="{up}feed.xml">RSS</a>
    </div>
  </div>
  <div class="f-bot">© 2026 Vishal Abhinav · Platform Ops — code MIT,
    <a href="{up}LICENSE">text &amp; diagrams CC BY-NC-ND 4.0</a></div>
</footer>
{JS}
</body>
</html>
"""
