<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ██████╗ ██╗      █████╗ ████████╗███████╗ ██████╗ ██████╗    ║
║    ██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗   ║
║    ██████╔╝██║     ███████║   ██║   █████╗  ██║   ██║██████╔╝   ║
║    ██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝  ██║   ██║██╔═══╝    ║
║    ██║     ███████╗██║  ██║   ██║   ██║     ╚██████╔╝██║        ║
║    ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚═╝        ║
║                                                                  ║
║              O P S   ×   N E W S L E T T E R                     ║
║            Tech with Vishal Abhinav  ·  Open Source              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

![Live Issues](https://img.shields.io/badge/Live%20Issues-11-e53935?style=for-the-badge&logo=gitbook&logoColor=white)
![Glossary](https://img.shields.io/badge/Glossary-190%20Terms-f59e0b?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/Vishal-Abhinav/Platform-ops-Newsletter?style=for-the-badge&logo=github&color=00c2d4)
![License](https://img.shields.io/badge/License-MIT-84cc16?style=for-the-badge)
![Pages](https://img.shields.io/badge/GitHub%20Pages-Deployed-0a66c2?style=for-the-badge&logo=githubpages&logoColor=white)

<br/>

**A free, open-source knowledge base for DevOps Engineers, SREs, and Platform Builders.**
*Deep-dive issues · Architecture diagrams · Runbooks · A 190-term Linux & Unix glossary.*

### 🌐 **[Read it live → vishal-abhinav.github.io/Platform-ops-Newsletter](https://vishal-abhinav.github.io/Platform-ops-Newsletter/)**

[📚 Issues](#-published-issues) · [🗺️ Knowledge Map](#️-knowledge-map) · [🗂️ Structure](#️-repository-structure) · [🚀 Run Locally](#-quick-start)

</div>

---

## 🧭 What is This?

> *"I write the runbooks I wish existed the first time something broke at 2 AM."*

**Platform Ops** is a monthly technical newsletter covering the **Platform Engineering, Kubernetes, SRE and Infrastructure** stack — written by one practitioner working in production, not slideware.

This repository *is* the newsletter. Every issue is a self-contained HTML page served straight from GitHub Pages — no build step, no framework, no tracking. Fork it, read it offline, or lift a diagram for your own docs.

**Currently in this repo:** 11 full issue pages, a 190-term Linux & Unix glossary with 12 standalone term pages, 2 section hubs, and a homepage index — 26 pages in total.

---

## 🗺️ Knowledge Map

Live = published and linked. Roadmap = planned, not yet written.

```
platform-ops/
│
├── ⚙️  DevOps ........................................ 6 live · 3 planned
│   ├── ✅ Kubernetes Architecture .................... issue #048
│   ├── ✅ Kubernetes Networking ...................... issue #047
│   ├── ✅ Kubernetes & OpenShift Error Runbook ....... issue #049
│   ├── ✅ Kubernetes Storage ......................... issue #050
│   ├── ✅ Kubernetes Observability ................... issue #051
│   ├── ✅ CI/CD & GitOps ............................. issue #052
│   └── 🔜 RBAC · Admission Controllers · Multi-Cluster Federation
│
├── 📡  SRE ........................................... 1 live · 5 planned
│   ├── ✅ Incident Management & Postmortems .......... issue #053
│   └── 🔜 SLIs/SLOs/SLAs · Error Budgets · Reliability Eng
│          Chaos Engineering · On-Call Design
│
├── 🏗️  Infrastructure ................................ 4 live · 6 planned
│   ├── ✅ Linux Fundamentals ......................... issue #054
│   ├── ✅ Linux Advanced ............................. issue #055
│   ├── ✅ Linux Troubleshooting ...................... issue #056
│   ├── ✅ Linux & Unix Glossary (190 terms) .......... issue #057
│   └── 🔜 Windows Server · Unix/BSD · Virtualization
│          AWS · Azure · GCP
│
└── 🌐  Networking .................................... 1 live · 6 planned
    ├── ✅ Kubernetes Networking Decoded .............. issue #047
    └── 🔜 OSI Model · TCP/IP · Load Balancing
           Gateway API · Service Mesh · eBPF
```

---

## 📚 Published Issues

Issues with a link below have a full page in this repo. The rest are archive listings from earlier
editions of the newsletter that have not been migrated here yet.

| Issue | Date | Topic | Page |
|:-----:|:-----|:------|:-----|
| **#057** | Sep 2026 | [**Linux & Unix Glossary**](./Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html) — 190 terms, 15 categories, searchable | ✅ Live |
| **#056** | Sep 2026 | [**Linux Troubleshooting**](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) — load, OOM, disk/IO, network, boot failures | ✅ Live |
| **#055** | Sep 2026 | [**Linux Advanced**](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) — systemd, sysctl, namespaces, cgroups, LVM | ✅ Live |
| **#054** | Sep 2026 | [**Linux Fundamentals**](./Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html) — FHS, permissions, packages, shell | ✅ Live |
| **#053** | Sep 2026 | [**Incident Management & Postmortems**](./SRE/INCIDENT-MANAGEMENT/incident-management.html) — severity, IC role, blameless writeups | ✅ Live |
| **#052** | Aug 2026 | [**CI/CD & GitOps Deep-Dive**](./DevOps/CICD/cicd-pipelines.html) — Jenkins, GitLab CI, ArgoCD/Flux, canary | ✅ Live |
| **#051** | Jul 2026 | [**Observability Stack**](./DevOps/K8/OBSERVABILITY/k8-observability.html) — Prometheus, Grafana, Loki, Jaeger, SLO alerting | ✅ Live |
| **#050** | Jun 2026 | [**Kubernetes Storage**](./DevOps/K8/STORAGE/k8-storage.html) — PV/PVC, StorageClasses, CSI, StatefulSets, DR | ✅ Live |
| **#049** | May 2026 | [**K8s & OpenShift Error Runbook**](./DevOps/K8/ERROR/K8-error.html) — 32 error types across 5 layers | ✅ Live |
| **#048** | Apr 2026 | [**Kubernetes Architecture**](./DevOps/K8/ARCHITECTURE/k8-architecture.html) — control plane, nodes, QoS, scheduling | ✅ Live |
| **#047** | Mar 2026 | [**Kubernetes Networking Decoded**](./DevOps/K8/Networking/k8-networking.html) — CNI, Ingress, NetworkPolicy, CoreDNS | ✅ Live |
| #045 | Jan 2026 | AI/ML Workloads on Kubernetes | 🗄️ Archive listing |
| #044 | Dec 2025 | Platform Engineering & Backstage | 🗄️ Archive listing |
| #043 | Nov 2025 | GitOps at Scale with ArgoCD & Flux | 🗄️ Archive listing |
| #042 | Oct 2025 | Observability: Prometheus + Loki + Tempo | 🗄️ Archive listing |

**Section hubs:** [DevOps / Kubernetes](./DevOps/K8/index.html) · [Infrastructure / OS](./Infrastructure/OS/index.html)

---

## 🗂️ Repository Structure

Content is organised by **topic**, not by date — the folder path is the taxonomy.

```
Platform-ops-Newsletter/
│
├── index.html                          ← Homepage: hero, knowledge map, archive, author
├── README.md                           ← You are here
├── LICENSE                             ← MIT
│
├── .github/workflows/
│   └── static.yml                      ← Deploys the whole repo to GitHub Pages
│
├── DevOps/
│   ├── CICD/cicd-pipelines.html                        #052
│   └── K8/
│       ├── index.html                                  ← Kubernetes hub
│       ├── ARCHITECTURE/k8-architecture.html           #048
│       ├── ERROR/K8-error.html                         #049
│       ├── Networking/k8-networking.html               #047
│       ├── OBSERVABILITY/k8-observability.html         #051
│       └── STORAGE/k8-storage.html                     #050
│
├── Infrastructure/
│   └── OS/
│       ├── index.html                                  ← OS / Linux hub
│       └── LINUX/
│           ├── FUNDAMENTALS/linux-fundamentals.html    #054
│           ├── ADVANCED/linux-advanced.html            #055
│           ├── TROUBLESHOOTING/linux-troubleshooting.html  #056
│           └── GLOSSARY/
│               ├── linux-unix-glossary.html            #057 — 190 terms
│               └── TERMS/fundamentals/                 ← 12 standalone term pages
│                   ├── bash.html          ├── proc.html
│                   ├── init.html          ├── shell.html
│                   ├── kernel-modules.html├── sys.html
│                   ├── linux-commands.html├── sysctl.html
│                   ├── linux-distributions.html
│                   ├── linux-kernel.html  ├── terminal-cli.html
│                   └── linux-unix-fundamentals.html
│
└── SRE/
    └── INCIDENT-MANAGEMENT/incident-management.html    #053
```

**Convention:** each issue is one self-contained `.html` file — inline CSS, inline JS, no external
dependencies beyond Google Fonts. Links between pages are **relative**, so the site works when
opened from disk, from a local server, or from GitHub Pages.

---

## ✨ Site Features

The homepage is a single hand-written HTML file with no framework behind it:

| Feature | What it does |
|:--------|:-------------|
| 🌓 **Dark / light toggle** | Theme switch in the nav, remembered via `localStorage`, applied before first paint so there's no flash |
| ♾️ **Animated DevOps loop** | SVG infinity loop with the eight lifecycle stages and a light pulse racing the path |
| 🗺️ **Knowledge map** | Terminal-style `tree` view of every live and planned topic, plus a click-to-expand accordion per domain |
| 📜 **Scrollable archive** | Latest Issues is an internal scroll panel that stays height-matched to the topics column |
| 🔍 **Searchable glossary** | 190 terms across 15 categories, with standalone deep-dive pages for the terms that need one |
| 🦶 **Shared footer** | One footer across all 26 pages, with links rebuilt per directory depth |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Vishal-Abhinav/Platform-ops-Newsletter.git
cd Platform-ops-Newsletter

# Open the homepage directly — no build step needed
open index.html          # macOS
xdg-open index.html      # Linux
start index.html         # Windows
```

### Run with a local server

Relative links work from the filesystem, but a server matches production more closely:

```bash
python3 -m http.server 8080     # → http://localhost:8080
# or
npx serve .                     # → http://localhost:3000
```

### Check every internal link

Because every page cross-links by relative path, it's worth verifying after any move:

```bash
# lists any href/src that doesn't resolve to a tracked file
python3 - <<'EOF'
import subprocess, re, posixpath
tree = subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
tset, broken = set(tree), []
for f in [x for x in tree if x.endswith(".html")]:
    base = posixpath.dirname(f)
    for link in re.findall(r'(?:href|src)="([^"]+)"', open(f, encoding="utf-8").read()):
        if link.startswith(("http","mailto:","#","//","data:")): continue
        t = posixpath.normpath(posixpath.join(base, link.split("#")[0].split("?")[0]))
        if t and t not in tset: broken.append((f, link))
print(f"{len(broken)} broken links")
[print(" ", f, "->", l) for f, l in broken]
EOF
```

---

## 🤖 Deployment

Pushing to `main` triggers `.github/workflows/static.yml`, which uploads the **entire repository**
as the Pages artifact and deploys it — so a new issue goes live as soon as it's merged.

```yaml
on:
  push:
    branches: ["main"]
  workflow_dispatch:        # or deploy manually from the Actions tab
```

No build, no bundler, no `node_modules`. What's in the repo is what's on the site.

---

## ➕ Adding a New Issue

```bash
# 1. Branch
git checkout -b issue/058-gateway-api

# 2. Create the page in its topic folder (not a date folder)
mkdir -p Networking/GATEWAY-API
$EDITOR Networking/GATEWAY-API/gateway-api.html

# 3. Wire it into the homepage so it stops being a dead end:
#    - add the file to the knowledge-map tree in index.html
#    - add a topic-card badge link for its domain
#    - add an .issue-card entry in the Latest Issues archive
#    - bump the live/planned counts for that domain

# 4. Verify, commit, push
#    (run the link checker above — it catches wrong ../ depth immediately)
git add Networking/ index.html
git commit -m "Issue #058: Gateway API — the future of Ingress"
git push origin issue/058-gateway-api
```

> **Relative-path gotcha:** a page three folders deep needs `../../../index.html` to reach home.
> Getting this wrong is the single most common break — always run the link checker before pushing.

---

## 🔧 Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Hosting** | GitHub Pages, auto-deployed via GitHub Actions |
| **Pages** | Self-contained HTML — inline CSS + JS, zero runtime dependencies |
| **Diagrams** | Hand-written inline SVG and CSS |
| **Fonts** | Bebas Neue · DM Mono · Instrument Serif · Manrope (Google Fonts) |
| **Build** | None. That's the point. |
| **License** | MIT |

---

## ✍️ Author

<table>
  <tr>
    <td align="center">
      <b>Vishal Abhinav</b><br/>
      <sub>Platform Ops · Kubernetes · Platform Engineering · Cloud Architecture · DevOps · SRE · Infrastructure Automation</sub><br/>
      <sub>OCI Certified · CISSP Certified · AWS Certified · Cloud Native (in progress)</sub><br/><br/>
      <a href="https://github.com/Vishal-Abhinav">@Vishal-Abhinav</a> ·
      <a href="https://www.linkedin.com/in/vishal-abhinav/">LinkedIn</a>
    </td>
  </tr>
</table>

Platform Ops Engineer with 4+ years across Kubernetes, infrastructure and SRE-engineered systems —
designing for failure, automating the boring parts, and specialising in notification engine
architecture on SMPP and PDU session handling.

---

## 🤝 Contributing

Corrections and additions are welcome — this is a knowledge base, and knowledge bases rot.

```
🐛  Broken link or typo       → open a PR directly
📝  Technical correction      → open a PR, cite the source
💡  Suggest a topic           → open a GitHub Issue
🖼️  Contribute a diagram      → inline SVG please, no binaries
⭐  Star the repo             → helps other engineers find it
```

**Before opening a PR:** run the link checker above, and open your page in a browser at both
desktop and mobile widths.

---

## 📄 License

**MIT** — Copyright © 2026 Vishal Abhinav. See [LICENSE](./LICENSE).

Use it, fork it, quote it, build on it. Attribution appreciated, not required.

---

<div align="center">

**Platform Ops · Tech with Vishal Abhinav**

*Built for engineers, by an engineer.*

**[Read the latest issue →](https://vishal-abhinav.github.io/Platform-ops-Newsletter/)**

</div>
