#!/usr/bin/env python3
"""Build colophon/index.html — how this site is put together, on the site.

The README has carried an Architecture section since it was written, but only
GitHub could render its Mermaid diagram, so a visitor to the site could not
see any of it. This page is that section, for readers.

It is NOT a second copy of the prose. The numbers come off the same taxonomy,
issue register and command corpus everything else does, and the diagram is the
SVG rendered from the README's own Mermaid source by make_arch_svg.py — so the
two documents cannot describe different sites.

That last part is enforced rather than hoped for: the sha256 of the Mermaid
source is committed next to the SVGs, and this build stage refuses to run if
the source has moved on. Editing the diagram and forgetting to re-render it
stops the build with an instruction instead of shipping a stale picture.
"""
import hashlib
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import re                                                     # noqa: E402
from content_page import CSS, render, section, table, note, term, esc   # noqa: E402
from taxonomy import PILLARS, cat_stats                        # noqa: E402
from build_feed import ISSUES                                  # noqa: E402
from siteconf import BASE_HOST                                 # noqa: E402
from cmd_data import ALL as CMD_SPECS                          # noqa: E402

OUT = ROOT / "colophon"
ARCH = ROOT / "assets" / "arch"
SRC_MD = TOOLS / "README.base.md"

# ── the numbers, from the same places every other page gets them ────────────
T_LIVE = T_PIPE = T_PLAN = 0
for _p, _cats in PILLARS:
    for _c, _i, _t in _cats:
        l, p, n = cat_stats(_t)
        T_LIVE += l; T_PIPE += p; T_PLAN += n
N_TOPICS = T_LIVE + T_PIPE + T_PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_PILL = len(PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])
N_PAGES = len([q for q in ROOT.rglob("*.html")
               if "tools" not in q.parts and q.name != "kit-template.html"])


# ── the diagram, checked against the source it was rendered from ────────────
def diagram_svgs():
    md = SRC_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```mermaid\n(.*?)\n```", md, re.S)
    assert len(blocks) == 1, (
        f"README.base.md: expected one mermaid block, found {len(blocks)}")
    want = hashlib.sha256(blocks[0].strip().encode("utf-8")).hexdigest()

    stamp = ARCH / "dataflow.sha256"
    assert stamp.exists(), (
        "assets/arch/dataflow.sha256 is missing — run:\n"
        "    python3 tools/make_arch_svg.py")
    have = stamp.read_text(encoding="utf-8").strip()
    assert have == want, (
        "The Mermaid diagram in tools/README.base.md has changed since the SVGs\n"
        "were rendered, so the site would show the old picture. Run:\n"
        "    python3 tools/make_arch_svg.py\n"
        f"  source now : {want[:16]}…\n"
        f"  rendered   : {have[:16]}…")

    out = {}
    for theme in ("light", "dark"):
        f = ARCH / f"dataflow-{theme}.svg"
        assert f.exists(), f"{f.relative_to(ROOT)} is missing — run make_arch_svg.py"
        out[theme] = f.read_text(encoding="utf-8")
    return out


SVG = diagram_svgs()

EXTRA_CSS = """
/* ─── COLOPHON: the rendered Mermaid diagram ─── */
.arch{margin:6px 0 4px;overflow-x:auto;padding-bottom:6px;}
.arch svg.arch-svg{width:100%;min-width:640px;height:auto;display:block;}
/* These must out-specify the rule above: ".arch svg.arch-svg" is (0,2,1) and
   sets display:block, so a (0,2,0) ".arch .arch-dark{display:none}" loses and
   BOTH diagrams render. Matching on svg.<class> keeps them even, and the
   later rule wins. */
.arch svg.arch-dark{display:none;}
html[data-theme="dark"] .arch svg.arch-light{display:none;}
html[data-theme="dark"] .arch svg.arch-dark{display:block;}
.arch-note{font-size:12.5px;color:var(--muted);margin-top:14px;font-style:italic;}
"""

BODY_DIAGRAM = (f'<div class="arch">{SVG["light"]}{SVG["dark"]}</div>'
                '<p class="arch-note">Rendered once at build time from the same '
                'Mermaid source the README uses — the page itself loads no '
                'diagramming library.</p>')

