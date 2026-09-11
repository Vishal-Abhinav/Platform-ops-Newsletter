#!/usr/bin/env python3
"""Regenerate sitemap.xml, then refuse to let a broken build through.

Checks, in order:
  1. every relative href/src resolves to a file that exists
  2. every page's tags are balanced
  3. every page carries the analytics loader, the RSS link and the copyright meta
  4. the counts on the homepage match the topics actually rendered there
  5. sitemap.xml and feed.xml parse

Exit status is non-zero if anything fails, so it can gate a commit.
"""
import datetime
import os
import pathlib
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
from siteconf import BASE           # canonical origin, one source of truth
SKIP_NAMES = {"kit-template.html"}

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source',
        'track', 'wbr', 'path', 'circle', 'rect', 'line', 'polygon', 'polyline', 'ellipse',
        'stop', 'use', 'animate', 'animateMotion', 'animateTransform', 'feGaussianBlur',
        'image', 'feOffset', 'feMerge', 'feMergeNode'}


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
        if ".git" in f.parts or "tools" in f.parts or f.name in SKIP_NAMES:
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

        # 3. required chrome
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

    # 5. sitemap
    today = datetime.date.today().isoformat()
    urls = []
    for f in pages():
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        loc = BASE + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        if rel == "index.html":
            loc, pri = BASE, "1.0"
        elif rel.startswith("categories/"):
            pri = "0.8" if rel == "categories/index.html" else "0.6"
        else:
            pri = "0.7"
        urls.append((loc, pri))
    body = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
                   f"    <priority>{p}</priority>\n  </url>\n" for u, p in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
        encoding="utf-8")
    for x in ("sitemap.xml", "feed.xml"):
        try:
            ET.parse(ROOT / x)
        except Exception as e:                                    # noqa: BLE001
            fails.append(f"malformed    {x}: {e}")

    print(f"pages checked : {n}")
    print(f"sitemap urls  : {len(urls)}")
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
