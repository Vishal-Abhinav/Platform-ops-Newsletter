#!/usr/bin/env bash
# Regenerate every derived file in the repo from tools/taxonomy.py.
#
#   ./tools/build.sh
#
# Everything below is DERIVED. Edit the source in tools/, never the output:
#   index.html      <- index.base.html + build_kmap/features/wire/library
#   README.md       <- README.base.md  + build_readme/library
#   categories/     <- build_hubs      (33 hubs + index + hub.css)
#   categories/kubernetes-openshift-map/ <- build_topicmap (46-group reader topic list, live/pipe/planned)
#   Foundation/     <- build_foundation (topic pages + topic.css)
#   Commands/       <- build_commands   (command references + commands.css)
#   OpenShift/      <- build_openshift  (deep-dives + topic.css)
#   Kubernetes/     <- build_k8s        (K8s + Service Mesh deep-dives)
#   3 legacy pages  <- build_legacy_dg  (injects a .dg diagram, idempotent)
#   25 hand-written <- build_legacy_chrome (one nav, one footer, theme toggle)
#   colophon/       <- build_colophon   (how the site is built; SVG from make_arch_svg)
#   terminal/       <- build_terminal   (simulated shell; FS + exercises in terminal_fs)
#   feed.xml        <- build_feed
#   LinkedIn column <- tools/linkedin_posts.py (hand-kept list of post URLs)
#   assets/megamenu.* <- build_nav    (nav data, styles, behaviour)
#   sitemap.xml     <- verify.py
#   canonical URLs  <- tools/siteconf.py (BASE) via build_canonical.py
#   JSON-LD         <- build_seo       (schema.org, from each page + build_feed)
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

say "Kubernetes + OpenShift complete topic map"
python3 tools/build_topicmap.py

say "topic pages"
python3 tools/build_foundation.py fnd_a fnd_b

say "OpenShift deep-dives"
python3 tools/build_openshift.py ocp_a ocp_b ocp_c

say "Kubernetes + Service Mesh deep-dives"
python3 tools/build_k8s.py k8s_a k8s_b mesh_a

say "command references"
python3 tools/build_commands.py

say "diagrams for the hand-written pages"
python3 tools/build_legacy_dg.py

say "shared chrome on the hand-written pages"
python3 tools/build_legacy_chrome.py

say "colophon"
python3 tools/build_colophon.py

say "practice terminal"
python3 tools/build_terminal.py

say "feed"
python3 tools/build_feed.py

say "mega-menu (assets + wiring into every page)"
python3 tools/build_nav.py

say "global search (index + wiring into every page)"
python3 tools/build_search.py

say "structured data (JSON-LD + article dates)"
python3 tools/build_seo.py

say "canonical origin (every page -> siteconf.BASE)"
python3 tools/build_canonical.py

say "verify + sitemap"
python3 tools/verify.py

say "done — review 'git status', then commit"
