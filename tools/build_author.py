#!/usr/bin/env python3
"""Author section: profile on the left, LinkedIn on the right.

The section used to be a 1fr 2fr grid — heading on the left, one wide author
card on the right. This splits it: the heading runs full width across the top,
then the author card takes the left column and a LinkedIn column takes the
right.

The LinkedIn column renders whatever post URLs tools/linkedin_posts.py lists.
That file is hand-kept on purpose: LinkedIn publishes no public feed for a
personal profile, so a static page has nothing to poll. With the list empty the
column falls back to a profile card and a follow CTA, so the layout is complete
either way and no third-party script loads until there is a post to show.
"""
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT / "tools"))

from linkedin_posts import POSTS, PROFILE, SHOW      # noqa: E402
from taxonomy import PILLARS                         # noqa: E402

SRC = ROOT / "index.html"
src = SRC.read_text(encoding="utf-8")

LI_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="3" '
          'fill="#0A66C2"/><path fill="#fff" d="M7.1 9.3H4.6V19h2.5V9.3zM5.85 8.2a1.45 1.45 0 '
          '1 0 0-2.9 1.45 1.45 0 0 0 0 2.9zM19.4 19h-2.5v-4.7c0-1.12-.02-2.56-1.56-2.56-1.56 '
          '0-1.8 1.22-1.8 2.48V19H11V9.3h2.4v1.33h.04c.33-.63 1.15-1.3 2.37-1.3 2.54 0 3.6 '
          '1.67 3.6 3.84V19z"/></svg>')


DEFAULT_H = 560          # only used when a bare URL was pasted


def parse(entry):
    """Read one POSTS entry — a whole embed snippet, or a bare post URL.

    Returns (src, height) or None.

    The URN TYPE is carried through rather than assumed. LinkedIn uses
    urn:li:ugcPost:, urn:li:share: and urn:li:activity: for posts created
    different ways, and the embed renders an empty box if you name the wrong
    one — so a pasted snippet is used verbatim, and only a bare URL falls back
    to a guess.
    """
    m = re.search(r'src="([^"]*/embed/feed/update/[^"]+)"', entry)
    if m:                                   # a full <iframe …> snippet
        h = re.search(r'height="(\d+)"', entry)
        return m.group(1), int(h.group(1)) if h else DEFAULT_H

    m = re.search(r"urn:li:(\w+):(\d+)", entry)      # a urn-shaped URL
    if m:
        return (f"https://www.linkedin.com/embed/feed/update/"
                f"urn:li:{m.group(1)}:{m.group(2)}", DEFAULT_H)

    m = re.search(r"(\d{19})", entry)                 # …-activity-<id>-XXXX
    if m:
        return (f"https://www.linkedin.com/embed/feed/update/"
                f"urn:li:share:{m.group(1)}", DEFAULT_H)
    return None


embeds = [e for e in (parse(x) for x in POSTS[:SHOW]) if e]

if embeds:
    # width 504 is what LinkedIn measured those heights against; hold the
    # column to it on desktop so nothing reflows and nothing clips. The
    # narrow fallback is handled in CSS, where the height gets slack.
    feed = "\n".join(
        f'      <iframe class="li-embed" style="--h:{h}px" src="{src}"\n'
        f'        loading="lazy" frameborder="0" allowfullscreen=""\n'
        f'        title="LinkedIn post"></iframe>'
        for src, h in embeds)
    feed_note = f"{len(embeds)} most recent"
else:
    # No posts configured. A real panel, not an empty box: what the column is
    # for, the pillars carrying the most published work, and the one link that
    # always works. Counted from the taxonomy rather than asserted.
    live = sorted(
        ((p, sum(1 for _, _, ts in cats for t in ts if t[1] == "L")) for p, cats in PILLARS),
        key=lambda x: -x[1])
    tags = "".join(f'<span class="li-tag">{p}</span>' for p, n in live[:5] if n)
    feed = f"""      <div class="li-empty">
        <div class="li-av">{LI_SVG}</div>
        <div class="li-who">
          <b>Vishal Abhinav</b>
          <span>Platform Ops Engineer · Kubernetes · SRE</span>
        </div>
        <p class="li-say">Posts land here as they go up — runbooks, postmortems and
          the odd 2 AM lesson. Follow along on LinkedIn in the meantime.</p>
        <div class="li-tags">{tags}</div>
      </div>"""
    feed_note = "follow for updates"

