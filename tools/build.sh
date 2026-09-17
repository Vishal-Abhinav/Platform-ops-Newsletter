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
#   categories/kubernetes/, categories/openshift/ <- build_hub_topicmap also appends the
#     reader's list (split 1-24 / 25-46) onto the end of each hub page, idempotently
#   categories/kubernetes-openshift-map/topics/ <- build_topic_pages, one honest page per
#     checklist item that isn't Live yet (stale ones removed when an item goes Live)
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
#
# WHERE THINGS LIVE
# -----------------
#   tools/     the build system            — source, never published
#   content/   the 25 hand-written pages   — source, never mutated
#   static/    files copied verbatim       — icons, OG cards, LICENSE, NOTICE
#   dist/      everything this script makes — THE ONLY THING DEPLOYED
#
# The output directory is the point. The deploy used to publish the whole repo
# filtered by a deny-list in .assetsignore, which meant anything new was
# published BY DEFAULT — that is how tools/ (every build script, the command
# corpus, siteconf.py with both Search Console tokens) and a ~4,700-file
# Mermaid install ended up fetchable on the public web. Publishing from dist/
# inverts that: only what this script deliberately wrote can ship, so a leak
# needs a mistake here rather than merely an omission somewhere else.
#
# The second gain is that content/ stops being mutated in place. The 25
# hand-written pages used to be both source and output — build_legacy_chrome
# and build_seo rewrote them where they sat, which is exactly why build_seo's
# trailing-newline bug accumulated a blank line on those 25 files and on no
# others: every other page is wiped and regenerated each run, so the damage
# never had anywhere to collect. Now they are copied into dist/ and mutated
# there, and the originals stay pristine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist"
export PO_ROOT="$OUT"
cd "$ROOT"

say() { printf '\n\033[1m── %s\033[0m\n' "$*"; }

say "seed the output directory"
# Rebuilt from empty every run, so a file that stops being generated also stops
# being deployed. Under the old layout a renamed or dropped page lingered in
# the repo — and therefore on the site — until somebody noticed.
rm -rf "$OUT"
mkdir -p "$OUT"
cp -R content/. "$OUT"/
cp -R static/.  "$OUT"/
printf '  seeded %s files from content/ + static/\n' \
  "$(find "$OUT" -type f | wc -l | tr -d ' ')"

say "reset the two generated files to their bases"
cp tools/index.base.html "$OUT/index.html"
cp tools/README.base.md  "$OUT/README.md"

say "index.html"
python3 tools/build_kmap.py          # knowledge map, from the taxonomy
python3 tools/build_features.py      # topic requests, analytics, RSS link
python3 tools/build_wire.py          # category hub links, nav, licence line

say "sticky archive"
python3 tools/build_sticky.py

say "author section (profile + LinkedIn)"
python3 tools/build_author.py

# ── ordering rule for everything below ─────────────────────────────────────
# A stage that COUNTS or CLASSIFIES against the filesystem must run after the
# stages that write what it counts. That sounds obvious; it was not true here
# until dist/ made it checkable. With the repo as its own output directory,
# build_readme counted last build's pages, build_hubs classified against last
# build's deep-dives and build_colophon counted a site that was still half
# written. Every one of those numbers was a build behind, and a clean build
# produced different output from an incremental one — the definition of an
# unreproducible build.
#
# So the sequence is now: content first, aggregation second.
#
# build_hubs is the one genuine cycle and it runs TWICE, deliberately. It
# produces categories/hub.css, which build_legacy_dg reads, so it has to come
# early; but it also prints the reader-checklist counts on each hub, and those
# are only right once the deep-dives and command references it classifies
# against exist. One pass cannot satisfy both. The second run regenerates the
# hub pages from scratch with correct numbers, and build_hub_topicmap folds
# its section in afterwards — so the order below is load-bearing, not
# cosmetic. Moving build_hub_topicmap above the second build_hubs would
# silently discard its work.

say "category hubs — pass 1 (structure + hub.css, which build_legacy_dg needs)"
python3 tools/build_hubs.py

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

say "category hubs — pass 2 (now the checklist counts have evidence to read)"
python3 tools/build_hubs.py

# ── the reader checklist, and why it runs HERE ──────────────────────────────
# These three used to sit before the deep-dives, the command references and
# the legacy pages. That only worked because the output directory was the repo
# itself, so build_topicmap read LAST BUILD'S copies of the pages it classifies
# against — the build was never reproducible from empty, and nobody could tell,
# because nobody ever built from empty.
#
# Wiping dist/ each run made it visible immediately: 33 checklist items lost
# their evidence and dropped from Live to Planned, because the pages proving
# they were covered had not been generated yet. classify() reads the real
# rendered text of each group's HOME pages, so every stage that writes one has
# to have run first — the deep-dives, the command references, and the legacy
# chrome/diagram passes that add text to the hand-written pages.
say "Kubernetes + OpenShift complete topic map"
python3 tools/build_topicmap.py

say "folding the topic list into the Kubernetes and OpenShift hub pages"
python3 tools/build_hub_topicmap.py

say "a page for every checklist item that isn't live yet"
python3 tools/build_topic_pages.py

say "practice terminal"
python3 tools/build_terminal.py

say "feed"
python3 tools/build_feed.py

# ── aggregation: every stage below counts the finished site ────────────────
say "colophon"
python3 tools/build_colophon.py      # counts pages + reads build.sh's own stage list

#   (README moved below build_search — it quotes the search index size)

say "mega-menu (assets + wiring into every page)"
python3 tools/build_nav.py

say "global search (index + wiring into every page)"
python3 tools/build_search.py

# README last of the aggregators: it quotes the page count, the category count
# AND the size of the search index, so it cannot be written until search.js
# exists. It used to run fourth, quoting the previous build's 2067 entries.
say "README.md"
python3 tools/build_readme.py

say "reference library (README only now)"
python3 tools/build_library.py

say "structured data (JSON-LD + article dates)"
python3 tools/build_seo.py

say "canonical origin (every page -> siteconf.BASE)"
python3 tools/build_canonical.py

say "verify + sitemap"
python3 tools/verify.py

say "done — review 'git status', then commit"
