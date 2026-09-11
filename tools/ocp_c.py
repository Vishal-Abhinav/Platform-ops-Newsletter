#!/usr/bin/env python3
"""OpenShift content, batch C: Operations (issue #060).

Covers four taxonomy topics: OpenShift Monitoring, OpenShift Logging,
OpenShift Security, OpenShift Upgrades.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section

# ═══════════════════════════════════════════════════════════════════════════
# 03 · OPENSHIFT OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════
OPS_DIAGRAM = diagram([
    ("Sources", [("kubelet / cAdvisor", "core"), ("node-exporter", "core"),
                 ("Operator metrics", "core"), ("Your /metrics", "core")]),
    ("Discovery", [("ServiceMonitor", "warm"), ("PodMonitor", "warm")]),
    ("Platform", [("Prometheus (openshift-monitoring)", "hot")]),
    ("Workload", [("Prometheus (user-workload)", "hot")]),
    ("Rules", [("PrometheusRule", "calm"), ("Alertmanager", "calm")]),
    ("Query", [("Thanos Querier", "go"), ("Console dashboards", "go"),
               ("Grafana / external", "go")]),
    ("Long term", [("Remote write → Thanos / Mimir / Cortex", "plain")]),
], "Two Prometheus instances, one query endpoint — and user metrics are off until you turn them on")

UPG_DIAGRAM = diagram([
    ("Decide", [("Channel: stable / fast / eus", "core"), ("Target version", "core")]),
    ("Verify", [("Release signature", "warm"), ("Upgradeable=True", "warm"),
                ("Deprecated API check", "warm")]),
    ("Control plane", [("CVO applies manifests in order", "hot"),
                       ("etcd → apiserver → controllers", "hot")]),
    ("Operators", [("~30 cluster operators, sequenced", "calm")]),
    ("Nodes", [("MCO renders config", "go"), ("cordon → drain → reboot", "go"),
               ("one pool at a time", "go")]),
    ("Settle", [("All co Available", "plain"), ("MCPs Updated", "plain")]),
], "The node phase is the long one — 12 workers at maxUnavailable 1 is 12 sequential reboots")

OPS_CORE = "".join([
 card(1, "The monitoring stack, and the half of it that is off by default",
      "Platform metrics work out of the box. Yours do not, and nothing tells you.",
      ["Prometheus", "ServiceMonitor", "user-workload"], """
<p>OpenShift ships a complete monitoring stack, but it is deliberately split in two:</p>
<ul>
<li><strong>Platform monitoring</strong> (<code>openshift-monitoring</code>) — scrapes the
cluster itself. Always on, not configurable by you, and it will not scrape your namespaces.</li>
<li><strong>User workload monitoring</strong> (<code>openshift-user-workload-monitoring</code>)
— scrapes your applications. <strong>Disabled by default.</strong></li>
</ul>
<p>This is the single most common "our metrics don't work" cause on OpenShift. A team writes a
<code>ServiceMonitor</code>, applies it, sees no error — because a ServiceMonitor with nothing
watching it is a perfectly valid object — and the metrics never appear. Nothing is broken;
the second Prometheus simply does not exist yet.</p>
""" + term("turning it on, and confirming the target is actually scraped", [
    ("$", "oc -n openshift-monitoring get cm cluster-monitoring-config -o yaml"),
    ("#", "if absent, create it — this one key is the whole switch:"),
    ("", "data:"),
    ("", "  config.yaml: |"),
    ("", "    enableUserWorkload: true"),
    ("$", "oc -n openshift-user-workload-monitoring get pods"),
    ("", "prometheus-user-workload-0   6/6   Running"),
    ("#", "then verify the TARGET, not the ServiceMonitor — a valid SM can still match nothing"),
    ("$", "oc -n openshift-user-workload-monitoring exec prometheus-user-workload-0 -c prometheus -- \\"),
    ("", "  curl -s localhost:9090/api/v1/targets | jq '.data.activeTargets[].labels.job'"),
]) + note("warn", "A ServiceMonitor matches ports by NAME",
          "<p><code>spec.endpoints[].port</code> is the Service's <em>port name</em>, not its "
          "number. An unnamed port cannot be selected at all, and a mismatched name matches "
          "nothing — silently, with the ServiceMonitor still showing as healthy. If the target "
          "list is empty, check the port name before anything else.</p>")),

 card(2, "Alerting that pages for the right reasons",
      "Burn rate over threshold, and the silence you forgot to remove.",
      ["Alertmanager", "PrometheusRule", "burn rate"], """
