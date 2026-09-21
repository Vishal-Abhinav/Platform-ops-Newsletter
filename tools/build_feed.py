#!/usr/bin/env python3
"""Generate feed.xml — RSS 2.0 for the published issues.

Only issues with a real page are included; the four archive-only listings
(#042-#045) have nothing to link to, so a reader would just get a dead item.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
# TOOLS is the real tools/ directory — derived from this file's own
# location, never from ROOT. ROOT is the OUTPUT root (dist/) and source
# must never be looked up underneath it.
TOOLS = _pl.Path(__file__).resolve().parent

import html
import json
import pathlib
from email.utils import format_datetime
from datetime import datetime, timezone

from siteconf import BASE           # canonical origin, one source of truth

# (issue, path, title, blurb, published-at)
# The five September issues went out in the same month; they are staggered by
# issue number so readers order them the way the archive does.
ISSUES = [
    (67, "Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html",
     "Service Mesh Operations",
     "mTLS identity that turns policy into a statement about services rather than subnets, the "
     "AuthorizationPolicy default that flips one workload to deny while its neighbours stay "
     "open, retries that multiply through a call graph, and the trace headers your application "
     "still has to forward itself.",
     datetime(2026, 9, 15, 15, 0, tzinfo=timezone.utc)),
    (66, "Kubernetes/SERVICE-MESH-FUNDAMENTALS/service-mesh-fundamentals.html",
     "Service Mesh Fundamentals",
     "What a sidecar mesh actually buys and what it costs, the four Envoy objects every mesh "
     "CRD renders into, what service discovery adds on top of kube-dns, and the Service port "
     "name that silently disables every L7 feature.",
     datetime(2026, 9, 15, 14, 0, tzinfo=timezone.utc)),
    (65, "Kubernetes/KUBERNETES-CLUSTER-OPERATIONS/kubernetes-cluster-operations.html",
     "Kubernetes Cluster Operations",
     "Pod Security rolled out with warn before enforce, the removed API that takes workloads "
     "with it on upgrade, the difference between an etcd snapshot and a real backup, and the "
     "three cluster failures that stay silent until they are outages.",
     datetime(2026, 9, 15, 13, 0, tzinfo=timezone.utc)),
    (64, "Kubernetes/KUBERNETES-AUTOSCALING/kubernetes-autoscaling.html",
     "Kubernetes Autoscaling",
     "The HPA algorithm in one line and the missing resource request that silently disables it, "
     "VPA as a measuring tool before it is an actuator, why the two fight on CPU, and the single "
     "pod that pins a node against every scale-down.",
     datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)),
    (63, "Kubernetes/KUBERNETES-SCHEDULING/kubernetes-scheduling.html",
     "Kubernetes Scheduling",
     "Taints as the node's veto and the NoExecute effect that evicts what is already running, "
     "affinity as the pod's request, the topologyKey that gives anti-affinity its meaning, and "
     "why Pending is always a filtering result you can read verbatim.",
     datetime(2026, 9, 15, 11, 0, tzinfo=timezone.utc)),
    (62, "Kubernetes/KUBERNETES-CONFIG-AND-ACCESS/kubernetes-config-and-access.html",
     "Kubernetes Config & Access",
     "ConfigMaps that update in place except when they do not, Secrets that are encoded rather "
     "than encrypted, namespaces that isolate far less than people assume, and RBAC's one rule "
     "\u2014 purely additive, no deny \u2014 that explains every access surprise.",
     datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)),
    (61, "Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html",
     "Kubernetes Workloads",
     "ReplicaSets and why a stuck rollout is legible, DaemonSets and the update strategy that "
     "silently never rolls, Jobs and CronJobs that pile up on their own schedule, and the "
     "liveness probe that turns a dependency blip into a restart storm.",
     datetime(2026, 9, 15, 9, 0, tzinfo=timezone.utc)),
    (60, "OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html",
     "OpenShift Operations",
     "Monitoring that is half switched off by default, LogQL that returns before it times "
     "out, the four security gates and which one refused you, and the upgrade that stops on "
     "one PodDisruptionBudget — with the pre-upgrade checks that prevent the bad ones.",
     datetime(2026, 9, 11, 11, 0, tzinfo=timezone.utc)),
    (59, "OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html",
     "OpenShift Networking & Storage",
     "Routes and the four TLS modes, OVN-Kubernetes and the MTU fault everybody "
     "misdiagnoses, NetworkPolicy isolation that silently blinds monitoring, storage "
     "binding and access modes, and the CSI chain where each stage fails in a different log.",
     datetime(2026, 9, 11, 10, 0, tzinfo=timezone.utc)),
    (58, "OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html",
     "OpenShift Architecture & Fundamentals",
     "What the distribution adds on top of Kubernetes — the Cluster Version Operator "
     "ownership chain, projects and the project template, the operator pattern under CVO "
     "and OLM, MachineConfig, SCC admission, image streams and etcd — each with the "
     "failure mode it actually produces and how to triage it.",
     datetime(2026, 9, 11, 9, 0, tzinfo=timezone.utc)),
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

if __name__ == "__main__":
    # ISSUES below is the issue register, and build_readme.py imports it to
    # count issues and label the repository tree. Guarding the write keeps that
    # import from silently regenerating feed.xml out of turn.
    out = ROOT / 'feed.xml'
    out.write_text(feed, encoding='utf-8')

    latest_num, latest_path, latest_title, latest_blurb, latest_when = ISSUES[0]
    latest = {
        "number": latest_num,
        "path": latest_path,
        "title": latest_title,
        "blurb": latest_blurb,
        "url": BASE + latest_path,
        "published_at": latest_when.isoformat(),
    }
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "latest-issue.json").write_text(
        json.dumps(latest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # well-formedness is not optional for a feed — readers reject the whole file
    import xml.etree.ElementTree as ET  # noqa: E402
    ET.parse(out)
    print(f"feed.xml -> {len(feed)} bytes, {len(ISSUES)} items, parses clean")
