# Platform Ops: page design and writing architecture

Status: proposed design blueprint. This document defines the reusable reading and writing experience; it does not change the published site.

## Purpose

Every topic should help an engineer understand the system, make a decision, perform the work, verify the result, and recover when it fails. Comprehensive coverage means answering those questions with evidence, rather than adding length.

Support three reader journeys:

- Learn: category → prerequisites → architecture → worked example → next topic.
- Operate: search → runbook → checks → commands → verification → rollback.
- Decide: topic → alternatives → tradeoffs → recommendation with stated assumptions.

## Site information architecture

| Destination | Reader need | Main elements |
| --- | --- | --- |
| Home | Find a useful starting point | Clear purpose, latest issue, Learn/Operate/Decide entry points, topic search, featured series |
| Categories | Explore a domain | Pillars, topic filters, published/pipeline/planned labels, short scope descriptions |
| Category hub | Understand topic relationships | Architecture map, prerequisites, ordered learning path, published articles |
| Article | Understand and apply one subject | Article structure below, local contents, diagrams, examples, references |
| Runbook | Resolve a specific symptom | Scope, diagnostic decision tree, ordered actions, verification, escalation |
| Commands | Find syntax quickly | Search, environment/version, explanation, expected output, risk and reversibility |
| Practice | Build familiarity | Existing simulated terminal, exercises, clear simulation limits |
| Archive | Browse releases | Issue number, date, topic, synopsis, filters |
| About and editorial policy | Assess credibility | Author, sourcing, corrections, revision history, contact route |

Keep primary navigation short: Topics, Runbooks, Commands, Archive, Search. Place secondary destinations in the footer or relevant contextual links. Runbooks can initially be a filtered view of existing content; create a separate destination only when enough published material supports it.

## Reusable article structure

1. **Orientation:** breadcrumb, title, concrete outcome, short summary, difficulty, prerequisites, author, published date, last reviewed date, and tested versions.
2. **Problem and scope:** the production scenario, symptoms, constraints, intended audience, and boundaries.
3. **Architecture:** one readable overview with component responsibilities, request/data/control flow, dependencies, trust boundaries, and failure domains. Follow it with a text explanation.
4. **Core concepts:** only the concepts needed to understand the example; link to deeper foundational references.
5. **Decisions and tradeoffs:** compare alternatives by operational complexity, reliability, security, performance, and cost. State when the recommendation changes.
6. **Implementation:** prerequisites, ordered steps, configuration, executable examples, expected output, and a verification checkpoint.
7. **Operations:** signals, dashboards, actionable alerts, ownership, capacity assumptions, and routine maintenance.
8. **Failure handling:** symptom → evidence → likely cause → corrective action → recovery check. Include escalation conditions.
9. **Security and access:** permissions, secrets, network boundaries, sensitive data handling, and audit evidence relevant to this topic.
10. **Performance and cost:** workload assumptions, bottlenecks, measurement approach, limits, and practical optimization choices.
11. **Recovery and lifecycle:** rollback, backup/restore where relevant, upgrades, compatibility, cleanup, and known limitations.
12. **Quick reference:** compact checklist, essential commands, and decision summary.
13. **Evidence and continuation:** primary references, test environment/date, revision notes, related articles, and next exercise.

For each operational concern, supply substantive coverage, link to an existing detailed article, or explain why it does not apply. Do not create empty sections merely to complete the template. Distinguish observed results from illustrative output.

## Page layout

