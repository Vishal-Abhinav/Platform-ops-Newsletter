#!/usr/bin/env python3
"""Structured data and article dates for every published page.

WHY
---
Titles, descriptions, canonicals, sitemap and robots.txt were all already
correct. What was missing on all 81 pages was JSON-LD: the machine-readable
statement of what a page IS. Without it a search engine has to infer from
prose that this is a technical article, by whom, published when, about what —
and it mostly does not bother.

This is not a ranking silver bullet. It is the difference between a page
Google has to guess about and one that declares itself, which is what makes a
page eligible for article rich results and author/date display.

WHAT IT EMITS
-------------
  every page      BreadcrumbList   (from the page's own crumb trail)
  homepage        WebSite + Blog + Person
  issue pages     TechArticle, with datePublished from build_feed's register
  category hubs   CollectionPage
  other pages     WebPage

Also adds article:published_time / article:modified_time meta to issue pages,
and points each issue's og:image at its own card when one exists, falling
back to the site card when it does not.

Idempotent: a page already carrying our block has it replaced, not appended.
"""
import html
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from siteconf import BASE, skip_page           # noqa: E402
from build_feed import ISSUES                  # noqa: E402
from chrome import icons                       # noqa: E402

MARK_OPEN = "<!-- seo:jsonld -->"
MARK_CLOSE = "<!-- /seo:jsonld -->"

# The favicon links get their own marked block rather than riding inside the
# JSON-LD one: a marker named "jsonld" wrapping <link rel="icon"> would lie
# about its contents, and the two have different reasons to change. This stage
# carries them because it is the only one that walks EVERY page — build_nav
# reaches 853 and the 25 hand-written pages get their chrome from
# build_legacy_chrome, so neither alone covers the site.
ICON_OPEN = "<!-- seo:icons -->"
ICON_CLOSE = "<!-- /seo:icons -->"
# skip list now lives in siteconf

AUTHOR = {
    "@type": "Person",
    "name": "Vishal Abhinav",
    "url": "https://www.linkedin.com/in/vishal-abhinav/",
    "jobTitle": "Platform Ops Engineer",
    "sameAs": [
        "https://www.linkedin.com/in/vishal-abhinav/",
        "https://github.com/Vishal-Abhinav",
        "https://www.researchgate.net/profile/Vishal-Abhinav/research",
        "https://www.hackerrank.com/Vishal_Abhinav",
    ],
}

PUBLISHER = {
    "@type": "Organization",
    "name": "Platform Ops",
    "url": BASE,
    "logo": {"@type": "ImageObject", "url": f"{BASE}assets/og/home.png"},
}

# issue number and date, keyed by the page path
ISSUE_BY_PATH = {path: (num, when) for num, path, _t, _b, when in ISSUES}


def text_of(pattern, src, default=""):
    m = re.search(pattern, src, re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else default


def crumbs_of(src, page_url):
    """Build a BreadcrumbList from the page's own crumb trail.

    Derived from the markup rather than from a hardcoded map, so a page whose
    navigation changes cannot end up advertising a trail it no longer has.
    """
    m = re.search(r'<div class="crumb">(.*?)</div>', src, re.S)
    if not m:
        return None
    items, pos = [], 1
    for href, label in re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', m.group(1), re.S):
        label = html.unescape(re.sub(r"<[^>]+>", "", label)).strip()
        if not label:
            continue
        target = href.replace("../", "").lstrip("./")
        # "/" is the canonical root; "/index.html" is a second URL for the same
        # page, and advertising both is exactly the duplication a canonical is
        # meant to prevent.
        if target in ("index.html", ""):
            target = ""
        items.append({"@type": "ListItem", "position": pos, "name": label,
                      "item": BASE + target})
        pos += 1
    cur = text_of(r'<span class="cur">(.*?)</span>', src)
    if cur:
        items.append({"@type": "ListItem", "position": pos, "name": cur, "item": page_url})
    if len(items) < 2:
        return None
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def blocks_for(rel, src):
    """The JSON-LD objects this particular page should carry."""
    page_url = BASE if rel == "index.html" else BASE + rel
    title = text_of(r"<title>(.*?)</title>", src)
    desc = text_of(r'<meta name="description" content="([^"]*)"', src)
    out = []

    if rel == "index.html":
        out.append({
            "@context": "https://schema.org", "@type": "WebSite",
            "name": "Platform Ops · Tech with Vishal Abhinav",
            "alternateName": "Platform Ops", "url": BASE, "description": desc,
            "inLanguage": "en", "author": AUTHOR, "publisher": PUBLISHER,
        })
        out.append({
            "@context": "https://schema.org", "@type": "Blog",
            "name": "Platform Ops", "url": BASE, "description": desc,
            "author": AUTHOR, "publisher": PUBLISHER,
            "blogPost": [
                {"@type": "BlogPosting", "headline": t,
                 "url": BASE + p, "datePublished": w.date().isoformat(),
                 "author": AUTHOR}
                for num, p, t, _b, w in ISSUES[:10]
            ],
        })
    elif rel in ISSUE_BY_PATH:
        num, when = ISSUE_BY_PATH[rel]
        img = f"assets/og/i{num:03d}.png"
        image = BASE + (img if (ROOT / img).exists() else "assets/og/home.png")
        out.append({
            "@context": "https://schema.org", "@type": "TechArticle",
            "headline": title.split(" · ")[0][:110], "description": desc,
            "url": page_url, "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
            "datePublished": when.isoformat(), "dateModified": when.isoformat(),
            "author": AUTHOR, "publisher": PUBLISHER, "image": image,
            "inLanguage": "en", "isAccessibleForFree": True,
            "articleSection": "Platform Engineering",
        })
    elif rel.startswith("categories/"):
        out.append({
            "@context": "https://schema.org", "@type": "CollectionPage",
            "name": title.split(" · ")[0], "description": desc, "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": "Platform Ops", "url": BASE},
            "author": AUTHOR, "publisher": PUBLISHER, "inLanguage": "en",
        })
    else:
        out.append({
            "@context": "https://schema.org", "@type": "WebPage",
            "name": title.split(" · ")[0], "description": desc, "url": page_url,
            "isPartOf": {"@type": "WebSite", "name": "Platform Ops", "url": BASE},
            "author": AUTHOR, "publisher": PUBLISHER, "inLanguage": "en",
        })

    crumbs = crumbs_of(src, page_url)
    if crumbs:
        out.append(crumbs)
    return out


