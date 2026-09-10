#!/usr/bin/env python3
"""Second build stage for index.html:

  1. topic requests  — clicking a pipeline/planned topic queues it, and the
                       subscribe form posts the queue to Kit as a custom field
  2. analytics       — GoatCounter loader (inert until the code is filled in)
                       plus events for search, filters, requests and signups
  3. RSS             — discovery link in the head, links in the page
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import pathlib
import re

SRC = ROOT / 'index.html'
src = SRC.read_text(encoding='utf-8')

# ── 1. head: analytics loader + RSS discovery ────────────────────────────────
HEAD = """
<!-- Privacy-friendly analytics (GoatCounter). Put your site code between the
     quotes on the PO_GC line below; left empty, nothing loads and nothing is
     sent. The README has a one-liner that sets it across every page at once. -->
<script>
(function(){var PO_GC='';
 if(!PO_GC) return;
 var s=document.createElement('script');
 s.async=true; s.src='https://gc.zgo.at/count.js';
 s.setAttribute('data-goatcounter','https://'+PO_GC+'.goatcounter.com/count');
 document.head.appendChild(s);})();
</script>
<link rel="alternate" type="application/rss+xml" title="Platform Ops — new issues" href="feed.xml">
"""

src = src.replace('</head>', HEAD + '</head>', 1)

# ── 2. CSS ───────────────────────────────────────────────────────────────────
CSS = """
/* ─── TOPIC REQUESTS ─── */
.km-hint{display:flex;align-items:center;gap:7px;font-family:'DM Mono',monospace;font-size:9.5px;
  letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin:-14px 0 22px;}