# ── stages, read off build.sh so the list cannot go stale ───────────────────
STAGE_NOTE = {
    "build_kmap": ("taxonomy + issue register",
                   "knowledge map, coverage terminal, hero counter, newest-issue links"),
    "build_features": ("—", "topic-request queue, analytics loader, RSS discovery"),
    "build_wire": ("taxonomy", "category-hub links, nav, licence line"),
    "build_readme": ("taxonomy + register + commands",
                     "the README map, badge, inventory, feature table, repo tree"),
    "build_library": ("taxonomy", "the reference-library listing"),
    "build_sticky": ("—", "pins the Latest Issues panel beside the map"),
    "build_author": ("linkedin_posts.py", "author profile + LinkedIn column"),
    "build_hubs": ("taxonomy + hubs_spec.py", "the category hubs, diagrams and cross-links"),
    "build_topicmap": ("topicmap_data.py (46-group reader topic list)",
                       "the Kubernetes & OpenShift Complete Topic Map, every item marked "
                       "live / pipeline / planned"),
    "build_hub_topicmap": ("the same 46-group list, split 1-24 / 25-46",
                           "folds the reader's list onto categories/kubernetes/ and "
                           "categories/openshift/ directly, not just the standalone page"),
    "build_topic_pages": ("build_topicmap.classify()",
                          "one honest page per checklist item that isn't Live yet, so a "
                          "Pipeline/Planned chip links somewhere instead of dead-ending"),
    "build_foundation": ("fnd_a.py, fnd_b.py", "the Foundation deep-dives"),
    "build_openshift": ("ocp_a.py – ocp_c.py", "the OpenShift deep-dives"),
    "build_k8s": ("k8s_a.py, k8s_b.py, mesh_a.py", "the Kubernetes and Service Mesh deep-dives"),
    "build_commands": ("cmd_data.py", "the command references"),
    "build_legacy_dg": ("hub.css + the Kubernetes hub",
                        "injects a diagram into the hand-written pages that have none"),
    "build_legacy_chrome": ("chrome.py + the issue register",
                            "one nav, one footer and a theme toggle on the 25 "
                            "hand-written pages, which had twenty-three between them"),
    "build_colophon": ("everything above", "this page"),
    "build_terminal": ("terminal_fs.py",
                       "the practice terminal: a shell simulated over an in-memory tree"),
    "build_feed": ("the issue register", "feed.xml"),
    "build_nav": ("taxonomy", "mega-menu assets, wired into every page"),
    "build_search": ("everything on disk", "the search index, wired into every page"),
    "build_seo": ("each page + register", "JSON-LD, article dates, per-issue og:image"),
    "build_canonical": ("siteconf.BASE", "rewrites every origin to the canonical one"),
    "verify": ("the built site", "sitemap.xml, and a non-zero exit if anything is wrong"),
}

_sh = (TOOLS / "build.sh").read_text(encoding="utf-8")
STAGES = re.findall(r"^\s*python3 tools/(\w+)\.py", _sh, re.M)
assert STAGES, "build.sh: no stages found — the parser or the file has changed"
_unknown = [s for s in STAGES if s not in STAGE_NOTE]
assert not _unknown, (
    f"build_colophon: build.sh runs {_unknown} but this page has no description "
    f"for them. Add one to STAGE_NOTE.")

stage_rows = [("0", "<i>reset</i>", "index.base.html, README.base.md",
               "index.html, README.md")]
for i, s in enumerate(STAGES, 1):
    reads, writes = STAGE_NOTE[s]
    stage_rows.append((str(i), f"<code>{esc(s)}.py</code>", esc(reads), esc(writes)))


