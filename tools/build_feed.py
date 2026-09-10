#!/usr/bin/env python3
"""Generate feed.xml — RSS 2.0 for the published issues.

Only issues with a real page are included; the four archive-only listings
(#042-#045) have nothing to link to, so a reader would just get a dead item.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

import html
import pathlib
from email.utils import format_datetime
from datetime import datetime, timezone

BASE = "https://vishal-abhinav.github.io/Platform-ops-Newsletter/"

# (issue, path, title, blurb, published-at)
# The five September issues went out in the same month; they are staggered by
# issue number so readers order them the way the archive does.
ISSUES = [
    (57, "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html",
     "Linux & Unix Glossary",
     "190 terms across 15 categories — fundamentals, permissions, processes, networking, "
     "storage, security, monitoring and troubleshooting — searchable in one place, with "
     "standalone deep-dive pages for the terms that need one.",
     datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)),
    (56, "Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html",
     "Linux Troubleshooting",
     "A runbook, not a tutorial — high load and CPU, memory and OOM, disk and I/O, "
     "network, and boot failures, each with the commands to run and what their output means.",
     datetime(2026, 9, 7, 9, 0, tzinfo=timezone.utc)),
    (55, "Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html",
     "Linux Advanced",
     "systemd internals, kernel and sysctl tuning, namespaces and cgroups, performance "
     "profiling, and LVM.",
     datetime(2026, 9, 5, 9, 0, tzinfo=timezone.utc)),
    (54, "Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html",
     "Linux Fundamentals",
     "Filesystem hierarchy, users and permissions, package management, process basics, "
     "and shell scripting.",
     datetime(2026, 9, 3, 9, 0, tzinfo=timezone.utc)),
    (53, "SRE/INCIDENT-MANAGEMENT/incident-management.html",
     "Incident Management & Postmortems",
     "Severity classification, the Incident Commander role, blameless postmortems, and "
     "action-item follow-through that actually closes.",
     datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)),
    (52, "DevOps/CICD/cicd-pipelines.html",
     "CI/CD & GitOps Deep-Dive",
     "Jenkins and GitLab CI, GitOps with ArgoCD and Flux, security gates, canary and "
     "blue-green rollouts, and secrets management.",
     datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)),
    (51, "DevOps/K8/OBSERVABILITY/k8-observability.html",
     "Observability Stack Deep-Dive",
     "Prometheus and Grafana, Loki and ELK, Jaeger and OpenTelemetry, and SLO burn-rate "
     "alerting that pages you for the right reasons.",
     datetime(2026, 7, 1, 9, 0, tzinfo=timezone.utc)),
    (50, "DevOps/K8/STORAGE/k8-storage.html",
     "Kubernetes Storage Deep-Dive",
     "PV and PVC, StorageClasses, CSI driver internals, StatefulSets, and a backup and DR "
     "strategy that's been tested.",
     datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    (49, "DevOps/K8/ERROR/K8-error.html",
     "Kubernetes & OpenShift Error Runbook",
     "32 error types across 5 layers — Pod, Worker Node, Cluster, API Server and "
     "OpenShift — each with the production fix.",
     datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc)),
    (48, "DevOps/K8/ARCHITECTURE/k8-architecture.html",
     "Kubernetes Architecture Deep-Dive",
     "Control plane, worker nodes, storage, CSI, PersistentVolumes, QoS classes and "
     "scheduling — with diagrams.",
     datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc)),
    (47, "DevOps/K8/Networking/k8-networking.html",
     "Kubernetes Networking Decoded",
     "Six architecture diagrams covering Pod networking, CNI plugins, Ingress, "
     "NetworkPolicy and CoreDNS.",
     datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc)),
]


def e(s):
    return html.escape(s, quote=False)


items = []
for num, path, title, blurb, when in ISSUES:
    url = BASE + path
    items.append(f"""    <item>
      <title>#{num:03d} — {e(title)}</title>
      <link>{e(url)}</link>
      <guid isPermaLink="true">{e(url)}</guid>
      <pubDate>{format_datetime(when)}</pubDate>
      <description>{e(blurb)}</description>
      <author>vishalabhinav.co.in@gmail.com (Vishal Abhinav)</author>
    </item>""")

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Platform Ops — Tech with Vishal Abhinav</title>
    <link>{BASE}</link>
    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml" />
    <description>Monthly deep-dives on Kubernetes, SRE, infrastructure and platform
      engineering — written from production, not slideware.</description>
    <language>en</language>
    <managingEditor>vishalabhinav.co.in@gmail.com (Vishal Abhinav)</managingEditor>
    <webMaster>vishalabhinav.co.in@gmail.com (Vishal Abhinav)</webMaster>
    <lastBuildDate>{format_datetime(ISSUES[0][4])}</lastBuildDate>
    <ttl>1440</ttl>
    <image>
      <url>{BASE}assets/og/home.png</url>
      <title>Platform Ops — Tech with Vishal Abhinav</title>
      <link>{BASE}</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>
"""

out = ROOT / 'feed.xml'
out.write_text(feed, encoding='utf-8')

# well-formedness is not optional for a feed — readers reject the whole file
import xml.etree.ElementTree as ET  # noqa: E402
ET.parse(out)
print(f"feed.xml -> {len(feed)} bytes, {len(ISSUES)} items, parses clean")
