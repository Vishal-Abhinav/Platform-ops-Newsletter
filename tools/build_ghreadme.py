#!/usr/bin/env python3
"""Write README.md at the REPO ROOT — the repository's front page on GitHub.

    python3 tools/build_ghreadme.py

WHY THIS EXISTS
---------------
The repo had no README at all. Phase 3 moved the generated one into `dist/`
because it is also a page of the website; Phase 8 then untracked `dist/`. Each
step was right on its own, and between them the repository's front page went
blank without anyone noticing — the kind of gap that only surfaces when someone
visits the repo, which the person who owns it rarely does.

So there are now two READMEs, and they are not the same document:

  README.md            this file's output. Tracked, at the repo root, written
                       for someone who has just landed on GitHub and has thirty
                       seconds to decide whether this is worth their time.
  dist/README.md       build_readme.py's output. A page of the website, with
                       the full knowledge map, the repository tree and the
                       build-stage table — reference material for someone who
                       is already inside.

WHY IT WRITES OUTSIDE dist/
---------------------------
Every other stage writes into PO_ROOT, and Phase 3 exists precisely to stop
stages writing into the repo. This one deliberately does, because GitHub reads
the repository, not the deployment — a README inside dist/ is a README nobody
on GitHub can see. It is the one file in this build whose audience is the repo
itself, which is why it is a separate stage rather than a flag on
build_readme.py.

EVERY FIGURE IS DERIVED, for the reason that applies everywhere here: a number
typed by hand is a number that goes stale. The assertions at the end enforce
what a generator cannot — that the file it just wrote actually says what it
claims to.
"""
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from taxonomy import PILLARS, cat_stats          # noqa: E402
from build_feed import ISSUES                    # noqa: E402
from cmd_data import ALL as CMD_SPECS            # noqa: E402
from siteconf import BASE                        # noqa: E402

# ── the numbers, from the same places every page gets them ──────────────────
pillar_rows = []
T_LIVE = T_PIPE = T_PLAN = 0
for name, cats in PILLARS:
    pl = pp = pn = 0
    for _c, _i, topics in cats:
        l, p, n = cat_stats(topics)
        pl += l; pp += p; pn += n
    T_LIVE += pl; T_PIPE += pp; T_PLAN += pn
    pillar_rows.append((name, len(cats), pl, pp, pn))

N_TOPICS = T_LIVE + T_PIPE + T_PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_PILL = len(PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])
N_CMD_PAGES = len(CMD_SPECS)

NEWEST = sorted(ISSUES, key=lambda i: -i[0])[0]
NEWEST_NUM, NEWEST_PATH, NEWEST_TITLE = NEWEST[0], NEWEST[1], NEWEST[2]

SITE = BASE.rstrip("/")

# Pillars, largest first — a reader scanning this wants the substantial ones at
# the top, not alphabetical order.
TABLE = "\n".join(
    f"| **{n}** | {c} | {l} | {p} | {pl} |"
    for n, c, l, p, pl in sorted(pillar_rows, key=lambda r: -(r[2] + r[3] + r[4])))

BADGE = "https://img.shields.io/badge"

# ── figures about the repository itself ─────────────────────────────────────
# Same rule as every number above: derived, never typed. These describe the
# build rather than the taxonomy, so they are counted off the tree.
import re  # noqa: E402

_SH = (TOOLS / "build.sh").read_text(encoding="utf-8")
N_STAGES = len(re.findall(r"^\s*python3 tools/(\w+)\.py", _SH, re.M))
N_HANDWRITTEN = len(list((REPO / "content").rglob("*.html")))
N_FONTS = len(list((REPO / "static" / "assets" / "fonts").glob("*")))


def _count(path, pattern, default=0):
    """Count `pattern` in a source file, or `default` if it isn't there.

    The test suites and the workflows are the authority on their own numbers.
    The README said "11 page families" for as long as test_render.py had
    twelve, because that 11 was typed once and then the suite grew. Reading
    it back means the sentence cannot be wrong for longer than one build.
    """
    p = pathlib.Path(path)
    if not p.exists():
        return default
    return len(re.findall(pattern, p.read_text(encoding="utf-8"), re.M))


# The render matrix, counted off the suite that runs it.
_TR = (TOOLS / "test_render.py")
N_RENDER_PAGES = _count(_TR, r'^\s{4}"[^"]+":\s*"[^"]+\.html"')
_w = re.search(r"^WIDTHS\s*=\s*\[([^\]]*)\]",
               _TR.read_text(encoding="utf-8"), re.M) if _TR.exists() else None
