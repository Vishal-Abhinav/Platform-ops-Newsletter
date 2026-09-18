#!/usr/bin/env python3
"""Assert the site honours prefers-reduced-motion, in a real browser.

    python3 tools/test_motion.py            # tests ./dist
    python3 tools/test_motion.py path/to/dir

WHY THIS EXISTS
---------------
On 18 Sep 2026 this site honoured prefers-reduced-motion on zero of 880
pages, while running twelve distinct infinite animations — a drifting
background, pulsing status dots on 27 pages, a ticker on 24, and a terminal
cursor on `blink 1s infinite`. Nothing failed, because nothing asked.

verify.py reads HTML and test_render.py measures layout. Neither can see
motion: an animation is a property of the running page, not of its markup.
So this opens the pages twice — once as an ordinary visitor, once as a
visitor whose OS asks for less motion — and compares.

WHAT IT ASSERTS, under prefers-reduced-motion: reduce
  1. no animation is still running once the page has settled
  2. nothing is left invisible    (the failure mode of `animation: none`)
  3. nothing is left part-moved   (a reveal frozen on its FIRST keyframe)
  4. JS counters show their real totals, not a number caught mid-count

And, so the fix cannot be "delete all the animation":
  5. WITHOUT the preference, the motion is still there.

That last one is the point. A test that only checks the reduced case passes
just as happily on a site with no animation at all, and would have let the
entire design be deleted in the name of accessibility.

WHY THE FIX IS SPLIT IN TWO, which this test checks as one thing
  * assets/motion.css gates everything driven by CSS, site-wide.
  * a stylesheet cannot reach a number counting up inside setInterval, so
    the homepage's typewriter and counters are gated in JS against the same
    media query.
Both must hold; this asserts the observable result rather than either
mechanism, so a future rewrite that moves the boundary still passes.
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

# The homepage carries the JS effects and the richest CSS motion; the others
# are one per family that animates. A page with no motion at all is a valid
# result for the reduce run but proves nothing, so PAGES is deliberately a
# list of pages that DO move.
PAGES = {
    # bg-drift, dash-flow, tn-pulse-anim, pulse-badge, the typewriter, the
    # counters — plus every effect below, since the homepage has them all.
    "homepage":      "index.html",
    # pulse-dot, fb-dot-pulse and the ticker: the three that run on 24-27
    # pages each. Without this entry the suite never sees any of them.
    "incident":      "SRE/INCIDENT-MANAGEMENT/incident-management.html",
    # `blink 1s infinite` — a terminal cursor that never stops.
    "k8s networking": "DevOps/K8/Networking/k8-networking.html",
    "architecture":  "architecture/index.html",
    "category hub":  "categories/kubernetes/index.html",
    "topic map":     "categories/kubernetes-openshift-map/index.html",
    "deep-dive":     "Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html",
}

# Pages that MUST still animate without the preference. Naming them, rather
# than counting "at least one page somewhere", is what stops this suite from
# quietly weakening if the homepage is the only thing left that moves.
MUST_ANIMATE = ["homepage", "incident", "k8s networking"]

# Long enough for the homepage typewriter (500ms + 52 lines) and the 1800ms
# counters to finish. If they have NOT finished by now under reduce, they
# were never gated.
SETTLE_MS = 4000

PROBE = """() => {
  const running = [...document.querySelectorAll('body *')]
    .flatMap(e => e.getAnimations ? e.getAnimations() : [])
    .filter(a => a.playState === 'running')
    .map(a => a.animationName || 'transition');

  // Invisible: an element that occupies layout but was left at opacity 0.
  // This is what `animation: none` does to an entrance that starts hidden,
  // and it is a worse bug than the motion it removes.
  const invisible = [...document.querySelectorAll(
      'h1,h2,h3,p,li,.tl,.kt-row,.reveal,.stat,.issue-card')]
    .filter(e => e.getClientRects().length)
    .filter(e => parseFloat(getComputedStyle(e).opacity) < 0.9).length;

  // Part-moved: a reveal frozen on its first keyframe rather than its last.
  const shifted = [...document.querySelectorAll('.kt-row,.reveal')]
    .filter(e => e.getClientRects().length)
    .filter(e => {
      const t = getComputedStyle(e).transform;
      return t && t !== 'none' && !/matrix\\(1, 0, 0, 1, 0, 0\\)/.test(t);
    }).length;

  // Counters must read their declared target, not a value caught mid-count.
  const counters = [...document.querySelectorAll('.count-up')]
    .filter(c => c.dataset.target)
    .map(c => ({got: c.textContent.trim(), want: c.dataset.target}));

  return {running, invisible, shifted,
          badCounters: counters.filter(c => c.got !== c.want)};
}"""


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    httpd = socketserver.TCPServer(
        ("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def sample(browser, base, rel, mode):
    """Load one page with one motion preference and report what moved."""
    ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                              reduced_motion=mode)
    page = ctx.new_page()
    page.goto(base + rel, wait_until="load")
    # Scroll the whole page: every reveal here is IntersectionObserver-driven
    # and a section never scrolled to has simply not been asked to animate.
    page.evaluate("""async () => {
      const step = innerHeight * 0.9;
      for (let y = 0; y < document.body.scrollHeight; y += step) {
        scrollTo(0, y); await new Promise(r => requestAnimationFrame(r));
      }
      scrollTo(0, 0);
    }""")
    page.wait_for_timeout(SETTLE_MS)
    result = page.evaluate(PROBE)
    ctx.close()
    return result


def main():
    if not (OUT / "index.html").exists():
        sys.exit(f"FAIL  not a built site: {OUT}")
    missing = [p for p in PAGES.values() if not (OUT / p).exists()]
    if missing:
        sys.exit("FAIL  expected pages absent:\n  " + "\n  ".join(missing))

    httpd, port = serve(OUT)
    base = f"http://127.0.0.1:{port}/"
    fails, moving_pages = [], 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, rel in PAGES.items():
            calm = sample(browser, base, rel, "reduce")
            loud = sample(browser, base, rel, "no-preference")

            if calm["running"]:
                uniq = sorted(set(calm["running"]))[:6]
                fails.append(f"{name}: {len(calm['running'])} animation(s) still "
                             f"running under reduced motion {uniq}")
            if calm["invisible"]:
                fails.append(f"{name}: {calm['invisible']} element(s) left "
                             f"INVISIBLE under reduced motion")
            if calm["shifted"]:
                fails.append(f"{name}: {calm['shifted']} element(s) left "
                             f"part-moved under reduced motion")
            if calm["badCounters"]:
                fails.append(f"{name}: counter(s) not at final value "
                             f"{calm['badCounters'][:3]}")

            # 5. the motion must still exist for everyone else
            if loud["running"] or loud["invisible"] or loud["shifted"]:
                moving_pages += 1
            elif name in MUST_ANIMATE:
                fails.append(
                    f"{name}: nothing animated even WITHOUT the preference. "
                    f"Either the motion was deleted rather than gated, or the "
                    f"media query is being matched when it should not be.")

            print(f"  {name:16s} reduce: {len(calm['running']):3d} running   "
                  f"normal: {len(loud['running']):3d} running")
        browser.close()
    httpd.shutdown()

    if moving_pages == 0:
        fails.append(
            "no page animated even WITHOUT the preference — reduced motion "
            "cannot be 'verified' on a site that no longer moves at all")

    if fails:
        print(f"\nFAILED ({len(fails)}):")
        for f in fails:
            print(f"  {f}")
        return 1
    print(f"\nall motion checks passed ({len(PAGES)} pages x 2 preferences; "
          f"{moving_pages} still animate without the preference)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