.km-hint svg{width:12px;height:12px;stroke:var(--crimson);fill:none;stroke-width:2;flex-shrink:0;}
.km-t.req{background:var(--crimson)!important;border-color:var(--crimson)!important;color:#fff!important;}
.km-t.req::before{content:'✓';margin-right:5px;font-size:9px;}
button.km-t.pipe:hover,button.km-t.plan:hover{border-color:var(--crimson);color:var(--crimson);}
button.km-t.req:hover{opacity:.85;}

/* Bottom-LEFT, not right: the Latest Issues panel has its own scrollbar just
   inside the right edge, and a pill at bottom-right sat on top of it. */
.req-pill{position:fixed;left:22px;bottom:22px;z-index:60;display:none;align-items:center;gap:12px;
  background:var(--coal);color:var(--paper);border:0;border-radius:40px;padding:13px 15px 13px 20px;
  box-shadow:0 18px 44px rgba(0,0,0,.32);cursor:pointer;font-family:'DM Mono',monospace;
  font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;
  animation:req-pop .3s cubic-bezier(.34,1.56,.64,1);}
.req-pill.show{display:flex;}
html[data-theme="dark"] .req-pill{background:var(--paper);color:var(--coal);}
.req-pill b{color:var(--lime);font-weight:400;}
html[data-theme="dark"] .req-pill b{color:#4c840f;}
.req-pill .go{background:var(--crimson);color:#fff;border-radius:30px;padding:6px 12px;}
@keyframes req-pop{from{transform:translateY(14px) scale(.94);opacity:0;}to{transform:none;opacity:1;}}
@media(max-width:600px){.req-pill{left:12px;right:12px;bottom:12px;justify-content:space-between;}}

/* The subscribe band follows the page background, so these use theme tokens —
   hardcoded whites vanished against it in light mode. */
/* A 6px, 20%-opacity thumb on a dark panel reads as "no scrollbar". Note
   scrollbar-width:thin wins over ::-webkit-scrollbar in current Chromium, so
   the original "thin" had to go for the width below to apply on Windows. */
.kr-issues .issues-scroll{scrollbar-width:auto!important;scrollbar-gutter:stable;
  scrollbar-color:rgba(255,255,255,.34) rgba(255,255,255,.07)!important;}
.kr-issues .issues-scroll::-webkit-scrollbar{width:9px!important;}
.kr-issues .issues-scroll::-webkit-scrollbar-track{background:rgba(255,255,255,.07)!important;}
.kr-issues .issues-scroll::-webkit-scrollbar-thumb{background:rgba(255,255,255,.34)!important;
  border-radius:5px!important;}
.kr-issues .issues-scroll::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.55)!important;}

.sub-requests{max-width:520px;margin:0 auto 20px;display:none;}
.sub-requests.show{display:block;}
.sub-req-title{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:2px;
  text-transform:uppercase;color:var(--muted);margin-bottom:10px;}
.sub-req-chips{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;}
.sub-req-chip{display:inline-flex;align-items:center;gap:7px;background:var(--wash-2);
  border:1px solid var(--hairline-4);color:var(--heading-fg);border-radius:20px;
  padding:5px 8px 5px 12px;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:.8px;
  text-transform:uppercase;}
.sub-req-chip button{background:none;border:0;color:var(--muted);cursor:pointer;
  font:inherit;font-size:12px;line-height:1;padding:0 2px;transition:color .2s;}
.sub-req-chip button:hover{color:var(--crimson);}
.sub-rss{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--muted);margin-top:14px;}
.sub-rss a{color:#b97309;text-decoration:none;border-bottom:1px dashed rgba(185,115,9,.45);}
.sub-rss a:hover{color:var(--crimson);border-color:var(--crimson);}
html[data-theme="dark"] .sub-rss a{color:var(--amber);border-color:rgba(245,158,11,.45);}
html[data-theme="dark"] .sub-rss a:hover{color:#fff;border-color:#fff;}
"""
src = src.replace('/* ─── TOOLCHAIN DIAGRAM ─── */', CSS.strip() + '\n\n/* ─── TOOLCHAIN DIAGRAM ─── */', 1)

# ── 3. hint line under the knowledge-map controls ────────────────────────────
HINT = """    <div class="km-hint">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 01-3.4 0"/></svg>
      Click any pipeline or planned topic to be told when it lands
    </div>
"""
src = src.replace('    <div class="km-result" id="kmResult" aria-live="polite"></div>\n',
                  '    <div class="km-result" id="kmResult" aria-live="polite"></div>\n' + HINT, 1)

# ── 4. request pill ──────────────────────────────────────────────────────────
src = src.replace('<!-- ═══════════ SUBSCRIBE ═══════════ -->',
                  '<button class="req-pill" id="reqPill" type="button" hidden>\n'
                  '  <span><b id="reqPillN">0</b> topics queued</span>\n'
                  '  <span class="go">Get notified →</span>\n'
                  '</button>\n\n'
                  '<!-- ═══════════ SUBSCRIBE ═══════════ -->', 1)

# ── 5. subscribe form: queued-topic chips, the Kit field, an RSS alternative ──
src = src.replace(
    '    <form class="sub-form" id="subscribeForm"',
    '    <div class="sub-requests" id="subRequests">\n'
    '      <div class="sub-req-title">Notify me when these land</div>\n'
    '      <div class="sub-req-chips" id="subReqChips"></div>\n'
    '    </div>\n'
    '    <form class="sub-form" id="subscribeForm"', 1)

src = src.replace(
    '      <button class="sub-btn" type="submit">Subscribe →</button>',
    '      <!-- Kit custom field. Create a field named topic_request in Kit\n'
    '           (Grow → Subscribers → the gear → Custom fields) or Kit drops it. -->\n'
    '      <input type="hidden" name="fields[topic_request]" id="subTopicField" value="">\n'
    '      <button class="sub-btn" type="submit">Subscribe →</button>', 1)

src = src.replace(
    '    <div class="sub-note">No spam · Unsubscribe anytime · Published monthly</div>',
    '    <div class="sub-note">No spam · Unsubscribe anytime · Published monthly</div>\n'
    '    <div class="sub-rss">Prefer a reader? <a href="feed.xml">RSS feed</a></div>', 1)

# ── 6. footer: RSS in the Connect column ─────────────────────────────────────
src = src.replace(
    '          <a href="#">Back to Top ↑</a>',
    '          <a href="feed.xml">RSS Feed</a>\n'
    '          <a href="#">Back to Top ↑</a>', 1)

# ── 7. JS ────────────────────────────────────────────────────────────────────
JS = """
/* ── Analytics events (no-ops until a GoatCounter code is set) ── */
function poTrack(path, title){
  try{
    if (window.goatcounter && window.goatcounter.count)
      window.goatcounter.count({ path: path, title: title || path, event: true });
  }catch(e){}
}

/* ── Topic requests ──────────────────────────────────────────────────────
   A pipeline or planned topic is a dead end otherwise: there's nothing to
   click through to. Queuing it turns that into a signup and, in Kit, into a
   ranked list of what people actually want written next. Kept in
   sessionStorage so a reload mid-browse doesn't lose the queue. ---------- */
(function(){
  const MAX = 8;
  const pill   = document.getElementById('reqPill');
  const pillN  = document.getElementById('reqPillN');
  const box    = document.getElementById('subRequests');
  const chips  = document.getElementById('subReqChips');
  const field  = document.getElementById('subTopicField');
  if (!pill || !box || !chips || !field) return;

  /* the ✓ on a queued chip is a CSS ::before, so it never lands in textContent */
  const label = b => b.textContent.trim();

  let queue = [];
  try { queue = JSON.parse(sessionStorage.getItem('po-topics') || '[]'); } catch(e){ queue = []; }
  if (!Array.isArray(queue)) queue = [];

  function save(){
    try { sessionStorage.setItem('po-topics', JSON.stringify(queue)); } catch(e){}
  }

  function render(){
    document.querySelectorAll('button.km-t').forEach(b => {
      b.classList.toggle('req', queue.indexOf(label(b)) !== -1);
    });
    pillN.textContent = queue.length;
    pill.hidden = queue.length === 0;
    pill.classList.toggle('show', queue.length > 0);
    box.classList.toggle('show', queue.length > 0);
    field.value = queue.join(', ').slice(0, 250);
    chips.innerHTML = '';
    queue.forEach(t => {
      const c = document.createElement('span');
      c.className = 'sub-req-chip';
      c.appendChild(document.createTextNode(t));
      const x = document.createElement('button');
      x.type = 'button'; x.textContent = '×';
      x.setAttribute('aria-label', 'Remove ' + t);
      x.addEventListener('click', () => { toggle(t); });
      c.appendChild(x);
      chips.appendChild(c);
    });
  }

  function toggle(topic){
    const i = queue.indexOf(topic);
    if (i !== -1) { queue.splice(i, 1); }
    else {
      if (queue.length >= MAX) return;
      queue.push(topic);
      poTrack('topic-request/' + topic.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
              'Topic requested: ' + topic);
    }
    save(); render();
  }

  document.addEventListener('click', e => {
    const b = e.target.closest('button.km-t');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();   /* don't fold the category shut */
    toggle(label(b));
  });

  pill.addEventListener('click', () => {
    const s = document.getElementById('subscribe');
    if (s) s.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const inp = document.getElementById('subEmail');
    if (inp) setTimeout(() => inp.focus({ preventScroll: true }), 600);
  });

  window.poClearTopics = function(){ queue = []; save(); render(); };
  render();
})();
"""
src = src.replace('/* ── Knowledge map: two-level accordion',
                  JS.strip() + '\n\n/* ── Knowledge map: two-level accordion', 1)

# hook the existing handlers, rather than duplicating them
src = src.replace(
    """      result.innerHTML = '<b>' + shown + '</b> of ' + TOTAL + ' topics' +""",
    """      if (q.length >= 3) {
        clearTimeout(window.__kmTrack);
        window.__kmTrack = setTimeout(() => poTrack(
          'kmap-search/' + q.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40),
          'Knowledge-map search: ' + q), 900);
      }
      result.innerHTML = '<b>' + shown + '</b> of ' + TOTAL + ' topics' +""", 1)

src = src.replace("""      filter = btn.dataset.f;
      apply();""",
                  """      filter = btn.dataset.f;
      poTrack('kmap-filter/' + filter, 'Knowledge-map filter: ' + filter);
      apply();""", 1)

src = src.replace("""      say('Almost there — check your inbox to confirm your subscription.', 'ok');
      form.reset();""",
                  """      say('Almost there — check your inbox to confirm your subscription.', 'ok');
      poTrack('subscribe/success', 'Newsletter signup');
      form.reset();
      if (window.poClearTopics) window.poClearTopics();""", 1)

SRC.write_text(src, encoding='utf-8')
print(f"index.html -> {len(src)} bytes")
for probe in ('PO_GC', 'reqPill', 'fields[topic_request]', 'poTrack', 'feed.xml',
              'sub-req-chips', 'km-hint', 'RSS Feed'):
    print(f"  {probe:24} x{src.count(probe)}")
