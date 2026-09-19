#!/usr/bin/env python3
"""Reduce the homepage to gateways and align its closing calls to action."""
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
SRC = ROOT / "index.html"
src = SRC.read_text(encoding="utf-8")

# The homepage no longer has an on-page contents rail. Keep this in the final
# composition stage so earlier builders can continue to use their historical
# anchors without allowing the rail to reappear in generated output.
rail_start = src.index('<aside class="docs-rail">')
rail_end = src.index('</aside>', rail_start) + len('</aside>')
src = src[:rail_start] + src[rail_end:]

# The moving keyword ticker duplicates labels already available in search and
# the category map. Between two interactive sections it reads as a divider ad,
# so remove it from the final homepage composition.
ticker_start = src.index('<!-- ═══════════ TICKER ═══════════ -->')
ticker_end = src.index('<!-- ═══════════ DOCS RAIL + CONTENT (Tier 3) ═══════════ -->', ticker_start)
src = src[:ticker_start] + src[ticker_end:]

start = src.index('<div class="knowledge-row">')
end = src.index('<!-- ═══════════ AUTHORS ═══════════ -->')

portals = """<section class="home-portals" aria-labelledby="explore-heading">
  <div class="home-portals-inner reveal">
    <div class="home-portals-head">
      <h2 id="explore-heading">Explore Platform Ops</h2>
      <p>Choose the knowledge map or the published archive.</p>
    </div>
    <div class="home-portal-grid">
      <a class="home-portal" href="categories/index.html">
        <span class="home-portal-no">01</span>
        <div><b>What We Cover</b><p>All pillars, categories, live topics, pipeline work, and planned coverage.</p></div>
        <span class="home-portal-arrow" aria-hidden="true">→</span>
      </a>
      <a class="home-portal home-portal-dark" href="issues/index.html">
        <span class="home-portal-no">02</span>
        <div><b>Latest Issues</b><p>The complete published archive, newest first, with every deep-dive linked.</p></div>
        <span class="home-portal-arrow" aria-hidden="true">→</span>
      </a>
    </div>
  </div>
</section>

"""
src = src[:start] + portals + src[end:]

authors = src.index('<!-- ═══════════ AUTHORS ═══════════ -->')
subscribe = src.index('<!-- ═══════════ SUBSCRIBE ═══════════ -->', authors)
docs_end = src.index('<!-- ═══════════ /DOCS RAIL + CONTENT ═══════════ -->', subscribe)
closing = '\n</div>\n</div>\n'
closing_at = src.rfind(closing, subscribe, docs_end)
assert closing_at != -1, "homepage docs-content closing block not found"
src = src[:authors] + '<div class="home-cta-row">\n' + src[authors:closing_at] + '</div>\n' + src[closing_at:]

