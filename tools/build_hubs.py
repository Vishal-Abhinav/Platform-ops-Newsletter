#!/usr/bin/env python3
"""Generate categories/index.html plus one hub per category (33 of them).

Each hub carries an architecture diagram built from that category's own
topics, so a block can only show as live if taxonomy.py says a published
page covers it — the picture cannot drift away from the map.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import html
import pathlib
import shutil
import sys

sys.path.insert(0, str(TOOLS))
from taxonomy import PILLARS, cat_stats          # noqa: E402
from hubs_spec import SPEC                       # noqa: E402

OUT = ROOT / 'categories'
BASE = "https://vishal-abhinav.github.io/Platform-ops-Newsletter/"
KEY = {"L": "live", "P": "pipe", "-": "plan"}
ZONE = {"live": "Live now", "pipe": "In pipeline", "plan": "Planned"}

# Which issue each live page is, for the article cards.
PAGES = {
 "DevOps/K8/ARCHITECTURE/k8-architecture.html": ("#048", "Kubernetes Architecture Deep-Dive",
   "Control plane, worker nodes, QoS classes and scheduling — with diagrams."),
 "DevOps/K8/Networking/k8-networking.html": ("#047", "Kubernetes Networking Decoded",
   "Pod networking, CNI plugins, Ingress, NetworkPolicy and CoreDNS."),
 "DevOps/K8/ERROR/K8-error.html": ("#049", "Kubernetes & OpenShift Error Runbook",
   "32 error types across 5 layers, each with the production fix."),
 "DevOps/K8/STORAGE/k8-storage.html": ("#050", "Kubernetes Storage Deep-Dive",
   "PV and PVC, StorageClasses, CSI internals, StatefulSets, backup and DR."),
 "DevOps/K8/OBSERVABILITY/k8-observability.html": ("#051", "Observability Stack Deep-Dive",
   "Prometheus and Grafana, Loki and ELK, Jaeger and OpenTelemetry, SLO alerting."),
 "DevOps/CICD/cicd-pipelines.html": ("#052", "CI/CD & GitOps Deep-Dive",
   "Jenkins and GitLab CI, ArgoCD and Flux, security gates, canary and blue-green."),
 "SRE/INCIDENT-MANAGEMENT/incident-management.html": ("#053", "Incident Management & Postmortems",
   "Severity, the Incident Commander role, blameless postmortems, follow-through."),
 "Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html": ("#054", "Linux Fundamentals",
   "Filesystem hierarchy, users and permissions, packages, processes, shell scripting."),
 "Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html": ("#055", "Linux Advanced",
   "systemd internals, kernel and sysctl tuning, namespaces and cgroups, LVM."),
 "Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html": ("#056", "Linux Troubleshooting",
   "High load, memory and OOM, disk and I/O, network, and boot failures."),
 "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html": ("#057", "Linux & Unix Glossary",
   "190 terms across 15 categories, searchable, with deep-dive term pages."),
 # Reference deep-dives — not monthly issues, so they carry no issue number.
 "Foundation/COMPUTER-FUNDAMENTALS/computer-fundamentals.html": ("Reference", "Computer Fundamentals",
   "Caches, translation, interrupts, and the six orders of magnitude between L1 and a disk seek."),
 "Foundation/OPERATING-SYSTEMS/operating-systems.html": ("Reference", "Operating Systems",
   "The syscall boundary, the scheduler, the page cache, cgroups, and the failures each one causes."),
 "Foundation/SHELL-AND-BASH/shell-and-bash.html": ("Reference", "Shell & Bash",
   "Expansion order, exit codes, redirection, strict mode's blind spots, traps and parallelism."),
 "Foundation/PYTHON/python.html": ("Reference", "Python",
   "The GIL, choosing a concurrency model, streaming large files, subprocess and logging."),
 "Foundation/GIT-VERSION-CONTROL/git-version-control.html": ("Reference", "Git & Version Control",
   "The object model, the three trees, reflog recovery, bisect, and repository weight."),
 "Commands/LINUX-COMMANDS/linux-commands.html": ("Reference", "Linux Commands",
   "132 commands in 10 groups — files, permissions, text, processes, packages, disk, network."),
 "Commands/KUBERNETES-COMMANDS/kubernetes-commands.html": ("Reference", "Kubernetes Commands",
   "62 kubectl commands by task — inspect, apply, debug, roll out, and script the output."),
 "Commands/DOCKER-COMMANDS/docker-commands.html": ("Reference", "Docker Commands",
   "59 commands — run, build, inspect, network, compose, and reclaim the disk."),
}

STATUS_FILL = {"live": "var(--n-live-bg)", "pipe": "var(--n-pipe-bg)", "plan": "var(--n-plan-bg)"}
STATUS_LINE = {"live": "var(--n-live-br)", "pipe": "var(--n-pipe-br)", "plan": "var(--n-plan-br)"}
STATUS_TEXT = {"live": "var(--n-live-fg)", "pipe": "var(--n-pipe-fg)", "plan": "var(--n-plan-fg)"}


def esc(s):
    return html.escape(str(s), quote=True)


# ── index the taxonomy ───────────────────────────────────────────────────────
CATS, ORDER = {}, []
for pname, cats in PILLARS:
    for cname, icon, topics in cats:
        CATS[cname] = {"pillar": pname, "icon": icon, "topics": topics,
                       "status": {t[0]: t[1] for t in topics},
                       "href": {t[0]: t[2] for t in topics}}
        ORDER.append(cname)


# ── SVG architecture diagram ─────────────────────────────────────────────────
W, LABEL_W, PAD_R = 1000, 168, 20
NODE_H, GAP_X, GAP_Y, LAYER_GAP = 44, 10, 10, 26
AREA = W - LABEL_W - PAD_R
CHAR = 6.35          # DM Mono advance at 10.5px


def wrap(text, width_px, max_lines=2):
    limit = max(6, int((width_px - 14) / CHAR))
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if not lines:
        lines = [text[:limit]]
    # anything that still won't fit gets an ellipsis rather than spilling out
    if len(lines) == max_lines:
        used = sum(len(x) for x in lines) + len(lines) - 1
        if used < len(text):
            lines[-1] = lines[-1][:max(3, limit - 1)] + "…"
    return lines


def diagram(cname):
    info = CATS[cname]
    layers = SPEC[cname][2]
    parts, y = [], 14

    for label, names in layers:
        # split a crowded layer into rows that keep the boxes readable
        per_row = len(names)
        while per_row > 1 and (AREA - GAP_X * (per_row - 1)) / per_row < 104:
            per_row -= 1
        rows = [names[i:i + per_row] for i in range(0, len(names), per_row)]
        rows_h = len(rows) * NODE_H + (len(rows) - 1) * GAP_Y
        mid = y + rows_h / 2

        parts.append(f'<text class="dg-layer" x="{LABEL_W - 22}" y="{mid + 4:.1f}">{esc(label.upper())}</text>')
        parts.append(f'<circle class="dg-tick" cx="{LABEL_W - 8}" cy="{mid:.1f}" r="3"/>')

        for ri, row in enumerate(rows):
            n = len(row)
            w = (AREA - GAP_X * (n - 1)) / n
            ry = y + ri * (NODE_H + GAP_Y)
            for i, name in enumerate(row):
                x = LABEL_W + i * (w + GAP_X)
                st = KEY.get(info["status"].get(name, "-"), "plan")
                href = info["href"].get(name)
                lines = wrap(name, w)
                ty = ry + NODE_H / 2 + (4 if len(lines) == 1 else -2)
                body = (
                    f'<rect x="{x:.1f}" y="{ry}" width="{w:.1f}" height="{NODE_H}" rx="4" '
                    f'fill="{STATUS_FILL[st]}" stroke="{STATUS_LINE[st]}" '
                    f'{"stroke-dasharray=&quot;3 3&quot; " if st == "plan" else ""}stroke-width="1"/>'
                )
                for li, ln in enumerate(lines):
                    body += (f'<text class="dg-node" x="{x + w / 2:.1f}" y="{ty + li * 12:.1f}" '
                             f'fill="{STATUS_TEXT[st]}">{esc(ln)}</text>')
                if st == "live":
                    body += (f'<circle cx="{x + 9:.1f}" cy="{ry + 9}" r="3" '
                             f'fill="var(--n-live-dot)"/>')
                if st == "live" and href:
                    parts.append(f'<a class="dg-a" href="../../{esc(href)}">{body}</a>')
                else:
                    parts.append(f'<g class="dg-g">{body}</g>')
        y += rows_h + LAYER_GAP

    h = y - LAYER_GAP + 14
    spine = (f'<line class="dg-spine" x1="{LABEL_W - 8}" y1="14" '
             f'x2="{LABEL_W - 8}" y2="{h - 14:.1f}"/>')
    return (f'<svg class="dg" viewBox="0 0 {W} {h:.0f}" role="img" '
            f'aria-label="{esc(cname)} architecture — live blocks link to the issue that covers them">'
            f'{spine}{"".join(parts)}</svg>')


# ── CSS shared by every hub ──────────────────────────────────────────────────
CSS = """
:root{--ink:#08090c;--paper:#f2f0eb;--smoke:#e4e0d8;--ash:#b8b2a7;--coal:#1c1f26;
 --cyan:#00c2d4;--amber:#f59e0b;--crimson:#e53935;--lime:#84cc16;--purple:#7c3aed;
 --page-bg:#f2f0eb;--panel-bg:#e4e0d8;--card-bg:#f8f7f4;--page-fg:#1c1f26;--heading-fg:#1c1f26;
 --muted:#6b6860;--line-1:rgba(0,0,0,.06);--line-2:rgba(0,0,0,.1);--line-3:rgba(0,0,0,.16);
 --wash:rgba(0,0,0,.04);--nav-bg:rgba(242,240,235,.9);
 --n-live-bg:rgba(132,204,22,.16);--n-live-br:#84cc16;--n-live-fg:#3f6f0c;--n-live-dot:#84cc16;
 --n-pipe-bg:rgba(245,158,11,.13);--n-pipe-br:rgba(245,158,11,.55);--n-pipe-fg:#8a5806;
 --n-plan-bg:transparent;--n-plan-br:rgba(0,0,0,.2);--n-plan-fg:#8d8981;}
html[data-theme="dark"]{--page-bg:#0c0e12;--panel-bg:#14161c;--card-bg:#181b22;--page-fg:#e7e5df;
 --heading-fg:#eeece6;--muted:#9a978e;--line-1:rgba(255,255,255,.07);--line-2:rgba(255,255,255,.11);
 --line-3:rgba(255,255,255,.18);--wash:rgba(255,255,255,.05);--nav-bg:rgba(12,14,18,.9);
 --n-live-bg:rgba(132,204,22,.16);--n-live-fg:#a7e137;
 --n-pipe-bg:rgba(245,158,11,.14);--n-pipe-fg:#f5b544;
 --n-plan-br:rgba(255,255,255,.2);--n-plan-fg:#8a877f;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--page-bg);color:var(--page-fg);font-family:'Manrope',system-ui,sans-serif;
 -webkit-font-smoothing:antialiased;}
a{color:inherit;}
.wrap{max-width:1120px;margin:0 auto;padding:0 40px;}
@media(max-width:700px){.wrap{padding:0 20px;}}

nav{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:18px;
 padding:14px 40px;background:var(--nav-bg);backdrop-filter:blur(14px);
 border-bottom:1px solid var(--line-1);}
.nav-logo{display:flex;align-items:center;gap:9px;font-family:'Bebas Neue',sans-serif;
 font-size:19px;letter-spacing:2.5px;text-decoration:none;color:var(--heading-fg);flex-shrink:0;}
.nav-logo span{width:8px;height:8px;border-radius:50%;background:var(--crimson);}
.crumb{flex:1;min-width:0;display:flex;align-items:center;gap:8px;flex-wrap:wrap;
 font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;
 color:var(--muted);}
.crumb a{text-decoration:none;color:var(--muted);}
.crumb a:hover{color:var(--crimson);}
.crumb .cur{color:var(--heading-fg);}
.nav-right{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.tt{width:32px;height:32px;border:1px solid var(--line-2);background:transparent;border-radius:50%;
 cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);}
.tt:hover{color:var(--crimson);border-color:var(--crimson);}
.tt svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;}
html:not([data-theme="dark"]) .tt .moon,html[data-theme="dark"] .tt .sun{display:none;}
@media(max-width:700px){nav{padding:12px 18px;gap:12px;}.crumb{display:none;}}

