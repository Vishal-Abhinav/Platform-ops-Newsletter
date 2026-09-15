#!/usr/bin/env python3
"""Put the 25 hand-written pages on the same chrome as everything else.

WHAT THIS FIXES
---------------
A scan of the 93 live pages found twenty-four different navigation bars. The
generated pages account for one of them — the pillar slot varies, the bar does
not. The other twenty-three were these hand-written pages, each with its own
vocabulary: "← Newsletter", "← K8s Series", "← OS Series", "← Glossary", one
page still carrying the labels of a homepage design that no longer exists, and
one page with no bar at all. None of them offered the Lab. None of them had a
theme toggle, so a reader in dark mode was flashbanged on every click through.
And their footers all advertised issue #057 as the newest when it was #067.

These pages are not generated from a spec — their prose is the source. So this
stage does not rebuild them; it replaces four things in place:

    <nav>...</nav>        ->  chrome.nav(up, crumb)
    <footer>...</footer>  ->  chrome.footer(up)
    the chrome stylesheet ->  appended to the page's own <style>
    the theme scripts     ->  pre-paint in <head>, handler before </body>

IDEMPOTENCE
-----------
Everything this stage adds sits between markers, and every run strips the
markers before re-adding. Run it a hundred times and the bytes do not move —
which matters, because these pages are in git and a stage that rewrites them
differently on each build makes every diff unreadable. There is a test for
this at the bottom: run with --check and it builds twice and compares.

WHY NOT JUST REGENERATE THESE PAGES
-----------------------------------
Because the content is hand-written and good. The nav being wrong is not a
reason to throw away the prose. k8-networking.html is the one exception — it
was built to a different visual standard entirely — and it gets the
PRIVATE_PALETTE treatment further down rather than the generic conversion.
"""
import os
import pathlib as _pl
import re
import sys

ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import chrome                                       # noqa: E402

CSS_OPEN, CSS_CLOSE = "/* chrome:begin */", "/* chrome:end */"
PRE_OPEN, PRE_CLOSE = "<!-- chrome:prepaint -->", "<!-- /chrome:prepaint -->"
JS_OPEN, JS_CLOSE = "<!-- chrome:js -->", "<!-- /chrome:js -->"

# ── where each page sits ────────────────────────────────────────────────────
# (path, crumb trail). The trail is written out rather than parsed from the old
# markup: two of these pages have no usable trail to parse, and an explicit
# table is something you can read and correct.
#
# Each entry is a list of (label, href-or-None); None means "you are here".
PAGES = {
    "DevOps/CICD/cicd-pipelines.html": [
        ("Categories", "categories/index.html"),
        ("GitOps", "categories/gitops/index.html"),
        ("CI/CD & GitOps", None)],
    "DevOps/K8/index.html": [
        ("Categories", "categories/index.html"),
        ("Kubernetes", "categories/kubernetes/index.html"),
        ("K8s Series", None)],
    "DevOps/K8/ARCHITECTURE/k8-architecture.html": [
        ("Categories", "categories/index.html"),
        ("Kubernetes", "categories/kubernetes/index.html"),
        ("Architecture", None)],
    "DevOps/K8/ERROR/K8-error.html": [
        ("Categories", "categories/index.html"),
        ("Kubernetes", "categories/kubernetes/index.html"),
        ("Error Runbook", None)],
    "DevOps/K8/OBSERVABILITY/k8-observability.html": [
        ("Categories", "categories/index.html"),
        ("Observability", "categories/observability/index.html"),
        ("Observability Stack", None)],
    "DevOps/K8/STORAGE/k8-storage.html": [
        ("Categories", "categories/index.html"),
        ("Storage", "categories/storage/index.html"),
        ("Kubernetes Storage", None)],
    "DevOps/K8/Networking/k8-networking.html": [
        ("Categories", "categories/index.html"),
        ("Networking", "categories/networking/index.html"),
        ("Kubernetes Networking", None)],
    "SRE/INCIDENT-MANAGEMENT/incident-management.html": [
        ("Categories", "categories/index.html"),
        ("SRE", "categories/sre/index.html"),
        ("Incident Management", None)],
    "Infrastructure/OS/index.html": [
        ("Categories", "categories/index.html"),
        ("IT Infrastructure", "categories/it-infrastructure/index.html"),
        ("OS / Linux Series", None)],
    "Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html": [
        ("Categories", "categories/index.html"),
        ("Foundation", "categories/foundation/index.html"),
        ("Linux Fundamentals", None)],
    "Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html": [
        ("Categories", "categories/index.html"),
        ("Foundation", "categories/foundation/index.html"),
        ("Linux Advanced", None)],
    "Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html": [
        ("Categories", "categories/index.html"),
        ("Troubleshooting", "categories/troubleshooting/index.html"),
        ("Linux Troubleshooting", None)],
    "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html": [
        ("Categories", "categories/index.html"),
        ("Foundation", "categories/foundation/index.html"),
        ("Linux & Unix Glossary", None)],
}

