#!/usr/bin/env python3
"""OpenShift content, batch A: Architecture & Fundamentals (issue #058).

Covers four taxonomy topics: OpenShift Fundamentals, OpenShift Architecture,
Projects, Operators.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section

# ═══════════════════════════════════════════════════════════════════════════
# 01 · OPENSHIFT ARCHITECTURE & FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════════════════
ARCH_DIAGRAM = diagram([
    ("Clients", [("oc / kubectl", "core"), ("Web console", "core"),
                 ("CI pipeline", "core")]),
    ("Auth", [("OAuth server", "warm"), ("Identity provider", "warm"),
              ("Token / kubeconfig", "warm")]),
    ("API", [("kube-apiserver", "hot"), ("openshift-apiserver", "hot"),
             ("Admission plugins + SCC", "hot")]),
    ("State", [("etcd (quorum 2/3)", "calm")]),
    ("Control", [("kube-controller-mgr", "calm"), ("scheduler", "calm"),
                 ("Cluster Version Operator", "calm")]),
    ("Operators", [("Ingress", "go"), ("Network", "go"), ("Storage", "go"),
                   ("Monitoring", "go"), ("Authentication", "go"),
                   ("Machine Config", "go")]),
    ("Nodes", [("kubelet", "plain"), ("CRI-O", "plain"),
               ("OVN-Kubernetes", "plain")]),
    ("Workload", [("Pod in a Project", "plain"), ("Bound to an SCC", "plain")]),
], "Every request enters through OAuth, is admitted or rejected by SCC, and only then becomes etcd state")

ARCH_CORE = "".join([
 card(1, "OpenShift is Kubernetes plus a supply chain",
      "What the distribution actually adds, and why that changes how you debug it.",
      ["distribution", "CVO", "opinionated"], """
<p>OpenShift is a conformant Kubernetes distribution. Every <code>kubectl</code> command works,
every Kubernetes object behaves the way the upstream docs say. What Red Hat adds is not a
different API — it is <strong>a managed lifecycle for the whole platform</strong>.</p>
<p>That distinction is the single most useful thing to internalise, because it tells you where
to look when something breaks. On vanilla Kubernetes, the cluster is whatever you assembled:
if the ingress controller is broken, you go and look at the ingress controller. On OpenShift,
almost every platform component is owned by an <strong>operator</strong>, and those operators are
owned by the <strong>Cluster Version Operator (CVO)</strong>. A broken router is not just a broken
deployment — it is a <code>ClusterOperator</code> reporting <code>Degraded=True</code>, and the
CVO will keep reconciling it back to its declared state.</p>
<h3>What that means in practice</h3>
<ul>
<li><strong>You cannot fix the platform by editing its Deployments.</strong> Scale the router
deployment to zero and the ingress operator scales it back. The change belongs on the operator's
custom resource, not the object it manages.</li>
<li><strong>Cluster health has a single front door.</strong> <code>oc get clusteroperators</code>
is the first command of any OpenShift incident — it tells you which of ~30 platform components
believes it is unhealthy, before you go looking at pods.</li>
<li><strong>Upgrades are a cluster-level transaction</strong>, not a set of component upgrades
you sequence yourself.</li>
</ul>
""" + term("the first two commands of any OpenShift incident", [
    ("$", "oc get clusteroperators"),
    ("", "NAME            VERSION   AVAILABLE   PROGRESSING   DEGRADED   SINCE"),
    ("", "authentication  4.16.9    True        False         False      4d"),
    ("", "ingress         4.16.9    True        False         True       22m"),
    ("", "monitoring      4.16.9    False       True          True       18m"),
    ("$", "oc describe clusteroperator/ingress | sed -n '/Conditions/,/Events/p'"),
    ("#", "the Degraded condition's message names the actual failing resource"),
])),

 card(2, "The control plane and the Cluster Version Operator",
      "One operator reconciles the operators. Understand it or upgrades stay mysterious.",
      ["CVO", "reconcile", "manifests"], """
