#!/usr/bin/env python3
"""Kubernetes & OpenShift — Complete Topic Map.

A reader supplied a 46-category reference list (Kubernetes and OpenShift,
concepts through error vocabulary) and asked for it to be added, grouped
exactly as given, each item marked Live / Pipeline / Planned.

That list is far more granular than the curated Kubernetes/OpenShift/Service
Mesh categories on the existing hub pages (categories/kubernetes/,
categories/openshift/) — those track ~35-13 topics each, each one backed by
a specific published issue. Folding 942 granular items into that page would
turn a clean per-issue index into a wall of text, so this is a SEPARATE
page: a completeness map over the reader's own list, not a replacement for
the hub pages.

STATUS IS NOT GUESSED. An item is marked Live only when either:
  (a) it matches — by exact name — a topic already tagged "L" in
      taxonomy.py, which is the site's own single source of truth and
      already carries a real link, or
  (b) the item is a *distinctive* string (a CamelCase API/error name like
      OOMKilled, a hyphenated component name like kube-apiserver, a
      `kubectl`/`oc` command, an HTTP status code, or a named product like
      Prometheus) and that exact phrase is found, word-bounded, in the page
      that actually covers this category.
Everything else that merely appears in nearby prose (a bare word like
"storage" or "console") is Pipeline, not Live — a generic word matching is
not evidence a specific checklist line is documented. Anything not found at
all is Planned. This errs toward under-claiming, deliberately: the one
thing worse than a slow roadmap is a wrong "live" badge on a dead link.
"""
import html
import os
import pathlib as _pl
import re
import sys

TOOLS = _pl.Path(__file__).resolve().parent
ROOT = _pl.Path(os.environ.get("PO_ROOT") or TOOLS.parent)
sys.path.insert(0, str(TOOLS))

from siteconf import BASE                              # noqa: E402
from taxonomy import PILLARS                            # noqa: E402
from topicmap_data import GROUPS                        # noqa: E402
import chrome                                            # noqa: E402

# Not imported from build_hubs.py: that module runs its whole build as a
# side effect of being imported (no __main__ guard around it), so importing
# it here would silently rebuild every category hub a second time. Same
# three lines every hub page already carries — verify.py checks for exactly
# this string.
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

OUT_DIR = ROOT / "categories" / "kubernetes-openshift-map"
OUT = OUT_DIR / "index.html"
UP = "../../"
SELF_PATH = "categories/kubernetes-openshift-map/index.html"

# ── the pages this list is checked against ──────────────────────────────────
HOME = {
 "Kubernetes Fundamentals": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Pods": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Deployments": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Stateful Applications": ["DevOps/K8/STORAGE/k8-storage.html"],
 "DaemonSets": ["Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html"],
 "Jobs & CronJobs": ["Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html"],
 "Services": ["DevOps/K8/Networking/k8-networking.html"],
 "Networking": ["DevOps/K8/Networking/k8-networking.html"],
 "Ingress": ["DevOps/K8/Networking/k8-networking.html"],
 "Storage": ["DevOps/K8/STORAGE/k8-storage.html"],
 "ConfigMap & Secrets": ["Kubernetes/KUBERNETES-CONFIG-AND-ACCESS/kubernetes-config-and-access.html"],
 "Scheduling": ["Kubernetes/KUBERNETES-SCHEDULING/kubernetes-scheduling.html"],
 "Resources": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Security": ["Kubernetes/KUBERNETES-CLUSTER-OPERATIONS/kubernetes-cluster-operations.html"],
 "Kubernetes Certificates": ["Kubernetes/KUBERNETES-CLUSTER-OPERATIONS/kubernetes-cluster-operations.html"],
 "etcd": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Control Plane": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Kubelet": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Container Runtime": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Container Images": ["DevOps/K8/ARCHITECTURE/k8-architecture.html"],
 "Health Checks": ["Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html"],
 "Autoscaling": ["Kubernetes/KUBERNETES-AUTOSCALING/kubernetes-autoscaling.html"],
 "Observability": ["DevOps/K8/OBSERVABILITY/k8-observability.html"],
 "Kubernetes Troubleshooting": ["Commands/KUBERNETES-COMMANDS/kubernetes-commands.html"],
 "OpenShift Fundamentals": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift CLI": ["Commands/OPENSHIFT-COMMANDS/openshift-commands.html"],
 "OpenShift Projects": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift Routes": ["OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html"],
 "OpenShift Security Context Constraints — SCC": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift Operators": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift Cluster Operators": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "OpenShift Nodes": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "MachineConfig": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "OpenShift Networking": ["OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html"],
 "OpenShift Image Registry": ["OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html"],
 "OpenShift Builds": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift Monitoring": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "OpenShift Storage": ["OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html"],
 "OpenShift Authentication": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "OpenShift API": ["OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html"],
 "OpenShift Web Console": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "OpenShift Upgrade": ["OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html"],
 "Disaster Recovery": ["Kubernetes/KUBERNETES-CLUSTER-OPERATIONS/kubernetes-cluster-operations.html"],
 "Performance Troubleshooting": ["DevOps/K8/ERROR/K8-error.html"],
 "Application Troubleshooting": ["DevOps/K8/ERROR/K8-error.html"],
 "Database Connectivity from Kubernetes/OpenShift": ["DevOps/K8/ERROR/K8-error.html"],
}
ERROR_PAGE = "DevOps/K8/ERROR/K8-error.html"