# The twelve glossary term pages share a shape, so they are generated rather
# than typed out twelve times with eleven chances to differ.
TERMS = {
    "bash": "Bash", "init": "Init", "kernel-modules": "Kernel Modules",
    "linux-commands": "Linux Commands", "linux-distributions": "Linux Distributions",
    "linux-kernel": "Linux Kernel", "linux-unix-fundamentals": "Linux/Unix Fundamentals",
    "proc": "/proc", "shell": "Shell", "sys": "/sys", "sysctl": "sysctl",
    "terminal-cli": "Terminal & CLI",
}
for slug, label in TERMS.items():
    PAGES[f"Infrastructure/OS/LINUX/GLOSSARY/TERMS/fundamentals/{slug}.html"] = [
        ("Categories", "categories/index.html"),
        ("Foundation", "categories/foundation/index.html"),
        ("Glossary", "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html"),
        (label, None)]


def up_for(rel):
    """Relative prefix from a page back to the site root."""
    return "../" * (rel.count("/"))


def crumb_html(rel, trail):
    """The breadcrumb, in the same markup the generated pages use."""
    up = up_for(rel)
    bits = [f'<a href="{up}index.html">Home</a>']
    for label, href in trail:
        bits.append("<span>/</span>")
        if href is None:
            bits.append(f'<span class="cur">{label}</span>')
        else:
            bits.append(f'<a href="{up}{href}">{label}</a>')
    # Inner content only — chrome.nav() supplies the <div class="crumb"> wrapper.
    return "".join(bits)


# ── theming the page body ───────────────────────────────────────────────────
# These pages were never light-only by accident: they already used CSS
# variables. They used the WRONG ONES. --paper, --coal, --text and --smoke are
# raw brand colours — fixed values that must not move, because the terminal
# blocks and dark bands on these pages are painted with them and are correct in
# both themes. The semantic tokens (--page-bg, --heading-fg, --panel-bg) are
# the ones that flip. So the conversion is not a hunt through three thousand
# hex values; it is a few hundred token references that mean "the page
# surface" and were spelled "the brand's paper colour".
#
# Property-aware, because the same token means different things by property:
#   background: var(--paper)   a light surface   -> --page-bg   (flips)
#   color:      var(--paper)   near-white text on a dark band -> unchanged
#   background: var(--coal)    an intentional dark band       -> unchanged
#   color:      var(--coal)    a heading on light             -> --heading-fg
#
# Anything not listed here is left alone. Accents (crimson, cyan, amber, lime,
# purple) are brand colours and read correctly on both surfaces.
TOKEN_MAP = {
    ("color", "var(--text)"): "var(--page-fg)",
    ("color", "var(--coal)"): "var(--heading-fg)",
    ("color", "var(--ink)"): "var(--heading-fg)",
    ("background", "var(--paper)"): "var(--page-bg)",
    ("background-color", "var(--paper)"): "var(--page-bg)",
    ("background", "var(--smoke)"): "var(--panel-bg)",
    ("background-color", "var(--smoke)"): "var(--panel-bg)",
    ("border", "var(--coal)"): "var(--heading-fg)",
    ("border-color", "var(--coal)"): "var(--heading-fg)",
}

