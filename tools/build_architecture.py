#!/usr/bin/env python3
"""Build architecture/index.html — the system, drawn, for someone evaluating it.

WHY A SEPARATE PAGE FROM THE COLOPHON
-------------------------------------
The colophon answers "how is this made" for a reader who already likes the
site: one dataflow picture, the stage list, the assertions. That is a
craft note.

This page answers a different question, asked by a different person: "what IS
this system, end to end, and would I trust it." It needs the boundaries drawn,
the data flow followed, the contribution path stated, the failure modes named
and the security posture shown. Those are seven diagrams, not one, and folding
them into the colophon would bury both documents.

EVERY DIAGRAM IS DRAWN WITH THE SAME PRIMITIVES THE REST OF THE SITE USES —
diagrams.detail(), diagrams.flow(), content_page.diagram(). Not because it is
less work (it is), but because a reader who has learned to read a deep-dive's
diagrams can read these without learning a second visual language.

AUTHORING RULE, unchanged and load-bearing: every edge label must be something
you could act on — a file, a port, an exit code, a count. "deploys" is not a
label; "wrangler deploy dist/ · 879 files" is.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import re                                                        # noqa: E402
import diagrams                                                  # noqa: E402
from content_page import CSS, render, section, table, note, diagram  # noqa: E402
from taxonomy import PILLARS, cat_stats                          # noqa: E402
from build_feed import ISSUES                                    # noqa: E402
from cmd_data import ALL as CMD_SPECS                            # noqa: E402
from siteconf import BASE_HOST                                   # noqa: E402

OUT = ROOT / "architecture"

# ── the numbers, from the same places every other page gets them ────────────
T_LIVE = T_PIPE = T_PLAN = 0
for _p, _cats in PILLARS:
    for _c, _i, _t in _cats:
        l, p, n = cat_stats(_t)
        T_LIVE += l; T_PIPE += p; T_PLAN += n
N_TOPICS = T_LIVE + T_PIPE + T_PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])
N_PAGES = len([q for q in ROOT.rglob("*.html")
               if "tools" not in q.parts and q.name != "kit-template.html"])

# Stage count read off build.sh rather than typed, for the same reason as
# everywhere else: the list moves, and a number that describes it must move too.
_SH = (TOOLS / "build.sh").read_text(encoding="utf-8")
N_STAGES = len(re.findall(r"^\s*python3 tools/(\w+)\.py", _SH, re.M))


# ═══════════════════════════════════════════════════════════════════════════
# 1. THE SYSTEM, END TO END
# ═══════════════════════════════════════════════════════════════════════════
SYSTEM = diagram([
    ("Source of truth", [
        ("taxonomy.py", "core"),
        ("issue register", "core"),
        ("command corpus", "core"),
        ("reader checklist", "core"),
    ]),
    ("Authored", [
        ("content/ 25 pages", "calm"),
        ("static/ assets + fonts", "calm"),
        ("index.base.html", "calm"),
    ]),
    ("Build", [
        (f"build.sh {N_STAGES} stages", "warm"),
        ("page generators", "warm"),
        ("whole-site passes", "warm"),
    ]),
    ("Gates", [
        ("verify.py", "go"),
        ("test_render.py", "go"),
        ("origin audit", "go"),
        ("empty-build gate", "go"),
    ]),
    ("Delivery", [
        ("GitHub Actions", "hot"),
        ("wrangler deploy dist/", "hot"),
    ]),
    ("Edge", [
        (f"Cloudflare Worker", "core"),
        ("_headers CSP HSTS", "core"),
    ]),
], label="What the system is made of, bottom to top")


# ═══════════════════════════════════════════════════════════════════════════
# 2. DATA FLOW — one topic, from the file it is declared in to the reader
# ═══════════════════════════════════════════════════════════════════════════
DATAFLOW = diagrams.flow([
    ("taxonomy.py", "core", None),
    ("generator", "warm", "import PILLARS"),
    ("dist/*.html", "warm", "write page"),
    ("whole-site pass", "warm", "inject nav, search, JSON-LD, fonts"),
    ("verify.py", "go", "read back and assert"),
    ("sitemap.xml", "go", "if not noindex"),
    ("wrangler", "hot", "upload changed assets"),
    ("reader", "core", ":443 · cached 1 week"),
], label="One topic, declared once, ending up on a page", per_row=4)


# ═══════════════════════════════════════════════════════════════════════════
# 3. THE BUILD, OPENED UP
# ═══════════════════════════════════════════════════════════════════════════
BUILD = diagrams.detail(
    "tools/build.sh",
    [
        ("Seed", [
            ("rm -rf dist/", "hot", "rebuilt from empty every run"),
            ("cp content/ static/", "calm", "sources copied, never mutated"),
        ]),
        ("Content generators", [
            ("build_hubs", "warm", "45 category hubs — runs twice"),
            ("build_k8s / openshift / foundation", "warm", "the deep-dives"),
            ("build_commands", "warm", f"{N_CMDS} commands"),
            ("build_topicmap", "warm", "the 942-item checklist"),
            ("build_topic_pages", "warm", "one honest page per unwritten item"),
        ]),
        ("Aggregation — counts the finished site", [
            ("build_colophon", "calm", "stage list, page count"),
            ("build_about", "calm", "derived from taxonomy, not the README"),
            ("build_architecture", "calm", "this page"),
        ]),
        ("Whole-site passes", [
            ("build_nav", "core", "mega-menu into every page"),
            ("build_search", "core", "index + wiring"),
            ("build_seo", "core", "JSON-LD, icons, font stylesheet"),
            ("build_canonical", "core", "one origin, everywhere"),
        ]),
        ("Gates", [
            ("build_headers", "go", "CSP derived from what pages fetch"),
            ("verify.py", "go", "links, nesting, page agreement, sitemap"),
        ]),
    ],
    label=f"{N_STAGES} stages, and why the order is load-bearing",
    inputs=("taxonomy.py", "content/", "static/"),
    outputs=("dist/ — 879 files", "_headers", "sitemap.xml"))


# ═══════════════════════════════════════════════════════════════════════════
# 4. PULL REQUEST FLOW
# ═══════════════════════════════════════════════════════════════════════════
PR_FLOW = diagrams.flow([
    ("fork", "calm", None),
    ("branch", "calm", "git checkout -b"),
    ("edit tools/", "warm", "source only — dist/ is untracked"),
    ("bash tools/build.sh", "warm", "must print: all checks passed"),
    ("open PR", "core", "against main"),
    ("pr-checks.yml", "go", "build + verify + render, NO secrets"),
    ("review", "core", "maintainer approves"),
    ("merge to main", "hot", "squash"),
    ("deploy.yml", "hot", "build → gate → render → wrangler"),
], label="A change, from a fork to the live site", per_row=3)


# ═══════════════════════════════════════════════════════════════════════════
# 5. THE REQUEST PATH
# ═══════════════════════════════════════════════════════════════════════════
REQUEST = diagrams.flow([
    ("reader", "core", None),
    ("DNS", "plain", f"{BASE_HOST} → Cloudflare"),
    ("edge PoP", "core", ":443 TLS 1.3"),
    ("Worker static assets", "warm", "path → file in dist/"),
    ("_headers", "go", "CSP · HSTS · nosniff applied"),
    ("HTML + assets", "core", "assets/* cached 604800s"),
], label="What happens between a click and a rendered page", per_row=3)


# ═══════════════════════════════════════════════════════════════════════════
# 6. DEPLOY AND ROLLBACK
# ═══════════════════════════════════════════════════════════════════════════
DEPLOY = diagrams.flow([
    ("push to main", "core", None),
    ("checkout", "plain", "actions/checkout @ SHA"),
    ("build", "warm", "bash tools/build.sh"),
    ("empty-build gate", "go", "find dist -name '*.html' | wc -l ≥ 500"),
    ("render tests", "go", "11 pages x 13 widths, real browser"),
    ("wrangler deploy", "hot", "npx --yes wrangler@4.134.0"),
    ("live", "core", "new version id"),
    ("wrangler rollback", "hot", "any prior version, on failure"),
], label="Every gate between a push and production — and the way back",
    per_row=4)


# ═══════════════════════════════════════════════════════════════════════════
# 7. TRUST BOUNDARIES
# ═══════════════════════════════════════════════════════════════════════════
TRUST = diagrams.detail(
    "What is public, what is not",
    [
        ("Public by design", [
            ("the repository", "calm", "sources readable, not writable"),
            ("the rendered site", "calm", "879 pages, crawlable"),
            ("Search Console tokens", "calm", "served in a meta tag anyway"),
        ]),
        ("Secret — never in the repo", [
            ("CLOUDFLARE_API_TOKEN", "hot", "GitHub Actions secret"),
            ("CLOUDFLARE_ACCOUNT_ID", "hot", "GitHub Actions secret"),
        ]),
        ("What can execute with those secrets", [
            ("push to main", "go", "maintainer only"),
            ("workflow_dispatch", "go", "maintainer only"),
            ("a fork's pull request", "plain", "NEVER — no pull_request_target"),
        ]),
        ("Enforced at the edge", [
            ("frame-ancestors 'none'", "go", "clickjacking"),
            ("base-uri 'none'", "go", "an injected base tag"),
            ("object-src 'none'", "go", "plugin content"),
            ("HSTS 2y preload", "go", "downgrade"),
        ]),
    ],
    label="Where the boundary is, and what crosses it",
    inputs=("contributor", "reader", "crawler"),
    outputs=("Cloudflare", "GitHub"))


# ═══════════════════════════════════════════════════════════════════════════
# THE PAGE
# ═══════════════════════════════════════════════════════════════════════════
S_OVERVIEW = section(
    "Overview", "A content pipeline with a gate at every seam",
    f"{N_ISSUES} issues, {N_TOPICS} topics across {N_CATS} categories and "
    f"{N_CMDS} commands, rendered into {N_PAGES} static pages by "
    f"{N_STAGES} build stages and published to one origin. No framework, no "
    f"client-side rendering, no runtime dependencies.",
    diagrams.figures([
        ("System", "What is this made of?", SYSTEM,
         "Source of truth at the bottom, reader at the top. Everything above "
         "the first band is derived — none of it is edited by hand, and a "
         "stage that would let two derived values disagree fails the build.")])
    + "<p>The shape matters more than the stack. Four data files describe the "
      "subject; everything a reader sees is computed from them at build time. "
      "That is why the count on the homepage, the count on a category hub and "
      "the count in the repository's README cannot drift apart — they are the "
      "same expression evaluated three times, not three numbers maintained in "
      "three places.</p>")

S_DATA = section(
    "Data flow", "One topic, from declaration to reader",
    "Follow a single topic through the system. Every hop is a real file "
    "boundary, and the label on each edge is the operation that crosses it.",
    diagrams.figures([
        ("Data flow", "How does one topic become a page?", DATAFLOW,
         "The read-back at verify.py is the important hop. The build does not "
         "trust what it just wrote — it reads the rendered HTML and asserts "
         "against it, which is how a page that claims 35 topics while "
         "rendering 34 gets caught.")])
    + note("info", "Why the sitemap is a fork in the path",
           "<p>784 of the pages are honest placeholders for checklist items "
           "not yet written, marked <code>noindex,follow</code>. They are real "
           "pages with real internal links, so they belong in the site — but a "
           "sitemap is a request to crawl, and asking a crawler to fetch 784 "
           "URLs that then decline to be indexed wastes the crawl budget of a "
           "site that has very little. So the sitemap carries the "
           "95 indexable ones and the rest stay linked but unsubmitted.</p>"))

S_BUILD = section(
    "The build", "Opened up",
    f"{N_STAGES} stages in a fixed order. The order is not stylistic: a stage "
    f"that counts or classifies against the filesystem must run after the "
    f"stages that write what it counts.",
    diagrams.figures([
        ("Build", "What runs, in what order, reading what?", BUILD,
         "build_hubs appears once but runs twice. It emits the stylesheet a "
         "later stage needs, so it must come early; it also prints counts that "
         "are only right once the pages it classifies exist. One pass cannot "
         "satisfy both.")])
    + "<p>Before the output directory existed, this ordering problem was "
      "invisible. The build wrote into the repository, so every counting stage "
      "read the <em>previous</em> build's output and was quietly one build "
      "behind. Wiping <code>dist/</code> on every run exposed it immediately: "
      "33 checklist items dropped from Live to Planned because the pages "
      "proving they were covered had not been generated yet.</p>")

S_PR = section(
    "Contribution", "Pull request flow",
    "What happens to a change between a fork and the live site — and, "
    "deliberately, what does not happen.",
    diagrams.figures([
        ("PR flow", "How does a change get in?", PR_FLOW,
         "Only source is edited. dist/ is untracked, so a pull request is "
         "never an 800-file diff — it is the change itself.")])
    + note("warn", "A fork's pull request never sees the deploy secrets",
           "<p>The deploy workflow triggers on <code>push</code> to main and "
           "<code>workflow_dispatch</code> only. There is no "
           "<code>pull_request</code> trigger and — the one that matters — no "
           "<code>pull_request_target</code>. That is the difference between a "
           "safe public CI pipeline and the attack that has drained plenty of "
           "real projects: a stranger's code never executes in a job holding "
           "the Cloudflare token.</p>"
           "<p>PR validation therefore runs as its own workflow with no "
           "secrets at all. It can build, verify and render — it cannot "
           "deploy, and it has nothing to leak.</p>"))

S_REQUEST = section(
    "Runtime", "The request path",
    "There is no application server. A request resolves to a file, and the "
    "only computation at request time is header attachment.",
    diagrams.figures([
        ("Request", "What happens between a click and a page?", REQUEST,
         "The headers are generated at build time by walking the built pages "
         "for the origins they actually fetch from — so the policy cannot "
         "permit something the site stopped using, or block something it "
         "started.")]))

S_DEPLOY = section(
    "Delivery", "Deploy, and the way back",
    "Push is the only action. Everything between it and production is "
    "automated, and every gate can stop it.",
    diagrams.figures([
        ("Deploy", "What can stop a bad build reaching readers?", DEPLOY,
         "The empty-build gate exists because a deploy from an empty output "
         "directory once published a site where every page 404'd. wrangler "
         "read zero files and reported success.")])
    + table(["Gate", "Catches", "What it looked like when it did not exist"],
            [("<b>all checks passed</b>", "broken links, unbalanced tags, wrong canonicals, pages that disagree",
              "All 878 canonicals named a host being retired"),
             ("<b>empty-build gate</b>", "a build that produced nothing",
              "A deploy published 0 files; the whole site 404'd"),
             ("<b>render tests</b>", "horizontal overflow, duplicate fixed headers",
              "Every page family scrolled sideways between 761px and 950px"),
             ("<b>origin audit</b>", "a page fetching from an unaccounted-for host",
              "Two LinkedIn iframes loaded on every homepage visit, unnoticed"),
             ("<b>wrangler rollback</b>", "anything the gates missed",
              "Used once, in anger, and it worked")]))

S_TRUST = section(
    "Security", "Trust boundaries",
    "The repository is public and the site is public. What is not public is "
    "exactly two values, and neither has ever been in the repository — a "
    "full-history scan confirms it.",
    diagrams.figures([
        ("Trust", "What crosses the boundary, and who can push it?", TRUST,
         "Sources being readable and sources being writable are different "
         "things. A public repo is read-only to everyone but the maintainer; "
         "visibility was never about who can change it.")])
    + "<p>One gap is left open deliberately rather than filled badly. The "
      "policy declares no <code>script-src</code>, because allowing the "
      "site's inline handlers would require <code>'unsafe-inline'</code> — a "
      "directive that scores well on a header scanner and stops approximately "
      "no XSS. There is no live vector to close: the search box escapes every "
      "interpolated value, nothing reads a query parameter, and there is no "
      "backend. A policy that overstates its own strength is worse than an "
      "honest gap.</p>")

SECTIONS = (S_OVERVIEW + S_DATA + S_BUILD + S_PR + S_REQUEST + S_DEPLOY
            + S_TRUST)

PAGER = ('<div class="pager">'
         '<a href="../colophon/index.html">← Colophon<b>How it is built</b></a>'
         '<a class="next" href="../about/index.html">About →'
         '<b>What this is</b></a></div>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n" + diagrams.CSS, encoding="utf-8")

html_out = render(
    slug="architecture",
    title="Architecture",
    tagline=("The system end to end: what it is made of, how one topic becomes "
             "a page, how a change gets in, and what stops a bad build "
             "reaching readers."),
    eyebrow="The system, drawn",
    crumbs=[("Home", "../index.html"), ("Architecture", None)],
    meta=[f"{N_STAGES} stages", f"{N_PAGES} pages", "7 diagrams", "no framework"],
    sections=SECTIONS,
    pager=PAGER,
    up="../",
    css="topic.css",
    canon="architecture/")

(OUT / "index.html").write_text(html_out, encoding="utf-8")

# A diagram page whose diagrams failed to render is a page of empty boxes, and
# nothing else here would notice.
n_svg = html_out.count("<svg")
assert n_svg >= 7, f"architecture: expected at least 7 diagrams, rendered {n_svg}"
print(f"  {len(html_out) // 1024:3d} KB  architecture/index.html  "
      f"({n_svg} diagrams, {N_STAGES} stages)")
