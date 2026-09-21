#!/usr/bin/env python3
"""Where this site lives, in one place.

Named siteconf, not site: the builders put tools/ on sys.path, and a module
called site.py there would shadow Python's own stdlib `site`.

The public URL was hardcoded in five builders, which is four too many: a
change had to be made five times and any one of them could be missed
silently — a stale canonical or sitemap entry looks fine in the HTML and only
shows up as a search engine indexing the wrong host.

BASE is the canonical origin. Everything that emits an absolute URL —
canonical tags, OG/Twitter meta, sitemap.xml, feed.xml — imports it from here.

The site is served from two hosts:

  https://platform-ops-blog.vishal-abhinav.workers.dev/   <- canonical, public
  https://vishal-abhinav.github.io/Platform-ops-Newsletter/   <- the Pages origin

Both serve identical content, which is duplicate content as far as a search
engine is concerned. Pointing every canonical at ONE of them is what resolves
that; the other host then reads as a mirror rather than a competing copy.
"""

# ── where the site is served from ───────────────────────────────────────────
# One entry per host this site can be canonical at. Switching between them is
# changing ACTIVE below and rebuilding — nothing else, because every absolute
# URL in the repo is derived from whichever profile is active.
#
# Each profile carries its OWN Search Console token. Those are issued per
# property, not per site, so a single global token would silently be the wrong
# one the moment the origin changed — which reads as a broken deploy and is
# not. An empty token emits no verification tag at all, which is the correct
# state for a property that does not exist yet.
SITES = {
    "workers": {
        "base": "https://platform-ops-blog.vishal-abhinav.workers.dev/",
        "gsc": "bderTx4lj4QRZNCauyzfCdi3rV2LbGqO4NMazuHoa0Y",
        "note": "the Cloudflare Worker mirror — canonical today",
    },
    "platformops": {
        "base": "https://platformops.srivantechnologies.com/",
        "gsc": "Dsw5vFDfgmwABqWL4QXxsmxA8ZfH5kh2SrutfB10C6k",
        "note": "the custom subdomain, now bound to the Worker as a custom domain",
    },
}

# ── the active profile ──────────────────────────────────────────────────────
# Flip this ONLY once the new host actually resolves and serves the site.
# Pointing 93 canonicals at a host that 404s tells a search engine the real
# version of every page does not exist, which is worse than the wrong host.
#
# Flipped to platformops on 17 Sep 2026. The precondition above was checked
# first, not assumed: https://platformops.srivantechnologies.com/ was fetched
# live and returns 200 with the full site — it is the same Worker answering on
# a custom domain, so it serves identical bytes. Before the flip every page
# declared its canonical to be the workers.dev host, which meant that on the
# custom domain each page pointed search engines away from itself.
#
# The workers.dev host keeps serving until "workers_dev": false is set in
# wrangler.jsonc — that is a separate, deliberate step, taken only after these
# canonicals are confirmed live, so there is never a window where the old host
# is gone and the new canonicals have not landed.
ACTIVE = "platformops"

assert ACTIVE in SITES, f"ACTIVE={ACTIVE!r} is not a profile in SITES"

BASE = SITES[ACTIVE]["base"]

# The Pages origin the repo deploys to. Kept so the mirror can be named
# accurately where that matters; never used to build a canonical URL.
PAGES_ORIGIN = "https://vishal-abhinav.github.io/Platform-ops-Newsletter/"

# Every origin this site has ever been, or could be, served from. A page
# carrying any of these gets rewritten to BASE — which is what makes the
# switch work in BOTH directions rather than stranding pages on an old host.
KNOWN_ORIGINS = [PAGES_ORIGIN] + [s["base"] for s in SITES.values()]

assert BASE.endswith("/"), "BASE must end with a slash — URLs are built by concatenation"
assert all(o.endswith("/") for o in KNOWN_ORIGINS), "every origin must end with a slash"

# The bare host of the active origin, for prose that names it in running text
# rather than linking it. Derived, so the README and the colophon cannot go on
# advertising a host the site is no longer served from.
BASE_HOST = BASE.split("//", 1)[1].rstrip("/")

# ── Google Search Console ───────────────────────────────────────────────────
# Paste ONLY the token from the meta tag Search Console gives you — the value
# of content=, not the whole <meta> element. Empty means nothing is emitted,
# which is the right default: an empty verification tag on a live page is
# noise, and a wrong one is a failed verification you have to debug.
#
#   Search Console → Settings → Ownership verification → HTML tag
#   <meta name="google-site-verification" content="PASTE_THIS_PART" />
#
# Take it from the HTML TAG panel, nothing else. Search Console issues a
# DIFFERENT token per verification method, and the one shown as
#   google-site-verification=<token>
# is the DNS TXT record, not this. Pasting that one here verifies
# nothing: Google finds the tag, reads it, and rejects it as belonging
# to another method — which looks like a broken deploy and is not.
#
# It goes on the homepage only, which is what a URL-prefix property at the
# root is checked against. The tag has to be LIVE before you press Verify:
# build, commit, push, confirm it is actually being served, then verify.
#
# Every profile's token is emitted, not just ACTIVE's — deliberately. Right
# now every profile in SITES is the SAME Worker answering on multiple
# hostnames, so whichever URL Google actually fetches gets the identical
# homepage HTML back. A Search Console property for platformops needs its
# tag live on https://platformops.srivantechnologies.com/ *before* ACTIVE is
# ever flipped to it — waiting for the flip would mean verifying a property
# that is not allowed to be canonical yet just to prove it can be. Multiple
# google-site-verification meta tags on one page is explicitly supported by
# Google: each one verifies its own property independently, and a tag for a
# property you are not currently canonical for is inert, not wrong.
GOOGLE_SITE_VERIFICATION = SITES[ACTIVE]["gsc"]      # kept for anything reading the active token alone

GOOGLE_SITE_VERIFICATIONS = list(dict.fromkeys(     # de-duplicated, order preserved
    s["gsc"] for s in SITES.values() if s.get("gsc")
))

for _tok in GOOGLE_SITE_VERIFICATIONS:
    assert "<" not in _tok, (
        "a gsc token wants just the value, not the whole <meta> tag")


# ── files that are NOT pages ────────────────────────────────────────────────
# Five build stages walk ROOT.rglob("*.html") — build_nav, build_search,
# build_seo, build_canonical and verify — and each kept its own copy of this
# list, two of them as a bare string comparison. That was survivable with one
# entry. It stopped being survivable when Search Console's verification file
# arrived: it is a one-line text file that happens to end in .html, and every
# one of those stages would have injected a mega-menu, a search index and
# JSON-LD into it, leaving Google a file that no longer says what it must say.
#
# Google's verification files are always google<hex>.html, so the pattern is
# matched rather than the specific token — re-verifying later with a different
# file needs no code change.
import re as _re                                       # noqa: E402

SKIP_NAMES = set()
_GOOGLE_VERIFY = _re.compile(r"google[0-9a-f]{8,}\.html\Z")


def skip_page(name):
    """True for a file that ends in .html but is not one of our pages."""
    return name in SKIP_NAMES or bool(_GOOGLE_VERIFY.match(name))
