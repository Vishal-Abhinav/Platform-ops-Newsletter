#!/usr/bin/env python3
"""Fourth build stage: the Reference Library.

Every reference deep-dive, listed on the homepage and in the README with the
sections it actually contains — the headings are scraped back out of the
rendered pages, so the listing cannot claim coverage the page doesn't have.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import html
import importlib
import pathlib
import re
import sys

sys.path.insert(0, str(TOOLS))

MODULES = ["fnd_a", "fnd_b"]
CATEGORY = "Foundation"

# slug -> path, matching build_foundation's layout
def page_path(slug):
    return f"Foundation/{slug.upper()}/{slug}.html"


def esc(s):
    return html.escape(str(s), quote=True)


def strip(s):
    # the harvested names are already HTML-escaped inside the page, so they
    # have to be decoded before we escape them again for a new context
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


# ── harvest what each page actually covers ───────────────────────────────────
topics = {}
for mod in MODULES:
    for t in importlib.import_module(mod).TOPICS:
        topics[t["slug"]] = t

ORDER = ["computer-fundamentals", "operating-systems", "shell-and-bash",
         "python", "git-version-control"]

LIB = []
for slug in ORDER:
    t = topics[slug]
    body = t["sections"]
    # split at the section headings so CORE and ADVANCED cards stay separate
    parts = re.split(r'<h2>(CORE CONCEPTS|ADVANCED)</h2>', body)
    buckets = {}
    for i in range(1, len(parts) - 1, 2):
        buckets[parts[i]] = re.findall(r'<span class="rc-name">(.*?)</span>', parts[i + 1])
    core = [strip(x) for x in buckets.get("CORE CONCEPTS", [])]
    adv = [strip(x) for x in buckets.get("ADVANCED", [])]
    # the diagram's layer labels describe the model the page opens with
    layers = re.findall(r'<text class="dg-layer"[^>]*>(.*?)</text>', body)
    read = strip(t["meta"][0])
    LIB.append(dict(slug=slug, title=t["title"], tagline=t["tagline"],
                    path=page_path(slug), read=read, core=core, adv=adv,
                    layers=[strip(x).title() for x in layers]))
    assert core and adv, f"{slug}: failed to harvest card names"


# ── homepage section ─────────────────────────────────────────────────────────
def homepage_html():
    cards = ""
    for i, e in enumerate(LIB, 1):
        core = "".join(f'<li>{esc(c)}</li>' for c in e["core"])
        adv = "".join(f'<li>{esc(c)}</li>' for c in e["adv"])
        model = " → ".join(esc(l) for l in e["layers"])
        cards += f"""
      <article class="lib-card">
        <a class="lib-hit" href="{e['path']}" aria-label="{esc(e['title'])}"></a>
        <div class="lib-top">
          <span class="lib-n">{i:02d}</span>
          <div class="lib-id">
            <h3 class="lib-title">{esc(e['title'])}</h3>
            <div class="lib-meta"><span class="lib-kind">Reference</span>
              <span>{esc(e['read'])}</span><span>{CATEGORY}</span></div>
          </div>
        </div>
        <p class="lib-desc">{esc(e['tagline'])}</p>
        <div class="lib-model"><b>The model</b> {model}</div>
        <div class="lib-cols">
          <div class="lib-col"><div class="lib-col-t core">Core</div><ul>{core}</ul></div>
          <div class="lib-col"><div class="lib-col-t adv">Advanced</div><ul>{adv}</ul></div>
        </div>
        <div class="lib-go">Read {esc(e['title'])} →</div>
      </article>"""

    n_core = sum(len(e["core"]) for e in LIB)
    n_adv = sum(len(e["adv"]) for e in LIB)
    return f"""
