#!/usr/bin/env python3
"""Regenerate sitemap.xml, then refuse to let a broken build through.

Checks, in order:
  1. every relative href/src resolves to a file that exists
  2. every page's tags are balanced
  3. every page carries the analytics loader, the RSS link and the copyright meta
  4. the counts on the homepage match the topics actually rendered there
  5. every category card agrees with the hub page it links to
  6. sitemap.xml and feed.xml parse

Exit status is non-zero if anything fails, so it can gate a commit.
"""
import os
import pathlib
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

def _root():
    """The tree to verify.

    build.sh exports PO_ROOT=dist, so the pipeline has always checked the
    right thing. Run by hand, though, this used to fall back to the REPO
    ROOT — which still holds ~900 HTML files from the pre-dist layout. That
    made `python3 tools/verify.py` either crash on wording that has since
    changed, or, far worse, report "all checks passed" about a tree nobody
    deploys. A verifier that green-lights the wrong directory is not a
    weaker check, it is a misleading one.

    So: honour PO_ROOT, else prefer ./dist when it looks built, and say out
    loud which tree is being read either way.
    """
    env = os.environ.get("PO_ROOT")
    if env:
        return pathlib.Path(env)
    repo = pathlib.Path(__file__).resolve().parent.parent
    dist = repo / "dist"
    if (dist / "index.html").exists():
        return dist
    return repo


ROOT = _root()
from siteconf import BASE, skip_page   # canonical origin + the non-page filter
# skip list now lives in siteconf

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source',
        'track', 'wbr', 'path', 'circle', 'rect', 'line', 'polygon', 'polyline', 'ellipse',
        'stop', 'use', 'animate', 'animateMotion', 'animateTransform', 'feGaussianBlur',
        'image', 'feOffset', 'feMerge', 'feMergeNode'}

# These paths are implemented by src/worker.mjs rather than emitted as files.
RUNTIME_PATH_PREFIXES = ("/auth/",)


class Nesting(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag.lower() not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag.lower() in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}>")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"</{tag}> closes <{self.stack[-1]}>")
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i] == tag:
                    del self.stack[i:]
                    return
        else:
            self.stack.pop()


def pages():
    """Published pages only — tools/ holds templates, not deployable pages."""
    for f in sorted(ROOT.rglob("*.html")):
        if ".git" in f.parts or "tools" in f.parts or skip_page(f.name):
            continue
        yield f


