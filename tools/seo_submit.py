#!/usr/bin/env python3
"""Submit changed URLs to IndexNow.

Usage:  python3 tools/seo_submit.py pages.txt
        INDEXNOW_KEY must be set.

WHAT THIS DOES AND DOES NOT DO
------------------------------
IndexNow is a single POST that names the host, the key, and the URLs that
changed. Bing, Yandex, Seznam and Naver share submissions with each other, so
one call reaches all of them.

Google is NOT an IndexNow participant and its sitemap ping endpoint was
retired in June 2023, so there is nothing to call for Google. It discovers
changes from sitemap.xml, which robots.txt advertises and verify.py keeps
current with real lastmod dates. That is the whole of the Google story, and
adding a ping would be theatre.

The key must also be served as a text file at the site root:

    https://<host>/<key>.txt     containing exactly <key>

That file is how IndexNow proves you own the host. Without it every
submission is rejected with 403.
"""
import os
import pathlib
import sys
import urllib.error
import urllib.request
import json

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT / "tools"))

from siteconf import BASE          # noqa: E402

ENDPOINT = "https://api.indexnow.org/IndexNow"
MAX_URLS = 10000                   # protocol limit per request


def main():
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    if not key:
        # Not a failure. The site is fine without IndexNow; it just means
        # search engines find changes on their own schedule instead.
        print("INDEXNOW_KEY is not set — skipping submission.")
        print("To enable: generate a key, add it as a repo secret named")
        print("INDEXNOW_KEY, and commit <key>.txt at the repo root containing")
        print("exactly that key.")
        return 0

    listfile = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "pages.txt")
    if not listfile.exists():
        print(f"{listfile} not found — nothing to submit.")
        return 0

    host = BASE.split("//", 1)[1].rstrip("/")
    urls = []
    for line in listfile.read_text(encoding="utf-8").splitlines():
        rel = line.strip()
        if not rel:
            continue
        # index.html is the directory itself — submit the canonical form
        if rel == "index.html":
            urls.append(BASE)
        elif rel.endswith("/index.html"):
            urls.append(BASE + rel[:-len("index.html")])
        else:
            urls.append(BASE + rel)

    urls = sorted(set(urls))[:MAX_URLS]
    if not urls:
        print("No published pages in the change list — nothing to submit.")
        return 0

    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{BASE}{key}.txt",
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"})

    print(f"submitting {len(urls)} URL(s) to IndexNow for {host}")
    for u in urls[:20]:
        print(f"  {u}")
    if len(urls) > 20:
        print(f"  … and {len(urls) - 20} more")

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            # 200 accepted, 202 accepted but key still being validated
            print(f"IndexNow responded {r.status} {r.reason}")
            return 0
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        print(f"IndexNow responded {e.code}: {detail}")
        if e.code == 403:
            print(f"403 means the key file is missing or wrong. It must be at "
                  f"{BASE}{key}.txt and contain exactly the key.")
        # Search-engine notification is best-effort. A failure here must not
        # fail a build whose only job was to publish a page successfully.
        return 0
    except Exception as e:                       # noqa: BLE001
        print(f"IndexNow submission failed: {e}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
