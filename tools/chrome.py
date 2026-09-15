#!/usr/bin/env python3
"""The site furniture: one top bar and one footer, for every page.

WHY THIS FILE EXISTS
--------------------
A scan of the 93 live pages found twenty-four different navigation bars. Not
twenty-four pillar variations — twenty-four different vocabularies. Some said
"Home", some said "← Newsletter", one said "← K8s Series", one still carried
labels ("Topics / Issues / Authors") from a homepage design that no longer
exists, and one page had no bar at all. LAB appeared on 17 of 93 pages, which
is why the practice terminal was hard to find. A reader moving between two
pages could not tell they were on the same site.

The same scan found seventy-one pages telling readers the newest issue was
#057 when it was #067, because the string was hardcoded in build_hubs.py
while build_kmap.py derived it properly for the homepage alone. That is the
whole argument for this module: furniture that is written out by hand in
four places drifts in four directions.

So: every generator imports nav() and footer() from here, and the issue
number comes off the register. There is no second copy to forget.

WHAT IS FIXED AND WHAT VARIES
-----------------------------
Fixed on every page: the PLATFORM OPS wordmark (home), the theme toggle, LAB,
SUBSCRIBE, and the three footer columns. Varies: the crumb, which names where
you are. That is the whole contract — if a page needs a different bar, the
answer is a crumb, not a different bar.
"""
import os
import pathlib as _pl
import sys

ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT / "tools"))

from build_feed import ISSUES                       # noqa: E402  the register

# ── the newest issue, derived ───────────────────────────────────────────────
# Sorted descending by number so [0] is the newest. Everything that wants to
# say "newest" asks here; nothing types a number.
_NEWEST = sorted(ISSUES, key=lambda i: -i[0])[0]
LATEST_NUM = f"{_NEWEST[0]:03d}"
LATEST_PATH = _NEWEST[1]
LATEST_TITLE = _NEWEST[2]

# Srivan Technologies' own site links out to this newsletter everywhere (the
# footer, a featured-work band on every page, a whole Writing page) — this
# newsletter never linked back. A reader who finishes an issue had no way to
# discover who wrote it or that there's a studio site at all. One line in the
# footer's existing Connect column closes that loop, same pattern as the
# GitHub Repo link right above it.
STUDIO = "https://srivantechnologies.com/"


# ── the theme control, in three pieces ──────────────────────────────────────
# The button, the script that reads the saved choice BEFORE first paint (so a
# dark reader never gets a white flash), and the click handler.
TOGGLE = ('<button class="tt" id="tt" type="button" aria-label="Toggle dark mode">'
          '<svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/>'
          '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2'
          'M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
          '<svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/>'
          '</svg></button>')

PREPAINT = ("<script>\n"
            "(function(){try{var t=localStorage.getItem('po-theme');\n"
            " if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}catch(e){}})();\n"
            "</script>")

TOGGLE_JS = """<script>
(function(){var b=document.getElementById('tt'); if(!b) return;
b.addEventListener('click',function(){
  var d=document.documentElement.getAttribute('data-theme')==='dark';
  if(d){document.documentElement.removeAttribute('data-theme');}
  else{document.documentElement.setAttribute('data-theme','dark');}
  try{localStorage.setItem('po-theme',d?'light':'dark');}catch(e){}
});})();
</script>"""

# ── the chrome's own stylesheet ─────────────────────────────────────────────
# Topic and hub pages get this through their linked stylesheet. The 25
# hand-written pages have no shared stylesheet, so build_legacy_chrome.py
# appends this block to their inline <style> instead. Keeping one copy here is
# the point: the bar cannot look different on those pages by accident.
#
# The semantic tokens come first. Every one of them was missing from at least
# one hand-written page, which is why those pages could not be themed: they
# defined --paper and --ink but nothing that says "the surface a card sits on".
TOKENS = """:root{--ink:#08090c;--paper:#f2f0eb;--smoke:#e4e0d8;--ash:#b8b2a7;--coal:#1c1f26;
 --cyan:#00c2d4;--amber:#f59e0b;--crimson:#e53935;--lime:#84cc16;--purple:#7c3aed;
 --page-bg:#f2f0eb;--panel-bg:#e4e0d8;--card-bg:#f8f7f4;--page-fg:#1c1f26;--heading-fg:#1c1f26;
 --muted:#6b6860;--line-1:rgba(0,0,0,.06);--line-2:rgba(0,0,0,.1);--line-3:rgba(0,0,0,.16);
 --wash:rgba(0,0,0,.04);--nav-bg:rgba(242,240,235,.9);--code-bg:#0d0f14;
 /* Accents AS TEXT. The brand colours are tuned to be seen as fills and
    borders; at 9-11px on paper, --lime and --cyan are close to illegible.
    The diagrams already carried a second set for exactly this and kept it
    private, so every page that wanted a coloured label reached for the fill
    colour instead. These are that set, promoted to tokens. */
 --cyan-t:#066c77;--lime-t:#3f6f0c;--amber-t:#8a5806;
 --purple-t:#5b21b6;--crimson-t:#a32b28;}
html[data-theme="dark"]{--page-bg:#0c0e12;--panel-bg:#14161c;--card-bg:#181b22;--page-fg:#e7e5df;
 --heading-fg:#eeece6;--muted:#9a978e;--line-1:rgba(255,255,255,.07);--line-2:rgba(255,255,255,.11);
 --line-3:rgba(255,255,255,.18);--wash:rgba(255,255,255,.05);--nav-bg:rgba(12,14,18,.9);
 --cyan-t:#4dd6e4;--lime-t:#a7e137;--amber-t:#f5b544;
 --purple-t:#b596f5;--crimson-t:#f07570;}"""