# Hardcoded blacks on light surfaces. In dark mode black-on-dark is invisible,
# so these are the rules that make a converted page look half-finished. The
# alpha decides which hairline token it is; the property decides wash vs line.
BLACK = re.compile(r"rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*(0?\.\d+|0|1)\s*\)")


def _black_token(prop, alpha):
    a = float(alpha)
    if prop in ("background", "background-color"):
        return "var(--wash)" if a <= .08 else None
    if prop.startswith("border") or prop in ("outline", "stroke"):
        return "var(--line-1)" if a <= .07 else ("var(--line-2)" if a <= .14 else None)
    if prop == "color":
        return "var(--line-2)" if a <= .1 else None
    return None


# Selectors that paint a deliberately dark component. A light-looking value
# inside one of these is a light chip ON a dark band and must not be flipped;
# the measurement pass proved these stay dark in both themes.
DARK_SCOPES = ("hero", "ticker", "footer", "cmd-", "code-", "term", "tb-",
               "arch-diagram", "arch-inner", "inside-", "el-", "cheat")


def _in_dark_scope(sel):
    return any(k in sel for k in DARK_SCOPES)


# ── the one page that is not a variant of the others ────────────────────────
# Issue #047 was built before the design system existed, to a different visual
# standard: its own palette (--bg #050a14, --accent #00e5ff), its own three
# typefaces, dark-only, and no nav at all. It is not an old version of the site
# design — it is a different design.
#
# It does not get the generic conversion above, and that is not a detail: the
# generic rule maps `color:var(--text)` to --page-fg because on the other
# twenty-four pages --text is the dark body colour on a light page. Here --text
# is #e2e8f0, the LIGHT colour on a dark page, so the same rule puts dark text
# on a dark background. Applying it cost this page its readability until the
# measurement caught it.
#
# Instead its private palette is aliased onto the shared tokens. Every rule on
# the page already goes through those names, so redefining them once converts
# the whole page — and it starts flipping with the theme like everything else.
PRIVATE_PALETTE = {
    "DevOps/K8/Networking/k8-networking.html": {
        "--bg": "var(--page-bg)",
        "--surface": "var(--panel-bg)",
        "--surface2": "var(--card-bg)",
        "--accent": "var(--cyan)",
        "--accent2": "var(--purple)",
        "--accent3": "var(--lime)",
        "--accent4": "var(--amber)",
        "--danger": "var(--crimson)",
        "--text": "var(--page-fg)",
        "--border": "var(--line-2)",
        # --muted is dropped entirely: chrome.TOKENS defines a themed one, and
        # the page's own #64748b does not move with the theme.
        "--muted": None,
    },
}

# Hardcoded accents that bypassed even the private palette, and the three
# typefaces this page used that appear nowhere else on the site.
PRIVATE_FIXUP = {
    "DevOps/K8/Networking/k8-networking.html": [
        # Accents used AS TEXT go to the readable variants, not the fill
        # colours: this page was dark, where bright lime on near-black is fine,
        # and turning it light left 9px labels at a 1.45 contrast ratio.
        ("color: var(--accent);", "color: var(--cyan-t);"),
        ("color: var(--accent2);", "color: var(--purple-t);"),
        ("color: var(--accent3);", "color: var(--lime-t);"),
        ("color: var(--accent4);", "color: var(--amber-t);"),
        ("color: var(--danger);", "color: var(--crimson-t);"),
        ("#34d399", "var(--lime-t)"),
        ("#a78bfa", "var(--purple-t)"),
        ("'Syne', sans-serif", "'Manrope', system-ui, sans-serif"),
        ("'Space Mono', monospace", "'DM Mono', monospace"),
        ("'IBM Plex Mono', monospace", "'DM Mono', monospace"),
        # The page requested three faces nothing else on the site uses, and
        # after the swap above it uses Manrope without loading it. One
        # substitution fixes both: same request count, right families.
        ("family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800"
         "&family=IBM+Plex+Mono:wght@300;400;600",
         "family=Manrope:wght@300;400;500;600;700;800"),
    ],
}