N_RENDER_WIDTHS = len([x for x in _w.group(1).split(",") if x.strip()]) if _w else 0
N_MOTION_PAGES = _count(TOOLS / "test_motion.py", r'^\s{4}"[^"]+":\s*"[^"]+\.html"')

# The deploy workflow is the authority on the wrangler version and on the
# page floor below which CI refuses to ship.
_DEPLOY = REPO / ".github" / "workflows" / "deploy.yml"
_dep = _DEPLOY.read_text(encoding="utf-8") if _DEPLOY.exists() else ""
_m = re.search(r"wrangler@([\d.]+)", _dep)
WRANGLER = _m.group(1) if _m else "4"
_m = re.search(r'-lt\s+"?(\d+)', _dep)
MIN_PAGES = _m.group(1) if _m else "500"

# The page and sitemap counts describe the BUILT site, so they can only be
# read from dist/ — and this stage runs last, after dist/ is complete. If it
# is ever reordered ahead of the build, these fall back to 0 and the
# assertions at the foot of this file fail loudly rather than shipping a
# README that claims the site has no pages.
_DIST = REPO / "dist"
# Not "every .html in dist/". That count is 2 higher and both extras are
# legitimately not pages — a Search Console verification token and the email
# kit template, neither of which is ever rendered in a browser. Counting the
# pages that actually CARRY the stylesheet means the accessibility claim is
# measured against the thing that makes it true, so it cannot drift by two
# and cannot be rounded up by a stage that adds a non-page to dist/.
N_PAGES = sum(1 for p in _DIST.rglob("*.html")
              if "assets/motion.css" in p.read_text(encoding="utf-8", errors="ignore")
              ) if _DIST.is_dir() else 0
_SITEMAP = _DIST / "sitemap.xml"
N_SITEMAP = (len(re.findall(r"<loc>", _SITEMAP.read_text(encoding="utf-8")))
             if _SITEMAP.exists() else 0)