PROPER_NOUNS = {n.lower() for n in [
 "Prometheus", "Grafana", "Alertmanager", "Thanos", "Velero", "OADP", "CoreDNS", "Kubelet",
 "containerd", "CRI-O", "CRI", "CNI", "CSI", "RBAC", "SCC", "OLM", "LDAP", "HTPasswd",
 "OAuth", "OIDC", "SAML", "PKI", "HPA", "VPA", "IPVS", "MTU", "NXDOMAIN", "SERVFAIL",
 "Envoy", "Istio", "Linkerd", "Jaeger", "OpenTelemetry", "CSR", "etcd",
]}

_TAG = re.compile(r"<[^>]+>")


def _text_of(rel_path):
    p = ROOT / rel_path
    if not p.exists():
        return ""
    raw = p.read_text(encoding="utf-8", errors="ignore")
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", raw))).lower()


def _found(phrase, hay):
    return re.search(r'(?<!\w)' + re.escape(phrase.lower()) + r'(?!\w)', hay) is not None


def _distinctive(item):
    if re.search(r'[a-z][A-Z]', item):
        return True
    if re.match(r'^[a-z0-9]+(-[a-z0-9]+){1,}$', item):
        return True
    if item.startswith("kubectl ") or item.startswith("oc "):
        return True
    head = item.split()[0] if item.split() else item
    if re.fullmatch(r'\d{3}', head):
        return True
    if item.lower() in PROPER_NOUNS:
        return True
    if "=" in item or item.startswith("x509") or item.startswith("certificate signed"):
        return True
    return False


def classify():
    tax_index = {}
    for _, cats in PILLARS:
        for _, _, topics in cats:
            for name, status, href in topics:
                if status == "L" and href:
                    tax_index[name.strip().lower()] = href

    page_cache = {}

    def text_for(rel):
        if rel not in page_cache:
            page_cache[rel] = _text_of(rel)
        return page_cache[rel]

    err_text = text_for(ERROR_PAGE)

    out = []
    live = pipe = plan = 0
    for title, items in GROUPS:
        home_pages = HOME[title]
        home_text = " ".join(text_for(p) for p in home_pages)
        rows = []
        for it in items:
            key = it.strip().lower()
            if key in tax_index:
                rows.append((it, "L", UP + tax_index[key]))
                live += 1
                continue
            fh = _found(it, home_text)
            fe = _found(it, err_text)
            if _distinctive(it) and (fh or fe):
                link = UP + (home_pages[0] if fh else ERROR_PAGE)
                rows.append((it, "L", link))
                live += 1
            elif fh or fe:
                rows.append((it, "P", None))
                pipe += 1
            else:
                rows.append((it, "-", None))
                plan += 1
        out.append((title, rows))
    return out, live, pipe, plan


def esc(s):
    return html.escape(s, quote=True)


def slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def zone_block(status_class, label, rows):
    items = [r for r in rows if r[1] == status_class]
    if not items:
        return ""
    chips = []
    for name, _, href in items:
        cls = {"L": "chip live", "P": "chip pipe", "-": "chip plan"}[status_class]
        if href:
            chips.append(f'<a class="{cls}" href="{href}">{esc(name)}</a>')
        else:
            chips.append(f'<span class="{cls}">{esc(name)}</span>')
    zclass = {"L": "live", "P": "pipe", "-": "plan"}[status_class]
    return (f'<div class="zone {zclass}">{label} · {len(items)}</div>'
            f'<div class="chips">{"".join(chips)}</div>')


def build():
    groups, live, pipe, plan = classify()
    total = live + pipe + plan

    toc_cards = []
    sections = []
    for n, (title, rows) in enumerate(groups, 1):
        g_live = sum(1 for _, s, _ in rows if s == "L")
        g_pipe = sum(1 for _, s, _ in rows if s == "P")
        g_plan = len(rows) - g_live - g_pipe
        anchor = slug(title)
        toc_cards.append(
            f'<a class="card" href="#{anchor}"><div class="num">{n:02d}</div>'
            f'<h3>{esc(title)}</h3>'
            f'<p>{len(rows)} items — {g_live} live · {g_pipe} pipeline · {g_plan} planned</p></a>'
        )
        zones = (zone_block("L", "Live now", rows)
                 + zone_block("P", "In pipeline", rows)
                 + zone_block("-", "Planned", rows))
        sections.append(
            f'<section id="{anchor}"><div class="wrap">'
            f'<div class="eyebrow">{n:02d} / 46</div>'
            f'<h2>{esc(title)}</h2>'
            f'<p class="lede">{len(rows)} items · {g_live} live · {g_pipe} pipeline · {g_plan} planned</p>'
            f'{zones}'
            f'</div></section>'
        )

    title_tag = "Kubernetes & OpenShift — Complete Topic Map"
    desc = (f"Every concept and error state across Kubernetes and OpenShift, in the 46 groups a "
            f"reader asked for — {total} items, each marked live, in pipeline, or planned.")
    # verify.py's rule (and every sibling hub page): an index.html canonical
    # is the DIRECTORY url, no filename — canonical/og:url use this; only the
    # JSON-LD "url" field keeps the literal index.html, matching build_hubs.py.
    canonical = BASE + SELF_PATH[:-len("index.html")]
    full_url = BASE + SELF_PATH

    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title_tag)} · Platform Ops · Vishal Abhinav</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="Vishal Abhinav">
