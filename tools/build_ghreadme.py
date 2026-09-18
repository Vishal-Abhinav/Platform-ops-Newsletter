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

```
tools/      the build system         source, never published
content/    hand-written pages       source, never mutated
static/     copied verbatim          icons, OG cards, self-hosted fonts
    │
    ▼  tools/build.sh — sequential stages, set -euo pipefail
    ▼
dist/       everything the build makes — the only thing deployed
    │
    ▼  verify.py + test_render.py — no pass, no deploy
    ▼
GitHub Actions → Cloudflare Workers → {SITE.split('//')[1]}
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
- **11 page families × 13 viewport widths** are opened in a real browser and
  asserted for horizontal overflow and duplicate fixed headers.
- CI **refuses to deploy** a build holding fewer than 500 pages, after a deploy
  from an empty directory once published a site where everything 404'd.

Drawn in full on the [architecture page]({SITE}/architecture/); the
stage-by-stage account is in the [colophon]({SITE}/colophon/).

---

## Running it

```bash
git clone https://github.com/Vishal-Abhinav/Platform-ops-Newsletter.git
cd Platform-ops-Newsletter
bash tools/build.sh          # writes dist/ — wait for: all checks passed
python3 -m http.server -d dist
```

Python 3.11+, standard library only. The render tests additionally want
`pip install playwright && playwright install chromium`.

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
    out.write_text(README, encoding="utf-8")

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
            (SITE, "the site URL")):
        assert needle in text, f"README.md is missing {why} ({needle!r})"
    assert (REPO / "brand" / "banner.svg").exists(), (
        "brand/banner.svg is missing, so the README's first image would be a "
        "broken one on the repo's front page. Run tools/make_banner.py first — "
        "build.sh runs it immediately before this stage.")

    print(f"  {len(text) // 1024 + 1} KB  README.md  "
          f"({N_ISSUES} issues, {N_TOPICS} topics, {N_CATS} categories, "
          f"{N_CMDS} commands)")