<p>Alerts are <code>PrometheusRule</code> objects. Platform rules ship with the cluster; yours
live in your namespace and are picked up by user-workload Prometheus.</p>
<p>The design question is not "what threshold" but <strong>what makes a human get out of
bed</strong>. A CPU-above-80% alert fires constantly and teaches people to ignore the pager.
An SLO burn-rate alert fires when you are consuming the error budget fast enough to miss the
objective — which is the same thing the user is experiencing.</p>
<p>Multi-window burn rate is the standard shape: a fast window catches sudden severe breakage,
a slow window catches sustained mild breakage, and requiring both to be hot suppresses the
one-minute blip that recovered on its own.</p>
""" + term("a burn-rate rule that means something", [
    ("", "groups:"),
    ("", "- name: api-slo"),
    ("", "  rules:"),
    ("", "  - alert: APIErrorBudgetBurnFast"),
    ("", "    # 14.4x burn over 1h AND 5m = 2% of a 30-day budget in an hour"),
    ("", "    expr: |"),
    ("", "      (job:slo_errors:ratio_rate1h{job=\"api\"} > (14.4 * 0.001))"),
    ("", "      and"),
    ("", "      (job:slo_errors:ratio_rate5m{job=\"api\"} > (14.4 * 0.001))"),
    ("", "    for: 2m"),
    ("", "    labels: { severity: critical }"),
    ("#", "and the thing that actually causes missed incidents:"),
    ("$", "oc -n openshift-monitoring exec alertmanager-main-0 -c alertmanager -- \\"),
    ("", "  amtool silence query --alertmanager.url=http://localhost:9093"),
    ("#", "an expired-in-name-only silence from last month's maintenance window"),
])),

 card(3, "Logging — the stack changed, and the old assumptions did not",
      "Loki not Elasticsearch, three tenants, and retention you must set.",
      ["Loki", "LokiStack", "ClusterLogForwarder"], """
<p>OpenShift logging moved from Elasticsearch/Kibana to <strong>Loki</strong> with the console
as the UI. The practical differences matter:</p>
<ul>
<li><strong>Loki indexes labels, not content.</strong> Queries filter by label first and then
grep the stream. A query with no label selector scans everything and will time out on a busy
cluster. This is the opposite of the Elasticsearch habit.</li>
<li><strong>Three tenants</strong> — <code>application</code>, <code>infrastructure</code>,
<code>audit</code> — with separate access. Audit logs are <em>not</em> collected by default.</li>
<li><strong>Retention is a LokiStack setting</strong>, and the default sizing is far smaller
than most teams assume. Storage pressure silently drops the oldest streams.</li>
</ul>
<p>The collector is Vector, configured by a <code>ClusterLogForwarder</code>. That object is
also how you ship elsewhere — Splunk, Kafka, an external Loki — and you can forward and store
locally at the same time.</p>
""" + term("LogQL that returns before the timeout", [
    ("#", "bad — no label selector, scans every stream in the tenant"),
    ("", "{} |= \"OutOfMemory\""),
    ("#", "good — narrow by label, THEN filter"),
    ("", "{kubernetes_namespace_name=\"prod\", kubernetes_container_name=\"api\"}"),
    ("", "  |= \"OutOfMemory\" | json | line_format \"{{.msg}}\""),
    ("#", "rate of errors per pod, which is what you actually want during an incident"),
    ("", "sum by (kubernetes_pod_name) ("),
    ("", "  rate({kubernetes_namespace_name=\"prod\"} |= \"level=error\" [5m]))"),
    ("$", "oc -n openshift-logging get lokistack logging-loki -o jsonpath='{.spec.limits.global.retention}'"),
])),

 card(4, "Security — the layers, and which one rejected you",
      "Authentication, RBAC, SCC and NetworkPolicy each say no in a different voice.",
      ["RBAC", "SCC", "OAuth"], """
