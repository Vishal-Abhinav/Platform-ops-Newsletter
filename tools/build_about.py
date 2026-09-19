#!/usr/bin/env python3
"""Build about/index.html — what this newsletter is, and why it exists.

WHY THIS PAGE EXISTS
--------------------
Until now the only place that answered "what is this?" was README.md on a
public GitHub repo. That made a code-hosting page the front door to a reading
site, and it put the project's own description somewhere the author does not
control the design, the URL or the audience.

The repo is going private. Everything in it — the generators, the command
corpus, siteconf.py with the Search Console tokens — is build machinery, and
the Phase 3 audit found the whole of tools/ publicly fetchable precisely
because "the repo is the deploy surface" was never questioned. Private is the
right answer for the machinery. But the description is not machinery, and it
should not disappear with it.

So the description moves here, onto the domain, where it gets a canonical URL,
a sitemap row, the mega-menu, global search and the same chrome as every other
page — and where it is indexable by search engines that will never see a
private repo.

WHAT THIS PAGE IS NOT
---------------------
It is not README.md rendered as HTML, and it deliberately does not read
dist/README.md. Two reasons, one of design and one of mechanics.

Design: the README's bulk is a repository tree, a build-stage table and a
940-line knowledge map — all of it addressed to someone who has cloned the
repo. A reader who lands on /about/ wants to know what the newsletter covers
and whether it is worth their time. The colophon already answers "how is this
built"; this page answers "what is this and should I read it".

Mechanics: build_readme.py cannot run until build_search.py has written the
search index it quotes, and build_search.py wires search into every page that
exists when it runs. A page generated FROM the finished README would therefore
be written after the pass that gives every page its search box, and would ship
without one. Deriving from taxonomy.py instead breaks that cycle — this stage
runs with the other content generators, and the whole-site passes pick it up
like any other page. Same rule as everywhere else in this build: derive from
the source of truth, never scrape a generated artefact.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
# TOOLS is the real tools/ directory — derived from this file's own location,
# never from ROOT. ROOT is the OUTPUT root (dist/) and source must never be
# looked up underneath it.
TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from content_page import CSS, render, section, table, note   # noqa: E402
from taxonomy import PILLARS, cat_stats                      # noqa: E402
from build_feed import ISSUES                                # noqa: E402
from cmd_data import ALL as CMD_SPECS                        # noqa: E402

OUT = ROOT / "about"

# ── the numbers, from the same places every other page gets them ────────────
PILLAR_ROWS = []
T_LIVE = T_PIPE = T_PLAN = 0
for _name, _cats in PILLARS:
    p_l = p_p = p_n = 0
    for _c, _i, _t in _cats:
        l, p, n = cat_stats(_t)
        p_l += l; p_p += p; p_n += n
    T_LIVE += p_l; T_PIPE += p_p; T_PLAN += p_n
    PILLAR_ROWS.append((_name, len(_cats), p_l, p_p, p_n))

N_TOPICS = T_LIVE + T_PIPE + T_PLAN
N_CATS = sum(len(c) for _, c in PILLARS)
N_PILL = len(PILLARS)
N_ISSUES = len(ISSUES)
N_CMDS = sum(len(g[3]) for spec in CMD_SPECS for g in spec["groups"])
N_CMD_PAGES = len(CMD_SPECS)

NEWEST = sorted(ISSUES, key=lambda i: -i[0])[0]
NEWEST_NUM, NEWEST_PATH, NEWEST_TITLE = NEWEST[0], NEWEST[1], NEWEST[2]

# ── what it covers ──────────────────────────────────────────────────────────
COVER = table(
    ["Pillar", "Categories", "Live", "Pipeline", "Planned"],
    [(f"<b>{n}</b>", str(c), str(l), str(p), str(pl))
     for n, c, l, p, pl in PILLAR_ROWS]
    + [("<b>Total</b>", f"<b>{N_CATS}</b>", f"<b>{T_LIVE}</b>",
        f"<b>{T_PIPE}</b>", f"<b>{T_PLAN}</b>")])

S_WHAT = section(
    "What this is", "A newsletter about running things in production",
    "Platform Ops is written by one engineer, from production systems rather "
    "than from vendor documentation. Every issue starts with something that "
    "broke, something that was slower than it should have been, or something "
    "whose official explanation turned out to be incomplete.",
    "<p>The subject is the operational half of platform engineering: "
    "Kubernetes and OpenShift, the Linux underneath them, the networking and "
    "storage they depend on, and the observability that tells you which of "
    "those is lying to you. It assumes you already know what a Pod is. It "
    "does not assume the default settings are correct.</p>"
    "<p>There is no sponsorship, no tracking beyond page counts, and nothing "
    "is behind a signup wall — every page is readable without an account. "
    "The archive stays up; issues are corrected in place rather than "
    "silently replaced.</p>")

S_COVERS = section(
    "Scope", "What it covers",
    f"{N_TOPICS} topics, grouped into {N_CATS} categories under {N_PILL} "
    f"pillars. The table is generated from the same file the site's knowledge "
    f"map and every category page read, so these numbers cannot disagree with "
    f"the ones you see elsewhere.",
    COVER
    + note("info", "What the three columns mean",
           "<p><b>Live</b> means a published page covers it and the topic "
           "links straight there. <b>Pipeline</b> means it sits next to a "
           "series already running, so it is queued rather than hypothetical. "
           "<b>Planned</b> means it is on the backlog with no date attached — "
           "it moves up when the series in front of it lands.</p>"
           "<p>Publishing the planned list is deliberate. A coverage map that "
           "only shows what is finished tells you nothing about what the "
           "project is actually trying to be.</p>"))

S_READ = section(
    "Where to start", "Four ways in",
    "Depending on whether you came here to read something, to look something "
    "up, or to find out whether a subject is covered at all.",
    table(["Start here", "If you want"],
          [(f'<a href="../{NEWEST_PATH}">Issue #{NEWEST_NUM:03d} — {NEWEST_TITLE}</a>',
            f"The newest issue. There are {N_ISSUES} in the archive, all linked "
            f"from the homepage."),
           ('<a href="../categories/index.html">Category hubs</a>',
            f"To browse by subject. Each of the {N_CATS} categories has its own "
            f"page with a generated architecture diagram and its full topic list."),
           ('<a href="../categories/kubernetes-openshift-map/index.html">'
            'The Kubernetes &amp; OpenShift topic map</a>',
            "To check whether something specific is covered, queued or planned "
            "before you spend time looking."),
           (f'<a href="../Commands/KUBERNETES-COMMANDS/kubernetes-commands.html">'
            f'Command references</a>',
            f"To look something up fast. {N_CMD_PAGES} references covering "
            f"{N_CMDS} commands, searchable and filterable by group.")])
    + "<p>There is also a <a href=\"../terminal/index.html\">practice "
      "terminal</a> — a Unix shell simulated over an in-memory filesystem, so "
      "you can try the commands without a cluster and without consequences.</p>")

S_BUILT = section(
    "How it's made", "One source of truth, and assertions that stop the build",
    "Every page here is static HTML generated by a Python build from a single "
    "taxonomy file. No framework, no client-side rendering, no build-time "
    "JavaScript.",
    "<p>That choice is not nostalgia. It means the counts on the homepage, in "
    "the category hubs, in the topic map and on this page are all computed "
    "from one file at build time — so they cannot drift apart, and a stage "
    "that would make them disagree fails the build instead of shipping. Pages "
    "load without waiting for a bundle, and they keep working with JavaScript "
    "off.</p>"
    "<p>The <a href=\"../colophon/index.html\">colophon</a> has the full "
    "account: the build stages in order, what each one reads and writes, and "
    "the checks that gate a deploy.</p>")

S_PLATFORM = section(
    "Platform Ops", "The publication promise",
    "A technical newsletter on Kubernetes, OpenShift, SRE and platform "
    "engineering — written from production systems, not from documentation.",
    table(["Promise", "What it means"],
          [("No paywall",
            "Every page is readable without an account. There is nothing to "
            "sign up for in order to read."),
           ("Corrected in place",
            "When an issue is wrong it is fixed at its original URL, not "
            "quietly replaced or reposted."),
           ("First-hand",
            "Where an issue describes a failure it is a failure that happened; "
            "where it gives a number, the number was measured."),
           ("Open build",
            "The generator, the tests and this page are public. What you read "
            "is what the repository produces.")])
    + "<p><b>Build. Operate. Understand.</b> Learn the technology, understand "
      "how the components connect, build reliable systems, and when something "
      "breaks, understand the problem before applying the fix.</p>")

S_WHO = section(
    "Who writes it", "Vishal Abhinav",
    "A platform engineer who spends his working days on the systems this "
    "newsletter is about.",
    "<div id=\"author\"></div>"
    "<p>Vishal Abhinav is a Software Engineer specializing in Infrastructure, "
    "DevOps, Platform Operations, Observability and production systems. His "
    "work focuses on building, automating, deploying, troubleshooting, and "
    "operating reliable technology platforms across Linux, Networking, Cloud, "
    "Git, CI/CD, Containers, Kubernetes, OpenShift, Automation, Observability, "
    "and SRE.</p>"
    "<p>The writing is first-hand. Where an issue describes a failure, it is "
    "a failure that happened; where it gives a number, the number was measured "
    "rather than quoted. When something here turns out to be wrong, the page "
    "is corrected and the correction is visible.</p>"
    + table(["Author", "Links"],
            [("Vishal Abhinav",
              '<a href="https://www.linkedin.com/in/vishal-abhinav/" '
              'target="_blank" rel="noopener">LinkedIn</a> · '
              '<a href="https://github.com/Vishal-Abhinav" target="_blank" '
              'rel="noopener">GitHub</a> · '
              '<a href="https://www.hackerrank.com/Vishal_Abhinav?hr_r=1" '
              'target="_blank" rel="noopener">HackerRank</a> · '
              '<a href="https://www.researchgate.net/profile/Vishal-Abhinav/research" '
              'target="_blank" rel="noopener">ResearchGate</a>'),
             ("Areas of focus",
              "Infrastructure, DevOps, Linux, Networking, Cloud, Kubernetes, "
              "OpenShift, CI/CD, Containers, GitOps, Automation, Observability, "
              "SRE, Platform Engineering")])
    + "<p>Platform Ops is published by "
    "<a href=\"https://srivantechnologies.com/\" target=\"_blank\" "
    "rel=\"noopener\">Srivan Technologies</a>.</p>")

S_LICENCE = section(
    "Licence", "What you may do with this",
    "Two licences, because the code and the writing are different things.",
    table(["What", "Licence", "In practice"],
          [("The build system and code samples", "MIT",
            "Use them, change them, ship them commercially. Attribution "
            "appreciated, not required."),
           ("The writing and the diagrams", "CC BY-NC-ND 4.0",
            "Quote it with credit and a link. Don't republish it wholesale, "
            "don't sell it, and don't publish an edited version as though it "
            "were the original.")])
    + "<p>If you want to do something the second licence doesn't allow — "
      "translate an issue, use a diagram in training material, reprint a "
      "piece internally — ask. The answer is usually yes.</p>"
    + note("warn", "On machine-generated summaries",
           "<p>Several issues here describe failure modes where a confident "
           "but wrong answer costs real downtime. If you are feeding this "
           "site to a model and publishing what comes out, link the source "
           "page so a reader can check it against the original.</p>"))

SECTIONS = S_WHAT + S_COVERS + S_READ + S_BUILT + S_PLATFORM + S_WHO + S_LICENCE

PAGER = ('<div class="pager">'
         '<a href="../index.html">← Home<b>Platform Ops</b></a>'
         '<a class="next" href="../colophon/index.html">Colophon →'
         '<b>How it\'s built</b></a>'
         '</div>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n", encoding="utf-8")

html_out = render(
    slug="about",
    title="About",
    tagline=("Platform Ops is a newsletter about running Kubernetes, OpenShift "
             "and the Linux underneath them in production — written from "
             "systems that broke, not from vendor documentation."),
    eyebrow="What this is and why it exists",
    crumbs=[("Home", "../index.html"), ("About", None)],
    meta=[f"{N_ISSUES} issues", f"{N_TOPICS} topics", f"{N_CATS} categories",
          "free, no signup"],
    sections=SECTIONS,
    pager=PAGER,
    up="../",
    css="topic.css",
    canon="about/")

(OUT / "index.html").write_text(html_out, encoding="utf-8")
print(f"  {len(html_out) // 1024:3d} KB  about/index.html  "
      f"({N_PILL} pillars, {N_CATS} categories, {N_TOPICS} topics, "
      f"{N_ISSUES} issues)")
