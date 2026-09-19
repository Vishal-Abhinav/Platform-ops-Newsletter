#!/usr/bin/env python3
"""Build the free, browser-only Platform Ops troubleshooting assistant.

The assistant is retrieval, not a language model. It searches text already
published on the site and cites the pages it found. No question leaves the
browser unless the reader explicitly opens one of the Google search links.
"""
import html
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from siteconf import BASE_HOST, skip_page  # noqa: E402

ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def plain(fragment):
    fragment = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", fragment,
                      flags=re.I | re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def chunks_for(src):
    """Return compact, section-aware chunks from visible article blocks."""
    src = re.sub(r"<(script|style|nav|footer|svg)\b.*?</\1>", " ", src,
                 flags=re.I | re.S)
    section = "Overview"
    chunks, pending = [], []

    def flush():
        nonlocal pending
        text = " ".join(pending).strip()
        if len(text) >= 80:
            while len(text) > 760:
                cut = text.rfind(". ", 0, 760)
                if cut < 320:
                    cut = text.rfind(" ", 0, 760)
                cut = cut + 1 if cut > 0 else 760
                chunks.append((section, text[:cut].strip()))
                text = text[cut:].strip()
            if len(text) >= 80:
                chunks.append((section, text))
        pending = []

    block = re.compile(r"<(h[1-3]|p|li|pre|blockquote)\b[^>]*>(.*?)</\1>",
                       re.I | re.S)
    for match in block.finditer(src):
        tag, text = match.group(1).lower(), plain(match.group(2))
        if not text:
            continue
        if tag.startswith("h"):
            flush()
            section = text[:140]
        else:
            pending.append(text)
            if sum(map(len, pending)) >= 620:
                flush()
    flush()
    return chunks[:48]


rows = []
for page in sorted(ROOT.rglob("*.html")):
    if "tools" in page.parts or skip_page(page.name):
        continue
    src = page.read_text(encoding="utf-8", errors="replace")
    if re.search(r'<meta name="robots"[^>]*noindex', src, re.I):
        continue
    rel = page.relative_to(ROOT).as_posix()
    href = rel[:-len("index.html")] if rel.endswith("index.html") else rel
    if rel == "index.html":
        href = ""
    title_match = re.search(r"<title>(.*?)</title>", src, re.I | re.S)
    title = plain(title_match.group(1)) if title_match else rel
    title = re.split(r"\s+[·|]\s+Platform Ops", title, maxsplit=1)[0]
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', src, re.I)
    desc = html.unescape(desc_match.group(1)).strip() if desc_match else ""
    if desc:
        rows.append([title, href, "Summary", desc])
    for section, text in chunks_for(src):
        rows.append([title, href, section, text])

# build_search.py runs immediately before this stage. Reuse its structured
# taxonomy and command rows so a term such as CrashLoopBackOff remains
# findable even when the linked article discusses it inside a diagram or card
# that the prose chunker deliberately skips. Planned placeholders are omitted:
# the assistant cites published guidance, not the backlog.
search_js = ASSETS / "search.js"
if search_js.exists():
    match = re.search(r"^var PO_SEARCH = (.*);$",
                      search_js.read_text(encoding="utf-8"), re.M)
    assert match, "assistant could not read PO_SEARCH from assets/search.js"
    for kind, name, href, group, extra in json.loads(match.group(1)):
        if kind == 1 and extra != "live":
            continue
        if kind == 0:
            detail = f"Platform Ops category covering {group}."
        elif kind == 1:
            detail = f"Published topic in {group}."
        elif kind == 2:
            detail = f"Published Platform Ops page in {group}."
        else:
            detail = extra or f"Command reference in {group}."
        rows.append([name, href, group, detail])

assert len(rows) >= 150, f"assistant corpus is unexpectedly small: {len(rows)} chunks"
DATA = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