<p>Four independent gates sit between a request and a running workload. Reading the refusal
tells you which one, and they are not interchangeable:</p>
<table class="tbl"><thead><tr><th>Gate</th><th>Answers</th><th>Refusal looks like</th></tr></thead>
<tbody>
<tr><td><strong>Authentication</strong></td><td>Who are you?</td><td><code>Unauthorized</code>, 401</td></tr>
<tr><td><strong>RBAC</strong></td><td>May you perform this verb on this resource?</td><td><code>Forbidden: User "x" cannot get pods</code></td></tr>
<tr><td><strong>SCC</strong></td><td>May this POD have the privileges it asks for?</td><td><code>unable to validate against any security context constraint</code></td></tr>
<tr><td><strong>NetworkPolicy</strong></td><td>May this packet arrive?</td><td>Nothing. Timeout.</td></tr>
</tbody></table>
<p>The last row is the operationally important one: <strong>NetworkPolicy has no error
message</strong>. Every other layer tells you it refused. A policy drop is indistinguishable
from a dead backend, which is why it is worth proving or excluding early rather than late.</p>
<h3>RBAC, resolved rather than guessed</h3>
""" + term("stop reading RoleBindings and ask the API", [
    ("$", "oc auth can-i create deployments -n prod --as=jane"),
    ("", "no"),
    ("$", "oc auth can-i --list -n prod --as=jane | head"),
    ("#", "and for a service account, which is where this usually bites:"),
    ("$", "oc auth can-i list secrets -n prod \\"),
    ("", "  --as=system:serviceaccount:prod:api-sa"),
    ("$", "oc adm policy who-can delete pods -n prod"),
    ("#", "the reverse question, and far quicker than auditing bindings by hand"),
]) + note("good", "Audit logs answer 'who did this', but only if you collect them",
          "<p>The API server writes audit events for every request. They are on the masters at "
          "<code>/var/log/kube-apiserver/</code> and reachable with "
          "<code>oc adm node-logs --role=master --path=kube-apiserver/audit.log</code>. They are "
          "<em>not</em> forwarded to Loki unless the ClusterLogForwarder names the "
          "<code>audit</code> input — so the one log you need after a security question is "
          "usually the one nobody enabled.</p>")),
])

OPS_ADV = "".join([
 card(5, "Upgrades — channels, and the check that prevents the bad ones",
      "Upgradeable=False is the cluster telling you it already knows.",
      ["channel", "CVO", "EUS"], """
<p>Channels decide which versions are offered:</p>
<ul>
<li><strong>stable-4.x</strong> — released and soaked. The default for production.</li>
<li><strong>fast-4.x</strong> — released, less soak. Fine for pre-production.</li>
<li><strong>eus-4.x</strong> — Extended Update Support, for the even-numbered releases you can
stay on longer and hop between while skipping a minor.</li>
<li><strong>candidate-4.x</strong> — pre-release. Never production.</li>
</ul>
<p>Before any upgrade, the cluster has already formed an opinion. The
<code>Upgradeable</code> condition on <code>ClusterVersion</code> is set to <code>False</code>
by any operator that knows the upgrade will hurt — most often because <strong>a deprecated API
is still in use</strong> and the next minor removes it. Upgrading anyway is how a workload
disappears mid-upgrade.</p>
""" + term("the pre-upgrade checklist, as commands", [
    ("$", "oc get clusterversion -o jsonpath='{.items[0].status.conditions}' \\"),
    ("", "  | jq -r '.[]|select(.type==\"Upgradeable\")|.status + \": \" + .message'"),
    ("", "False: Cluster operator kube-apiserver should not be upgraded between minor"),
    ("", "versions: APIRemovedInNextReleaseInUse: flowcontrol.apiserver.k8s.io/v1beta2"),
    ("#", "find WHO is still calling it, before you go looking through manifests:"),
    ("$", "oc get apirequestcount flowschemas.v1beta2.flowcontrol.apiserver.k8s.io \\"),
    ("", "  -o jsonpath='{.status.currentHour.byNode[*].byUser[*].username}'"),
    ("$", "oc adm upgrade                     # what is actually on offer"),
    ("$", "oc adm upgrade --to=4.16.11"),
])),

 card(6, "What actually happens during an upgrade, and where it stalls",
      "Control plane in minutes, nodes in hours, and one PDB can stop the lot.",
      ["MCO", "drain", "PodDisruptionBudget"], """
