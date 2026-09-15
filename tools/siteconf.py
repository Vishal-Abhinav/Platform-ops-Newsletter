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

# Canonical origin. Must end with a slash.
BASE = "https://platform-ops-blog.vishal-abhinav.workers.dev/"

# The Pages origin the repo deploys to. Kept so the mirror can be named
# accurately where that matters; never used to build a canonical URL.
PAGES_ORIGIN = "https://vishal-abhinav.github.io/Platform-ops-Newsletter/"

assert BASE.endswith("/"), "BASE must end with a slash — URLs are built by concatenation"

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
GOOGLE_SITE_VERIFICATION = "bderTx4lj4QRZNCauyzfCdi3rV2LbGqO4NMazuHoa0Y"

assert "<" not in GOOGLE_SITE_VERIFICATION, (
    "GOOGLE_SITE_VERIFICATION wants just the token, not the whole <meta> tag")


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

SKIP_NAMES = {"kit-template.html"}
_GOOGLE_VERIFY = _re.compile(r"google[0-9a-f]{8,}\.html\Z")


def skip_page(name):
    """True for a file that ends in .html but is not one of our pages."""
    return name in SKIP_NAMES or bool(_GOOGLE_VERIFY.match(name))
