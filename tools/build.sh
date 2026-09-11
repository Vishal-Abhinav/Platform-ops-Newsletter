#!/usr/bin/env bash
# Regenerate every derived file in the repo from tools/taxonomy.py.
#
#   ./tools/build.sh
#
# Everything below is DERIVED. Edit the source in tools/, never the output:
#   index.html      <- index.base.html + build_kmap/features/wire/library
#   README.md       <- README.base.md  + build_readme/library
#   categories/     <- build_hubs      (33 hubs + index + hub.css)
#   Foundation/     <- build_foundation (topic pages + topic.css)
#   Commands/       <- build_commands   (command references + commands.css)
#   OpenShift/      <- build_openshift  (deep-dives + topic.css)
#   feed.xml        <- build_feed
#   LinkedIn column <- tools/linkedin_posts.py (hand-kept list of post URLs)
#   assets/megamenu.* <- build_nav    (nav data, styles, behaviour)
#   sitemap.xml     <- verify.py
#   canonical URLs  <- tools/siteconf.py (BASE) via build_canonical.py
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PO_ROOT="$ROOT"
cd "$ROOT"

say() { printf '\n\033[1m── %s\033[0m\n' "$*"; }

say "reset the two generated files to their bases"
cp tools/index.base.html index.html
cp tools/README.base.md  README.md

say "index.html"
python3 tools/build_kmap.py          # knowledge map, from the taxonomy
python3 tools/build_features.py      # topic requests, analytics, RSS link
python3 tools/build_wire.py          # category hub links, nav, licence line

say "README.md"
python3 tools/build_readme.py        # knowledge map section

say "reference library (README only now)"
python3 tools/build_library.py

say "sticky archive"
python3 tools/build_sticky.py

say "author section (profile + LinkedIn)"
python3 tools/build_author.py

say "category hubs"
python3 tools/build_hubs.py

say "topic pages"
python3 tools/build_foundation.py fnd_a fnd_b

say "OpenShift deep-dives"
python3 tools/build_openshift.py ocp_a

say "command references"
python3 tools/build_commands.py

say "feed"
python3 tools/build_feed.py

say "mega-menu (assets + wiring into every page)"
python3 tools/build_nav.py

say "global search (index + wiring into every page)"
python3 tools/build_search.py

say "canonical origin (every page -> siteconf.BASE)"
python3 tools/build_canonical.py

say "verify + sitemap"
python3 tools/verify.py

say "done — review 'git status', then commit"
