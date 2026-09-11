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