<p>The CVO is the root of the ownership tree. It reads the release payload — a container image
holding every manifest for that exact version — and reconciles the cluster towards it. Each
platform component gets a second-level operator; the CVO owns those operators, and they own
their own workloads.</p>
<p>The chain is worth saying out loud because it is the debugging path:</p>
<p><code>ClusterVersion</code> → <code>CVO</code> → <code>ClusterOperator</code> →
second-level operator Deployment → the workload it manages → Pods.</p>
<h3>The failure mode people hit first</h3>
<p>An upgrade "hangs". <code>oc get clusterversion</code> shows <code>PROGRESSING=True</code>
for an hour with no version change. The CVO applies manifests <em>in order</em> and stops at
the first one that will not become ready — so the answer is never "the upgrade is slow", it is
always "component N is not reconciling and everything behind it is queued".</p>
""" + term("finding where an upgrade is actually stuck", [
    ("$", "oc get clusterversion -o jsonpath='{.items[0].status.conditions}' | jq -r '.[]|select(.type==\"Progressing\").message'"),
    ("", "Working towards 4.16.11: 412 of 907 done (45% complete), waiting on machine-config"),
    ("#", "'waiting on X' names the blocking cluster operator — go straight there"),
    ("$", "oc get co machine-config -o yaml | yq '.status.conditions[] | select(.type==\"Degraded\")'"),
    ("", "message: 'Unable to apply 4.16.11: error during syncRequiredMachineConfigPools:"),
    ("", "  pool master has not progressed: node/master-1 is reporting Unschedulable'"),
])),

 card(3, "Projects — namespaces with a lifecycle and a policy",
      "Why oc new-project and kubectl create namespace are not the same operation.",
      ["project", "namespace", "self-provisioner"], """
<p>A <code>Project</code> is a namespace with an OpenShift wrapper around it. The underlying
object really is a namespace — <code>oc get namespace</code> shows it — but creating one through
the Project API does more than create the namespace:</p>
<ul>
<li>Applies the <strong>project template</strong>, which can inject a <code>ResourceQuota</code>,
a <code>LimitRange</code>, a default <code>NetworkPolicy</code> and RoleBindings automatically.
This is the hook to use when you want every new team namespace to arrive pre-governed.</li>
<li>Makes the creator the project <strong>admin</strong> via a RoleBinding.</li>
<li>Respects the <code>self-provisioner</code> cluster role, which decides whether ordinary
users may create projects at all.</li>
</ul>
<p>Projects also gate what a user can <em>see</em>. A user with no access to a namespace gets a
<code>Forbidden</code> on the namespace API but an empty list from the Project API — which is
why the console shows a user only their own projects without leaking the names of others.</p>
<h3>The trap</h3>
<p>Creating the namespace directly with <code>kubectl create namespace</code> skips the template
entirely. The namespace exists, workloads run, and three months later someone notices this one
namespace has no quota and no default NetworkPolicy. If your platform relies on the project
template for guardrails, <strong>namespace creation must be restricted to the Project API</strong>.</p>
""" + term("making the template do the governing", [
    ("$", "oc get template project-request -n openshift-config"),
    ("#", "if it does not exist, the default template is used and nothing is injected"),
    ("$", "oc adm create-bootstrap-project-template -o yaml > project-template.yaml"),
    ("#", "edit it: add ResourceQuota, LimitRange, a default-deny NetworkPolicy"),
    ("$", "oc create -f project-template.yaml -n openshift-config"),
    ("$", "oc patch project.config.openshift.io/cluster --type=merge \\"),
    ("", "  -p '{\"spec\":{\"projectRequestTemplate\":{\"name\":\"project-request\"}}}'"),
    ("#", "and take away blanket project creation if the template is your control point"),
    ("$", "oc adm policy remove-cluster-role-from-group self-provisioner \\"),
    ("", "  system:authenticated:oauth"),
])),

 card(4, "Operators and the operator pattern",
      "A controller with domain knowledge — and the thing that will overwrite your hotfix.",
      ["CRD", "reconcile", "OLM"], """