<!-- ═══════════ REFERENCE LIBRARY ═══════════ -->
<div class="lib-section" id="library">
  <div class="lib-inner reveal">
    <div class="section-tag">Reference Library</div>
    <h2 class="section-title">DEEP-DIVES, IN FULL</h2>
    <p class="section-lead">Standing reference pages, separate from the monthly issues — each one
      an architecture diagram, a core section, an advanced section, worked examples and a
      cheatsheet. Everything each page covers is listed below.</p>
    <div class="lib-stats">
      <div><b>{len(LIB)}</b><i>Pages</i></div>
      <div><b>{n_core}</b><i>Core topics</i></div>
      <div><b>{n_adv}</b><i>Advanced topics</i></div>
      <div><b>{CATEGORY}</b><i>Category</i></div>
    </div>
    <div class="lib-grid">{cards}
    </div>
  </div>
</div>
"""


CSS = """
/* ─── REFERENCE LIBRARY ─── */
.lib-section{background:var(--panel-bg);border-top:1px solid var(--hairline-2);}
.lib-inner{max-width:1200px;margin:0 auto;padding:100px 64px 90px;}
.lib-stats{display:flex;flex-wrap:wrap;gap:1px;background:var(--hairline-2);
  border:1px solid var(--hairline-2);margin:-32px 0 40px;}
.lib-stats > div{flex:1 1 120px;background:var(--page-bg);padding:15px 20px;text-align:center;}
.lib-stats b{display:block;font-family:'Bebas Neue',sans-serif;font-size:28px;line-height:1;
  color:var(--heading-fg);font-weight:400;}
.lib-stats i{display:block;font-style:normal;font-family:'DM Mono',monospace;font-size:8.5px;
  letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);margin-top:6px;}
.lib-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:2px;}
.lib-card{position:relative;background:var(--card-bg);border:1px solid var(--hairline-1);
  padding:26px 26px 22px;transition:background .22s,border-color .22s;}
.lib-card:hover{background:var(--page-bg);border-color:var(--hairline-4);}
/* one full-card hit area, so the nested lists stay selectable text */
.lib-hit{position:absolute;inset:0;z-index:1;text-indent:-9999px;overflow:hidden;}
.lib-card > *:not(.lib-hit){position:relative;pointer-events:none;}
.lib-top{display:flex;align-items:flex-start;gap:14px;}
.lib-n{font-family:'DM Mono',monospace;font-size:10px;color:var(--ash);padding-top:5px;}
.lib-title{font-family:'Bebas Neue',sans-serif;font-size:27px;letter-spacing:.6px;line-height:1;
  color:var(--heading-fg);font-weight:400;}