# A few rules on a converted page need saying outright rather than deriving.
# Blanket substitutions cannot tell a label on paper from a label on a dark
# code block: the same "use the readable accent" rule that fixed the 9px tags
# made .tip-code worse, because .tip-code paints its own dark surface and the
# bright accent was right there all along.
PRIVATE_CSS = {
    "DevOps/K8/Networking/k8-networking.html": """
/* Code blocks keep a dark surface in both themes, so they keep the bright
   accent — the readable variants are for accents on the page surface. */
.tip-code{background:var(--code-bg);color:var(--lime);}
.tip-number{color:var(--line-2);}
""",
}
PCSS_OPEN, PCSS_CLOSE = "/* page:begin */", "/* page:end */"


def private_palette(rel, src):
    """Alias a page's own colour names onto the site's semantic tokens."""
    table = PRIVATE_PALETTE.get(rel)
    if not table:
        return src, 0
    n = 0

    def fix_root(m):
        nonlocal n
        decls = []
        for d in m.group(1).split(";"):
            if ":" not in d:
                if d.strip():
                    decls.append(d)
                continue
            name, _, val = d.partition(":")
            key = name.strip()
            if key in table:
                repl = table[key]
                n += 1
                if repl is None:
                    continue                     # drop it, inherit the shared one
                decls.append(f"{name}:{repl}")
            else:
                decls.append(d)
        return ":root{" + ";".join(x.strip() for x in decls if x.strip()) + "}"

    src = re.sub(r":root\s*\{([^}]*)\}", fix_root, src, count=1)
    for a, b in PRIVATE_FIXUP.get(rel, ()):
        if a in src:
            n += src.count(a)
            src = src.replace(a, b)
    return src, n


def theme(rel, src):
    """Point this page's surface declarations at the tokens that flip."""
    if rel in PRIVATE_PALETTE:
        return private_palette(rel, src)
    blocks = list(re.finditer(r"<style[^>]*>(.*?)</style>", src, re.S | re.I))
    if not blocks:
        return src, 0
    out, n, last = [], 0, 0
    for m in blocks:
        css = m.group(1)
        # never touch the canonical chrome block
        guard = re.search(r"/\* chrome:begin \*/.*?/\* chrome:end \*/", css, re.S)
        keep = guard.group(0) if guard else None
        if keep:
            css = css.replace(keep, "\x00CHROME\x00")

        def fix_rule(rm):
            nonlocal n
            sel, decls = rm.group(1), rm.group(2)
            flat = re.sub(r"\s+", " ", sel).strip()
            if flat.startswith("@") or _in_dark_scope(flat):
                return rm.group(0)
            parts = []
            for d in decls.split(";"):
                if ":" not in d:
                    parts.append(d)
                    continue
                prop, _, val = d.partition(":")
                p = prop.strip().lower()
                v = val.strip()
                repl = TOKEN_MAP.get((p, v))
                if repl:
                    n += 1
                    parts.append(f"{prop}:{repl}")
                    continue
                bm = BLACK.fullmatch(v)
                if bm:
                    t = _black_token(p, bm.group(1))
                    if t:
                        n += 1
                        parts.append(f"{prop}:{t}")
                        continue
                if p in ("background", "background-color") and v.lower() in ("#fff", "#ffffff"):
                    n += 1
                    parts.append(f"{prop}:var(--card-bg)")
                    continue
                parts.append(d)
            return f"{sel}{{{';'.join(parts)}}}"

        css = re.sub(r"([^{}]+)\{([^{}]*)\}", fix_rule, css)
        if keep:
            css = css.replace("\x00CHROME\x00", keep)
        out.append(src[last:m.start(1)])
        out.append(css)
        last = m.end(1)
    out.append(src[last:])
    return "".join(out), n