<p>An operator is a controller plus a CRD. The CRD gives you an object that describes intent
(<q>I want a 3-node PostgreSQL with PITR</q>); the controller watches that object and does
whatever a human operator would do to make reality match — provision, configure, back up,
fail over, upgrade.</p>
<p>The part that matters operationally is the <strong>reconcile loop</strong>. It is level-driven,
not edge-driven: the controller does not react to your change, it repeatedly compares desired
state to actual state and corrects the difference. So any manual change to a managed resource
has a half-life measured in seconds.</p>
<h3>Two operator systems, and they are not the same</h3>
<table class="tbl"><thead><tr><th>System</th><th>Installs</th><th>Managed by</th></tr></thead>
<tbody>
<tr><td><strong>CVO</strong></td><td>The ~30 core platform operators</td><td>Red Hat, tied to the cluster version</td></tr>
<tr><td><strong>OLM</strong> (Operator Lifecycle Manager)</td><td>Optional and third-party operators from catalogs</td><td>You, via Subscription objects</td></tr>
</tbody></table>
<p>OLM adds its own vocabulary: a <code>CatalogSource</code> is a catalog of operators, a
<code>Subscription</code> says "install this one and keep it updated on this channel", an
<code>InstallPlan</code> is the pending upgrade, and a <code>ClusterServiceVersion</code> (CSV)
is the installed operator version. When an operator will not upgrade, the InstallPlan is
almost always where the answer is — most often waiting on a manual approval nobody gave.</p>
""" + term("why an operator is stuck on an old version", [
    ("$", "oc get subscription -A"),
    ("$", "oc get installplan -n openshift-logging"),
    ("", "NAME            CSV                        APPROVAL   APPROVED"),
    ("", "install-x7k2n   cluster-logging.v5.9.4     Manual     false"),
    ("#", "Manual approval and nobody approved it — the operator never moves"),
    ("$", "oc patch installplan install-x7k2n -n openshift-logging --type=merge \\"),
    ("", "  -p '{\"spec\":{\"approved\":true}}'"),
]) + note("warn", "Manual is the safe default, until it is not",
          "<p>Manual approval stops an operator upgrading itself into an incident. It also means "
          "an operator can sit months behind, quietly, with nothing alerting on it. If you choose "
          "Manual, alert on pending InstallPlans — otherwise you have chosen 'never upgrade' "
          "without deciding to.</p>")),
])

ARCH_ADV = "".join([
 card(5, "MachineConfig — the operating system is declarative too",
      "Node-level config as a cluster object, and why a bad one takes out a whole pool.",
      ["MCO", "MachineConfigPool", "Ignition"], """
<p>On OpenShift the node OS (RHCOS) is not configured by you logging in. It is configured by
<code>MachineConfig</code> objects, rendered by the Machine Config Operator into an Ignition
config, and applied by a per-node daemon that <strong>cordons, drains, writes, and reboots</strong>
the node.</p>
<p>MachineConfigs are grouped by <code>MachineConfigPool</code> — <code>master</code> and
<code>worker</code> by default. The MCO renders all MachineConfigs matching a pool into one
merged config and rolls it out node by node, respecting <code>maxUnavailable</code>.</p>
<h3>The failure mode that matters</h3>
<p>A malformed MachineConfig does not fail at admission. It renders, rolls out to the first
node, and that node fails to come back. The pool then reports <code>Degraded</code> and
<strong>stops</strong> — which is the MCO protecting you. The cluster is now in a half-applied
state and the fix is to delete the offending MachineConfig and let the pool re-render.</p>
""" + term("a pool that stopped mid-roll", [
    ("$", "oc get mcp"),
    ("", "NAME     CONFIG                  UPDATED  UPDATING  DEGRADED  MACHINECOUNT  READY"),
    ("", "master   rendered-master-a91f2   True     False     False     3             3"),
    ("", "worker   rendered-worker-3c80d   False    True      True      12            9"),
    ("$", "oc describe mcp worker | grep -A5 'Degraded'"),
    ("$", "oc get nodes -l node-role.kubernetes.io/worker -o custom-columns=\\"),
    ("", "  NAME:.metadata.name,STATE:.metadata.annotations.machineconfiguration\\\\.openshift\\\\.io/state"),
    ("", "worker-04   Degraded"),
    ("$", "oc logs -n openshift-machine-config-operator ds/machine-config-daemon \\"),
    ("", "  -c machine-config-daemon --tail=50 | grep -i error"),
])),

 card(6, "Security Context Constraints — the admission layer that surprises everyone",
      "Why a Helm chart that works everywhere else fails here, and the right way to fix it.",
      ["SCC", "restricted-v2", "admission"], """