Desktop, approximately 1200 px and wider:

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Platform Ops      Topics  Runbooks  Commands  Archive   Search Theme │
├─────────────────────────────────────────────────────────────────────┤
│ Breadcrumb                                                          │
│ Title, outcome, summary, author, dates, tested versions              │
├─────────────┬───────────────────────────────────────┬───────────────┤
│ On this page│ Article                                   │ Context   │
│             │ Problem → Architecture → Decisions        │ Prereqs   │
│ Active      │ Implementation → Operations → Recovery    │ Related   │
│ section     │ Quick reference → Sources                 │ Version   │
├─────────────┴───────────────────────────────────────┴───────────────┤
│ Next topic · Correction link · RSS/subscription                      │
└─────────────────────────────────────────────────────────────────────┘
```

Target a maximum shell width around 1440 px, a 200–220 px contents rail, a 65–75 character reading measure, and an optional 220 px context rail. Wide diagrams and tables may use the available main-content width. Avoid permanently occupying the context rail when there is little useful content.

At intermediate widths, move context below the article. On phones, use one column and a compact expandable contents control. Keep tables and code horizontally scrollable within their own containers. A sticky header must not obscure anchor targets or consume excessive screen height.

## Visual language

Extend the existing paper/ink theme and dark mode. Use the existing semantic CSS tokens rather than adding a separate palette to each article.

| Element | Design rule |
| --- | --- |
| Body | Existing Manrope family, 16–18 px, approximately 1.65 line height |
| Titles | Clear editorial hierarchy; reserve display typography for short headings |
| Code and metadata | Existing monospace family; preserve whitespace and distinguish input/output |
| Spacing | Consistent 4/8 px increments; larger space between sections than within a section |
| Accent | Cyan for system relationships, amber for cautions, crimson for destructive effects, lime for verified success |
| Cards | Use for bounded references or alternatives; keep long-form prose in the reading column |
| Diagrams | Consistent node roles, labeled arrows, legend when needed, text explanation |
| Motion | Small functional transitions; respect reduced-motion preferences |

Color supplements labels and icons. Check each foreground/background combination in both themes; existing brand colors are not automatically suitable for body text.

## Interaction and accessibility

- Search offers useful excerpts and topic/type filters, with a clear empty state and an easy reset.
- Contents links have stable URLs, indicate the current section, and work with keyboard navigation.
- Code blocks provide copy feedback and a fallback if clipboard access fails. Keep prompts and example output out of copied commands.
- Put operation impact, prerequisites, and reversibility beside commands that change systems.
- Expandable sections expose state to assistive technology. Keep the main explanation and essential recovery instructions visible by default.
- Architecture diagrams have an accessible description and an equivalent explanation in text. Allow large diagrams to be opened at readable size.
- Use semantic landmarks, a skip link, ordered headings, visible focus indicators, descriptive links, labeled controls, and comfortable touch targets.
- Preserve the reading experience without JavaScript. Add search enhancements, copying, theme persistence, and section tracking progressively.
- Planned topics display their status and useful context without implying a finished article exists.

## Writing model

Use one structured content record per article. The following is a proposed contract to adapt to the current Python data structures:

```text
identity: slug, title, synopsis, category, tags, content_type, status
ownership: author, reviewer, published_at, updated_at, reviewed_at
context: audience, difficulty, prerequisites, tested_versions, environment
content: problem, architecture, concepts, decisions, implementation
operations: observability, troubleshooting, security, performance, cost
lifecycle: rollback, recovery, upgrades, cleanup, limitations
evidence: expected_results, test_notes, references, revision_history
navigation: related_topics, next_topic
```

Dates and test claims must reflect actual work. Optional fields should disappear cleanly when absent. Published status requires meaningful content, not merely a generated page.

Writing flow: choose reader outcome → map dependencies → draft architecture → verify worked example → document failure and recovery → edit for clarity → preview desktop/mobile → review evidence → publish through the existing workflow.

## Fit with the existing implementation

| Existing source | Intended responsibility |
| --- | --- |
| `tools/taxonomy.py` | Topic identity, grouping, publication status; retain as the coverage source |
| `tools/content_page.py` | Reusable article structure, reference cards, terminal examples, diagram rendering |
| `tools/chrome.py` and `tools/build_nav.py` | Shared shell and navigation; inspect current ownership before modifying |
| `tools/index.base.html` | Home-page entry points and editorial hierarchy |
| `tools/build_search.py` | Search index and discoverability |
| `content/` | Authored source pages |
| `static/` | Shared static assets and existing email wrapper |
| `tools/build.sh` | Generate deploy output in `dist/` |
| `tools/verify.py` | Existing build checks; extend only for meaningful new content requirements |

Keep reader pages statically generated using the existing Python and HTML/CSS architecture. A future authoring interface can produce validated content records consumed by that pipeline. Preview its import result before writing source files, validate required fields, and escape untrusted text.

Email is a separate presentation of the same issue: title, short problem statement, key takeaway, and link to the full article inside the existing Kit wrapper. Wide diagrams and interactive features belong on the web page.

No external design or writing tool has been selected or imported. The requested tool must be identified before choosing its integration, format, and credentials, if any.

## Delivery sequence and acceptance

1. Pilot this structure on one existing substantial article. Confirm the reader journeys and section order with real content.
2. Implement reusable layout and components in source templates. Verify phone, intermediate, and desktop widths in both themes.
3. Add content metadata and integrate navigation/search without changing established article URLs unnecessarily.
4. Migrate related articles in small batches, retaining stable section anchors or compatible replacements.
5. Add an authoring/import interface only after selecting the requested tool and agreeing on the content contract.

Accept the pilot when readers can identify its purpose quickly, find an operational answer, follow a verified example, understand recovery, and inspect the evidence. Verify keyboard access, focus, contrast, zoom, mobile overflow, reduced motion, and no-JavaScript reading. Run the existing link/build checks for implementation changes and inspect representative rendered pages before publication.