css = """
/* Homepage gateways and paired closing calls to action */
.home-portals{padding:34px 48px;background:var(--page-bg);}
.home-portals-inner{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:230px minmax(0,1fr);gap:24px;align-items:stretch;}
.home-portals-head{display:flex;flex-direction:column;justify-content:center;border-left:2px solid var(--crimson);padding-left:18px;}
.home-portals-head h2{font-family:'Bebas Neue',sans-serif;font-size:30px;line-height:1;letter-spacing:0;color:var(--heading-fg);margin:0 0 8px;}
.home-portals-head p{font-size:13px;line-height:1.5;color:var(--muted);margin:0;}
.home-portal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:2px;}
.home-portal{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:20px;align-items:start;
  min-height:132px;padding:22px;background:var(--panel-bg);border:1px solid var(--hairline-2);
  color:var(--page-fg);text-decoration:none;transition:border-color .2s,transform .2s;}
.home-portal:hover{border-color:var(--crimson);transform:translateY(-2px);}
.home-portal-no{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;color:var(--crimson);}
.home-portal b{display:block;font-family:'Bebas Neue',sans-serif;font-size:29px;line-height:1;letter-spacing:0;color:var(--heading-fg);}
.home-portal p{margin:10px 0 0;font-size:13px;line-height:1.5;color:var(--muted);}
.home-portal-arrow{font-size:22px;color:var(--crimson);}
.home-portal-dark{background:var(--coal);border-color:rgba(255,255,255,.1);}
.home-portal-dark b{color:var(--paper);}.home-portal-dark p{color:rgba(255,255,255,.5);}
.home-cta-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:stretch;}
.home-cta-row>.authors-section,.home-cta-row>.subscribe-section{min-width:0;margin:0;padding:56px 48px;}
.home-cta-row .authors-inner.au-home{grid-template-columns:1fr!important;gap:28px;}
.home-cta-row .subscribe-inner{padding:0;}
.home-cta-row .subscribe-section{display:flex;align-items:center;justify-content:center;}
/* One rhythm and one content surface across the dark homepage bands. The
   hairline remains the section boundary; background changes are reserved for
   functional contrast such as the subscription action. */
.ks,.kn,.pf,.ib,.rj{background:#090b0f;padding-top:clamp(40px,4.5vw,58px);padding-bottom:clamp(40px,4.5vw,58px);}
.rj-head{margin-bottom:8px;}
.rj-lede{margin-bottom:22px;}
/* Compact production journey: the selected stage uses the full line instead
   of leaving two thirds of a large panel empty. */
@media(min-width:1000px){
  .pf{padding-top:34px;padding-bottom:34px;}
  .pf-lede{margin-bottom:18px;}
  .pf-rail{margin-bottom:18px;}
  .pf-panel{display:grid;grid-template-columns:minmax(280px,1fr) minmax(340px,1.2fr) minmax(170px,.65fr);
    grid-template-rows:auto auto 1fr;column-gap:24px;row-gap:5px;padding:18px 20px;align-items:start;}
  .pf-panel[hidden]{display:none;}
  .pf-step{grid-column:1;grid-row:1;margin-bottom:0;}
  .pf-title{grid-column:1;grid-row:2;margin-bottom:2px;}
  .pf-what{grid-column:1;grid-row:3;margin:0;font-size:13.5px;line-height:1.5;}
  .pf-techlabel{grid-column:2;grid-row:1;margin-bottom:0;}
  .pf-tech{grid-column:2;grid-row:2 / span 2;margin:0;align-content:start;}
  .pf-readlabel{grid-column:3;grid-row:1;margin-bottom:0;}
  .pf-read{grid-column:3;grid-row:2 / span 2;align-content:start;}
  .pf-read a{padding:6px 10px;}
}
/* The roles/journey band is a working index, so use the canvas instead of
   leaving editorial-width gutters. Denser tiles shorten the section without
   clipping any route or role. */
@media(min-width:1440px){
  .rj{padding-top:30px;padding-bottom:38px;}
  .rj-inner{max-width:none;padding-left:clamp(28px,2.5vw,48px);padding-right:clamp(28px,2.5vw,48px);
    gap:28px;grid-template-columns:minmax(0,1fr) minmax(0,1fr);}
  .rj-aside{padding-left:28px;}
  .rx-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;}
  .ej-track{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;}
  .rx-card{padding:14px;}
  .rx-meta{margin-bottom:10px;}
  .rx-path{gap:5px;}
  .rx-path a{padding:5px 7px;font-size:11.5px;}
  .ej-stop{padding:13px 13px 15px;}
  .ej-n{margin-bottom:4px;}
  .ej-c{margin:2px 0 6px;}
  .ej-w{font-size:12px;line-height:1.45;}
}
@media(max-width:1000px){.home-cta-row{grid-template-columns:1fr}.home-cta-row>.authors-section,.home-cta-row>.subscribe-section{padding:52px 32px}.home-portals{padding:34px 32px}.home-portals-inner{grid-template-columns:1fr}.home-portals-head{padding:0 0 0 16px}}
@media(max-width:700px){.home-portal-grid{grid-template-columns:1fr}.home-portal{min-height:0;padding:20px}.home-portals{padding:30px 20px}}
"""
i = src.rindex("</style>")
src = src[:i] + css + src[i:]
SRC.write_text(src, encoding="utf-8")
print("index.html -> dedicated page gateways + paired About/Subscribe row")