def apply_meta(src, rel):
    """Article dates, and the issue's own social card when one exists."""
    if rel not in ISSUE_BY_PATH:
        return src
    num, when = ISSUE_BY_PATH[rel]
    iso = when.isoformat()

    # author must be in this strip too — it was not, so it stacked one extra
    # copy per build until the head filled with them.
    src = re.sub(r'\n?<meta property="article:(published_time|modified_time|author)"[^>]*>',
                 "", src)
    tag = (f'\n<meta property="article:published_time" content="{iso}">'
           f'\n<meta property="article:modified_time" content="{iso}">'
           f'\n<meta property="article:author" content="Vishal Abhinav">')
    src = src.replace('<link rel="canonical"', tag.strip() + '\n<link rel="canonical"', 1)

    img = f"assets/og/i{num:03d}.png"
    if (ROOT / img).exists():
        src = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                     rf"\g<1>{BASE}{img}\g<2>", src)
        src = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")',
                     rf"\g<1>{BASE}{img}\g<2>", src)
    return src


count, with_article, with_crumbs = 0, 0, 0

for f in sorted(ROOT.rglob("*.html")):
    if "tools" in f.parts or skip_page(f.name):
        continue
    rel = f.relative_to(ROOT).as_posix()
    src = f.read_text(encoding="utf-8")

    # Replace our previous block rather than stacking a new one on each build.
    # The trailing \n? matters: `block` below ends in "{MARK_CLOSE}\n", and
    # without consuming that newline here too, every run leaves one stray
    # blank line behind and the next run's insertion goes after it — the
    # exact leak this doc's design-system notes already named build_seo.py
    # for, on the 25 hand-written pages that never get wiped and rebuilt from
    # a Python source between runs the way every generated page does. Those
    # get any stray lines wiped for free each build; these were accumulating
    # one every single time. (Confirmed the leak was still live, not merely
    # documented as fixed: `build_seo.py` run twice in isolation grew every
    # page it touched by one line each time before this fix.)
    src = re.sub(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE) + r"\n?",
                 "", src, flags=re.S)
    # Same strip-then-reinsert, same trailing \n? — see the note above for why
    # that newline is not optional.
    src = re.sub(re.escape(ICON_OPEN) + r".*?" + re.escape(ICON_CLOSE) + r"\n?",
                 "", src, flags=re.S)
    src = apply_meta(src, rel)

    blocks = blocks_for(rel, src)
    payload = "\n".join(
        '<script type="application/ld+json">'
        + json.dumps(b, ensure_ascii=False, separators=(",", ":"))
        + "</script>" for b in blocks)
    block = f"{MARK_OPEN}\n{payload}\n{MARK_CLOSE}\n"

    # Relative, not root-relative: every other link in this repo is relative so
    # the site can be opened from disk, and the GitHub Pages mirror served it
    # from a subpath. Depth comes from the page's own path.
    icon_block = f"{ICON_OPEN}\n{icons('../' * rel.count('/'))}\n{ICON_CLOSE}\n"

    assert src.count("</head>") == 1, f"{rel}: expected exactly one </head>"
    src = src.replace("</head>", icon_block + block + "</head>", 1)
    f.write_text(src, encoding="utf-8")

    count += 1
    if rel in ISSUE_BY_PATH:
        with_article += 1
    if any(b.get("@type") == "BreadcrumbList" for b in blocks):
        with_crumbs += 1

print(f"structured data -> {count} pages "
      f"({with_article} TechArticle, {with_crumbs} with breadcrumbs)")

# Every block must be valid JSON, or it is worse than having none — a parse
# error makes a search engine discard the whole page's structured data.
bad = []
for f in sorted(ROOT.rglob("*.html")):
    if "tools" in f.parts or skip_page(f.name):
        continue
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                         f.read_text(encoding="utf-8"), re.S):
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as e:
            bad.append(f"{f.relative_to(ROOT)}: {e}")
assert not bad, "invalid JSON-LD emitted:\n  " + "\n  ".join(bad[:5])
print("  all JSON-LD parses clean")