grid_cls = " has-embeds" if embeds else ""
feed_cls = " scrolls" if embeds else ""

RIGHT = f"""    <aside class="au-right">
      <div class="li-bar">
        <span class="li-mark">{LI_SVG}</span>
        <span class="li-title">Latest on LinkedIn</span>
        <span class="li-note">{feed_note}</span>
      </div>
      <div class="li-feed{feed_cls}">
{feed}
      </div>
      <a class="li-cta" href="{PROFILE}" target="_blank" rel="noopener">
        Follow on LinkedIn
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
        ><path d="M5 12h14M13 6l6 6-6 6"/></svg>
      </a>
    </aside>"""

# ── keep the author card exactly as it is; only its container changes ────────
start = src.index('<!-- ═══════════ AUTHORS ═══════════ -->')
end = src.index('<!-- ═══════════ SUBSCRIBE ═══════════ -->')
old = src[start:end]

m = re.search(r'( *)<div class="author-card">.*?\n\1</div>\n', old, re.S)
assert m, "author card not found"
card = m.group(0).rstrip("\n")

lead = re.search(r'<p class="section-lead"[^>]*>(.*?)</p>', old, re.S).group(1).strip()

NEW = f"""<!-- ═══════════ AUTHORS ═══════════ -->
<div class="authors-section" id="authors">
  <div class="authors-inner">
    <div class="au-head reveal">
      <div class="section-tag">Behind the Newsletter</div>
      <h2 class="section-title">THE AUTHOR</h2>
      <p class="section-lead" style="margin-bottom:0">{lead}</p>
    </div>
    <div class="au-grid reveal{grid_cls}">
    <div class="au-left">
{card}
    </div>
{RIGHT}
    </div>
  </div>
</div>

"""

src = src[:start] + NEW + src[end:]