<p>SCC is OpenShift's pod-level admission policy, and it predates Kubernetes' own Pod Security
Admission. It controls what a pod may ask for: running as root, host networking, host paths,
privileged mode, which capabilities, which SELinux context, which UID range.</p>
<p>By default every authenticated user gets <code>restricted-v2</code>, which refuses root,
drops nearly all capabilities, and assigns a <strong>random high UID from the namespace's
range</strong>. That last part is what breaks third-party charts: an image with
<code>USER 1000</code> and files owned by 1000 runs as UID 1000734512 instead and cannot write
to its own data directory.</p>
<h3>Diagnosing it</h3>
<p>The give-away is a pod that will not schedule with a message naming SCC, or a pod that
starts and immediately fails on permissions. The annotation on a running pod tells you which
SCC actually admitted it.</p>
""" + term("which SCC admitted this pod, and which one would", [
    ("$", "oc get pod api-7d9f -o jsonpath='{.metadata.annotations.openshift\\\\.io/scc}'"),
    ("", "restricted-v2"),
    ("#", "the error when it will not admit at all:"),
    ("", "Error creating: pods \"api-\" is forbidden: unable to validate against any"),
    ("", "security context constraint: [provider \"anyuid\": Forbidden: not usable by user]"),
    ("$", "oc adm policy scc-subject-review -z api-sa -n prod -f deployment.yaml"),
    ("#", "tells you which SCC WOULD admit this workload, before you grant anything"),
]) + note("bad", "Do not reach for anyuid",
          "<p>Granting <code>anyuid</code> to the service account makes the error go away and "
          "hands the workload the right to run as root. Fix the image instead: make the data "
          "directory group-writable and owned by GID 0, which is what OpenShift-compatible "
          "images do — the random UID is always in group 0. When you genuinely need elevated "
          "access, create a <em>custom SCC</em> granting only the specific capability, and bind "
          "it to one service account.</p>")
      + term("the image fix, not the policy fix", [
          ("#", "in the Dockerfile — works on OpenShift AND everywhere else"),
          ("", "RUN mkdir -p /data && chgrp -R 0 /data && chmod -R g=u /data"),
          ("", "USER 1001"),
      ])),

 card(7, "Image streams, the internal registry and builds",
      "An indirection layer that buys you rollback and breaks your CI if you ignore it.",
      ["ImageStream", "BuildConfig", "triggers"], """
<p>An <code>ImageStream</code> is a pointer to images, not a store of them. Each tag resolves
to an immutable digest, and the stream records the history of what that tag pointed at. That
gives you two things vanilla Kubernetes does not have out of the box: <strong>a rollback
target</strong>, and <strong>a trigger</strong> — a Deployment can be told to redeploy when a
stream tag moves.</p>
<p><code>BuildConfig</code> is the in-cluster build. Source-to-Image (S2I) takes application
source plus a builder image and produces a runnable image without a Dockerfile; Docker strategy
builds a Dockerfile; Custom runs your own builder image.</p>
<h3>Where teams get bitten</h3>
<ul>
<li><strong>A tag that points at <code>:latest</code> in an external registry</strong> resolves
once, at import. It does not follow upstream unless <code>scheduled: true</code> is set on the
tag — so "we pushed a new latest and nothing happened" is expected behaviour, not a bug.</li>
<li><strong>The internal registry is not a backup.</strong> On many installs it is backed by
ephemeral or single-replica storage. If your only copy of a release image is there, a registry
rebuild loses it.</li>
</ul>
""" + term("why the new image did not deploy", [
    ("$", "oc get is app -o jsonpath='{.spec.tags[?(@.name==\"latest\")]}' | jq"),
    ("", "{ \"name\": \"latest\", \"from\": {\"kind\":\"DockerImage\",\"name\":\"quay.io/org/app:latest\"},"),
    ("", "  \"importPolicy\": {} }"),
    ("#", "importPolicy empty = imported once, never re-checked"),
    ("$", "oc tag quay.io/org/app:latest app:latest --scheduled"),
    ("$", "oc import-image app:latest --confirm      # force a check now"),
    ("$", "oc rollout latest deploy/app              # or push the tag yourself"),
])),

 card(8, "etcd — the one component with no graceful degradation",
      "Quorum maths, the latency ceiling, and the backup you have not tested.",
      ["etcd", "quorum", "fsync"], """