<meta name="copyright" content="© 2026 Vishal Abhinav. Text and diagrams CC BY-NC-ND 4.0.">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Platform Ops · Tech with Vishal Abhinav">
<meta property="og:title" content="{esc(title_tag)} · Platform Ops · Vishal Abhinav">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}assets/og/home.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title_tag)} · Platform Ops · Vishal Abhinav">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}assets/og/home.png">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="alternate" type="application/rss+xml" title="Platform Ops — new issues" href="{UP}feed.xml">
<script>
(function(){{try{{var t=localStorage.getItem('po-theme');
 if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}}catch(e){{}}}})();
</script>
<link rel="stylesheet" href="../hub.css">
<style>
.toc{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:2px;margin-top:26px;}}
.eyebrow.small{{margin-top:0;}}
</style>
</head>
<body>
<nav>
  <a href="{UP}index.html" class="nav-logo"><span></span>PLATFORM OPS</a>
  <div class="crumb"><a href="{UP}index.html">Home</a><span>/</span><a href="{UP}categories/index.html">Categories</a><span>/</span><span class="cur">Kubernetes &amp; OpenShift Topic Map</span></div>
  <div class="nav-right">{chrome.TOGGLE}<a href="{UP}terminal/index.html" class="nav-lab" target="_blank" rel="noopener">LAB</a><a href="{UP}index.html#subscribe" class="nav-logo nav-sub" style="font-size:11px;letter-spacing:1.6px;font-family:'DM Mono',monospace">SUBSCRIBE</a></div>
</nav>

<header class="hero"><div class="wrap">
  <div class="eyebrow">Reference · Kubernetes + OpenShift · 46 groups</div>
  <h1><span class="ico">☸️</span>Complete Topic Map</h1>
  <p class="tagline">Every concept and error state across Kubernetes and OpenShift, grouped exactly
    as requested — {total} items, honestly marked: live only where a published page actually
    covers it, not where the word merely appears nearby.</p>
  <div class="stats">
    <div class="stat"><b>{total}</b><i>Items</i></div>
    <div class="stat"><b class="live">{live}</b><i>Live</i></div>
    <div class="stat"><b class="pipe">{pipe}</b><i>In pipeline</i></div>
    <div class="stat"><b class="plan">{plan}</b><i>Planned</i></div>
    <div class="stat"><b>46</b><i>Groups</i></div>
  </div>
  <div class="progress"><i class="live" style="flex:{live}"></i><i class="pipe" style="flex:{pipe}"></i><i class="plan" style="flex:{plan}"></i></div>
</div></header>

<section><div class="wrap">
  <h2>JUMP TO A GROUP</h2>
  <p class="lede">Numbered in the order the list was given — Kubernetes concepts first, then OpenShift, then the cross-cutting operational groups.</p>
  <div class="toc">{"".join(toc_cards)}</div>
</div></section>
"""

    import json as _json
    jsonld1 = ('<script type="application/ld+json">' + _json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": title_tag, "description": desc, "url": full_url,
        "isPartOf": {"@type": "WebSite", "name": "Platform Ops", "url": BASE},
        "author": {"@type": "Person", "name": "Vishal Abhinav",
                   "url": "https://www.linkedin.com/in/vishal-abhinav/",
                   "jobTitle": "Platform Ops Engineer"},
        "publisher": {"@type": "Organization", "name": "Platform Ops", "url": BASE,
                      "logo": {"@type": "ImageObject", "url": BASE + "assets/og/home.png"}},
        "inLanguage": "en",
    }) + '</script>')
    jsonld2 = ('<script type="application/ld+json">' + _json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Categories", "item": BASE + "categories/index.html"},
            {"@type": "ListItem", "position": 3, "name": title_tag, "item": full_url},
        ],
    }) + '</script>')
    head = head.replace("</head>", GC + "\n" + jsonld1 + "\n" + jsonld2 + "\n</head>")

    body_end = f"""
{"".join(sections)}
{chrome.footer(UP)}
{chrome.TOGGLE_JS}
</body>
</html>"""

    page = head + body_end
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(page)} bytes)")
    print(f"live={live} pipeline={pipe} planned={plan} total={total}")


if __name__ == "__main__":
    build()
