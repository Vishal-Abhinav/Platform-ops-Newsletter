#!/usr/bin/env python3
"""Final index.html stage: unstack the knowledge row.

The map and the archive were side by side in a 1fr 1fr grid. That gave an
expanded category about half the page to lay 30+ chips into — so its contents
were cramped on the left while the archive column left white space on the
right, and the two columns' heights had to be reconciled in JS.

Full width each, stacked. The chips get the whole page, the archive becomes a
real grid instead of a capped scroller, and the height-sync goes away with the
two bugs it caused.
"""
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
SRC = ROOT / "index.html"
src = SRC.read_text(encoding="utf-8")

CSS = """
/* ─── KNOWLEDGE ROW: STACKED, FULL WIDTH ─── */
/* Loaded last so it wins over the two-column rules above. */
.knowledge-row{display:block!important;}
.kr-topics.section{max-width:1240px!important;margin:0 auto!important;
  padding:96px 64px 72px!important;}
.kr-issues.issues-bg{padding:0!important;}
.kr-issues .issues-inner{max-width:1240px!important;margin:0 auto!important;
  padding:88px 64px 96px!important;display:block!important;}

/* the archive is a grid now, not a capped scroller */
.kr-issues .issues-scroll{max-height:none!important;overflow:visible!important;
  padding-right:0!important;margin-right:0!important;}
.kr-issues .issues-scroll-wrap::after{display:none!important;}
.issues-scroll-hint{display:none!important;}
.kr-issues .issues-grid{display:grid!important;
  grid-template-columns:repeat(auto-fill,minmax(330px,1fr))!important;gap:2px!important;}
.kr-issues .issue-featured-new,.kr-issues .issue-featured{margin-bottom:2px;}

/* the map has the full page now — let the pillars breathe */
.km-stats{grid-template-columns:repeat(5,1fr);}
.km-cats{padding:0 14px 14px;}
.km-topics{padding:6px 16px 20px;}
.km-c-head{padding:15px 18px;}
.km-p-head{padding:18px 24px;}
.km-p-name{font-size:25px;}

/* Cards are shorter in a grid than they were in the narrow scroll column, so
   the big ghost numeral now sits under the "no page yet" flag. Lift the text. */
.kr-issues .ic-soon-flag{position:relative;z-index:2;}
.kr-issues .ic-ghost-num{z-index:0;}

@media(max-width:1100px){
  .kr-topics.section{padding:72px 32px 56px!important;}
  .kr-issues .issues-inner{padding:64px 32px 72px!important;}
}
@media(max-width:600px){
  .kr-topics.section{padding:56px 20px 44px!important;}
  .kr-issues .issues-inner{padding:48px 20px 56px!important;}
}
"""

# append at the very end of the stylesheet so specificity ties break our way
anchor = "</style>"
assert src.count(anchor) >= 1
i = src.rindex(anchor)
src = src[:i] + CSS + src[i:]

# the height sync has nothing left to reconcile; keep the symbol so the
# accordion's existing calls stay valid
OLD_HEAD = "function syncIssuesScrollHeight(){"
j = src.index(OLD_HEAD)
k = src.index("\n}", j) + 2
src = src[:j] + ("function syncIssuesScrollHeight(){\n"
                 "  /* No-op: the archive is full width and uncapped, so there is no\n"
                 "     longer a column height to match. Kept because the knowledge-map\n"
                 "     accordion still calls it after each open. */\n"
                 "}\n") + src[k:]

SRC.write_text(src, encoding="utf-8")
print(f"index.html -> {len(src)} chars, knowledge row unstacked")
