#!/usr/bin/env python3
"""Emit dist/_headers — the security response headers Cloudflare serves.

WHY A GENERATED FILE
--------------------
A hand-written header file goes stale the moment a page starts loading
something new, and the failure is silent in the worst direction: either the
policy blocks something the site needs, or it quietly permits something it
shouldn't. So this stage reads the built site and derives what it finds —
the external origins actually referenced, the inline scripts actually
present — and refuses to run if it meets something it doesn't recognise.

WHAT IS ENFORCED TODAY, AND WHAT IS NOT
---------------------------------------
Enforced now, because none of it can break a page that behaves:

  frame-ancestors 'none'   this site is never framed, so clickjacking is out
  base-uri 'none'          an injected <base> can silently repoint every
                           relative URL on the page; nothing here needs one
  object-src 'none'        no <object>/<embed> anywhere; plugin content is a
                           classic XSS vector and this closes it outright
  form-action 'self'       the one <form> posts nowhere external

NOT enforced yet: script-src and style-src. The honest reason is that the
site currently has 306 inline onclick= handlers and 23 distinct inline
<script> blocks. A script-src that allowed those would need 'unsafe-inline',
and 'unsafe-inline' makes script-src worth approximately nothing against
XSS — it would look like protection on a report while providing none. A
CSP that lies about its own strength is worse than no CSP, so this file
ships the directives that are real and leaves a marked gap where the work
is, rather than filling it with a value that reads well.

Closing that gap is mechanical, not hard: the 306 handlers are only three
functions (toggleCard, toggleTerm, switchLevel) and become three delegated
listeners; the 23 inline blocks move into files. Then script-src becomes
'self' plus the analytics origin, with no exceptions at all. See the
HARDENING NOTES at the bottom.

THE OTHER HEADERS
-----------------
HSTS, nosniff, Referrer-Policy, Permissions-Policy and COOP are all
unconditional wins for a static content site and carry no breakage risk.
"""
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

OUT = ROOT / "_headers"

# ── the origins this site is allowed to talk to ─────────────────────────────
# Every entry is here because a built page references it. The audit below
# fails the build if a page starts referencing something that is not.
ALLOWED = {
    "gc.zgo.at":        "GoatCounter analytics (count.js + its beacon)",
    "www.linkedin.com": "the two post embeds on the homepage author section",
}
# fonts.googleapis.com and fonts.gstatic.com used to be here. The typefaces are
# served from this origin now, so there is no font exception to make — and the
# audit below proved it rather than being told: it walks the built pages and
# found nothing fetching from either host.

# There is deliberately no allow-list of "link-only" hosts here any more.
#
# There was one, holding about thirty domains this site links to, and it did
# real damage: it exempted by HOSTNAME, while `seen` below only ever collects
# hosts the browser actually FETCHES. So a host that was both — linked in the
# prose AND loaded as a resource — was waved through as harmless. That is
# precisely what happened with www.linkedin.com: two <iframe> embeds on the
# homepage, fetched by every visitor, invisible to this audit because the same
# domain also appears as an ordinary link. Found by watching a real browser's
# request log, not by reading this file.
#
# The rule now is simply: if it is fetched, it must be in ALLOWED.

# ── audit: does the built site load anything we have not accounted for? ─────
# Only things the BROWSER FETCHES count, and that distinction is the whole
# difficulty. An <a href> is a place the reader may choose to go; a <link
# rel="canonical"> is a statement to a crawler; <link rel="alternate"> names
# the feed. None of the three causes a request, so none belongs in a CSP.
#
# The first draft of this matched every <link href> and consequently reported
# the canonical host as an origin the site "fetches from". It passed only
# because canonicals point at this same host — so the bug was invisible
# exactly while it did no harm, and would have surfaced the first time the
# canonical origin differed from the serving one. Match on rel instead.
SRC = re.compile(
    r'<(?:script|img|iframe|source|video|audio|embed)\b[^>]*\bsrc="([^"]+)"', re.I)
LINK = re.compile(r'<link\b([^>]*)>', re.I)
CSS_URL = re.compile(r"url\(['\"]?(https?://[^'\")]+)", re.I)
# rel values that make the browser go and get something
FETCHING_REL = {"stylesheet", "icon", "apple-touch-icon", "preload",
                "prefetch", "manifest", "mask-icon"}

seen = {}


def note(url, f):
    if url.startswith(("http://", "https://")):
        seen.setdefault(url.split("/")[2], f.relative_to(ROOT).as_posix())


for f in ROOT.rglob("*.html"):
    text = f.read_text(encoding="utf-8", errors="replace")
    for m in SRC.finditer(text):
        note(m.group(1), f)
    for m in CSS_URL.finditer(text):
        note(m.group(1), f)
    for m in LINK.finditer(text):
        attrs = m.group(1)
        rel = re.search(r'\brel="([^"]+)"', attrs, re.I)
        href = re.search(r'\bhref="([^"]+)"', attrs, re.I)
        if rel and href and (set(rel.group(1).lower().split()) & FETCHING_REL):
            note(href.group(1), f)
    # The analytics loader assembles its <script src> in JavaScript, so none of
    # the patterns above can see it. Catch it the way it is actually written.
    for host in re.findall(r"src\s*=\s*'https://([a-z0-9.-]+)/", text):
        seen.setdefault(host, f.relative_to(ROOT).as_posix())

