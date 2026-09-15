#!/usr/bin/env python3
"""Give the three hand-written pages that have no architecture diagram one.

WHY
---
Every generated page already carries a `.dg` diagram: all 43 category hubs,
the 5 Foundation deep-dives, the 3 OpenShift ones and the 7 Kubernetes and
Service Mesh ones. An audit of the hand-written pages found that 10 of the 11
legacy issue pages have a diagram too — they just built their own in CSS,
before content_page.py existed. Three pages have nothing at all:

    DevOps/K8/index.html                    the Kubernetes series hub
    Infrastructure/OS/index.html            the Operating Systems series hub
    Infrastructure/.../linux-unix-glossary.html   issue #057, 190 terms

The two series hubs are the odd ones out in particular: every *category* hub
has a diagram, and these two sit at exactly the same place in the site.

HOW
---
These pages are NOT reset from a base at the start of a build the way
index.html and README.md are, so this stage cannot simply append — it injects
between markers and replaces whatever is already between them. Running it
twice is a no-op, which is what makes it safe in a pipeline that reruns.

The CSS is lifted out of categories/hub.css rather than copied into this file,
so a diagram on a hand-written page can never drift from the one on a
generated hub. The Kubernetes series hub goes further and lifts the *rendered
SVG* straight off the Kubernetes category hub — same diagram, same live
links, one source. That only works because both pages sit two directories
deep, so the "../../" in those hrefs is already correct; the check below
refuses to inject if that ever stops being true.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import re
import sys

sys.path.insert(0, str(TOOLS))
from content_page import diagram                      # noqa: E402

HUB_CSS = ROOT / "categories" / "hub.css"
K8_HUB = ROOT / "categories" / "kubernetes" / "index.html"

CSS_OPEN, CSS_CLOSE = "/* dg:auto */", "/* /dg:auto */"
MK_OPEN, MK_CLOSE = "<!-- dg:auto -->", "<!-- /dg:auto -->"

VARS = ("--line-3", "--lime",
        "--n-live-bg", "--n-live-br", "--n-live-dot", "--n-live-fg",
        "--n-pipe-bg", "--n-pipe-br", "--n-pipe-fg",
        "--n-plan-bg", "--n-plan-br", "--n-plan-fg")


# ── the shared look, taken from the generated hubs ──────────────────────────
def shared_css():
    src = HUB_CSS.read_text(encoding="utf-8")

    # The light values only: these pages have no dark mode, so the dark
    # redefinitions further down the file would be dead weight.
    # Every :root, not just the first: the shared token block and the hub-only
    # status swatches now live in two of them, and reading only the first
    # silently lost the swatches.
    roots = re.findall(r":root\s*\{(.*?)\}", src, re.S)
    assert roots, "hub.css: no :root block to take the diagram colours from"
    light = "\n".join(roots)
    decls = []
    for v in VARS:
        m = re.search(re.escape(v) + r"\s*:\s*([^;}]+)[;}]", light)
        assert m, f"hub.css :root no longer defines {v}"
        decls.append(f"{v}:{m.group(1).strip()};")

    rules = []
    for m in re.finditer(r"(?:^|\n)([^\n{}]*\.dg[a-z-]*[^\n{}]*)\{([^}]*)\}", src):
        sel, body = m.group(1).strip(), " ".join(m.group(2).split())
        rules.append(f"{sel}{{{body}}}")
    assert len(rules) >= 8, f"hub.css: only found {len(rules)} .dg rules, expected the full set"

    # .dg-wrap carries its own width. The hubs put the diagram inside .wrap,
    # but that class lives in hub.css and these three pages have never loaded
    # it — relying on it let the diagram run edge-to-edge with no padding at
    # all. These match each page's own section rhythm instead: 1200px centred,
    # 64px of side padding, 28px on a phone.
    return (f"{CSS_OPEN}\n:root{{{''.join(decls)}}}\n"
            + "\n".join(rules)
            + "\n.dg-wrap{max-width:1200px;margin:0 auto;padding:72px 64px 24px;}"
              "\n.dg-wrap .dg-cap{font-size:13px;color:var(--muted);margin-top:16px;"
              "max-width:760px;font-style:italic;line-height:1.6;}"
              "\n@media(max-width:820px){.dg-wrap{padding:48px 28px 16px;}}"
              f"\n{CSS_CLOSE}")


LEGEND = ('<div class="dg-key"><span><i class="live"></i> Live — click through</span>'
          '<span><i class="pipe"></i> In pipeline</span>'
          '<span><i class="plan"></i> Planned</span></div>')


def block(svg, caption, legend=False):
    return (f'{MK_OPEN}\n<section><div class="dg-wrap">\n'
            f'  <div class="section-tag">Architecture</div>\n'
            f'  <div class="dg-scroll">{svg}</div>\n'
            f'  {LEGEND if legend else ""}\n'
            f'  <p class="dg-cap">{caption}</p>\n'
            f'</div></section>\n{MK_CLOSE}')


def inject(path, anchor, css, html):
    """Idempotent: replace between the markers if they are there, else insert
    at the anchor. Every match is asserted, so a page that has been restructured
    fails the build instead of silently getting no diagram."""
    p = ROOT / path
    assert p.exists(), f"{path} does not exist"
    src = p.read_text(encoding="utf-8")

    if CSS_OPEN in src:
        a, b = src.index(CSS_OPEN), src.index(CSS_CLOSE) + len(CSS_CLOSE)
        src = src[:a] + css + src[b:]
    else:
        assert src.count("</style>") >= 1, f"{path}: no </style> to put the diagram CSS before"
        src = src.replace("</style>", css + "\n</style>", 1)

    if MK_OPEN in src:
        a, b = src.index(MK_OPEN), src.index(MK_CLOSE) + len(MK_CLOSE)
        src = src[:a] + html + src[b:]
    else:
        assert src.count(anchor) == 1, (
            f"{path}: anchor matched {src.count(anchor)} times, expected 1:\n  {anchor}")
        src = src.replace(anchor, html + "\n\n" + anchor, 1)

    p.write_text(src, encoding="utf-8")
    return len(src)


# ════════════════════════════════════════════════════════════════════════════
# 1. Kubernetes series hub — the category hub's own diagram, lifted whole
# ════════════════════════════════════════════════════════════════════════════
def k8_svg():
    src = K8_HUB.read_text(encoding="utf-8")
    assert src.count('<svg class="dg"') == 1, (
        f"{K8_HUB.name}: expected exactly one .dg diagram, found "
        f"{src.count('<svg class=' + chr(34) + 'dg' + chr(34))}")
    a = src.index('<svg class="dg"')
    svg = src[a:src.index("</svg>", a) + len("</svg>")]

    # Both pages are two directories deep, so the hrefs carry straight over.
    # If the hub ever moves, this is the check that catches it rather than
    # letting a wall of broken links ship.
    depth_ok = all(h.startswith("../../") for h in re.findall(r'class="dg-a" href="([^"]+)"', svg))
    assert depth_ok, "category-hub links are no longer ../../ — the lift would break them"
    assert "DevOps/K8/index.html".count("/") == 2, "target hub depth changed"
    return svg


# ════════════════════════════════════════════════════════════════════════════
# 2. Operating Systems series hub — the Linux stack, bottom to top
# ════════════════════════════════════════════════════════════════════════════
# Drawn as a stack, so it is listed top-down here and hardware lands at the
# BOTTOM — which is where anyone reading a stack diagram expects it. The first
# draft listed hardware first and the caption claimed "bottom to top" while the
# picture said the opposite.
OS_LAYERS = [
    ("Operate", [("Monitoring", "go"), ("Logging", "go"), ("Troubleshooting", "go"),
                 ("Hardening", "go")]),
    ("User Space", [("Shell & Bash", "core"), ("Text Processing", "core"),
                    ("Package Managers", "core"), ("Processes & Jobs", "core"),
                    ("Networking Tools", "core")]),
    ("Filesystem", [("FHS Layout", "calm"), ("Mounts", "calm"), ("LVM", "calm"),
                    ("Permissions & Ownership", "calm"), ("Users & Groups", "calm")]),
    ("Init & Services", [("systemd", "warm"), ("Units & Targets", "warm"),
                         ("Boot Process", "warm"), ("journald", "warm"),
                         ("Timers & Cron", "warm")]),
    ("Kernel", [("Process Scheduler", "hot"), ("Memory Management", "hot"),
                ("VFS", "hot"), ("Network Stack", "hot"), ("Device Drivers", "hot")]),
    ("Hardware", [("CPU", "plain"), ("Memory", "plain"), ("Disks", "plain"),
                  ("Network Interfaces", "plain")]),
]


# ════════════════════════════════════════════════════════════════════════════
# 3. Linux & Unix Glossary — its own 15 categories, counted off the page
# ════════════════════════════════════════════════════════════════════════════
GLOSSARY = "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html"

# Which layer each of the 15 categories belongs in, by its number on the page.
# Keeping this keyed on the number rather than the name means a reworded
# heading does not silently drop a category out of the diagram.
GL_LAYERS = [
    ("Core",      [1, 2, 5], "core"),
    ("Access",    [3, 4], "calm"),
    ("Working",   [6, 7, 8], "warm"),
    ("System",    [9, 10, 11, 12], "hot"),
    ("Operate",   [13, 14, 15], "go"),
]
GL_SHORT = {
    1: "Fundamentals, Kernel & Shell", 2: "Files & Filesystem",
    3: "Permissions & Ownership", 4: "Users & Groups", 5: "Processes & Jobs",
    6: "Environment & I/O", 7: "Text Processing", 8: "Shell Scripting",
    9: "Package Management", 10: "Services, systemd & Boot",
    11: "Storage, Disks & Backup", 12: "Networking",
    13: "Remote Access & Security", 14: "Logging & Monitoring",
    15: "Troubleshooting",
}


def glossary_layers():
    src = (ROOT / GLOSSARY).read_text(encoding="utf-8")
    found = {int(n): int(c) for n, c in
             re.findall(r"<!--[^>]*?(\d+)\.[^>]*?\((\d+)\)[^>]*?-->", src)}
    assert len(found) == 15, f"glossary: found {len(found)} category headings, expected 15"
    assert set(found) == set(GL_SHORT), "glossary: category numbering changed"
    total = sum(found.values())
    assert total == 190, f"glossary: counts sum to {total}, the page says 190"

    layers = []
    for label, nums, role in GL_LAYERS:
        layers.append((label, [(f"{GL_SHORT[n]} · {found[n]}", role) for n in nums]))
    return layers, total


# ── run ─────────────────────────────────────────────────────────────────────
css = shared_css()
done = []

done.append(("DevOps/K8/index.html", inject(
    "DevOps/K8/index.html",
    "<!-- ═══ WHAT'S INSIDE ═══ -->",
    css,
    block(k8_svg(),
          "The same map as the Kubernetes category hub, and the same links — every green "
          "block is covered by a published issue, so click one to go straight to it.",
          legend=True))))

done.append(("Infrastructure/OS/index.html", inject(
    "Infrastructure/OS/index.html",
    "<!-- ═══ WHAT'S INSIDE ═══ -->",
    css,
    block(diagram(OS_LAYERS, "The Linux stack, hardware upward"),
          "Where each issue in this series sits. The stack reads bottom to top: the kernel "
          "owns the hardware, systemd owns the kernel's services, and everything you type "
          "lives in the two layers above that."))))

gl_layers, gl_total = glossary_layers()
done.append((GLOSSARY, inject(
    GLOSSARY,
    '<section class="content-section reveal" id="glossaryTop">',
    css,
    block(diagram(gl_layers, "The 15 glossary categories, grouped"),
          f"All {gl_total} terms, grouped the way the reference below is ordered — "
          f"the number after each category is how many terms it holds."))))

for path, size in done:
    print(f"  {size // 1024:3d} KB  {path}")
print(f"injected a diagram into {len(done)} hand-written page(s)")
