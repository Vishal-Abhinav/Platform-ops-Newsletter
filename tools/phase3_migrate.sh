#!/usr/bin/env bash
# One-time repo reorganisation for the dist/ build. Run once, then delete.
#
#   bash tools/phase3_migrate.sh
#
# WHAT IT DOES
#   git mv  the 25 hand-written pages          -> content/
#   git mv  the files published verbatim       -> static/
#   git rm  the generated pages from the root  (they are rebuilt into dist/)
#
# WHY IT EXISTS AS A SCRIPT
# Every move is a `git mv`, so history follows the files rather than showing a
# delete plus an unrelated add. Doing that by hand across ~40 paths invites a
# typo that looks like a deleted page.
#
# SAFETY
#   * refuses to run on a dirty tree, so `git checkout .` always gets you back
#   * touches nothing outside the paths listed below
#   * does NOT commit — you review `git status` first
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit or stash first, so this is revertible."
  exit 1
fi

say() { printf '\n\033[1m── %s\033[0m\n' "$*"; }

say "1/3  hand-written pages -> content/"
mkdir -p content
for d in DevOps Infrastructure SRE; do
  [ -d "$d" ] && git mv "$d" "content/$d"
done

say "2/3  verbatim-published files -> static/"
mkdir -p static/assets static/newsletter
for f in LICENSE NOTICE favicon.ico; do
  [ -f "$f" ] && git mv "$f" "static/$f"
done
for f in google*.html; do
  [ -f "$f" ] && git mv "$f" "static/$f"
done
[ -f newsletter/kit-template.html ] && git mv newsletter/kit-template.html static/newsletter/
for f in assets/favicon-96.png assets/favicon-192.png assets/favicon.svg assets/apple-touch-icon.png; do
  [ -f "$f" ] && git mv "$f" "static/assets/$(basename "$f")"
done
for d in assets/og assets/arch; do
  [ -d "$d" ] && git mv "$d" "static/$d"
done
# one image that belongs to a hand-written page rather than to the build
if [ -f content/DevOps/K8/ERROR/og-error.png ]; then
  echo "  (og-error.png already moved with its page)"
fi

say "3/3  generated output -> removed from the root"
# These are all rebuilt into dist/. Anything NOT listed here is source.
for p in index.html README.md feed.xml robots.txt sitemap.xml \
         categories Foundation Commands Kubernetes OpenShift colophon terminal \
         assets newsletter; do
  [ -e "$p" ] && git rm -r -q --ignore-unmatch "$p"
done

say "done"
cat <<'NEXT'
Now:

  bash tools/build.sh          # writes everything into dist/
  git add -A
  git status                   # review: content/ + static/ moved, dist/ added
  git commit -m "Build into dist/; separate source from output"
  git push
  npx wrangler deploy          # now publishes dist/, not the repo

If anything looks wrong before you commit:  git reset --hard HEAD
NEXT