header.hero{padding:64px 0 40px;border-bottom:1px solid var(--line-1);}
.eyebrow{display:inline-flex;align-items:center;gap:10px;font-family:'DM Mono',monospace;
 font-size:10.5px;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;}
.eyebrow::before{content:'';width:22px;height:1px;background:var(--crimson);}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(42px,7vw,76px);line-height:.95;
 letter-spacing:-.5px;color:var(--heading-fg);display:flex;align-items:center;gap:16px;flex-wrap:wrap;}
h1 .ico{font-size:.6em;line-height:1;}
.tagline{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:19px;
 color:var(--muted);max-width:660px;margin-top:14px;}
.stats{display:flex;flex-wrap:wrap;gap:1px;background:var(--line-2);border:1px solid var(--line-2);
 margin-top:30px;}
.stat{background:var(--page-bg);padding:13px 22px;flex:1 1 100px;text-align:center;}
.stat b{display:block;font-family:'Bebas Neue',sans-serif;font-size:27px;line-height:1;
 color:var(--heading-fg);font-weight:400;}
.stat b.live{color:#4c840f;}.stat b.pipe{color:#a06508;}.stat b.plan{color:var(--ash);}
html[data-theme="dark"] .stat b.live{color:var(--lime);}
html[data-theme="dark"] .stat b.pipe{color:var(--amber);}
html[data-theme="dark"] .stat b.plan{color:#6e6b64;}
.stat i{display:block;font-style:normal;font-family:'DM Mono',monospace;font-size:8.5px;
 letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);margin-top:6px;}
.progress{display:flex;height:5px;background:var(--line-1);margin-top:1px;}
.progress i{display:block;}
.progress i.live{background:var(--lime);}.progress i.pipe{background:var(--amber);}
.progress i.plan{background:var(--line-3);}

section{padding:56px 0;border-bottom:1px solid var(--line-1);}
h2{font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:1px;color:var(--heading-fg);
 margin-bottom:8px;}
.lede{font-size:14px;color:var(--muted);max-width:660px;margin-bottom:30px;line-height:1.6;}

.dg-scroll{overflow-x:auto;padding-bottom:6px;}
.dg{width:100%;min-width:660px;height:auto;display:block;}
.dg-layer{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.6px;
 fill:var(--muted);text-anchor:end;}
.dg-node{font-family:'DM Mono',monospace;font-size:10.5px;letter-spacing:.2px;text-anchor:middle;}
.dg-spine,.dg-tick{stroke:var(--line-3);fill:var(--line-3);stroke-width:1;}
.dg-a{cursor:pointer;}
.dg-a rect{transition:fill .18s,stroke-width .18s;}
.dg-a:hover rect{fill:var(--lime);stroke-width:2;}
.dg-a:hover text{fill:#0c0e12;}
.dg-key{display:flex;flex-wrap:wrap;gap:18px;margin-top:20px;font-family:'DM Mono',monospace;
 font-size:9.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
.dg-key span{display:flex;align-items:center;gap:7px;}
.dg-key i{width:13px;height:9px;border-radius:2px;display:block;}
.dg-key i.live{background:var(--n-live-bg);border:1px solid var(--n-live-br);}
.dg-key i.pipe{background:var(--n-pipe-bg);border:1px solid var(--n-pipe-br);}
.dg-key i.plan{border:1px dashed var(--n-plan-br);}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:2px;}
.card{background:var(--card-bg);border:1px solid var(--line-1);padding:24px;text-decoration:none;
 display:block;transition:background .2s;position:relative;}
.card:hover{background:var(--panel-bg);}
.card .num{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:2px;color:var(--crimson);}
.card h3{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:.5px;
 color:var(--heading-fg);margin:8px 0 8px;font-weight:400;line-height:1.1;}
.card p{font-size:12.5px;line-height:1.6;color:var(--muted);}
.card .go{display:inline-block;margin-top:14px;font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:1.6px;text-transform:uppercase;color:var(--crimson);}

.zone{display:flex;align-items:center;gap:9px;font-family:'DM Mono',monospace;font-size:9px;
 letter-spacing:2.2px;text-transform:uppercase;margin:22px 0 10px;}
.zone::after{content:'';flex:1;height:1px;background:var(--line-1);}
.zone.live{color:#4c840f;}.zone.pipe{color:#8a5806;}.zone.plan{color:var(--ash);}
html[data-theme="dark"] .zone.live{color:var(--lime);}
html[data-theme="dark"] .zone.pipe{color:var(--amber);}
.chips{display:flex;flex-wrap:wrap;gap:6px;}
.chip{display:inline-block;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.6px;
 padding:5px 11px;border-radius:20px;text-transform:uppercase;text-decoration:none;
 border:1px solid transparent;transition:background .2s,color .2s,border-color .2s;}
button.chip{cursor:pointer;line-height:1.5;font-family:'DM Mono',monospace;}
.chip.live{background:var(--n-live-bg);border-color:var(--n-live-br);color:var(--n-live-fg);}
.chip.live::before{content:'●';font-size:7px;vertical-align:middle;margin-right:5px;color:var(--lime);}
.chip.live::after{content:' ↗';}
.chip.live:hover{background:var(--lime);color:#0c0e12;}
.chip.pipe{background:var(--n-pipe-bg);border-color:var(--n-pipe-br);color:var(--n-pipe-fg);}
.chip.plan{border:1px dashed var(--n-plan-br);color:var(--n-plan-fg);}
.chip.pipe:hover,.chip.plan:hover{border-color:var(--crimson);color:var(--crimson);}
.chip.req{background:var(--crimson)!important;border-color:var(--crimson)!important;color:#fff!important;}
.chip.req::before{content:'✓';margin-right:5px;font-size:9px;}
.hint{display:flex;align-items:center;gap:7px;font-family:'DM Mono',monospace;font-size:9.5px;
 letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin-bottom:18px;}
.hint b{color:var(--crimson);font-weight:400;}

.siblings{display:flex;flex-wrap:wrap;gap:2px;background:var(--line-1);border:1px solid var(--line-1);}
.sib{flex:1 1 200px;background:var(--card-bg);padding:16px 18px;text-decoration:none;
 transition:background .2s;}
.sib:hover{background:var(--panel-bg);}
.sib .n{font-family:'Bebas Neue',sans-serif;font-size:19px;letter-spacing:.5px;
 color:var(--heading-fg);display:block;}
.sib .c{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;color:var(--muted);
 text-transform:uppercase;margin-top:4px;display:block;}
.sib.cur{background:var(--panel-bg);border-left:3px solid var(--crimson);}
.pager{display:flex;gap:2px;margin-top:2px;}
.pager a{flex:1;background:var(--card-bg);border:1px solid var(--line-1);padding:16px 18px;
 text-decoration:none;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;
 text-transform:uppercase;color:var(--muted);transition:background .2s,color .2s;}
.pager a:hover{background:var(--panel-bg);color:var(--crimson);}
.pager a.next{text-align:right;}
.pager a b{display:block;font-family:'Bebas Neue',sans-serif;font-size:19px;letter-spacing:.5px;
 color:var(--heading-fg);font-weight:400;margin-top:5px;}

.req-pill{position:fixed;left:22px;bottom:22px;z-index:60;display:none;align-items:center;gap:12px;
 background:var(--coal);color:var(--paper);border:0;border-radius:40px;padding:13px 15px 13px 20px;
 box-shadow:0 18px 44px rgba(0,0,0,.32);cursor:pointer;font-family:'DM Mono',monospace;
 font-size:10.5px;letter-spacing:1.4px;text-transform:uppercase;text-decoration:none;}
.req-pill.show{display:flex;}
html[data-theme="dark"] .req-pill{background:var(--paper);color:var(--coal);}
.req-pill b{color:var(--lime);font-weight:400;}
html[data-theme="dark"] .req-pill b{color:#4c840f;}
.req-pill .go{background:var(--crimson);color:#fff;border-radius:30px;padding:6px 12px;}
@media(max-width:600px){.req-pill{left:12px;right:12px;bottom:12px;justify-content:space-between;}}

footer{background:var(--coal);color:var(--paper);padding:52px 40px 26px;margin-top:0;}
.f-in{max-width:1120px;margin:0 auto;}
.f-top{display:grid;grid-template-columns:1.3fr 2fr;gap:48px;}
.f-logo{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:3px;color:#fff;
 text-decoration:none;}
.f-tag{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-size:14px;
 color:rgba(255,255,255,.5);margin-top:12px;line-height:1.6;}
.f-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;}
.f-col-t{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:2.2px;text-transform:uppercase;
 color:rgba(255,255,255,.35);margin-bottom:12px;}
.f-cols a{display:block;font-size:12.5px;color:rgba(255,255,255,.72);text-decoration:none;
 padding:4px 0;transition:color .2s;}
.f-cols a:hover{color:var(--cyan);}
.f-bot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-top:38px;
 padding-top:18px;border-top:1px solid rgba(255,255,255,.1);
 font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.2px;color:rgba(255,255,255,.35);}
.f-bot a{color:rgba(255,255,255,.5);}
@media(max-width:820px){.f-top{grid-template-columns:1fr;gap:30px;}footer{padding:44px 20px 22px;}}
@media(max-width:560px){.f-cols{grid-template-columns:1fr 1fr;}}
"""

THEME_JS = """<script>
(function(){try{var t=localStorage.getItem('po-theme');
 if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}catch(e){}})();
</script>"""

GC = """<!-- Privacy-friendly analytics (GoatCounter). Put your site code between the
     quotes on the PO_GC line below; left empty, nothing loads and nothing is
     sent. The README has a one-liner that sets it across every page at once. -->
<script>
(function(){var PO_GC='';
 if(!PO_GC) return;
 var s=document.createElement('script');
 s.async=true; s.src='https://gc.zgo.at/count.js';
 s.setAttribute('data-goatcounter','https://'+PO_GC+'.goatcounter.com/count');
 document.head.appendChild(s);})();
</script>"""

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&'
         'family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&'
         'family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">')

TOGGLE = ('<button class="tt" id="tt" type="button" aria-label="Toggle dark mode">'
          '<svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/>'
          '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2'
          'M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
          '<svg class="moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/>'
          '</svg></button>')

SHARED_JS = """<script>
document.getElementById('tt').addEventListener('click',function(){
  var d=document.documentElement.getAttribute('data-theme')==='dark';
  if(d){document.documentElement.removeAttribute('data-theme');}
  else{document.documentElement.setAttribute('data-theme','dark');}
  try{localStorage.setItem('po-theme',d?'light':'dark');}catch(e){}
});
/* Topic requests share sessionStorage with the homepage — same origin, same
   key — so a topic queued on a hub is already in the form when you land there. */
(function(){
  var pill=document.getElementById('pill'), n=document.getElementById('pillN');
  if(!pill) return;
  var q=[]; try{q=JSON.parse(sessionStorage.getItem('po-topics')||'[]');}catch(e){}
  if(!Array.isArray(q)) q=[];
  function save(){try{sessionStorage.setItem('po-topics',JSON.stringify(q));}catch(e){}}
  function paint(){
    document.querySelectorAll('button.chip').forEach(function(b){
      b.classList.toggle('req', q.indexOf(b.textContent.trim())!==-1);
    });
    n.textContent=q.length; pill.classList.toggle('show', q.length>0);
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('button.chip'); if(!b) return;
    var t=b.textContent.trim(), i=q.indexOf(t);
    if(i!==-1){q.splice(i,1);} else if(q.length<8){q.push(t);}
    save(); paint();
  });
  paint();
})();
</script>"""


def page(title, desc, canonical, crumbs, body, up="../../"):
    css = "../hub.css" if up == "../../" else "hub.css"
    crumb = ""
    for i, (label, href) in enumerate(crumbs):
        if i:
            crumb += '<span>/</span>'
        crumb += (f'<a href="{esc(href)}">{esc(label)}</a>' if href
                  else f'<span class="cur">{esc(label)}</span>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Vishal Abhinav">
<meta name="copyright" content="© 2026 Vishal Abhinav. Text and diagrams CC BY-NC-ND 4.0.">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Platform Ops · Tech with Vishal Abhinav">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{BASE}assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}assets/og/home.png">
{FONTS}
<link rel="alternate" type="application/rss+xml" title="Platform Ops — new issues" href="{up}feed.xml">
{THEME_JS}
{GC}
<link rel="stylesheet" href="{css}">
</head>
<body>
<nav>
  <a href="{up}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>
  <div class="crumb">{crumb}</div>
  <div class="nav-right">{TOGGLE}<a href="{up}index.html#subscribe" class="nav-logo"
    style="font-size:11px;letter-spacing:1.6px;font-family:'DM Mono',monospace">SUBSCRIBE</a></div>
</nav>
{body}
<a class="req-pill" id="pill" href="{up}index.html#subscribe">
  <span><b id="pillN">0</b> topics queued</span><span class="go">Get notified →</span>
</a>
<footer>
  <div class="f-in">
    <div class="f-top">
      <div>
        <a class="f-logo" href="{up}index.html">PLATFORM OPS</a>
        <p class="f-tag">Field notes on Kubernetes, SRE, and Platform Engineering —
          written from production, not slideware.</p>
      </div>
      <div class="f-cols">
        <div><div class="f-col-t">Newsletter</div>
          <a href="{up}index.html#issues">Latest Issues</a>
          <a href="{up}Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html">Newest — Issue #057</a>
          <a href="{up}index.html#subscribe">Subscribe</a></div>
        <div><div class="f-col-t">Explore</div>
          <a href="{up}categories/index.html">All Categories</a>
          <a href="{up}index.html#topics">Knowledge Map</a>
          <a href="{up}index.html#authors">About the Author</a></div>
        <div><div class="f-col-t">Connect</div>
          <a href="https://github.com/Vishal-Abhinav/Platform-ops-Newsletter" target="_blank">GitHub Repo ↗</a>
          <a href="{up}feed.xml">RSS Feed</a>
          <a href="#">Back to Top ↑</a></div>
      </div>
    </div>
    <div class="f-bot">
      <div>© 2026 Vishal Abhinav · Platform Ops — code MIT,
        <a href="{up}LICENSE">text &amp; diagrams CC BY-NC-ND 4.0</a></div>
      <div>Built for engineers, by an engineer.</div>
    </div>
  </div>
</footer>
{SHARED_JS}
</body>
</html>
"""


def flexes(l, p, n):
    return "".join(f'<i class="{c}" style="flex:{v}"></i>'
                   for c, v in (("live", l), ("pipe", p), ("plan", n)) if v)


# ── build ────────────────────────────────────────────────────────────────────
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
(OUT / "hub.css").write_text(CSS.strip() + "\n", encoding='utf-8')

pillar_of = {c: CATS[c]["pillar"] for c in ORDER}
built = []

for idx, cname in enumerate(ORDER):
    info = CATS[cname]
    slug, tagline, _layers = SPEC[cname]
    l, p, n = cat_stats(info["topics"])
    total = l + p + n
    prev_c = ORDER[idx - 1] if idx else None
    next_c = ORDER[idx + 1] if idx + 1 < len(ORDER) else None

    # live articles behind this category, deduped by page, in issue order
    pages = []
    for t, st, href in info["topics"]:
        if st == "L" and href and href not in [x[0] for x in pages]:
            pages.append((href, [t]))
        elif st == "L" and href:
            next(x for x in pages if x[0] == href)[1].append(t)
    pages.sort(key=lambda x: (PAGES.get(x[0], ("#000",))[0] != "Reference",
                          PAGES.get(x[0], ("#000",))[0]), reverse=True)

    cards = ""
    for href, covered in pages:
        num, ptitle, pdesc = PAGES.get(href, ("", href, ""))
        label = esc(num) if num == "Reference" else f'Issue {esc(num)}'
        cards += (f'<a class="card" href="../../{esc(href)}">'
                  f'<div class="num">{label}</div><h3>{esc(ptitle)}</h3>'
                  f'<p>{esc(pdesc)}</p>'
                  f'<div class="go">Covers {esc(", ".join(covered[:4]))}'
                  f'{"…" if len(covered) > 4 else ""} →</div></a>')

    chips = ""
    for code in ("L", "P", "-"):
        group = [t for t in info["topics"] if t[1] == code]
        if not group:
            continue
        k = KEY[code]
        chips += f'<div class="zone {k}">{ZONE[k]} · {len(group)}</div><div class="chips">'
        for t, _st, href in group:
            if k == "live" and href:
                chips += f'<a class="chip live" href="../../{esc(href)}">{esc(t)}</a>'
            else:
                chips += f'<button type="button" class="chip {k}">{esc(t)}</button>'
        chips += '</div>'

    sibs = [c for c in ORDER if pillar_of[c] == info["pillar"]]
    sib_html = ""
    for c in sibs:
        cl, cp, cn = cat_stats(CATS[c]["topics"])
        cur = ' cur' if c == cname else ''
        sib_html += (f'<a class="sib{cur}" href="../{SPEC[c][0]}/index.html">'
                     f'<span class="n">{CATS[c]["icon"]} {esc(c)}</span>'
                     f'<span class="c">{cl} live · {cp} pipe · {cn} planned</span></a>')

    pager = '<div class="pager">'
    pager += (f'<a href="../{SPEC[prev_c][0]}/index.html">← Previous<b>{esc(prev_c)}</b></a>'
              if prev_c else '<a href="../index.html">← All categories<b>Index</b></a>')
    pager += (f'<a class="next" href="../{SPEC[next_c][0]}/index.html">Next →<b>{esc(next_c)}</b></a>'
              if next_c else '<a class="next" href="../index.html">All categories →<b>Index</b></a>')
    pager += '</div>'

    if pages:
        published_block = (
            '<section><div class="wrap"><h2>PUBLISHED ON THIS</h2>'
            f'<p class="lede">{len(pages)} issue{"s" if len(pages) != 1 else ""} covering '
            f'{l} of the {total} topics here.</p>'
            f'<div class="cards">{cards}</div></div></section>')
    else:
        published_block = (
            '<section><div class="wrap"><h2>NOTHING PUBLISHED YET</h2>'
            '<p class="lede">No issue covers this category so far. Queue the topics you want '
            "and you'll get an email the day one lands — that queue is also how the running "
            'order gets decided.</p></div></section>')

    body = f"""
<header class="hero"><div class="wrap">
  <div class="eyebrow">{esc(info['pillar'])} · Category {idx + 1:02d} of {len(ORDER)}</div>
  <h1><span class="ico">{info['icon']}</span>{esc(cname)}</h1>
  <p class="tagline">{esc(tagline)}</p>
  <div class="stats">
    <div class="stat"><b>{total}</b><i>Topics</i></div>
    <div class="stat"><b class="live">{l}</b><i>Live</i></div>
    <div class="stat"><b class="pipe">{p}</b><i>In pipeline</i></div>
    <div class="stat"><b class="plan">{n}</b><i>Planned</i></div>
    <div class="stat"><b>{len(pages)}</b><i>Issues</i></div>
  </div>
  <div class="progress">{flexes(l, p, n)}</div>
</div></header>

<section><div class="wrap">
  <h2>ARCHITECTURE</h2>
  <p class="lede">How this category fits together, bottom to top. Every green block is
    covered by a published issue — click it to go straight there.</p>
  <div class="dg-scroll">{diagram(cname)}</div>
  <div class="dg-key">
    <span><i class="live"></i> Live — click through</span>
    <span><i class="pipe"></i> In pipeline</span>
    <span><i class="plan"></i> Planned</span>
  </div>
</div></section>

{published_block}

<section><div class="wrap">
  <h2>ALL {total} TOPICS</h2>
  <div class="hint"><b>Click</b> any pipeline or planned topic to be told when it lands</div>
  {chips}
</div></section>

<section style="border-bottom:0"><div class="wrap">
  <h2>{esc(info['pillar'].upper())} PILLAR</h2>
  <p class="lede">The other categories sitting alongside this one.</p>
  <div class="siblings">{sib_html}</div>
  {pager}
</div></section>
"""

    title = f"{cname} · Platform Ops · Vishal Abhinav"
    canonical = f"{BASE}categories/{slug}/"
    crumbs = [("Home", "../../index.html"), ("Categories", "../index.html")]
    if info["pillar"] != cname:
        anchor = info["pillar"].lower().replace(" & ", "-").replace(" ", "-")
        crumbs.append((info["pillar"], "../index.html#" + anchor))
    crumbs.append((cname, None))
    (OUT / slug).mkdir()
    (OUT / slug / "index.html").write_text(
        page(title, tagline, canonical, crumbs, body), encoding='utf-8')
    built.append((cname, slug, l, p, n, total, len(pages)))

# ── categories/index.html ────────────────────────────────────────────────────
groups = ""
for pname, cats in PILLARS:
    pl = pp = pn = 0
    rows = ""
    for cname, icon, topics in cats:
        cl, cp, cn = cat_stats(topics)
        pl += cl; pp += cp; pn += cn
        rows += (f'<a class="sib" href="{SPEC[cname][0]}/index.html">'
                 f'<span class="n">{icon} {esc(cname)}</span>'
                 f'<span class="c">{cl} live · {cp} pipe · {cn} planned</span></a>')
    anchor = pname.lower().replace(" & ", "-").replace(" ", "-")
    groups += (f'<section id="{anchor}"><div class="wrap"><h2>{esc(pname.upper())}</h2>'
               f'<p class="lede">{len(cats)} categor{"y" if len(cats) == 1 else "ies"} · '
               f'{pl} live · {pp} in pipeline · {pn} planned.</p>'
               f'<div class="siblings">{rows}</div></div></section>')

TL = sum(b[2] for b in built); TP = sum(b[3] for b in built); TN = sum(b[4] for b in built)
idx_body = f"""
<header class="hero"><div class="wrap">
  <div class="eyebrow">Knowledge Map</div>
  <h1>ALL CATEGORIES</h1>
  <p class="tagline">Every subject this newsletter covers, or intends to — {TL + TP + TN} topics
    across {len(built)} categories and {len(PILLARS)} pillars. Each has its own page with an
    architecture diagram and links to whatever is already published.</p>
  <div class="stats">
    <div class="stat"><b>{TL + TP + TN}</b><i>Topics</i></div>
    <div class="stat"><b>{len(built)}</b><i>Categories</i></div>
    <div class="stat"><b class="live">{TL}</b><i>Live</i></div>
    <div class="stat"><b class="pipe">{TP}</b><i>In pipeline</i></div>
    <div class="stat"><b class="plan">{TN}</b><i>Planned</i></div>
  </div>
  <div class="progress">{flexes(TL, TP, TN)}</div>
</div></header>
{groups}
"""
(OUT / "index.html").write_text(
    page("All Categories · Platform Ops · Vishal Abhinav",
         f"All {len(built)} categories across {len(PILLARS)} pillars — {TL + TP + TN} topics, "
         f"{TL} of them covered by a published issue.",
         f"{BASE}categories/",
         [("Home", "../index.html"), ("Categories", None)],
         idx_body, up="../"), encoding='utf-8')

total_bytes = sum(f.stat().st_size for f in OUT.rglob('*.html'))
print(f"built {len(built)} category hubs + 1 index = {len(list(OUT.rglob('*.html')))} pages, "
      f"{total_bytes / 1024:.0f} KB")
print(f"totals: {TL} live / {TP} pipeline / {TN} planned")
for b in sorted(built, key=lambda x: -x[6])[:6]:
    print(f"   {b[0]:26} {b[6]} issues, {b[2]} live of {b[5]}")