def main():
    files = {str(p.relative_to(ROOT)).replace("\\", "/")
             for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
    fails, n = [], 0

    for f in pages():
        n += 1
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        src = f.read_text(encoding="utf-8")

        # 1. links
        base_dir = posixpath.dirname(rel)
        for m in re.finditer(r'(?:href|src)="([^"]+)"', src):
            u = m.group(1)
            if u.startswith(("http://", "https://", "#", "mailto:", "data:", "javascript:", "{{")):
                continue
            if u.startswith(RUNTIME_PATH_PREFIXES):
                continue
            tgt = posixpath.normpath(
                posixpath.join(base_dir, u.split("#")[0].split("?")[0])).lstrip("/")
            if tgt in ("", "."):
                continue
            if tgt not in files and f"{tgt}/index.html" not in files:
                fails.append(f"broken link  {rel} -> {u}")

        # 2. nesting
        p = Nesting()
        p.feed(src)
        if p.errors or p.stack:
            fails.append(f"unbalanced   {rel}: {p.errors[:2]} unclosed={p.stack[:3]}")

        # 3. the canonical must point at THIS page
        #
        # Added after all 3 OpenShift pages, all 7 Kubernetes and Service Mesh
        # pages and the colophon shipped with a canonical of
        # Foundation/<SLUG>/<slug>.html — a URL that 404s — because
        # content_page.render() built that path for every page regardless of
        # where it was written. Nothing caught it: the links checker skips
        # absolute URLs, and a Foundation page happens to match the pattern.
        # A canonical pointing at a 404 tells a search engine the real version
        # of the page does not exist, which is worse than having none at all.
        m = re.search(r'<link rel="canonical" href="([^"]+)"', src)
        if m:
            want = BASE + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            if m.group(1) != want:
                fails.append(f"canonical    {rel}: says {m.group(1)}, should be {want}")

        # 4. required chrome
        for needle, label in (("var PO_GC=", "analytics loader"),
                              ('type="application/rss+xml"', "RSS link"),
                              ('name="copyright"', "copyright meta")):
            if needle not in src:
                fails.append(f"missing      {rel}: {label}")
        if src.count("</head>") != 1:
            fails.append(f"head count   {rel}: {src.count('</head>')} </head>")

    # 4. the homepage's own numbers, against what it actually renders
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    stated = [int(x) for x in re.findall(r'<div class="km-stat-n[^"]*">(\d+)</div>', idx)]
    actual = [len(re.findall(r'class="km-t live"', idx)),
              len(re.findall(r'class="km-t pipe"', idx)),
              len(re.findall(r'class="km-t plan"', idx))]
    if len(stated) >= 5 and stated[2:5] != actual:
        fails.append(f"count drift  index.html says {stated[2:5]}, renders {actual}")
    total_chips = sum(actual)
    if len(stated) >= 1 and stated[0] != total_chips:
        fails.append(f"count drift  index.html total {stated[0]}, renders {total_chips}")

    # 5. every category card must tell the same story as the hub it links to
    #
    # WHY THIS EXISTS
    # Three separate defects this week were the same defect: two pages stating
    # the same fact differently. The index called Kubernetes "35 live · 0 pipe
    # · 0 planned" while its hub carried a 492-item checklist; it called
    # OpenShift complete while the OpenShift hub opened with 374 items
    # outstanding; and the hub heroes kept printing the zeros the index had
    # stopped printing. Every one was found by a reader opening two pages, and
    # not one of them tripped a check — because every check here asks whether a
    # number is COMPUTED correctly, and all of them were. Nothing asked whether
    # two pages AGREE.
    #
    # So this walks each card on categories/index.html, reads the figures off
    # the hub it points at, and fails the build if they differ. A future
    # special case for one category cannot silently desynchronise the pair.
    def _counts(s):
        """(total, live, pipe, plan) from a rendered counts line."""
        m = re.search(r"(\d+) topics? · all live", s)
        if m:
            t = int(m.group(1))
            return t, t, 0, 0
        live = int(re.search(r"(\d+) live", s).group(1))
        mp = re.search(r"(\d+) pipeline", s)
        mn = re.search(r"(\d+) planned", s)
        pipe = int(mp.group(1)) if mp else 0
        plan = int(mn.group(1)) if mn else 0
        return live + pipe + plan, live, pipe, plan

    cat_idx = ROOT / "categories" / "index.html"
    if cat_idx.exists():
        cidx = cat_idx.read_text(encoding="utf-8")
        cards = re.findall(
            r'<a class="sib" href="([a-z0-9-]+)/index\.html">(.*?)</a>', cidx, re.S)
        if not cards:
            fails.append("category sync: no cards found on categories/index.html")
        for slug, card in cards:
            hub = ROOT / "categories" / slug / "index.html"
            if not hub.exists():
                fails.append(f"category sync: {slug} card links to a missing hub")
                continue
            hsrc = hub.read_text(encoding="utf-8")
            tiles = re.findall(
                r'<div class="stat"><b[^>]*>([\d,]+)</b><i>([^<]+)</i></div>', hsrc)
            # the hero group ends at its Issues tile; anything after is the
            # separate reader checklist that build_hub_topicmap.py folds in
            keys = [k for _, k in tiles]
            cut = keys.index("Issues") + 1 if "Issues" in keys else len(tiles)
            hero, chk = dict(map(reversed, tiles[:cut])), tiles[cut:]

            want = (int(hero.get("Topics", -1)), int(hero.get("Live", -1)),
                    int(hero.get("In pipeline", 0)), int(hero.get("Planned", 0)))
            spans = re.findall(r'<span class="c"[^>]*>(.*?)</span>', card, re.S)
            if not spans:
                fails.append(f"category sync: {slug} card has no counts line")
                continue
            got = _counts(re.sub(r"<[^>]+>", " ", spans[0]))
            if got != want:
                fails.append(
                    f"category sync: {slug} — index card says "
                    f"total/live/pipe/plan {got}, hub page says {want}")

            # and the checklist line, in both directions
            card_chk = len(spans) > 1
            hub_chk = bool(chk)
            if card_chk != hub_chk:
                where = "card but not hub" if card_chk else "hub but not card"
                fails.append(
                    f"category sync: {slug} — reader checklist appears on the "
                    f"{where}. A hub that carries one must say so on the index.")
            elif hub_chk:
                d = dict(map(reversed, chk))
                hw = (int(d.get("Items", -1)), int(d.get("Live", -1)),
                      int(d.get("In pipeline", -1)), int(d.get("Planned", -1)))
                t = re.sub(r"<[^>]+>", " ", spans[1])
                cg = (int(re.search(r"(\d+)-item", t).group(1)),
                      int(re.search(r"(\d+) live", t).group(1)),
                      int(re.search(r"(\d+) pipeline", t).group(1)),
                      int(re.search(r"(\d+) planned", t).group(1)))
                if cg != hw:
                    fails.append(
                        f"category sync: {slug} checklist — index card says "
                        f"{cg}, hub page says {hw}")

    # 5b. SMIL must not outrun prefers-reduced-motion
    #
    # assets/motion.css gates every CSS animation on the site, and for a while
    # the README said so without qualification. It was not true: SVG SMIL is
    # not CSS, no stylesheet can stop it, and getAnimations() does not list it
    # — so the homepage's particles kept flying for a reader who had asked for
    # stillness, past both motion.css and test_motion.py.
    #
    # build_seo.py now injects an explicit pauseAnimations() call into any page
    # carrying <animate*>. This asserts the result rather than trusting the
    # stage: the invariant is "if a page can animate via SMIL, it can also stop",
    # and it is checked here, across every page, because the next SMIL diagram
    # will be added by someone who has never read this comment.
    unguarded = []
    for f in pages():
        src = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"<animate(Motion|Transform)?[\s>]", src) \
                and "pauseAnimations" not in src:
            unguarded.append(str(f.relative_to(ROOT)))
    for rel in unguarded[:5]:
        fails.append(
            f"reduced motion: {rel} uses SVG SMIL but never calls "
            f"pauseAnimations() — its animation ignores the reader's setting")

    # 6. sitemap
    #
    # Indexable pages only. A sitemap is a request to crawl; a page carrying
    # noindex then declines to be indexed, so listing one spends crawl budget
    # to be told no and fills Search Console with "Excluded by noindex"
    # entries that bury the real problems. This site is mostly such pages:
    # 784 of 878 are reader-checklist placeholders, deliberately
    # noindex,follow — internal linking scaffolding, not content to submit.
    # Before this filter the sitemap advertised all 878.
    #
    # The robots meta is read fresh here rather than reusing a set collected
    # in the checking loop above: this stays correct if that loop is ever
    # restructured, and re-reading 878 small files costs milliseconds against
    # a 25-stage build.
    urls, noindexed = [], 0
    for f in pages():
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        src = f.read_text(encoding="utf-8")
        if re.search(r'<meta name="robots"[^>]*noindex', src, re.I):
            noindexed += 1
            continue
        loc = BASE + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        if rel == "index.html":
            loc, pri = BASE, "1.0"
        elif rel.startswith("categories/"):
            pri = "0.8" if rel == "categories/index.html" else "0.6"
        else:
            pri = "0.7"
        modified = re.search(
            r'<meta property="article:modified_time" content="(\d{4}-\d{2}-\d{2})',
            src, re.I)
        urls.append((loc, pri, modified.group(1) if modified else None))
    body = "".join(
        f"  <url>\n    <loc>{u}</loc>\n"
        + (f"    <lastmod>{modified}</lastmod>\n" if modified else "")
        + f"    <priority>{p}</priority>\n  </url>\n"
        for u, p, modified in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
        encoding="utf-8")
    for x in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(ROOT / x)
        except Exception as e:                                    # noqa: BLE001
            fails.append(f"malformed    {x}: {e}")

    print(f"tree verified : {ROOT}")
    print(f"pages checked : {n}")
    print(f"sitemap urls  : {len(urls)} indexable ({noindexed} noindex pages withheld)")
    print(f"topics        : {actual[0]} live / {actual[1]} pipeline / {actual[2]} planned")
    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for x in fails[:40]:
            print("  " + x)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