CSS = """
/* ─── AUTHOR: PROFILE LEFT, LINKEDIN RIGHT ─── */
/* Last in the sheet, so it wins over the 1fr 2fr grid defined above. */
.authors-inner{display:block!important;max-width:1240px;}
.au-head{margin-bottom:40px;}
/* stretch, not start: the LinkedIn panel is shorter than the profile card
   until real posts are embedded, and `start` left a hole under it. */
.au-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);
  gap:40px;align-items:stretch;}
/* 504px is the width LinkedIn measured each embed's height against. Hold the
   column to it and the posts render exactly as LinkedIn laid them out —
   narrower and the text reflows taller than the height attribute allows, so
   the last lines get cut off inside the iframe. */
/* 520, not 504: the feed's own scrollbar eats ~10px, and the iframe has to
   END UP at 504 for the heights to be right. Any slack shows as an even
   margin either side of the post, which is invisible. */
@media (min-width:1001px){ .au-grid.has-embeds{grid-template-columns:minmax(0,1fr) 520px;} }
/* start, not stretch, once there are embeds. Stretch exists to close the hole
   under a SHORT LinkedIn panel; with posts in it the panel carries its own
   weight, and stretching then just padded the profile card with 180px of
   empty background. Two columns of near-equal height, each ending where its
   content does. */
.au-grid.has-embeds{align-items:start;}
.au-grid.has-embeds .author-card{height:auto;}
.au-left .author-card{height:100%;}

.au-right{display:flex;flex-direction:column;gap:0;background:var(--card-bg);
  border-radius:4px;box-shadow:0 2px 20px rgba(0,0,0,.06);overflow:hidden;}
.li-bar{display:flex;align-items:center;gap:10px;padding:16px 20px;
  border-bottom:1px solid var(--hairline-2);}
.li-mark svg{display:block;width:20px;height:20px;border-radius:3px;}
.li-title{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1.6px;
  text-transform:uppercase;color:var(--heading-fg);}
.li-note{margin-left:auto;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted);}

/* card-bg, not a hairline gap colour: with one empty state centred in a tall
   column the gap became two grey bands rather than a separator. */
.li-feed{display:flex;flex-direction:column;justify-content:center;
  flex:1;background:var(--card-bg);}
/* flex:0 0 auto — the feed is a flex COLUMN, so its children shrink along the
   main axis by default. The three iframes total ~3,570px and were being
   squashed to exactly fill the 600px box (150 + 261 + 189), which is not a
   scroll, it is three slivers. */
.li-embed{display:block;width:504px;max-width:100%;margin-inline:auto;
  border:0;background:var(--card-bg);height:var(--h,560px);flex:0 0 auto;}
.li-embed + .li-embed{border-top:1px solid var(--hairline-2);}

/* Three posts run to ~3,600px. Left to grow, the author section would be
   taller than the rest of the page put together, so the feed scrolls inside
   itself — the same move the archive makes. */
/* 420 puts the column at 53 + 420 + 46 = 519px, within a few pixels of the
   profile card's natural 515 — so the two read as a matched pair rather than
   one running 180px past the other. */
.li-feed.scrolls{justify-content:flex-start;overflow-y:auto;max-height:420px;
  scrollbar-width:thin;scrollbar-gutter:stable;}
.li-feed.scrolls::-webkit-scrollbar{width:8px;}
.li-feed.scrolls::-webkit-scrollbar-track{background:var(--wash-1);}
.li-feed.scrolls::-webkit-scrollbar-thumb{background:var(--hairline-5);border-radius:4px;}
@media (max-width:1000px){ .li-feed.scrolls{max-height:70vh;} }
/* Only once the column is genuinely narrower than 504px does the text reflow
   longer than the measured height — and only then does the slack belong.
   Applying it at 1000px padded the stacked-but-wide layout with blank card. */
@media (max-width:560px){ .li-embed{height:calc(var(--h,560px) * 1.3);} }

.li-empty{background:var(--card-bg);padding:28px 20px;text-align:center;flex:0 0 auto;}
.li-av{width:44px;height:44px;margin:0 auto 12px;}
.li-av svg{display:block;width:44px;height:44px;border-radius:6px;}
.li-who b{display:block;font-size:15px;font-weight:700;color:var(--heading-fg);}
.li-who span{display:block;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.1px;
  text-transform:uppercase;color:var(--muted);margin-top:4px;}
.li-say{font-size:13px;line-height:1.65;color:var(--muted);margin:14px auto 0;max-width:36ch;}
.li-tags{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;
  margin-top:18px;padding-top:18px;border-top:1px solid var(--hairline-2);}
.li-tag{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1px;
  text-transform:uppercase;color:var(--muted);background:var(--wash-1);
  border:1px solid var(--hairline-3);border-radius:14px;padding:4px 10px;}

.li-cta{display:flex;align-items:center;justify-content:center;gap:8px;
  padding:14px;text-decoration:none;background:#0A66C2;color:#fff;
  font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1.6px;text-transform:uppercase;
  transition:background .18s;}
.li-cta:hover{background:#004182;}
.li-cta svg{transition:transform .18s;}
.li-cta:hover svg{transform:translateX(3px);}

@media (max-width:1000px){
  .au-grid{grid-template-columns:1fr;gap:28px;}
  .au-head{margin-bottom:32px;}
}
"""

i = src.rindex("</style>")
src = src[:i] + CSS + src[i:]

SRC.write_text(src, encoding="utf-8")
print(f"index.html -> {len(src)} chars, author split "
      f"({len(embeds)} LinkedIn embed{'' if len(embeds) == 1 else 's'})")