unknown = {h: p for h, p in seen.items() if h not in ALLOWED}
assert not unknown, (
    "build_headers: the built site fetches from origins this policy does not\n"
    "cover. Either add them to ALLOWED (and to the CSP below), or find out why\n"
    "a page started loading from them:\n"
    + "\n".join(f"    {h:34s} first seen in {p}" for h, p in sorted(unknown.items())))

used = sorted(h for h in ALLOWED if h in seen)

# ── the policy ──────────────────────────────────────────────────────────────
# One directive per line for review; joined with '; ' on the way out.
CSP = [
    # NO default-src. This is the load-bearing decision in this file and it is
    # the opposite of what looks right.
    #
    # default-src is not a baseline, it is a FALLBACK: every fetch directive
    # that is absent inherits it. "default-src 'self'" with script-src absent
    # therefore means script-src 'self' — which blocks every inline <script>
    # and all 306 onclick= handlers on this site. The theme toggle, the
    # mega-menu, the search box and every expandable card stop working, on
    # all 879 pages, and the only symptom is console noise most readers never
    # open. This exact line was in the first draft of this file and a render
    # test caught it.
    #
    # The two ways out are to add script-src with 'unsafe-inline' — which
    # would be a script-src worth nothing, dressed as protection — or to not
    # claim the directive until the inline scripts are gone. This file does
    # the second. Everything listed below is a real restriction that the
    # site genuinely operates within; nothing here is decorative.
    "font-src 'self'",
    # Declared rather than omitted, and that matters: with no default-src, an
    # absent frame-src means frames are UNRESTRICTED. Naming the one embed
    # origin turns "anything may be framed here" into "these two LinkedIn
    # posts may".
    "frame-src 'self' https://www.linkedin.com",
    "img-src 'self' data: https://gc.zgo.at",
    "connect-src 'self' https://gc.zgo.at",
    "frame-ancestors 'none'",
    "base-uri 'none'",
    "object-src 'none'",
    "form-action 'self'",
    "upgrade-insecure-requests",
]

HEADERS = [
    ("Content-Security-Policy", "; ".join(CSP)),

    # 2 years, subdomains included. srivantechnologies.com and this host are
    # both HTTPS-only already, so nothing is cut off by asserting it.
    ("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"),

    # Stops a browser second-guessing a Content-Type. Without it, a file the
    # server calls text/plain can be executed as script if it looks like one.
    ("X-Content-Type-Options", "nosniff"),

    # Send the full URL to ourselves, origin-only cross-site. A reader's path
    # through this site is not other sites' business.
    ("Referrer-Policy", "strict-origin-when-cross-origin"),

    # frame-ancestors above is the modern control; this is the same statement
    # for browsers that predate it.
    ("X-Frame-Options", "DENY"),

    # Nothing here wants a camera, a microphone or a location, so decline them
    # before anything embedded can ask.
    ("Permissions-Policy",
     "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
     "magnetometer=(), microphone=(), payment=(), usb=()"),

    ("Cross-Origin-Opener-Policy", "same-origin"),

    # Explicitly OFF. The legacy XSS auditor introduced vulnerabilities of its
    # own and is gone from every current browser; '1; mode=block' is cargo cult.
    ("X-XSS-Protection", "0"),
]

BODY = "\n".join(f"  {k}: {v}" for k, v in HEADERS)

TEXT = f"""# GENERATED by tools/build_headers.py — do not edit.
#
# Origins this site is permitted to load from, each verified present in the
# build that produced this file:
{chr(10).join(f'#   {h:24s} {ALLOWED[h]}' for h in used)}
#
# The build fails if a page starts fetching from anywhere else.

/*
{BODY}

# Long-lived, content-addressed or rarely-changing assets.
/assets/*
  Cache-Control: public, max-age=604800

/favicon.ico
  Cache-Control: public, max-age=604800
"""

OUT.write_text(TEXT, encoding="utf-8")
print(f"  _headers -> {len(HEADERS)} headers, "
      f"{len(used)} external origin(s) allowed: {', '.join(used)}")

# ════════════════════════════════════════════════════════════════════════════
# HARDENING NOTES — what is left, and why it is not done here
#
# 1. script-src. Blocked on 306 inline onclick= handlers, which are only three
#    functions (toggleCard 132, toggleTerm 80, switchLevel 54 variants). Three
#    delegated listeners replace all of them. Then the 23 distinct inline
#    <script> blocks move into /assets/, and script-src becomes:
#        script-src 'self' https://gc.zgo.at
#    with no 'unsafe-inline' and no hash list to drift.
#
# 2. style-src. Blocked on inline <style> blocks and style="" attributes.
#    Lower severity than script — style injection can deface and can exfiltrate
#    via crafted selectors, but cannot execute. Worth doing after script-src.
#
# 3. DONE — the four families are self-hosted. Both Google origins are gone
#    from the policy, no reader's IP reaches a third party to render a page,
#    and the render tests run at full precision everywhere.
# ════════════════════════════════════════════════════════════════════════════