CSS = r"""/* Platform Ops local assistant */
.pa-launch{position:fixed;right:18px;bottom:18px;z-index:1200;width:48px;height:48px;
  display:grid;place-items:center;border:1px solid rgba(229,57,53,.65);border-radius:50%;
  background:#15171c;color:#fff;box-shadow:0 12px 34px rgba(0,0,0,.32);cursor:pointer;}
.pa-launch:hover,.pa-launch:focus-visible{background:#e53935;outline:none;}
.pa-launch svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.8;}
.pa-panel{position:fixed;right:18px;bottom:78px;z-index:1201;width:min(420px,calc(100vw - 24px));
  height:min(620px,calc(100vh - 100px));display:none;grid-template-rows:auto 1fr auto;
  background:#101217;color:#e9e7e1;border:1px solid rgba(255,255,255,.14);border-radius:6px;
  box-shadow:0 28px 90px rgba(0,0,0,.48);overflow:hidden;font-family:Manrope,Arial,sans-serif;}
.pa-panel.on{display:grid;}
.pa-head{display:flex;align-items:center;gap:10px;padding:13px 14px;border-bottom:1px solid rgba(255,255,255,.1);}
.pa-head-text{min-width:0;flex:1;}.pa-head b{display:block;font-family:'DM Mono',monospace;
  font-size:11px;letter-spacing:1.4px;}.pa-head span{display:block;margin-top:3px;color:#8f939d;
  font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;}
.pa-close{width:30px;height:30px;border:0;background:transparent;color:#9da0a8;font-size:22px;
  cursor:pointer}.pa-close:hover{color:#fff;}
.pa-log{overflow:auto;padding:15px;scrollbar-width:thin;scrollbar-color:#454851 transparent;}
.pa-msg{max-width:92%;margin:0 0 12px;padding:10px 12px;border-radius:5px;font-size:13px;
  line-height:1.55;background:#1a1d24;border:1px solid rgba(255,255,255,.08);}
.pa-msg.user{margin-left:auto;background:#262a32;border-color:rgba(0,194,212,.3);}
.pa-msg p{margin:0 0 8px}.pa-msg p:last-child{margin-bottom:0}
.pa-suggest{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px;}
.pa-chip{border:1px solid rgba(255,255,255,.15);background:transparent;color:#c9cbd0;
  border-radius:4px;padding:6px 8px;font:9px 'DM Mono',monospace;cursor:pointer;text-align:left;}
.pa-chip:hover{border-color:#00c2d4;color:#fff;}
.pa-path{margin:8px 0 10px;padding-left:18px;color:#c9cbd0}.pa-path li{margin:4px 0;}
.pa-result{display:block;margin-top:8px;padding:9px 10px;border-left:2px solid #84cc16;
  background:rgba(255,255,255,.035);color:inherit;text-decoration:none;}
.pa-result:hover{background:rgba(255,255,255,.07)}.pa-result b{display:block;color:#fff;font-size:12px;}
.pa-result small{display:block;margin:3px 0 5px;color:#84cc16;font:8px 'DM Mono',monospace;
  letter-spacing:.8px;text-transform:uppercase}.pa-result span{display:block;color:#aeb1b9;font-size:11.5px;line-height:1.45;}
.pa-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}.pa-actions a{color:#00c2d4;
  font:9px 'DM Mono',monospace;text-decoration:none;border:1px solid rgba(0,194,212,.35);
  border-radius:4px;padding:6px 8px}.pa-actions a:hover{border-color:#00c2d4;color:#fff;}
.pa-form{padding:11px;border-top:1px solid rgba(255,255,255,.1);background:#14161b;}
.pa-row{display:flex;gap:8px}.pa-input{min-width:0;flex:1;border:1px solid rgba(255,255,255,.16);
  border-radius:4px;background:#0d0f13;color:#fff;padding:10px 11px;font:12px Manrope,Arial,sans-serif;
  outline:none}.pa-input:focus{border-color:#00c2d4}.pa-send{width:40px;border:1px solid #e53935;
  border-radius:4px;background:#e53935;color:#fff;cursor:pointer;font-size:16px}.pa-send:hover{background:#c92c29}
.pa-local{margin-top:7px;color:#747883;font:8px 'DM Mono',monospace;letter-spacing:.7px;text-align:center;}
@media(max-width:520px){.pa-launch{right:12px;bottom:12px}.pa-panel{right:6px;bottom:68px;
  width:calc(100vw - 12px);height:min(680px,calc(100vh - 78px));}.pa-log{padding:12px}}
@media(prefers-reduced-motion:reduce){.pa-launch,.pa-panel{scroll-behavior:auto}}
"""