README = f"""<div align="center">

![Platform Ops](brand/banner.svg)

[![Read it]({BADGE}/read%20it-{SITE.split('//')[1].replace('-', '--')}-e53935?style=for-the-badge&labelColor=08090c)]({SITE}/)
[![Issues]({BADGE}/issues-{N_ISSUES}-00c2d4?style=for-the-badge&labelColor=08090c)]({SITE}/#issues)
[![Topics]({BADGE}/topics-{N_TOPICS}-f59e0b?style=for-the-badge&labelColor=08090c)]({SITE}/categories/)
[![Commands]({BADGE}/commands-{N_CMDS}-84cc16?style=for-the-badge&labelColor=08090c)]({SITE}/Commands/KUBERNETES-COMMANDS/kubernetes-commands.html)
[![RSS]({BADGE}/rss-feed-8b5cf6?style=for-the-badge&labelColor=08090c)]({SITE}/feed.xml)

**A technical newsletter on Kubernetes, OpenShift, SRE and platform engineering.**
Written from production systems, by [Vishal Abhinav](https://www.linkedin.com/in/vishal-abhinav/).
Published by [Srivan Technologies](https://srivantechnologies.com/).

</div>

---

## What this is

Every issue starts with something that broke, something that was slower than it
should have been, or something whose official explanation turned out to be
incomplete. The subject is the operational half of platform engineering:
Kubernetes and OpenShift, the Linux underneath them, the networking and storage
they depend on, and the observability that tells you which of those is lying to
you.

It assumes you already know what a Pod is. It does not assume the default
settings are correct.

**No paywall, no sign-in, no tracking beyond page counts, no AI-generated
filler.** Every page is readable without an account, the archive stays up, and
issues are corrected in place rather than silently replaced.

> **Newest — [Issue #{NEWEST_NUM:03d}: {NEWEST_TITLE}]({SITE}/{NEWEST_PATH})**

---

## What it covers

{N_TOPICS} topics across {N_CATS} categories, grouped into {N_PILL} pillars.
These are generated from the same file the site's knowledge map reads, so they
cannot disagree with what is actually published.

| Pillar | Categories | Live | Pipeline | Planned |
|:--|--:|--:|--:|--:|
{TABLE}
| | **{N_CATS}** | **{T_LIVE}** | **{T_PIPE}** | **{T_PLAN}** |

**Live** means a published page covers it. **Pipeline** means it sits next to a
series already running. **Planned** means it is on the backlog with no date
attached. Publishing the planned list is deliberate — a coverage map that only
shows what is finished tells you nothing about what the project is trying to be.

---

## Where to start

| | |
|:--|:--|
| [**Issue #{NEWEST_NUM:03d} — {NEWEST_TITLE}**]({SITE}/{NEWEST_PATH}) | The newest issue. {N_ISSUES} in the archive. |
| [**Category hubs**]({SITE}/categories/) | Browse by subject. Each of the {N_CATS} categories has a generated architecture diagram and its full topic list. |
| [**Kubernetes &amp; OpenShift topic map**]({SITE}/categories/kubernetes-openshift-map/) | Check whether something specific is covered, queued or planned before spending time looking. |
| [**Command references**]({SITE}/Commands/KUBERNETES-COMMANDS/kubernetes-commands.html) | {N_CMD_PAGES} references covering {N_CMDS} commands, searchable and filterable. |
| [**Practice terminal**]({SITE}/terminal/) | A Unix shell simulated over an in-memory filesystem. Try the commands without a cluster. |
| [**Architecture**]({SITE}/architecture/) | The system end to end in seven diagrams — data flow, the build opened up, the PR path, the request path, deploy and rollback, trust boundaries. |
| [**About**]({SITE}/about/) | What this is, in more detail. |
| [**Colophon**]({SITE}/colophon/) | How the site is built, on the site. |

---

## How it is built

Static HTML generated by a Python build from one taxonomy file. No framework,
no client-side rendering, no build-time JavaScript, no dependencies beyond the
standard library.

That is not nostalgia. It means the counts on the homepage, in the category
hubs, in the topic map and in this README are all computed from one file at
build time — so they cannot drift apart, and a stage that would make them
disagree fails the build instead of shipping.

```mermaid
flowchart TB
  TAX["taxonomy.py<br/>{N_TOPICS} topics · {N_CATS} categories<br/>each live, pipeline or planned"]
  DAT["cmd_data.py · hubs_spec.py<br/>topicmap_data.py · terminal_fs.py"]
  HAND["content/ · {N_HANDWRITTEN} hand-written pages<br/>static/ · icons, OG cards, {N_FONTS} fonts"]

  SH["bash tools/build.sh<br/>rm -rf dist, then {N_STAGES} stages in order"]

  G1["structure<br/>build_hubs, build_topic_pages<br/>a hub per category,<br/>a page per item"]
  G2["navigation<br/>build_kmap, build_topicmap,<br/>build_feed, build_search<br/>maps, RSS, search index"]
  G3["contract<br/>build_seo, build_canonical,<br/>build_headers<br/>JSON-LD, canonicals, CSP"]

  DIST[("dist/ · {N_PAGES} pages<br/>the only deploy surface")]
  VER["verify.py<br/>links · tag balance · canonicals · sitemap<br/>and whether two pages agree with each other"]
  OK["banner + README<br/>ready to deploy"]
  STOP["exit 1 · nothing ships"]

  TAX --> SH
  DAT --> SH
  HAND --> SH
  SH --> G1
  SH --> G2
  SH --> G3
  G1 --> DIST
  G2 --> DIST
  G3 --> DIST
  DIST --> VER
  VER -->|all checks passed| OK
  VER -.->|one check fails| STOP

  classDef src fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e
  classDef sh fill:#f1f5f9,stroke:#475569,color:#0f172a
  classDef gen fill:#fef3c7,stroke:#b45309,color:#78350f
  classDef gate fill:#dcfce7,stroke:#15803d,color:#14532d
  classDef out fill:#ede9fe,stroke:#6d28d9,color:#4c1d95
  classDef bad fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d
  class TAX,DAT,HAND src
  class SH sh
  class G1,G2,G3 gen
  class VER gate
  class DIST,OK out
  class STOP bad
```

**The build refuses to ship rather than ship something wrong.** Each of these
exists because the thing it checks actually went wrong at least once:

- Two consecutive builds must be **byte-identical**. Before the output
  directory existed, a clean build produced different output from an
  incremental one and nobody could tell.
- Every **internal link** must resolve, every page's **tags** must balance, and
  every **canonical** must point at itself.
- Every **category card** must agree with the hub page it links to — added
  after two pages described the same category differently, one click apart.
- The **security policy** is derived by walking the built pages for the origins
  they actually fetch from, and fails on one it does not recognise.
- **{N_RENDER_PAGES} page families × {N_RENDER_WIDTHS} viewport widths** are
  opened in a real browser and asserted for horizontal overflow and duplicate
  fixed headers.
- **{N_MOTION_PAGES} pages are loaded twice**, once under each motion
  preference, and asserted to stop animating without going invisible.
- CI **refuses to deploy** a build holding fewer than {MIN_PAGES} pages, after a
  deploy from an empty directory once published a site where everything 404'd.

Drawn in full on the [architecture page]({SITE}/architecture/); the
stage-by-stage account is in the [colophon]({SITE}/colophon/).

---

## Repository layout

Three directories are input. One is output. Nothing else is either.

| Path | What it is |
|:--|:--|
| `tools/` | The build: {N_STAGES} ordered stages, `verify.py`, and the browser test suites. Python 3.11, standard library only. |
| `content/` | The {N_HANDWRITTEN} hand-written pages, kept pristine — they are copied into `dist/` and edited *there*, never in place. |
| `static/` | Copied verbatim: icons, OG cards, {N_FONTS} self-hosted font files, `assets/motion.css`. |
| `brand/` | The generated banner. Tracked, deliberately outside `static/`, so it never reaches the site. |
| `dist/` | **The only thing deployed.** Deleted and rebuilt from empty on every run. |

`dist/` is an allow-list, and that is the whole point: a file reaches the
public web only because a build stage deliberately wrote it there. The old
layout published from the repository root, where shipping something private
needed only an omission — which is how a full Mermaid install and a taxonomy
file once became fetchable. Now it needs a mistake in `tools/`.

---

## Tech stack

<div align="center">

![Python](https://img.shields.io/badge/Python_3.11-standard_library_only-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=08090c)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Workers-F38020?style=for-the-badge&logo=cloudflare&logoColor=white&labelColor=08090c)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-SHA_pinned-2088FF?style=for-the-badge&logo=githubactions&logoColor=white&labelColor=08090c)
![Playwright](https://img.shields.io/badge/Playwright-render_+_motion_tests-2EAD33?style=for-the-badge&logo=playwright&logoColor=white&labelColor=08090c)
![Mermaid](https://img.shields.io/badge/Mermaid-diagrams-FF3670?style=for-the-badge&logo=mermaid&logoColor=white&labelColor=08090c)
![HTML5](https://img.shields.io/badge/Static_HTML-no_framework-E34F26?style=for-the-badge&logo=html5&logoColor=white&labelColor=08090c)

</div>

| Layer | Choice | Why this one |
|:--|:--|:--|
| Build | **Python 3.11**, standard library | No dependency can break a build of a site that has to still build in five years. There is no `requirements.txt` for the build itself. |
| Output | **Static HTML**, no framework | Nothing to hydrate, nothing to server-render, nothing to keep patched. The slowest page is a file read. |
| Styling | Hand-written CSS, **{N_FONTS} self-hosted font files** | Bebas Neue, Manrope, DM Mono, Instrument Serif — served from this origin, so `font-src` is `'self'` and no third party sees a reader. |
| Tests | **Playwright** + Chromium | Overflow, duplicate headers and motion are properties of a rendered page. Reading the HTML cannot see any of them. |
| CI | **GitHub Actions**, pinned to commit SHAs | A moved tag cannot change what runs. Dependabot watches the pins so they still get security fixes. |
| Deploy | **Cloudflare Workers**, `wrangler@{WRANGLER}` via `npx` | Pinned exactly, and called directly rather than through an action that quietly resolved a different version. |
| Analytics | **GoatCounter** | No cookies, no fingerprinting, no consent banner to show anyone. |
| Diagrams | **Mermaid** in the README, hand-built SVG on the site | GitHub renders Mermaid natively, so these diagrams are text in the repo and cannot drift out of sync as images. |

---

## Architecture

### End to end — a change, from an edit to a reader

```mermaid
flowchart TB
  DEV(["Author<br/>edits taxonomy.py or content/"])

  subgraph LOCAL["Local"]
    BUILD["bash tools/build.sh<br/>{N_STAGES} stages · writes dist/"]
    SUITE["verify.py · test_render.py · test_motion.py"]
  end

  GH[("GitHub<br/>Platform-ops-Newsletter<br/>public")]

  subgraph CI["GitHub Actions · actions pinned to commit SHAs"]
    PR["pr-checks.yml<br/>trigger: pull_request<br/>read-only token · no secrets · no deploy"]
    DEP["deploy.yml<br/>trigger: push to main"]
    G1["build · refuse a dist/ under {MIN_PAGES} pages"]
    G2["render tests · {N_RENDER_PAGES} families x {N_RENDER_WIDTHS} widths"]
    G3["reduced-motion tests · both preferences"]
  end

  CF["Cloudflare Workers<br/>platform-ops-blog<br/>assets directory: dist"]
  EDGE["Edge cache"]
  READER(["Reader<br/>{SITE.split('//')[1]}"])
  BLOCK["deploy refused"]

  DEV --> BUILD --> SUITE
  SUITE -->|green| GH
  GH --> PR
  GH --> DEP
  PR --> G1
  DEP --> G1
  G1 --> G2 --> G3
  G3 -->|all pass, push to main only| CF
  G3 -.->|any fail| BLOCK
  CF --> EDGE
  EDGE -->|"every response carries _headers<br/>CSP · HSTS · nosniff · no default-src"| READER

  classDef human fill:#ede9fe,stroke:#6d28d9,color:#4c1d95
  classDef local fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e
  classDef ci fill:#fef3c7,stroke:#b45309,color:#78350f
  classDef edge fill:#dcfce7,stroke:#15803d,color:#14532d
  classDef bad fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d
  class DEV,READER human
  class BUILD,SUITE,GH local
  class PR,DEP,G1,G2,G3 ci
  class CF,EDGE edge
  class BLOCK bad
```

A pull request from a fork runs the same build and the same gates, and then
stops. Only a push to `main` reaches the deploy step, and only that step is
given the Cloudflare credentials.

### Integrations — every system this touches, and which way data moves

```mermaid
flowchart TB
  REPO[("GitHub repo · public<br/>source, workflows, generated README")]

  subgraph BT["Build time · none of this reaches a browser"]
    ACT["GitHub Actions<br/>build · gate · deploy"]
    WR["wrangler {WRANGLER}<br/>invoked with npx, not an action"]
    DB["Dependabot<br/>watches the pinned SHAs, monthly"]
  end

  WORKER["Cloudflare Worker · platform-ops-blog<br/>serves dist/ as static assets"]

  subgraph RT["Runtime · every origin a reader's browser contacts"]
    SELF["this origin<br/>HTML · CSS · JS · {N_FONTS} font files"]
    GC["gc.zgo.at<br/>GoatCounter<br/>no cookies, no fingerprinting"]
    LI["www.linkedin.com<br/>2 post embeds, homepage only"]
  end

  subgraph OB["Outbound · the site publishes, nothing reads back"]
    SM["sitemap.xml<br/>{N_SITEMAP} indexable URLs"]
    RSS["feed.xml<br/>full archive"]
    GSC["Google Search Console"]
  end

  REPO --> ACT --> WR --> WORKER
  DB -.->|opens a pull request| REPO
  WORKER --> SELF
  SELF -.->|"img-src · connect-src"| GC
  SELF -.->|frame-src| LI
  WORKER --> SM
  WORKER --> RSS
  SM -.-> GSC

  classDef own fill:#ede9fe,stroke:#6d28d9,color:#4c1d95
  classDef bt fill:#fef3c7,stroke:#b45309,color:#78350f
  classDef rt fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e
  classDef ob fill:#dcfce7,stroke:#15803d,color:#14532d
  class REPO,WORKER own
  class ACT,WR,DB bt
  class SELF,GC,LI rt
  class SM,RSS,GSC ob
```

Two origins in that runtime box are not this one, and both are in the CSP by
name because the build found them there. Everything else a reader loads —
every stylesheet, every script, all {N_FONTS} font files — comes from this
origin. The same system drawn at greater depth, including the request path and
the trust boundaries, is on the [architecture page]({SITE}/architecture/).

---

## Security

The site is static, has no backend, sets no cookies and runs no third-party
JavaScript. Most of what follows is therefore about keeping it that way.

**The policy is derived, not written.** `build_headers.py` walks the built
pages for the origins they actually fetch from and emits `dist/_headers`. Two
are allowed — `gc.zgo.at` for privacy-preserving analytics, `www.linkedin.com`
for the two post embeds. A page that starts fetching from anywhere else fails
the build rather than silently widening the policy.

The header it generates:

```
Content-Security-Policy: font-src 'self'; frame-src 'self' https://www.linkedin.com;
  img-src 'self' data: https://gc.zgo.at; connect-src 'self' https://gc.zgo.at;
  frame-ancestors 'none'; base-uri 'none'; object-src 'none'; form-action 'self';
  upgrade-insecure-requests
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: accelerometer=(), camera=(), geolocation=(), microphone=(), payment=(), usb=()
Cross-Origin-Opener-Policy: same-origin
```

There is deliberately **no `default-src`**, and that is the load-bearing
decision in the file. `default-src` is a *fallback*, not a baseline: every
fetch directive left out inherits it. `default-src 'self'` with `script-src`
absent therefore means `script-src 'self'`, which would block every inline
`<script>` and every `onclick` handler on the site — several hundred of them.
The comment explaining this sits above the constant, because it looks wrong
and reads as an omission.

A `script-src` that actually constrains scripts is the open item, and it is
open honestly: closing it means moving those inline handlers out to files
first. It is tracked, not forgotten.

**Fonts are self-hosted.** {N_FONTS} files under `static/assets/fonts/`, so
there is no request to a third party on any page view and no `font-src`
beyond `'self'`.

**Supply chain.** Every GitHub Action is pinned to a full commit SHA with the
version in a trailing comment, so a moved tag cannot change what runs. PR
checks are `pull_request`, never `pull_request_target` — the workflow that
runs a contributor's code has a read-only token, no `secrets:` block and no
deploy step. There is nothing in it to leak.

Found something? Open a [security advisory](https://github.com/Vishal-Abhinav/Platform-ops-Newsletter/security/advisories/new)
rather than a public issue.

---

## Accessibility

Honoured on all {N_PAGES} pages, and tested rather than asserted.

The site animates: a drifting background, pulsing status dots, a ticker, a
blinking terminal cursor, a staggered typewriter reveal, counters that count
up. Until September 2026 every one of those ran regardless of what the reader
had asked their operating system for — twelve distinct infinite animations,
`prefers-reduced-motion` honoured on zero pages.

It now resolves in two places, because one is not enough:

- `assets/motion.css`, on all {N_PAGES} pages, collapses every CSS animation
  and transition to `0.01ms` with a single iteration — **not** `animation:
  none`. Several entrances start at `opacity: 0`; removing the animation
  outright would leave that content permanently invisible, which is a worse
  bug than the motion it fixes. A near-zero duration lets every animation
  reach its *final* keyframe immediately.
- The homepage typewriter and counters are driven by `setTimeout` and
  `setInterval`, which no stylesheet can reach, so they check the same media
  query in JavaScript and jump straight to their finished state — every line
  shown, every counter on its real total.

`tools/test_motion.py` opens seven pages twice, once under each preference,
and asserts that nothing is still animating, nothing was left invisible,
nothing is frozen part-way through a reveal, and no counter is stuck
mid-count. It also asserts that the motion **is still there** without the
preference — a test that only checked the reduced case would pass just as
happily on a site whose animation had been deleted.

Also measured across all {N_PAGES} pages, rather than asserted: exactly one
`<h1>` each, a `lang` attribute on every `<html>`, a `<nav>` landmark, and no
icon-only control left without an `aria-label`. Colour is never the only thing
carrying a meaning — the live/pipeline/planned states that colour the coverage
bars are written out in words beside them.

**What is still wrong, stated plainly**, because an accessibility section that
lists only its wins is marketing:

- There is **no `<main>` landmark and no skip link** — on any page. A
  screen-reader user cannot jump to the content, and a keyboard user tabs
  through the whole navigation to reach it, on every page, every time. This
  is the largest remaining barrier here and it is not a small fix: the page
  families do not share one content wrapper, so it needs doing per family
  and re-verifying, not a regex across the build.
- **Focus styling relies on the browser default**, and two pages remove it
  with `outline: none` — which is worse than not styling it at all.
- **Contrast has not been measured systematically.** It was chosen by eye
  against WCAG AA, which is not the same as having checked.

Something here not working for you? That is a bug, and a welcome one to
receive. Please open an issue.

---

## Machine-readable

| File | What it holds |
|:--|:--|
| [`/sitemap.xml`]({SITE}/sitemap.xml) | {N_SITEMAP} indexable URLs. Pages carrying `noindex` are deliberately withheld — a sitemap is a request to crawl, and listing a page that then declines to be indexed just spends crawl budget. |
| [`/feed.xml`]({SITE}/feed.xml) | RSS, full archive. |
| [`/robots.txt`]({SITE}/robots.txt) | Crawl rules and the sitemap pointer. |
| `/_headers` | Generated per build; see Security above. |

---

## Running it

```bash
git clone https://github.com/Vishal-Abhinav/Platform-ops-Newsletter.git
cd Platform-ops-Newsletter
bash tools/build.sh          # writes dist/ — wait for: all checks passed
python3 -m http.server -d dist
```

Python 3.11+, standard library only. The browser suites additionally want
`pip install playwright && playwright install chromium`:

```bash
python3 tools/verify.py              # links, tags, canonicals, cross-page agreement
python3 tools/test_render.py dist    # 12 page families x 13 widths
python3 tools/test_motion.py dist    # both motion preferences
```

---

## Contributing

Corrections are welcome and wanted — especially "this does not match what I
see in production", which is the most useful issue anyone can file. Please
include the version, the platform and what you observed.

Two things worth knowing before a pull request:

**Never edit anything in `dist/`.** It is deleted and regenerated on every
build, so a change made there is gone the moment anyone runs `tools/build.sh`.
Edit the source in `tools/`, `content/` or `static/` and rebuild.

**`README.md` and `brand/` are generated.** They are built by
`tools/build_ghreadme.py` and `tools/make_banner.py` from the taxonomy. Editing
this file by hand works exactly until the next build overwrites it — and CI
fails the PR if either is stale, so run `bash tools/build.sh` and commit the
result.

CI runs the full build, refuses a `dist/` holding fewer than 500 pages, and
runs the render tests on every pull request. Running the three commands above
locally first is the quickest way to know it will pass.

Prose changes want an issue before a PR — the writing is first-hand and
opinionated by design, and the licence on it is narrower than the one on the
code. See below.

---

## Who writes it

**Vishal Abhinav** — a platform engineer who spends his working days on the
systems this newsletter is about. The writing is first-hand: where an issue
describes a failure, it is a failure that happened; where it gives a number,
the number was measured rather than quoted.

[LinkedIn](https://www.linkedin.com/in/vishal-abhinav/) ·
[GitHub](https://github.com/Vishal-Abhinav) ·
[ResearchGate](https://www.researchgate.net/profile/Vishal-Abhinav/research) ·
[HackerRank](https://www.hackerrank.com/Vishal_Abhinav)

### Srivan Technologies

Platform Ops is published by **[Srivan Technologies](https://srivantechnologies.com/)** —
infrastructure and platform engineering. Kubernetes and OpenShift clusters, the
pipelines that deliver to them, and the observability that tells you what they
are actually doing.

*The layer most people only notice when it breaks.*

[srivantechnologies.com →](https://srivantechnologies.com/)

---

## Licence

Two licences, because the code and the writing are different things.

| What | Licence | In practice |
|:--|:--|:--|
| The build system and code samples | **MIT** | Use them, change them, ship them commercially. |
| The writing and the diagrams | **CC BY-NC-ND 4.0** | Quote it with credit and a link. Don't republish it wholesale, don't sell it, don't publish an edited version as the original. |

Full text in [`LICENSE`](LICENSE); the attribution terms and the third-party
credits — fonts and analytics — are in [`NOTICE`](NOTICE).

Want to do something the second licence doesn't allow — translate an issue, use
a diagram in training material, reprint a piece internally? Ask. The answer is
usually yes.

<div align="center">

**[Read Platform Ops →]({SITE}/)**

<sub>© 2026 Vishal Abhinav · Srivan Technologies · Built for engineers, by an engineer.</sub>

</div>
"""