SECTIONS = "".join([
    section("The one rule", "tools/ is the source",
            "Everything else in this repo is output.",
            "<p>There is no framework, no bundler, no runtime and no server. The site is a "
            "tree of self-contained HTML files — but almost none of them are written by "
            "hand. They are printed by Python from a handful of data files, and "
            "<code>./tools/build.sh</code> prints all of them in one pass.</p>"
            f"<p>That exists to solve one problem. A site with {N_TOPICS} topics, "
            f"{N_CATS} categories and {N_ISSUES} published issues has the <em>same number</em> "
            "in a dozen places — the hero counter, the pillar bars, the coverage terminal, "
            "the mega-menu, the search index, the category hubs, the feed, the sitemap, the "
            "README. Maintained by hand, those drift apart within two issues. Derived from "
            "one list, they cannot.</p>"
            + note("warn", "If you are editing index.html or README.md, stop",
                   "<p>The next build overwrites both. Edit "
                   "<code>tools/index.base.html</code> or "
                   "<code>tools/README.base.md</code> instead.</p>")),

    section("Data flow", "From seven files to the whole site",
            "Every page on this site comes out of the boxes on the left.",
            BODY_DIAGRAM),

    section("Build stages", "What runs, in order",
            "The first thing <code>build.sh</code> does is throw away the two generated "
            "files and copy their bases back over them, so every build starts clean and a "
            "half-applied edit can never accumulate.",
            table(["#", "Stage", "Reads", "Writes"], stage_rows, cls="stages")
            + "<p class=\"arch-note\">This table is generated from "
              "<code>build.sh</code> itself, so a stage cannot be added without "
              "appearing here.</p>"),

    section("A page", "How a deep-dive is made",
            "A deep-dive is never typed as HTML. It is a Python list of section "
            "dictionaries handed to <code>content_page.render()</code>, which returns one "
            "finished file.",
            term("build a topic page", [
                ("$", "python3 tools/build_k8s.py k8s_a k8s_b mesh_a"),
                ("", "  47 KB  Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html"),
                ("", "  52 KB  Kubernetes/KUBERNETES-SCHEDULING/kubernetes-scheduling.html"),
                ("#", "the CSS is written once per directory, as topic.css"),
                ("#", "the pager comes from ORDER, so an unwritten topic drops out"),
                ("#", "of the chain instead of leaving a dead link"),
            ])
            + table(["Consequence", "Why"], [
                ("The CSS lives in one place",
                 "<code>content_page.CSS</code> is written once per output directory as "
                 "<code>topic.css</code>; each page links it with the right number of "
                 "<code>../</code> for its depth."),
                ("The pager is built from the reading order",
                 "<code>ORDER</code> in each builder is the sequence. A topic with no "
                 "module yet drops out of the chain rather than producing a dead link."),
                ("Relative links, always",
                 "Every <code>href</code> counts <code>../</code> from the page's own "
                 "depth, so the site works opened from disk, from a local server, from "
                 "GitHub Pages and from the Worker — with no base URL configured "
                 "anywhere."),
            ])),

    section("In the browser", "No framework, nothing to hydrate",
            "Every interactive part of this site is plain DOM.",
            table(["Behaviour", "How"], [
                ("Theme", "Read from <code>localStorage</code> and applied to "
                          "<code>&lt;html&gt;</code> before first paint, so there is no "
                          "flash of the wrong theme"),
                ("Knowledge map", "A two-level accordion over static markup; search filters "
                                  "chips by <code>textContent</code>, the status pills by "
                                  "<code>data-s</code>"),
                ("Global search", "One JSON array inlined in <code>assets/search.js</code>, "
                                  "filtered in memory — no request, no index server"),
                ("Mega-menu", "One markup block injected into every page by "
                              "<code>build_nav.py</code>, with depth-correct links baked in"),
                ("Command tables", f"Group filter and substring match over the {N_CMDS} "
                                   "commands already in the document"),
                ("This diagram", "An inline SVG. Mermaid rendered it once, at build time"),
                ("Analytics", "GoatCounter, loaded only if a site code is set — empty by "
                              "default, so nothing is sent"),
            ])
            + "<p>The only external requests a page makes are Google Fonts and, if enabled, "
              "GoatCounter. No CDN, no third-party JavaScript.</p>"),

    section("Deployment", "What is committed is what is served",
            "Both origins serve the same static files. Nothing is compiled at deploy time.",
            term("deploy", [
                ("$", "git push origin main"),
                ("#", ".github/workflows/static.yml uploads the repo as the Pages artifact"),
                ("", "→ vishal-abhinav.github.io/Platform-ops-Newsletter/"),
                ("#", "a Cloudflare Worker serves the same files at the canonical origin"),
                ("", f"→ {BASE_HOST}"),
            ])
            + "<p><code>tools/siteconf.py</code> holds the canonical origin as a single "
              "constant, and <code>build_canonical.py</code> rewrites every known origin to "
              "it on each build, then asserts none survived — which is what keeps the Pages "
              "mirror from competing with the Worker in search results.</p>"),

    section("Correctness", "Why the build fails instead of drifting",
            "Every derivation asserts that it matched what it expected to match. This is "
            "the part worth copying.",
            table(["Check", "What it refuses to let through"], [
                ("<code>re.subn(..., count=1)</code> + <code>assert n == 1</code>",
                 "A reworded sentence in the README. It fails the build rather than "
                 "silently going unmaintained."),
                ("<code>build_canonical.py</code>",
                 "Any foreign origin surviving the canonical rewrite."),
                ("<code>make_og_card.py</code>",
                 "A missing webfont. It falls back silently and bakes the wrong typography "
                 "into a PNG, so the render is asserted instead."),
                ("<code>build_colophon.py</code>",
                 "A diagram edited in the README but not re-rendered — this page checks the "
                 "sha256 of the Mermaid source against the committed SVG."),
                ("<code>verify.py</code>",
                 f"A broken link, unbalanced tags, or a page missing its chrome, across all "
                 f"{N_PAGES} pages. It also compares the counts the homepage <em>states</em> "
                 f"against the chips it actually <em>renders</em>."),
            ])
            + note("tip", "Two of the worst bugs here were caught by these, not by review",
                   "<p>A non-greedy regex that marked 49 topics live against the wrong page, "
                   "and a CSS class defined twice — <code>.tt</code> as both a 32px "
                   "theme-toggle button and the terminal text — which clipped every command "
                   "line on 53 pages. Neither was visible in a diff.</p>")),
])

PAGER = ('<div class="pager">'
         '<a href="../index.html">← Home<b>Platform Ops</b></a>'
         '<a class="next" href="../categories/index.html">Categories →<b>All 43</b></a>'
         '</div>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n" + EXTRA_CSS, encoding="utf-8")

html_out = render(
    slug="colophon",
    title="Colophon",
    tagline=("How this site is built: one taxonomy, a Python build, and a set of "
             "assertions that stop the build rather than let a number go stale."),
    eyebrow="How this site is built",
    crumbs=[("Home", "../index.html"), ("Colophon", None)],
    meta=[f"{N_PAGES} pages", f"{N_ISSUES} issues", f"{N_TOPICS} topics",
          "no framework"],
    sections=SECTIONS,
    pager=PAGER,
    up="../",
    css="topic.css",
    canon="colophon/")

(OUT / "index.html").write_text(html_out, encoding="utf-8")
print(f"  {len(html_out) // 1024:3d} KB  colophon/index.html  "
      f"({len(STAGES)} stages, diagram sha ok)")