<p>The control plane phase is fast and mostly invisible. The <strong>node phase</strong> is
where the hours go: the MCO cordons a node, drains it, applies the new OS config, reboots it,
uncordons, and moves to the next — one at a time per pool by default.</p>
<p>Draining is where upgrades stop, and the cause is nearly always one of two things:</p>
<ul>
<li><strong>A PodDisruptionBudget that cannot be satisfied.</strong> A single-replica Deployment
with <code>minAvailable: 1</code> can never be evicted. The drain retries forever, politely,
and the upgrade sits at the same percentage for hours.</li>
<li><strong>A pod with no controller</strong> — a bare Pod, created by hand — which drain
refuses to evict because nothing would recreate it.</li>
</ul>
<p>Both are the cluster protecting availability exactly as instructed. The fix is the PDB or
the workload, not forcing the drain.</p>
""" + term("finding the PDB that is blocking the upgrade", [
    ("$", "oc get mcp worker -o jsonpath='{.status.conditions[?(@.type==\"Degraded\")].message}'"),
    ("", "failed to drain node worker-07 after 1h0m0s: error when evicting pod \"legacy-api-0\":"),
    ("", "Cannot evict pod as it would violate the pod's disruption budget"),
    ("$", "oc get pdb -A -o custom-columns=\\"),
    ("", "  NS:.metadata.namespace,NAME:.metadata.name,MIN:.spec.minAvailable,ALLOWED:.status.disruptionsAllowed"),
    ("", "prod   legacy-api-pdb   1   0      <- 0 disruptions allowed, 1 replica"),
    ("#", "the real fix is 2 replicas. The unblock-now fix is to relax the PDB:"),
    ("$", "oc patch pdb legacy-api-pdb -n prod --type=merge \\"),
    ("", "  -p '{\"spec\":{\"minAvailable\":0}}'"),
]) + note("warn", "maxUnavailable is the lever for a 100-node cluster",
          "<p>At the default of 1, a 100-node pool is 100 sequential reboots — easily a working "
          "day. Raising <code>maxUnavailable</code> on the MachineConfigPool to 3 or 5 cuts that "
          "proportionally, provided your workloads have enough replicas and spread to survive "
          "losing that many nodes at once. Check PDBs and topology spread before you raise "
          "it, not after.</p>")),

 card(7, "Compliance, images and the supply chain",
      "The operators that answer the questions an auditor will ask.",
      ["Compliance Operator", "quay", "signatures"], """
<p>Three Red Hat operators cover the security questions that arrive as audit findings:</p>
<ul>
<li><strong>Compliance Operator</strong> — runs OpenSCAP against profiles (CIS, PCI-DSS,
NIST 800-53) and produces <code>ComplianceCheckResult</code> objects. Many findings ship with an
auto-remediation you can apply as a MachineConfig.</li>
<li><strong>File Integrity Operator</strong> — AIDE on every node, alerting on unexpected
changes to system files.</li>
<li><strong>Quay / Clair</strong> — image vulnerability scanning at the registry.</li>
</ul>
<p>Independently: <strong>image signature verification</strong>. A cluster that will pull any
image from anywhere has no supply chain guarantee, and this is a cluster-wide policy, not a
per-workload one.</p>
""" + term("scoping the image sources a cluster will trust", [
    ("$", "oc edit image.config.openshift.io/cluster"),
    ("", "spec:"),
    ("", "  registrySources:"),
    ("", "    allowedRegistries:"),
    ("", "    - quay.io"),
    ("", "    - registry.redhat.io"),
    ("", "    - image-registry.openshift-image-registry.svc:5000"),
    ("#", "CAUTION: this rolls every node via the MCO. It is a node reboot, not a config reload."),
    ("#", "and omitting the internal registry breaks every build in the cluster."),
    ("$", "oc get compliancecheckresult -n openshift-compliance \\"),
    ("", "  --selector compliance.openshift.io/check-status=FAIL"),
])),

 card(8, "Backup, DR and what 'restore the cluster' actually means",
      "etcd is the cluster; your data is not in it.",
      ["etcd backup", "DR", "OADP"], """