def strip_marked(src, open_m, close_m):
    return re.sub(re.escape(open_m) + r".*?" + re.escape(close_m) + r"\n?",
                  "", src, flags=re.S)


def patch(rel, src):
    up = up_for(rel)

    # 1. the bar --------------------------------------------------------------
    bar = chrome.nav(up, crumb_html(rel, PAGES[rel]), toggle=chrome.TOGGLE)
    if re.search(r"<nav\b.*?</nav>", src, re.S):
        src = re.sub(r"<nav\b.*?</nav>", lambda m: bar, src, count=1, flags=re.S)
    else:
        # k8-networking had no bar at all; put one directly after <body>.
        src = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + bar, src, count=1)

    # 2. the footer -----------------------------------------------------------
    foot = chrome.footer(up)
    if re.search(r"<footer\b.*?</footer>", src, re.S):
        src = re.sub(r"<footer\b.*?</footer>", lambda m: foot, src, count=1, flags=re.S)
    else:
        src = re.sub(r"(</body>)", lambda m: foot + "\n" + m.group(1), src, count=1)

    # 3. the stylesheet -------------------------------------------------------
    # Appended to the LAST <style> so it wins ties against the page's own rules
    # by source order. The tokens it defines are the ones these pages were
    # missing — without them nothing on the page can respond to the theme.
    src = strip_marked(src, CSS_OPEN, CSS_CLOSE)
    # No leading newline: strip_marked takes the block and its trailing
    # newline, so a leading one would survive and the page would gain a blank
    # line per build — exactly the leak build_seo.py had.
    block = f"{CSS_OPEN}\n{chrome.CSS}\n{CSS_CLOSE}\n"
    i = src.rfind("</style>")
    if i == -1:
        raise SystemExit(f"{rel}: no <style> block to append the chrome CSS to")
    src = src[:i] + block + src[i:]

    # 4. the theme scripts ----------------------------------------------------
    src = strip_marked(src, PRE_OPEN, PRE_CLOSE)
    pre = f"{PRE_OPEN}\n{chrome.PREPAINT}\n{PRE_CLOSE}\n"
    src = src.replace("</head>", pre + "</head>", 1)

    src = strip_marked(src, JS_OPEN, JS_CLOSE)
    js = f"{JS_OPEN}\n{chrome.TOGGLE_JS}\n{JS_CLOSE}\n"
    src = src.replace("</body>", js + "</body>", 1)

    # 5. point the page's own surfaces at the tokens that flip ---------------
    src, converted = theme(rel, src)

    # 6. the handful of rules a page needs said outright ---------------------
    src = strip_marked(src, PCSS_OPEN, PCSS_CLOSE)
    extra = PRIVATE_CSS.get(rel)
    if extra:
        block = f"{PCSS_OPEN}{extra}{PCSS_CLOSE}\n"
        i = src.rfind("</style>")
        src = src[:i] + block + src[i:]
        converted += 1
    return src, converted


def run():
    n = total = 0
    for rel in sorted(PAGES):
        f = ROOT / rel
        if not f.exists():
            print(f"  skip (absent) {rel}")
            continue
        src = f.read_text(encoding="utf-8")
        out, conv = patch(rel, src)
        if out != src:
            f.write_text(out, encoding="utf-8")
        n += 1
        total += conv
        print(f"  {len(out) / 1024:6.0f} KB  {conv:>4} converted  {rel}")
    print(f"chrome applied to {n} hand-written page(s); "
          f"{total} declaration(s) pointed at semantic tokens")
    return n


if __name__ == "__main__":
    if "--check" in sys.argv:
        # Idempotence: patching twice must produce the same bytes as once.
        bad = []
        for rel in sorted(PAGES):
            f = ROOT / rel
            if not f.exists():
                continue
            a, _ = patch(rel, f.read_text(encoding="utf-8"))
            if patch(rel, a)[0] != a:
                bad.append(rel)
        print("NOT idempotent: " + ", ".join(bad) if bad else "idempotent on every page")
        sys.exit(1 if bad else 0)
    run()
