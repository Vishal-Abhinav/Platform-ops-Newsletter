#!/usr/bin/env python3
"""Render the built site in a real browser and assert it is not broken.

    python3 tools/test_render.py            # tests ./dist
    python3 tools/test_render.py path/to/dir

WHY THIS EXISTS
---------------
verify.py checks links, HTML nesting, canonicals and required chrome. All
valuable, and none of it looks at layout — so three real defects reached
production anyway:

  * a second <nav> inherited the site header's `position:fixed` rules and
    became a full-width bar pinned over the real one
  * every page family except the homepage scrolled sideways between 761px and
    900px, by up to 201px, because a flex fallback said `flex: 0 0 auto`
  * a deploy published an EMPTY output directory, and nothing objected

Each one is trivial to detect by opening the page. None is detectable by
reading the HTML. So this opens the pages.

WHAT IT ASSERTS
  1. the output directory is not empty          (the empty-deploy failure)
  2. no horizontal scrolling at any tested width (the overflow band)
  3. at most one full-width fixed header        (the duplicated-nav class)
  4. every page carries a canonical and favicon links

Exits non-zero on the first failing assertion, with the measurement that
failed rather than a bare "assertion error".
"""
import functools
import http.server
import pathlib
import socketserver
import sys
import threading

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is required:\n"
             "  pip install playwright && playwright install --with-deps chromium")

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist").resolve()

# One page per family. Adding a family here is cheaper than discovering its
# layout bug in production.
PAGES = {
    "homepage":        "index.html",
    "deep-dive":       "Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html",
    "openshift":       "OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html",
    "foundation":      "Foundation/PYTHON/python.html",
    "command ref":     "Commands/KUBERNETES-COMMANDS/kubernetes-commands.html",
    "category hub":    "categories/kubernetes/index.html",
    "categories index": "categories/index.html",
    "topic map":       "categories/kubernetes-openshift-map/index.html",
    "about":           "about/index.html",
    "architecture":    "architecture/index.html",
    "colophon":        "colophon/index.html",
    "member login":    "login/index.html",
    "admin account":   "admin/index.html",
    "user account":    "user/index.html",
    "legacy":          "Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html",
}

# 761 and 900 bracket the band that was broken; 360/390 are the common phones;
# 1479/1480 sit either side of the docs-rail breakpoint on the homepage.
WIDTHS = [360, 390, 430, 600, 759, 761, 800, 900, 960, 1100, 1479, 1480, 1920]

PROBE = """() => {
  const vw = document.documentElement.clientWidth;
  // Is the real display face available? The fallback is materially wider —
  // wide enough to produce ~20px of phantom overflow at 360px on pages that
  // are fine in production, so the test checks rather than assumes.
  //
  // This used to be the common case: the faces came from fonts.googleapis.com
  // and any sandbox without egress fell back, so the tolerance was relaxed on
  // most runs. They are served from this origin now, so a fallback here means
  // assets/fonts.css or the woff2 files did not make it into the build — a
  // real defect, not an environment quirk.
  // document.fonts.check() is the obvious call and the wrong one: it answers
  // "could this be rendered", which is true even when the answer is a
  // fallback. Ask the FontFaceSet for a face that actually finished loading.
  let webfont = false;
  try {
    webfont = [...document.fonts].some(
      f => /Bebas|DM Mono|Manrope/i.test(f.family) && f.status === 'loaded');
  } catch (e) {}
  const fixedBars = [...document.querySelectorAll('body *')].filter(el => {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' || cs.display === 'none') return false;
    const r = el.getBoundingClientRect();
    return r.width > vw * 0.6 && r.height > 8 && r.top < 80 && cs.opacity !== '0';
  }).map(el => (el.tagName + '.' + (el.getAttribute('class') || '')).slice(0, 40));
  return {
    overflow: document.documentElement.scrollWidth - vw,
    fixedBars, webfont,
    canonical: !!document.querySelector('link[rel="canonical"]'),
    icons: document.querySelectorAll('link[rel~="icon"]').length,
  };
}"""


def serve(root):
    """A real HTTP origin. file:// differs from production in enough ways
    (base URLs, fetch, some CSS) that testing over it proves less."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):        # one line per asset is not a report
            pass
    handler = functools.partial(Quiet, directory=str(root))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main():
    # 1. the empty-deploy check, first and cheapest
    if not OUT.is_dir():
        sys.exit(f"FAIL  output directory does not exist: {OUT}")
    n_html = sum(1 for _ in OUT.rglob("*.html"))
    if n_html < 50:
        sys.exit(f"FAIL  {OUT} holds {n_html} html files — that is not a built "
                 f"site. A deploy from here would publish nothing.")
    print(f"output    : {OUT}  ({n_html} html files)")

    missing = [p for p in PAGES.values() if not (OUT / p).exists()]
    if missing:
        sys.exit("FAIL  expected pages absent from the build:\n  " +
                 "\n  ".join(missing))

    httpd, port = serve(OUT)
    base = f"http://127.0.0.1:{port}/"
    fails, seen_webfont = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, rel in PAGES.items():
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page.goto(base + rel, wait_until="load")
            page.wait_for_timeout(400)
            head = page.evaluate(PROBE)
            if not head["canonical"]:
                fails.append(f"{name}: no <link rel=canonical>")
            if head["icons"] == 0:
                fails.append(f"{name}: no favicon links")
            ctx.close()

            row = []
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 900})
                page = ctx.new_page()
                page.goto(base + rel, wait_until="load")
                page.wait_for_timeout(300)
                r = page.evaluate(PROBE)
                seen_webfont.append(r["webfont"])
                tol = 2 if r["webfont"] else 24
                if r["overflow"] > tol:
                    fails.append(f"{name} @{w}px: horizontal overflow "
                                 f"+{r['overflow']}px")
                    row.append(f"{w}:+{r['overflow']}")
                if len(r["fixedBars"]) > 1:
                    fails.append(f"{name} @{w}px: {len(r['fixedBars'])} "
                                 f"full-width fixed bars {r['fixedBars']}")
                ctx.close()
            print(f"  {name:18s} {'ok' if not row else ' '.join(row)}")
        browser.close()
    httpd.shutdown()

    if not any(seen_webfont):
        print("\nWARNING  the self-hosted webfonts did NOT load, on any page.\n"
              "         They ship with the site now, so this is not an offline\n"
              "         sandbox — check assets/fonts.css and assets/fonts/ are in\n"
              "         the build. Tolerance was relaxed to 24px, so these results\n"
              "         are weaker than they look.")

    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for f in fails[:40]:
            print(f"  {f}")
        return 1
    print(f"\nall render checks passed "
          f"({len(PAGES)} pages x {len(WIDTHS)} widths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