<p>Two different things get called "backup" and conflating them is how a DR test fails:</p>
<table class="tbl"><thead><tr><th></th><th>etcd snapshot</th><th>Application backup (OADP/Velero)</th></tr></thead>
<tbody>
<tr><td>Contains</td><td>Every API object</td><td>Selected namespaces + PV data</td></tr>
<tr><td>Restores</td><td>The whole cluster, to that instant</td><td>Namespaces, into this or another cluster</td></tr>
<tr><td>Granularity</td><td>All or nothing</td><td>Per namespace, per label</td></tr>
<tr><td>PV contents</td><td><strong>No</strong></td><td>Yes, via snapshots or restic</td></tr>
<tr><td>Use for</td><td>Control-plane disaster</td><td>Namespace deleted, migration, real DR</td></tr>
</tbody></table>
<p>An etcd restore is disruptive by design: you stop the control plane, restore on one master,
and rebuild the others from it. It is the right tool for "we lost quorum", and the wrong tool
for "someone deleted the prod namespace" — for which OADP restores in minutes without touching
anything else.</p>
""" + term("both backups, and the check that they ran", [
    ("#", "etcd — on a master, produces a snapshot plus the static pod manifests"),
    ("$", "oc debug node/master-0 -- chroot /host /usr/local/bin/cluster-backup.sh \\"),
    ("", "  /home/core/backup"),
    ("#", "OADP — namespaces AND their volumes"),
    ("$", "oc get backup -n openshift-adp"),
    ("", "NAME              STATUS      ERRORS   ITEMS   AGE"),
    ("", "prod-daily-0911   Completed   0        1847    6h"),
    ("$", "oc get backup prod-daily-0911 -n openshift-adp \\"),
    ("", "  -o jsonpath='{.status.progress}'"),
    ("#", "restore one namespace without touching the rest of the cluster:"),
    ("$", "velero restore create --from-backup prod-daily-0911 --include-namespaces prod"),
]) + note("bad", "The DR test nobody runs is the one that matters",
          "<p>An etcd restore rolls every node and takes a cluster down for the duration. If it "
          "has never been rehearsed, the first rehearsal will be during an outage, under time "
          "pressure, by someone reading the docs for the first time. Schedule it on a cluster "
          "you can afford to break, and time it — the number you get is your real RTO.</p>")),
])

OPS_TROUBLE = """
<p>Operations failures are mostly <em>absences</em>: a metric that never arrived, a log that was
never collected, an alert that was silenced, an upgrade that stopped. Absences have no error
message, so each one needs a positive check rather than a glance at a dashboard.</p>
""" + table(
    ["Symptom", "The absence behind it", "Positive check"],
    [["App metrics missing", "User workload monitoring never enabled",
      "<code>oc -n openshift-user-workload-monitoring get pods</code>"],
     ["ServiceMonitor exists, no data", "Port name mismatch — it matched nothing",
      "Prometheus <code>/api/v1/targets</code>, not the ServiceMonitor"],
     ["Alert never fired", "An unexpired silence, or the rule is in the wrong namespace",
      "<code>amtool silence query</code>; <code>oc get prometheusrule -A</code>"],
     ["Logs stop at a date", "LokiStack retention, or storage pressure dropping streams",
      "<code>oc get lokistack -o yaml</code>; the ingester pod's logs"],
     ["No audit trail for an incident", "ClusterLogForwarder never included the audit input",
      "<code>oc adm node-logs --role=master --path=kube-apiserver/audit.log</code>"],
     ["Upgrade at the same % for hours", "A drain blocked by a PDB or a bare pod",
      "<code>oc get mcp -o yaml</code> — the Degraded message names the pod"],
     ["Upgrade refuses to start", "Upgradeable=False — a removed API is still in use",
      "<code>oc get apirequestcount</code> names the caller"],
     ["Node rebooted unexpectedly", "MCO applying a MachineConfig, as designed",
      "<code>oc get mcp</code>; the node's <code>machineconfiguration</code> annotations"],
     ]) + """