<p>Every object in the cluster is etcd state. etcd is a Raft cluster of 3 (or 5) members and
needs a <strong>strict majority</strong> to accept writes: 3 members tolerate 1 failure,
5 tolerate 2. Lose quorum and the API server goes read-only — the cluster does not "run
degraded", it stops accepting change.</p>
<p>etcd is also brutally sensitive to disk latency, because every write is fsynced before it
is acknowledged. The practical threshold is a <strong>99th-percentile fsync under ~10 ms</strong>.
Above that you get leader elections, and leader elections during an upgrade produce the
"everything is slow and nothing is broken" incident.</p>
""" + term("the two numbers that predict an etcd incident", [
    ("$", "oc exec -n openshift-etcd etcd-master-0 -c etcdctl -- etcdctl endpoint status -w table"),
    ("", "+------------------+----------+---------+--------+-----------+"),
    ("", "|    ENDPOINT      |    ID    | VERSION | DB SIZE| IS LEADER |"),
    ("", "| master-0:2379    | a1f2...  | 3.5.14  |  1.2 GB|    true   |"),
    ("#", "DB size climbing towards 8 GB (the default quota) = defrag or compaction problem"),
    ("#", "and in Prometheus, the number that actually predicts trouble:"),
    ("", "histogram_quantile(0.99,"),
    ("", "  rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.01"),
]) + note("warn", "A backup you have not restored is a hypothesis",
          "<p><code>oc debug node/&lt;master&gt;</code> then "
          "<code>/usr/local/bin/cluster-backup.sh</code> produces a snapshot and the static pod "
          "manifests. Restoring one is a documented but genuinely disruptive procedure that "
          "takes the cluster down and rolls every node. Do it once, on a cluster you can afford "
          "to break, before you need it.</p>")),
])

ARCH_TROUBLE = """
<p>OpenShift gives you one entry point for almost any platform failure, and it is not
<code>oc get pods</code>. Work down the ownership chain — cluster operator, then the operator's
own workload, then the resource it manages.</p>
""" + table(
    ["Symptom", "Where it actually is", "First command"],
    [["Console unreachable, API fine",
      "Ingress operator or the router pods",
      "<code>oc get co ingress -o yaml</code>"],
     ["<code>oc login</code> fails for everyone",
      "Authentication operator / OAuth pods / the IdP itself",
      "<code>oc get co authentication</code>; <code>oc logs -n openshift-authentication -l app=oauth-openshift</code>"],
     ["Pods Pending, nodes look fine",
      "Scheduler constraints, or a quota on the project",
      "<code>oc describe pod</code> — the Events tail names the predicate that failed"],
     ["Pods rejected at creation",
      "SCC admission",
      "<code>oc adm policy scc-subject-review -z &lt;sa&gt; -f &lt;file&gt;</code>"],
     ["Node NotReady, no obvious cause",
      "MCO mid-rollout, or kubelet/CRI-O on the node",
      "<code>oc get mcp</code>; then <code>oc debug node/&lt;n&gt; -- chroot /host journalctl -u kubelet -n 200</code>"],
     ["Upgrade stalled at N%",
      "The cluster operator named in the Progressing message",
      "<code>oc get clusterversion -o yaml</code>"],
     ["Everything slow, nothing down",
      "etcd fsync latency or a leader election storm",
      "<code>oc logs -n openshift-etcd etcd-&lt;master&gt; -c etcd | grep -i 'elected\\|slow'</code>"],
     ["Operator stuck on an old version",
      "An unapproved InstallPlan",
      "<code>oc get installplan -A</code>"],
     ]) + """
