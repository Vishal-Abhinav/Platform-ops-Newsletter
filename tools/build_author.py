#!/usr/bin/env python3
"""Replace the homepage author block with a compact pointer to /about/.

The full publication explanation and author biography live on about/index.html.
The homepage still keeps the #authors anchor because older links and the docs
rail point there, but the section is now a doorway rather than a duplicate.
"""
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
SRC = ROOT / "index.html"

src = SRC.read_text(encoding="utf-8")

start = src.index('<!-- ═══════════ AUTHORS ═══════════ -->')
end = src.index('<!-- ═══════════ SUBSCRIBE ═══════════ -->')

NEW = """<!-- ═══════════ AUTHORS ═══════════ -->
<div class="authors-section" id="authors">
  <div class="authors-inner reveal au-home">
    <div>
      <div class="section-tag">About + Author</div>
      <h2 class="section-title">READ THE FULL STORY</h2>
      <p class="section-lead" style="margin-bottom:0">Who writes Platform Ops, what it covers, why it exists, and how the pieces connect.</p>
    </div>
    <div class="au-home-panel">
      <p>Platform Ops is written by Vishal Abhinav and published by Srivan Technologies. The full About page carries the publication promise, author background, coverage model, licensing notes, and the starting points for new readers.</p>
      <div class="au-home-actions">
        <a href="about/index.html">About Platform Ops</a>
        <a href="about/index.html#author">About the Author</a>
        <a href="terminal/index.html">Practice Terminal</a>
      </div>
    </div>
  </div>
</div>

"""

src = src[:start] + NEW + src[end:]

CSS = """
/* ─── HOMEPAGE AUTHOR POINTER ─── */
.authors-inner.au-home{display:grid!important;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);
  gap:40px;align-items:center;max-width:1120px;}
.au-home-panel{background:var(--card-bg);border:1px solid var(--hairline-3);border-radius:8px;
  padding:26px;box-shadow:0 2px 20px rgba(0,0,0,.05);}
.au-home-panel p{margin:0;color:var(--page-fg);font-size:15px;line-height:1.7;}
.au-home-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;}
.au-home-actions a{font-family:'DM Mono',monospace;font-size:10.5px;letter-spacing:1.3px;
  text-transform:uppercase;text-decoration:none;color:var(--heading-fg);border:1px solid var(--hairline-4);
  border-radius:3px;padding:8px 11px;transition:border-color .18s,color .18s,background .18s;}
.au-home-actions a:first-child{background:var(--cta-bg);border-color:var(--cta-bg);color:var(--cta-fg);}
.au-home-actions a:hover{border-color:var(--crimson);color:var(--crimson);}
.au-home-actions a:first-child:hover{background:var(--crimson);border-color:var(--crimson);color:#fff;}
@media(max-width:900px){.authors-inner.au-home{grid-template-columns:1fr;gap:24px;}}
"""

i = src.rindex("</style>")
src = src[:i] + CSS + src[i:]

SRC.write_text(src, encoding="utf-8")
print(f"index.html -> {len(src)} chars, homepage about/author pointer")