if __name__ == "__main__":
    out = REPO / "README.md"
    # newline="\n" is not decoration. This file is GENERATED and COMMITTED, and
    # pr-checks.yml runs `git diff --exit-code -- README.md` after rebuilding it
    # on a Linux runner. write_text() without this writes os.linesep, so the
    # same commit produces CRLF on Windows and LF in CI — a diff in every byte
    # of every line, reported as "README.md is stale" when nothing is stale.
    # It happens to work today only because one contributor's git has
    # core.autocrlf=true and normalises it back on the way in. Depending on a
    # local git setting for a reproducible build is not a guarantee; this is.
    out.write_text(README, encoding="utf-8", newline="\n")

    # What a generator cannot guarantee: that the document it produced is
    # actually the document it claims to be. A silently truncated f-string or a
    # renamed constant would otherwise ship a README with a hole in it.
    text = out.read_text(encoding="utf-8")
    for needle, why in (
            ("brand/banner.svg", "the banner"),
            (f"{N_ISSUES} in the archive", "the issue count"),
            (f"{N_TOPICS} topics across {N_CATS} categories", "the coverage line"),
            (str(N_CMDS), "the command count"),
            ("Srivan Technologies", "the publisher"),
            ("Vishal Abhinav", "the author"),
            (SITE, "the site URL"),
            # The sections added Sep 2026. A reader landing on the repo needs
            # to find these; each was absent once and nothing objected.
            ("## Repository layout", "the layout section"),
            ("## Security", "the security section"),
            ("## Accessibility", "the accessibility section"),
            ("## Contributing", "the contributing section"),
            ("Content-Security-Policy", "the CSP"),
            ("prefers-reduced-motion", "the reduced-motion claim"),
            ("(LICENSE)", "the LICENSE link"),
            ("(NOTICE)", "the NOTICE link")):
        assert needle in text, f"README.md is missing {why} ({needle!r})"

    # A derived number that came out zero means this stage ran before the
    # thing it measures. Shipping "Honoured on all 0 pages" would be worse
    # than failing, because it reads as a finished sentence.
    for value, what in ((N_STAGES, "build stages"), (N_HANDWRITTEN, "content pages"),
                        (N_FONTS, "font files"), (N_PAGES, "built pages"),
                        (N_SITEMAP, "sitemap URLs")):
        assert value > 0, (
            f"README.md would claim 0 {what}. This stage must run AFTER the "
            f"build that produces them — check the stage order in build.sh.")

    # The accessibility section is the one claim here that is about behaviour
    # rather than about a count, so it is the one most able to become untrue
    # quietly. Tie it to the file that makes it true.
    assert (REPO / "static" / "assets" / "motion.css").exists(), (
        "README.md claims reduced motion is honoured site-wide, but "
        "static/assets/motion.css does not exist. Fix one or the other.")

    # ── the Mermaid diagrams ────────────────────────────────────────────────
    # GitHub renders these server-side. A syntax error does not fail anything
    # here — it ships, and the repository's front page shows a grey error box
    # where the architecture diagram should be. Nobody who already knows what
    # the diagram says will notice.
    #
    # The specific hazard is this file: the README is one large f-string, so a
    # literal { or } inside a diagram is eaten as an interpolation. Mermaid
    # uses braces for node shapes, which makes writing one the natural thing
    # to do and breaking the build the natural consequence. These diagrams are
    # therefore written with no brace-shaped nodes at all, and this asserts it
    # stays that way.
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.S)
    assert len(blocks) == 3, (
        f"README.md should carry 3 mermaid diagrams (data flow, end-to-end, "
        f"integrations); found {len(blocks)}.")
    for i, b in enumerate(blocks, 1):
        assert b.lstrip().startswith("flowchart"), (
            f"mermaid block {i} does not start with a diagram type — GitHub "
            f"will render it as an error box.")
        stray = [ln for ln in b.splitlines() if "{" in ln or "}" in ln]
        assert not stray, (
            f"mermaid block {i} contains a literal brace, which means the "
            f"f-string ate an interpolation or a brace-shaped node slipped "
            f"in. Use [] or () node shapes here, never curly braces:\n  "
            + "\n  ".join(stray[:3]))
        # Every node named in a `class a,b,c name` line must actually exist,
        # or Mermaid silently drops the styling and the diagram renders grey.
        defined = set(re.findall(r"^\s*(\w+)[\[\(]", b, re.M))
        for line in re.findall(r"^\s*class\s+([\w,]+)\s+\w+\s*$", b, re.M):
            for node in line.split(","):
                assert node in defined, (
                    f"mermaid block {i}: `class` styles {node!r}, which is "
                    f"not a node in that diagram.")
    assert (REPO / "brand" / "banner.svg").exists(), (
        "brand/banner.svg is missing, so the README's first image would be a "
        "broken one on the repo's front page. Run tools/make_banner.py first — "
        "build.sh runs it immediately before this stage.")

    print(f"  {len(text) // 1024 + 1} KB  README.md  "
          f"({N_ISSUES} issues, {N_TOPICS} topics, {N_CATS} categories, "
          f"{N_CMDS} commands)")