<h3>Collecting evidence while the incident is live</h3>
<p>Prometheus keeps platform metrics for roughly 15 days and Loki for whatever retention you
set. Both are shorter than most post-incident reviews take to schedule, so capture the query
results during the incident rather than planning to look later.</p>
""" + term("snapshot the evidence before it ages out", [
    ("#", "range query straight out of Thanos, into a file you keep"),
    ("$", "TOKEN=$(oc whoami -t); HOST=$(oc -n openshift-monitoring get route thanos-querier -o jsonpath='{.spec.host}')"),
    ("$", "curl -sk -H \"Authorization: Bearer $TOKEN\" \\"),
    ("", "  \"https://$HOST/api/v1/query_range?query=up{job=%22api%22}&start=...&end=...&step=60\" \\"),
    ("", "  > incident-up.json"),
    ("#", "and the events, which expire in ONE hour by default — always grab these first"),
    ("$", "oc get events -A --sort-by=.lastTimestamp -o json > incident-events.json"),
    ("$", "oc adm must-gather --dest-dir=./mg-$(date +%F)"),
]) + note("good", "Events expire in an hour",
          "<p>Kubernetes Events have a default TTL of 60 minutes. They hold the scheduling "
          "failures, admission rejections, image pull errors and probe failures that explain "
          "the incident — and they are gone before most postmortems begin. Capturing them is "
          "the first command of an incident, not the last.</p>")

OPS_CHEAT = table(["Command", "What it answers"], [
    ["<code>oc -n openshift-user-workload-monitoring get pods</code>", "Whether your metrics are being scraped at all"],
    ["<code>oc get servicemonitor,podmonitor -A</code>", "What has asked to be scraped"],
    ["<code>oc get prometheusrule -A</code>", "Every alert rule, platform and yours"],
    ["<code>amtool silence query</code>", "The silence that stopped the page"],
    ["<code>oc get lokistack -n openshift-logging -o yaml</code>", "Retention and storage sizing"],
    ["<code>oc get clusterlogforwarder -A</code>", "Which log tenants are collected and where they go"],
    ["<code>oc adm node-logs --role=master --path=kube-apiserver/audit.log</code>", "Who did what to the API"],
    ["<code>oc auth can-i --list -n &lt;ns&gt; --as=&lt;user&gt;</code>", "Effective RBAC, resolved"],
    ["<code>oc adm policy who-can &lt;verb&gt; &lt;res&gt;</code>", "The reverse RBAC question"],
    ["<code>oc adm upgrade</code>", "Which versions are on offer right now"],
    ["<code>oc get apirequestcount</code>", "Who is still calling a deprecated API"],
    ["<code>oc get pdb -A</code>", "The budget that will block the next drain"],
    ["<code>oc get compliancecheckresult -n openshift-compliance</code>", "Current compliance failures"],
    ["<code>oc get backup -n openshift-adp</code>", "Whether the application backup actually ran"],
    ["<code>oc get events -A --sort-by=.lastTimestamp</code>", "What just happened — expires in an hour"],
], "mono")

OPENSHIFT_OPERATIONS = dict(
    slug="openshift-operations",
    title="OpenShift Operations",
    tagline=("Monitoring that is half switched off by default, Loki queries that return before "
             "they time out, the four security gates and which one refused you, and the upgrade "
             "that stops on one PodDisruptionBudget."),
    eyebrow="Kubernetes · OpenShift",
    meta=["<b>27 min</b> read", "Level: <b>core → advanced</b>", "OpenShift <b>03 / 03</b>"],
    sections=(
        section("The model", "WHERE OBSERVABILITY DATA ACTUALLY COMES FROM",
                "Two Prometheus instances behind one query endpoint — and the one that scrapes "
                "your applications does not exist until you enable it.",
                f'<div class="dg-scroll">{OPS_DIAGRAM}</div>'
                '<p class="dg-cap">Thanos Querier is what the console and your dashboards talk '
                'to; it federates both instances. That is why platform metrics appear '
                'immediately and yours do not, from the same URL.</p>')
        + section("Core", "MONITORING, LOGGING & SECURITY",
                  "The three things you are asked for after every incident, and the default "
                  "that quietly prevents each one.", OPS_CORE)
        + section("Advanced", "UPGRADES",
                  "What the cluster already knows before you start, and where the hours go.",
                  f'<div class="dg-scroll">{UPG_DIAGRAM}</div>'
                  '<p class="dg-cap">The CVO applies manifests in a fixed order and stops at the '
                  'first that will not go ready, so a stalled upgrade always names its blocker '
                  'in the Progressing message.</p>' + OPS_ADV)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, OPS_TROUBLE)
        + section("Reference", "CHEATSHEET", None, OPS_CHEAT)
    ),
)

TOPICS = [OPENSHIFT_OPERATIONS]
