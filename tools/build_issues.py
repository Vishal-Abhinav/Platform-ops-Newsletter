#!/usr/bin/env python3
"""Build the standalone issue archive from the RSS issue register."""
import html
import os
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("PO_ROOT") or TOOLS.parent)
sys.path.insert(0, str(TOOLS))

from build_feed import ISSUES  # noqa: E402
from content_page import render, section  # noqa: E402

OUT = ROOT / "issues"
OUT.mkdir(parents=True, exist_ok=True)


def esc(value):
    return html.escape(str(value), quote=True)


cards = []
for index, (number, path, title, blurb, published) in enumerate(
        sorted(ISSUES, key=lambda issue: -issue[0])):
    newest = '<span class="ia-new">Newest</span>' if index == 0 else ""
    series = path.split("/", 1)[0].replace("-", " ")
    cards.append(f"""<a class="ia-card" href="../{esc(path)}">
  <div class="ia-meta">{published.strftime('%B %Y')} · Issue #{number:03d} {newest}</div>
  <h3>{esc(title)}</h3>
  <p>{esc(blurb)}</p>
  <div class="ia-foot"><span>{esc(series)}</span><b>Read issue <span aria-hidden="true">→</span></b></div>
</a>""")

body = '<div class="ia-grid">' + "".join(cards) + "</div>"
sections = section(
    "Published archive",
    "Every issue, newest first",
    "No truncated homepage list and no hidden scroll area. The complete published archive lives here.",
    body,
)

page = render(
    slug="issues",
    title="Latest Issues",
    tagline="The complete Platform Ops archive: practical deep-dives, architecture, commands, and production troubleshooting.",
    eyebrow=f"Archive · {len(ISSUES)} published issues",
    crumbs=[("Home", "../index.html"), ("Issues", "")],
    meta=[f"<b>{len(ISSUES)}</b> published", "Newest first", "RSS available"],
    sections=sections,
    pager='<a class="pager next" href="../feed.xml"><span>Follow updates</span><b>RSS feed →</b></a>',
    up="../",
    css="topic.css",
    canon="issues/",
)

css = (ROOT / "Foundation" / "topic.css").read_text(encoding="utf-8")
css += """
/* Standalone issue archive */
.ia-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:2px;margin-top:34px;}
.ia-card{display:flex;flex-direction:column;min-width:0;padding:28px;background:var(--card-bg);
  color:var(--page-fg);text-decoration:none;border:1px solid var(--hairline-2);
  transition:border-color .2s,transform .2s,background .2s;}
.ia-card:hover{border-color:var(--crimson);transform:translateY(-2px);background:var(--wash-1);}
.ia-meta{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);}
.ia-new{display:inline-block;margin-left:8px;padding:3px 7px;border:1px solid var(--crimson);border-radius:12px;color:var(--crimson);}
.ia-card h3{font-family:'Bebas Neue',sans-serif;font-size:30px;line-height:1.05;letter-spacing:0;margin:15px 0 10px;color:var(--heading-fg);}
.ia-card p{font-size:14px;line-height:1.65;color:var(--muted);margin:0 0 24px;}
.ia-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:auto;padding-top:16px;border-top:1px solid var(--hairline-2);font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);}
.ia-foot b{font-weight:400;color:var(--crimson);white-space:nowrap;}
@media(max-width:760px){.ia-grid{grid-template-columns:1fr}.ia-card{padding:22px}.ia-card h3{font-size:26px}}
"""

(OUT / "topic.css").write_text(css, encoding="utf-8")
(OUT / "index.html").write_text(page, encoding="utf-8")
print(f"wrote issues/index.html ({len(ISSUES)} published issues)")