<h3>must-gather — collect once, collect properly</h3>
<p><code>oc adm must-gather</code> is the supported way to capture cluster state. Run it with no
arguments and you get the full platform dump; point it at a component image and you get that
component's deep state instead. The full collection can run to several GB and take 15+ minutes,
so scope it when you already know the area.</p>
""" + term("scoping a must-gather instead of collecting everything", [
    ("$", "oc adm must-gather --dest-dir=./mg -- /usr/bin/gather_network_logs"),
    ("#", "network-only. Others: gather_audit_logs, and per-operator images:"),
    ("$", "oc adm must-gather --image=registry.redhat.io/openshift-logging/cluster-logging-rhel9-operator:latest"),
    ("#", "for a point-in-time snapshot of just what is unhealthy, this is often enough:"),
    ("$", "oc get co -o json | jq -r '.items[] | select(.status.conditions[]"),
    ("", "  | select(.type==\"Degraded\" and .status==\"True\")) | .metadata.name'"),
]) + note("good", "Read the Events before the logs",
          "<p>On OpenShift the useful message is nearly always in <code>oc describe</code> "
          "output or <code>oc get events --sort-by=.lastTimestamp</code>, not in a container "
          "log. Admission rejections, scheduling failures, image pull errors, quota denials "
          "and SCC refusals are all Events — none of them ever reach a pod log, because the pod "
          "never started.</p>")

ARCH_CHEAT = table(["Command", "What it answers"], [
    ["<code>oc get clusteroperators</code>", "Which of the ~30 platform components is unhealthy — start here"],
    ["<code>oc get clusterversion</code>", "Current version, and what an in-flight upgrade is waiting on"],
    ["<code>oc get mcp</code>", "Whether node config is mid-rollout or wedged"],
    ["<code>oc get nodes -o wide</code>", "Node state, roles, kernel and runtime versions"],
    ["<code>oc get events -A --sort-by=.lastTimestamp | tail -40</code>", "What the cluster just complained about"],
    ["<code>oc describe pod &lt;p&gt;</code>", "Scheduling, admission and image-pull failures"],
    ["<code>oc get pod &lt;p&gt; -o yaml | grep scc</code>", "Which SCC admitted it"],
    ["<code>oc adm policy scc-subject-review -z &lt;sa&gt; -f f.yaml</code>", "Which SCC would admit a workload"],
    ["<code>oc get subscription,installplan,csv -A</code>", "OLM operator state end to end"],
    ["<code>oc adm top nodes</code>", "Actual node CPU/memory pressure"],
    ["<code>oc debug node/&lt;n&gt; -- chroot /host journalctl -u kubelet</code>", "Node-level logs without SSH"],
    ["<code>oc adm must-gather --dest-dir=./mg</code>", "The supported full cluster dump"],
    ["<code>oc get project</code>", "Projects you can see (never leaks ones you cannot)"],
    ["<code>oc status -n &lt;ns&gt;</code>", "A readable summary of what is running in a project"],
], "mono")

OPENSHIFT_ARCHITECTURE = dict(
    slug="openshift-architecture",
    title="OpenShift Architecture & Fundamentals",
    tagline=("What the distribution adds on top of Kubernetes — the operator ownership chain, "
             "projects, SCC admission and the control plane — and how each one changes where "
             "you look when production breaks."),
    eyebrow="Kubernetes · OpenShift",
    meta=["<b>28 min</b> read", "Level: <b>core → advanced</b>", "OpenShift <b>01 / 03</b>"],
    sections=(
        section("The model", "HOW A REQUEST BECOMES CLUSTER STATE",
                "Nothing reaches etcd without passing OAuth and admission first — which is why "
                "most OpenShift-specific failures are rejections, not crashes.",
                f'<div class="dg-scroll">{ARCH_DIAGRAM}</div>'
                '<p class="dg-cap">The layers below the API are all reconciled by operators, '
                'and the operators are reconciled by the CVO. That chain is the debugging path: '
                'ClusterVersion → ClusterOperator → operator Deployment → the resource it '
                'manages → Pods.</p>')
        + section("Core", "CORE CONCEPTS",
                  "The four things that make OpenShift behave differently from the Kubernetes "
                  "you already know.", ARCH_CORE)
        + section("Advanced", "ADVANCED",
                  "Node configuration, admission policy, the image supply chain, and the one "
                  "component that has no graceful degradation.", ARCH_ADV)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, ARCH_TROUBLE)
        + section("Reference", "CHEATSHEET", None, ARCH_CHEAT)
    ),
)

TOPICS = [OPENSHIFT_ARCHITECTURE]