.lib-meta{display:flex;flex-wrap:wrap;gap:12px;margin-top:7px;font-family:'DM Mono',monospace;
  font-size:8.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
.lib-kind{color:var(--crimson);}
.lib-desc{font-size:13px;line-height:1.6;color:var(--muted);margin:14px 0 0;}
.lib-model{margin-top:14px;padding:10px 12px;background:var(--wash-1);
  border-left:2px solid var(--cyan);font-family:'DM Mono',monospace;font-size:9px;
  letter-spacing:.8px;line-height:1.8;color:var(--muted);text-transform:uppercase;}
.lib-model b{display:block;color:var(--cyan);letter-spacing:1.6px;margin-bottom:3px;font-weight:400;}
.lib-cols{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px;}
.lib-col-t{font-family:'DM Mono',monospace;font-size:8.5px;letter-spacing:2px;text-transform:uppercase;
  padding-bottom:6px;margin-bottom:8px;border-bottom:1px solid var(--hairline-2);}
.lib-col-t.core{color:#4c840f;}
.lib-col-t.adv{color:#8a5806;}
html[data-theme="dark"] .lib-col-t.core{color:var(--lime);}
html[data-theme="dark"] .lib-col-t.adv{color:var(--amber);}
.lib-col ul{list-style:none;margin:0;padding:0;}
.lib-col li{font-size:11.5px;line-height:1.5;color:var(--muted);padding:3px 0 3px 12px;
  position:relative;}
.lib-col li::before{content:'';position:absolute;left:0;top:10px;width:4px;height:1px;
  background:var(--hairline-4);}
.lib-go{margin-top:20px;padding-top:14px;border-top:1px solid var(--hairline-2);
  font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.6px;text-transform:uppercase;
  color:var(--crimson);}
@media(max-width:900px){.lib-inner{padding:70px 32px 64px;}}
@media(max-width:560px){.lib-inner{padding:56px 20px 50px;}.lib-cols{grid-template-columns:1fr;gap:14px;}}
"""


# ── README section ───────────────────────────────────────────────────────────
def readme_md():
    rows = "\n".join(
        f"| **[{e['title']}](./{e['path']})** | {e['read'].replace(' read','')} | "
        f"{len(e['core'])} core · {len(e['adv'])} advanced | {e['tagline'].split(' — ')[0]} |"
        for e in LIB)
    detail = ""
    for e in LIB:
        core = "".join(f"<li>{html.escape(c)}</li>" for c in e["core"])
        adv = "".join(f"<li>{html.escape(a)}</li>" for a in e["adv"])
        detail += (f"\n<details>\n<summary><b>{html.escape(e['title'])}</b> — "
                   f"{e['read']}, {len(e['core'])} core + {len(e['adv'])} advanced sections</summary>\n\n"
                   f"*{html.escape(e['tagline'])}*\n\n"
                   f"**The model:** {' → '.join(html.escape(l) for l in e['layers'])}\n\n"
                   f"<table><tr><th align=\"left\">Core</th><th align=\"left\">Advanced</th></tr>\n"
                   f"<tr><td valign=\"top\"><ul>{core}</ul></td>"
                   f"<td valign=\"top\"><ul>{adv}</ul></td></tr></table>\n\n"
                   f"[Read it →](./{e['path']})\n</details>\n")

    return f"""## 📖 Reference Library

Standing deep-dives, separate from the monthly issues. Each is an architecture diagram, a
**core** section, an **advanced** section, worked terminal examples, a decision table and a
cheatsheet. They carry no issue number and are not mailed out — they are the reference the
issues link back to.

| Page | Read | Sections | Covers |
|:--|:--|:--|:--|
{rows}

Expand any of them for the full contents:
{detail}
---

"""


if __name__ == "__main__":
    # 1. homepage
    SRC = ROOT / 'index.html'
    src = SRC.read_text(encoding='utf-8')
    if 'id="library"' in src:
        print('index.html already has the library section — skipping')
    else:
      src = src.replace('<!-- ═══════════ AUTHORS ═══════════ -->',
                      homepage_html() + '\n<!-- ═══════════ AUTHORS ═══════════ -->', 1)
      src = src.replace('/* ─── TOOLCHAIN DIAGRAM ─── */',
                        CSS.strip() + '\n\n/* ─── TOOLCHAIN DIAGRAM ─── */', 1)
      src = src.replace('    <li><a href="categories/index.html">Categories</a></li>\n',
                        '    <li><a href="categories/index.html">Categories</a></li>\n'
                        '    <li><a href="#library">Library</a></li>\n', 1)
      src = src.replace('          <a href="categories/index.html">All Categories</a>',
                        '          <a href="#library">Reference Library</a>\n'
                        '          <a href="categories/index.html">All Categories</a>', 1)
      SRC.write_text(src, encoding='utf-8')
    print(f'index.html -> {len(src)} chars, library section added')

    # 2. README
    R = ROOT / 'README.md'
    md = R.read_text(encoding='utf-8')
    start = md.find('## 📖 Reference Library')
    if start != -1:
        end = md.index('## 🗂️ Repository Structure')
        md = md[:start] + md[end:]
    anchor = '## 🗂️ Repository Structure'
    md = md.replace(anchor, readme_md() + anchor, 1)
    md = md.replace('[📚 Issues](#-published-issues) · ',
                    '[📚 Issues](#-published-issues) · [📖 Library](#-reference-library) · ', 1)
    R.write_text(md, encoding='utf-8')
    print(f'README.md -> {len(md)} chars, {len(LIB)} reference pages listed')
    for e in LIB:
        print(f"   {e['title']:26} {len(e['core'])} core + {len(e['adv'])} advanced")