JS = r"""var PO_ASSISTANT_DATA=__DATA__;
(function(){
  var script=document.currentScript||document.querySelector('script[src$="assistant.js"]');
  var ROOT=(script&&script.getAttribute('data-root'))||'';
  var STOP={the:1,a:1,an:1,and:1,or:1,to:1,of:1,in:1,on:1,for:1,is:1,are:1,
    my:1,with:1,how:1,what:1,why:1,when:1,from:1,this:1,that:1,not:1,can:1,i:1};
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
  function words(s){return String(s).toLowerCase().split(/[^a-z0-9_.-]+/)
    .filter(function(x){return x.length>1&&!STOP[x]})}
  function snippet(text,tokens){var low=text.toLowerCase(),at=-1;
    tokens.some(function(t){at=low.indexOf(t);return at>=0});
    var start=Math.max(0,(at<0?0:at)-90),out=text.slice(start,start+310).trim();
    return(start?'…':'')+out+(start+310<text.length?'…':'')}
  function search(q){var phrase=q.toLowerCase().trim(),ts=words(q),found=[];
    if(!ts.length)return found;
    PO_ASSISTANT_DATA.forEach(function(r){var title=r[0].toLowerCase(),sec=r[2].toLowerCase(),
      body=r[3].toLowerCase(),score=0,hits=0;
      if(title.indexOf(phrase)>=0)score+=70;if(sec.indexOf(phrase)>=0)score+=35;
      if(body.indexOf(phrase)>=0)score+=24;
      ts.forEach(function(t){var hit=false;if(title.indexOf(t)>=0){score+=15;hit=true}
        if(sec.indexOf(t)>=0){score+=9;hit=true}if(body.indexOf(t)>=0){score+=3;hit=true}
        if(hit)hits++});
      if(hits)score+=hits===ts.length?25:hits*2;
      if(score>4)found.push({r:r,s:score});
    });
    found.sort(function(a,b){return b.s-a.s});
    var seen={};return found.filter(function(x){var k=x.r[1]+'|'+x.r[2];
      if(seen[k])return false;seen[k]=1;return true}).slice(0,5)}
  function build(){if(document.querySelector('.pa-launch'))return;
    var launch=document.createElement('button');launch.className='pa-launch';launch.type='button';
    launch.setAttribute('aria-label','Open Platform Ops assistant');launch.setAttribute('aria-expanded','false');
    launch.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/><path d="M8 9h8M8 13h5"/></svg>';
    var panel=document.createElement('section');panel.className='pa-panel';panel.setAttribute('role','dialog');
    panel.setAttribute('aria-label','Platform Ops assistant');panel.innerHTML=
      '<header class="pa-head"><div class="pa-head-text"><b>PLATFORM OPS ASSISTANT</b><span>LOCAL KNOWLEDGE · FREE</span></div><button class="pa-close" type="button" aria-label="Close assistant">×</button></header>'+
      '<div class="pa-log" aria-live="polite"></div><form class="pa-form"><div class="pa-row"><input class="pa-input" maxlength="240" autocomplete="off" placeholder="Describe the issue…" aria-label="Troubleshooting question"><button class="pa-send" type="submit" aria-label="Search">→</button></div><div class="pa-local">RUNS IN THIS BROWSER · NO QUESTION IS SENT</div></form>';
    document.body.appendChild(launch);document.body.appendChild(panel);
    var log=panel.querySelector('.pa-log'),input=panel.querySelector('.pa-input');
    function add(cls,body){var d=document.createElement('div');d.className='pa-msg '+cls;
      d.innerHTML=body;log.appendChild(d);log.scrollTop=log.scrollHeight;return d}
    function ask(q){q=q.trim();if(!q)return;add('user','<p>'+esc(q)+'</p>');input.value='';
      var hits=search(q),ts=words(q),out='<p><b>Relevant Platform Ops guidance</b></p>';
      if(/error|fail|down|pending|crash|timeout|refused|denied|slow|stuck|trouble|debug|unable/i.test(q))
        out+='<ol class="pa-path"><li>Confirm the symptom and scope.</li><li>Collect events, logs and current state.</li><li>Isolate the failing layer before changing it.</li><li>Apply one reversible change and verify.</li></ol>';
      if(!hits.length){out='<p>I could not find this in the published Platform Ops material.</p>'}
      else hits.forEach(function(x){var r=x.r;out+='<a class="pa-result" href="'+ROOT+esc(r[1])+'"><b>'+esc(r[0])+'</b><small>'+esc(r[2])+'</small><span>'+esc(snippet(r[3],ts))+'</span></a>'});
      var site='https://www.google.com/search?q='+encodeURIComponent('site:__HOST__ '+q);
      var web='https://www.google.com/search?q='+encodeURIComponent(q+' official documentation');
      out+='<div class="pa-actions"><a target="_blank" rel="noopener" href="'+site+'">GOOGLE · PLATFORM OPS</a><a target="_blank" rel="noopener" href="'+web+'">GOOGLE · OFFICIAL DOCS</a></div>';
      add('bot',out)}
    var welcome=add('bot','<p><b>What are you troubleshooting?</b></p><div class="pa-suggest"><button class="pa-chip" type="button">CrashLoopBackOff</button><button class="pa-chip" type="button">OpenShift route TLS</button><button class="pa-chip" type="button">Linux high load</button><button class="pa-chip" type="button">PVC pending</button></div>');
    welcome.addEventListener('click',function(e){if(e.target.classList.contains('pa-chip'))ask(e.target.textContent)});
    function toggle(on){panel.classList.toggle('on',on);launch.setAttribute('aria-expanded',String(on));if(on)setTimeout(function(){input.focus()},0)}
    launch.addEventListener('click',function(){toggle(!panel.classList.contains('on'))});
    panel.querySelector('.pa-close').addEventListener('click',function(){toggle(false);launch.focus()});
    panel.querySelector('form').addEventListener('submit',function(e){e.preventDefault();ask(input.value)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&panel.classList.contains('on'))toggle(false)});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build);else build();
})();
""".replace("__DATA__", DATA).replace("__HOST__", BASE_HOST)

(ASSETS / "assistant.css").write_text(CSS, encoding="utf-8")
(ASSETS / "assistant.js").write_text(JS, encoding="utf-8")

added, already = 0, 0
for page in sorted(ROOT.rglob("*.html")):
    if "tools" in page.parts or skip_page(page.name):
        continue
    rel = page.relative_to(ROOT).as_posix()
    src = page.read_text(encoding="utf-8")
    if "assets/assistant.js" in src:
        already += 1
        continue
    up = "../" * (len(pathlib.PurePosixPath(rel).parts) - 1)
    tags = (f'<link rel="stylesheet" href="{up}assets/assistant.css">\n'
            f'<script defer src="{up}assets/assistant.js" data-root="{up}"></script>\n')
    page.write_text(src.replace("</head>", tags + "</head>", 1), encoding="utf-8")
    added += 1

print(f"assistant corpus: {len(rows)} chunks; wired into {added} pages "
      f"({already} already had it)")