BAR_CSS = """nav{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:18px;padding:14px 40px;
 background:var(--nav-bg);backdrop-filter:blur(14px);border-bottom:1px solid var(--line-1);}
.nav-logo{display:flex;align-items:center;gap:9px;font-family:'Bebas Neue',sans-serif;font-size:19px;
 letter-spacing:2.5px;text-decoration:none;color:var(--heading-fg);flex-shrink:0;}
.nav-logo span{width:8px;height:8px;border-radius:50%;background:var(--crimson);}
/* nowrap + hidden: a long trail used to push the bar onto two or three lines,
   which made the header a different height on different pages. It truncates
   instead — the crumb is wayfinding, not content. */
.crumb{flex:1;min-width:0;display:flex;align-items:center;gap:8px;flex-wrap:nowrap;
 overflow:hidden;white-space:nowrap;
 font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
/* Segments keep their natural width and the container clips what does not
   fit. Letting them shrink instead gave 'H. / CA… / KU… / KUBERN…', which
   is a breadcrumb that has stopped telling you where you are. */
.crumb a,.crumb .cur,.crumb span{flex-shrink:0;}
.crumb a{text-decoration:none;color:var(--muted);}
.crumb a:hover{color:var(--crimson);}
.crumb .cur{color:var(--heading-fg);}
.nav-right{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.nav-lab{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.6px;
 text-transform:uppercase;text-decoration:none;color:var(--muted);
 border:1px solid var(--line-2);border-radius:3px;padding:5px 9px;
 transition:color .2s,border-color .2s,background .2s;white-space:nowrap;}
.nav-lab:hover{color:var(--crimson);border-color:var(--crimson);}
.nav-lab::after{content:' \\2197';font-size:9px;}
@media(max-width:560px){.nav-lab{padding:4px 7px;font-size:9px;}
  .nav-sub{display:none;}}
.tt{width:32px;height:32px;border:1px solid var(--line-2);background:transparent;border-radius:50%;
 cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);}
.tt:hover{color:var(--crimson);border-color:var(--crimson);}
.tt svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;}
html:not([data-theme="dark"]) .tt .moon,html[data-theme="dark"] .tt .sun{display:none;}
@media(max-width:760px){nav{padding:12px 18px;gap:12px;}.crumb{display:none;}}"""

FOOT_CSS = """footer{background:var(--coal);color:var(--paper);padding:52px 40px 26px;}
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
@media(max-width:560px){.f-cols{grid-template-columns:1fr 1fr;}}"""

CSS = TOKENS + "\n" + BAR_CSS + "\n" + FOOT_CSS


def nav(up="", crumb="", *, toggle="", lab=True, subscribe=True):
    """The top bar. `up` is the relative prefix back to the site root.

    `lab` and `subscribe` exist only for the Lab page itself, which should not
    link to itself. Everything else takes the defaults.
    """
    bits = [f'  <a href="{up}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>']
    if crumb:
        bits.append(f'  <div class="crumb">{crumb}</div>')
    right = [toggle]
    if lab:
        right.append(f'<a href="{up}terminal/index.html" class="nav-lab"'
                     f' target="_blank" rel="noopener">LAB</a>')
    if subscribe:
        right.append(f'<a href="{up}index.html#subscribe" class="nav-logo nav-sub"'
                     f' style="font-size:11px;letter-spacing:1.6px;'
                     f'font-family:\'DM Mono\',monospace">SUBSCRIBE</a>')
    bits.append(f'  <div class="nav-right">{"".join(right)}</div>')
    return "<nav>\n" + "\n".join(bits) + "\n</nav>"


def footer(up=""):
    """The footer. Same three columns everywhere, newest issue derived."""
    return f"""<footer>
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
          <a href="{up}{LATEST_PATH}">Newest — Issue #{LATEST_NUM}</a>
          <a href="{up}index.html#subscribe">Subscribe</a>
          <a href="{up}feed.xml">RSS Feed</a></div>
        <div><div class="f-col-t">Explore</div>
          <a href="{up}categories/index.html">All Categories</a>
          <a href="{up}index.html#topics">Knowledge Map</a>
          <a href="{up}categories/kubernetes-openshift-map/index.html">K8s &amp; OpenShift Topic Map</a>
          <a href="{up}terminal/index.html">Practice Terminal ↗</a>
          <a href="{up}colophon/index.html">Colophon</a></div>
        <div><div class="f-col-t">Connect</div>
          <a href="https://github.com/Vishal-Abhinav/Platform-ops-Newsletter" target="_blank">GitHub Repo ↗</a>
          <a href="{up}index.html#authors">About the Author</a>
          <a href="{STUDIO}" target="_blank" rel="noopener">Srivan Technologies ↗</a>
          <a href="#">Back to Top ↑</a></div>
      </div>
    </div>
    <div class="f-bot">
      <div>© 2026 Vishal Abhinav · Platform Ops — code MIT,
        <a href="{up}LICENSE">text &amp; diagrams CC BY-NC-ND 4.0</a></div>
      <div>Built for engineers, by an engineer.</div>
    </div>
  </div>
</footer>"""


if __name__ == "__main__":
    print(f"newest = #{LATEST_NUM}  {LATEST_TITLE}")
    print(f"         {LATEST_PATH}")
