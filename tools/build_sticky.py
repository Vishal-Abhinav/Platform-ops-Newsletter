#!/usr/bin/env python3
"""Pin the archive beside the map.

With every pillar and category open, the map column runs to several thousand
pixels while the archive is capped at a screen. That left the right-hand side
empty for most of the scroll. Sticky the archive instead: it travels with you,
so there is no dead space and the issues stay one glance away wherever you are
in the map.

The panel is then sized to what is actually left of the viewport below the
archive's own header, measured at runtime rather than guessed.
"""
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
SRC = ROOT / "index.html"
src = SRC.read_text(encoding="utf-8")

CSS = """
/* ─── STICKY ARCHIVE ─── */
/* Last in the sheet so it wins the cascade. */
@media (min-width: 1101px) {
  /* NB: no align-items:start. Sticky needs its containing block taller than
     itself, and it is the default `stretch` that gives the grid item the full
     row height. align-items:start shrink-wraps it and sticky never moves. */
  .kr-issues.issues-bg{position:relative;}

  /* The whole archive column scrolls as one pinned pane. Capping the inner
     scroll box instead made the flex column squash the two featured cards
     down to their badges — one scroll area, no squashing, everything
     reachable. */
  .kr-issues .issues-inner{position:sticky;top:0;height:100vh;overflow-y:auto;
    padding:44px 64px 40px 40px!important;display:block!important;
    scrollbar-width:auto;scrollbar-gutter:stable;
    scrollbar-color:rgba(255,255,255,.34) rgba(255,255,255,.07);}
  .kr-issues .issues-inner::-webkit-scrollbar{width:10px;}
  .kr-issues .issues-inner::-webkit-scrollbar-track{background:rgba(255,255,255,.07);}
  .kr-issues .issues-inner::-webkit-scrollbar-thumb{background:rgba(255,255,255,.34);
    border-radius:5px;}
  .kr-issues .issues-inner::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.55);}

  /* the inner box is no longer the scroller */
  .kr-issues .issues-scroll{max-height:none!important;overflow:visible!important;
    padding-right:0!important;margin-right:0!important;}
  .kr-issues .issues-scroll-wrap::after{display:none!important;}
  .issues-scroll-hint{display:none!important;}

  .kr-issues .issues-inner > .section-tag{margin-bottom:12px;}
  .kr-issues .issues-inner > .section-title{font-size:clamp(32px,3.2vw,44px);margin-bottom:8px;}
  .kr-issues .issues-inner > .section-lead{font-size:15px;margin-bottom:22px;}
}
"""

anchor = "</style>"
i = src.rindex(anchor)
src = src[:i] + CSS + src[i:]

# Size the panel from the room actually left below the archive's header, and
# leave the featured cards out of the sticky calculation only if they fit.
OLD = """  // Measure the non-scrolling chrome from the gaps around the wrap, not from
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

NEW = """  // Nothing to size on desktop: the whole archive column is one pinned,
  // scrolling pane, so the inner box just grows to its content. Below the
  // breakpoint the columns stack and the stylesheet's own cap applies.
  scrollBox.style.maxHeight = '';"""

assert OLD in src, "scroll-sizing block not found"
src = src.replace(OLD, NEW, 1)

SRC.write_text(src, encoding="utf-8")
print(f"index.html -> {len(src)} chars, archive pinned")
