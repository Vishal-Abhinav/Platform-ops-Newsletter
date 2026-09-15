#!/usr/bin/env python3
"""Kubernetes content, batch B: Scheduling (#063), Autoscaling (#064),
Cluster Operations (#065).

Topics covered:
  #063  Taints / Tolerations, Affinity / Anti-Affinity
  #064  Autoscaling, HPA, VPA, Cluster Autoscaling
  #065  Kubernetes Security, Upgrade, Backup, Multi-Cluster, Disaster Recovery
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section, refs

K8S = "https://kubernetes.io/docs/"

# ═══════════════════════════════════════════════════════════════════════════
# 03 · SCHEDULING
# ═══════════════════════════════════════════════════════════════════════════
SCH_DIAGRAM = diagram([
    ("Pod created", [("spec.nodeName empty", "core")]),
    ("Filter", [("resource fit", "warm"), ("nodeSelector", "warm"),
                ("taints vs tolerations", "warm"), ("node/pod affinity (required)", "warm"),
                ("volume topology", "warm")]),
    ("Feasible nodes", [("survivors, or none → Pending", "hot")]),
    ("Score", [("affinity (preferred)", "calm"), ("topology spread skew", "calm"),
               ("least/most allocated", "calm"), ("image locality", "calm")]),
    ("Bind", [("highest score wins", "go")]),
    ("After binding", [("taint added later → eviction, if NoExecute", "plain"),
                       ("preemption by higher priority", "plain")]),
], "Filter is a hard yes/no; score only ranks what survived. Pending always means filtering emptied the list")

SCH_CORE = "".join([
 card(1, "Taints and tolerations — the node's veto",
      "Repel by default, and the three effects that behave nothing alike.",
      ["taint", "toleration", "NoExecute"], """
<p>A <strong>taint</strong> is on the node and repels pods. A <strong>toleration</strong> is on
the pod and says "this one is allowed anyway". Note the direction: a toleration does not
<em>attract</em> a pod to a node — it only removes an objection. Wanting a pod to land on
specific nodes needs <code>nodeSelector</code> or affinity as well.</p>
<table class="tbl"><thead><tr><th>Effect</th><th>New pods</th><th>Already-running pods</th></tr></thead>
<tbody>
<tr><td><code>NoSchedule</code></td><td>Rejected unless tolerating</td><td>Left alone</td></tr>
<tr><td><code>PreferNoSchedule</code></td><td>Avoided if possible</td><td>Left alone</td></tr>
<tr><td><code>NoExecute</code></td><td>Rejected unless tolerating</td><td><strong>Evicted</strong> unless tolerating</td></tr>
</tbody></table>
<p>That last row is the one that causes surprise outages: adding a <code>NoExecute</code> taint
to a node evicts everything on it that does not tolerate it, immediately.</p>
<h3>The taints the cluster adds by itself</h3>
<p>Kubernetes taints nodes automatically on conditions — <code>not-ready</code>,
<code>unreachable</code>, <code>memory-pressure</code>, <code>disk-pressure</code>,
<code>pid-pressure</code>, <code>unschedulable</code>. The first two are
<code>NoExecute</code> with a default 300-second toleration injected into every pod, which is
why a node going unreachable takes five minutes to shed its pods. Shortening that
<code>tolerationSeconds</code> for latency-sensitive workloads is a real tuning knob, and one of
the few places where a default is too conservative rather than too aggressive.</p>
""" + term("why the pod will not schedule, or just got evicted", [
    ("$", "kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints"),
    ("", "NAME        TAINTS"),
    ("", "gpu-01      [map[effect:NoSchedule key:nvidia.com/gpu value:true]]"),
    ("$", "kubectl describe pod trainer | grep -A4 Events"),
    ("", "0/12 nodes are available: 11 node(s) had untolerated taint"),
    ("", "{nvidia.com/gpu: true}, 1 Insufficient nvidia.com/gpu."),
    ("#", "toleration alone does not PULL it there — pair with a selector:"),
    ("", "tolerations: [{key: nvidia.com/gpu, operator: Exists, effect: NoSchedule}]"),
    ("", "nodeSelector: { accelerator: nvidia }"),
    ("#", "faster failover than the 300s default, per pod:"),
    ("", "tolerations:"),
    ("", "- key: node.kubernetes.io/unreachable"),
    ("", "  operator: Exists"),
    ("", "  effect: NoExecute"),
    ("", "  tolerationSeconds: 30"),
]) + refs([
    ("Taints and Tolerations", K8S + "concepts/scheduling-eviction/taint-and-toleration/",
     "The three effects, the automatic condition taints, and tolerationSeconds."),
])),

 card(2, "Affinity and anti-affinity — the pod's preference",
      "required versus preferred, and the topologyKey that makes anti-affinity mean anything.",
      ["affinity", "topologyKey", "spread"], """
<p>Where taints are the node's veto, affinity is the pod's request. Two families:</p>
<ul>
<li><strong>nodeAffinity</strong> — about node labels. A richer <code>nodeSelector</code>, with
operators (<code>In</code>, <code>NotIn</code>, <code>Exists</code>, <code>Gt</code>,
<code>Lt</code>).</li>
<li><strong>podAffinity / podAntiAffinity</strong> — about other pods. "Near the cache" or, far
more commonly, "not on the same node as my other replicas".</li>
</ul>
<p>Each comes in two strengths, and the names are long enough that people copy them without
reading: <code>requiredDuringSchedulingIgnoredDuringExecution</code> is a hard filter — unmet
means Pending forever. <code>preferredDuringSchedulingIgnoredDuringExecution</code> is a
scoring hint — unmet just means a lower score. <strong>IgnoredDuringExecution</strong> in both
names is a promise: once bound, a pod is never moved because the rule stopped holding.</p>
<h3>topologyKey is the whole meaning of anti-affinity</h3>
<p>Anti-affinity says "not co-located", and <code>topologyKey</code> defines co-located.
<code>kubernetes.io/hostname</code> means one per node. <code>topology.kubernetes.io/zone</code>
means one per zone — which, with three replicas and three zones, is exactly what you want, and
with four replicas leaves one Pending forever if the rule is <code>required</code>.</p>
<h3>Prefer topologySpreadConstraints for the common case</h3>
<p>"Spread my replicas evenly" is better expressed with
<code>topologySpreadConstraints</code> than with anti-affinity: it takes a
<code>maxSkew</code>, so it degrades gracefully instead of wedging, and
<code>whenUnsatisfiable: ScheduleAnyway</code> gives you best-effort spreading that cannot cause
a Pending pod.</p>
""" + term("spread that degrades instead of wedging", [
    ("#", "brittle: 4 replicas, 3 zones, required -> one Pending forever"),
    ("", "podAntiAffinity:"),
    ("", "  requiredDuringSchedulingIgnoredDuringExecution:"),
    ("", "  - topologyKey: topology.kubernetes.io/zone"),
    ("", "    labelSelector: { matchLabels: { app: api } }"),
    ("#", "better: even spread, tolerates imbalance rather than failing"),
    ("", "topologySpreadConstraints:"),
    ("", "- maxSkew: 1"),
    ("", "  topologyKey: topology.kubernetes.io/zone"),
    ("", "  whenUnsatisfiable: ScheduleAnyway"),
    ("", "  labelSelector: { matchLabels: { app: api } }"),
    ("#", "where did they actually land?"),
    ("$", "kubectl get pods -l app=api -o custom-columns=\\"),
    ("", "  POD:.metadata.name,NODE:.spec.nodeName --no-headers | sort -k2"),
    ("$", "kubectl get pods -l app=api -o json | jq -r '.items[].spec.nodeName' \\"),
    ("", "  | xargs -I{} kubectl get node {} -o jsonpath='{.metadata.labels.topology\\.kubernetes\\.io/zone}{\"\\n\"}' | sort | uniq -c"),
]) + note("warn", "IgnoredDuringExecution means drift is permanent",
          "<p>Scheduling rules are evaluated once, at binding. If all three replicas end up in "
          "one zone because the other two were briefly full, they stay there after capacity "
          "returns — nothing rebalances them. A rolling restart is the rebalance, and "
          "<code>descheduler</code> is the tool if you want it continuous.</p>")
   + refs([
    ("Assigning Pods to Nodes", K8S + "concepts/scheduling-eviction/assign-pod-node/",
     "nodeSelector, node affinity, pod affinity and anti-affinity with full syntax."),
    ("Pod Topology Spread Constraints", K8S + "concepts/scheduling-eviction/topology-spread-constraints/",
     "maxSkew, whenUnsatisfiable, and how spreading interacts with affinity."),
    ("Kubernetes Scheduler", K8S + "concepts/scheduling-eviction/kube-scheduler/",
     "The filter-then-score model the Pending message comes from."),
])),
])

SCH_TROUBLE = """
<p><code>Pending</code> always means the same thing: <strong>filtering produced an empty list</strong>.
The scheduler says which predicate failed and on how many nodes, and that sentence is the entire
diagnosis — it is just easy to skim past.</p>
""" + table(
    ["Message fragment", "Cause", "Fix"],
    [["<code>Insufficient cpu</code> / <code>memory</code>", "No node has that much free — requests, not usage",
      "Lower requests, or add capacity"],
     ["<code>had untolerated taint</code>", "Node repels it", "Add the toleration, and a selector to attract it"],
     ["<code>didn't match Pod's node affinity/selector</code>", "No node carries the label",
      "<code>kubectl get nodes --show-labels</code>"],
     ["<code>didn't match pod anti-affinity rules</code>", "Its own replicas are in the way",
      "Relax to preferred, or use topology spread"],
     ["<code>node(s) had volume node affinity conflict</code>", "The PV is in another zone",
      "<code>WaitForFirstConsumer</code> on the StorageClass"],
     ["<code>node(s) were unschedulable</code>", "Cordoned", "<code>kubectl uncordon</code>"],
     ["<code>exceeded quota</code>", "ResourceQuota refused it before scheduling",
      "<code>kubectl describe quota -n &lt;ns&gt;</code>"],
     ]) + """
<h3>Requests are what scheduling uses — not usage</h3>
<p>A node showing 30% CPU in <code>top</code> can be 100% <em>allocated</em> and refuse new pods,
because the scheduler adds up <code>requests</code>, not actual consumption. That gap is the most
common "we have plenty of capacity, why is it Pending" confusion, and
<code>kubectl describe node</code> shows both numbers side by side.</p>
""" + term("allocated versus used, which are different numbers", [
    ("$", "kubectl describe node worker-04 | grep -A8 'Allocated resources'"),
    ("", "  Resource   Requests      Limits"),
    ("", "  cpu        7800m (97%)   14 (175%)"),
    ("", "  memory     29Gi (92%)    48Gi (152%)"),
    ("#", "97% ALLOCATED. Meanwhile actual usage:"),
    ("$", "kubectl top node worker-04"),
    ("", "NAME        CPU(cores)   CPU%   MEMORY   MEMORY%"),
    ("", "worker-04   2410m        30%    11Gi     34%"),
    ("#", "-> over-requested workloads, not a capacity problem. Right-size the requests."),
    ("$", "kubectl get pods -A -o json | jq -r '.items[]"),
    ("", "  | select(.spec.nodeName==\"worker-04\")"),
    ("", "  | \"\\(.spec.containers[].resources.requests.cpu // \"-\")\\t\\(.metadata.name)\"' | sort -rn | head"),
]) + note("good", "The Events tail is the answer, verbatim",
          "<p><code>kubectl describe pod</code> ends with a line of the form "
          "<code>0/12 nodes are available: 8 Insufficient cpu, 4 node(s) had untolerated "
          "taint</code>. That accounts for every node in the cluster and why each one was "
          "excluded. There is rarely anything to deduce beyond reading it.</p>")

SCH_CHEAT = table(["Command", "What it answers"], [
    ["<code>kubectl describe pod &lt;p&gt;</code>", "Which predicate failed, on how many nodes"],
    ["<code>kubectl get nodes --show-labels</code>", "What affinity rules can actually match"],
    ["<code>kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints</code>", "Every taint in one view"],
    ["<code>kubectl describe node &lt;n&gt; | grep -A8 Allocated</code>", "Requested versus capacity — what scheduling uses"],
    ["<code>kubectl top node</code>", "Actual usage, for contrast"],
    ["<code>kubectl taint node &lt;n&gt; key=value:NoSchedule</code>", "Repel new pods"],
    ["<code>kubectl taint node &lt;n&gt; key-</code>", "Remove a taint (trailing dash)"],
    ["<code>kubectl cordon</code> / <code>uncordon</code>", "Stop or resume scheduling"],
    ["<code>kubectl get pods -o wide --sort-by=.spec.nodeName</code>", "Where everything landed"],
    ["<code>kubectl get pods --field-selector status.phase=Pending -A</code>", "Everything stuck, cluster-wide"],
    ["<code>kubectl get priorityclass</code>", "What can preempt what"],
], "mono")

KUBERNETES_SCHEDULING = dict(
    slug="kubernetes-scheduling",
    title="Kubernetes Scheduling",
    tagline=("Taints as the node's veto and the NoExecute effect that evicts what is already "
             "running, affinity as the pod's request, the topologyKey that gives anti-affinity "
             "its meaning, and why Pending is always a filtering result you can read verbatim."),
    eyebrow="Kubernetes · Core",
    meta=["<b>22 min</b> read", "Level: <b>core → advanced</b>", "Kubernetes <b>03 / 05</b>"],
    sections=(
        section("The model", "HOW A POD PICKS A NODE",
                "Filter, then score. Every Pending pod is a filter that emptied the list, and "
                "the scheduler tells you which one.",
                f'<div class="dg-scroll">{SCH_DIAGRAM}</div>'
                '<p class="dg-cap">Scoring never rescues a pod that failed filtering — it only '
                'ranks the survivors. That is why "add more nodes" does not fix an affinity '
                'rule no node can satisfy.</p>')
        + section("Core", "THE TWO PLACEMENT MECHANISMS",
                  "One belongs to the node and one to the pod; they are routinely confused for "
                  "each other.", SCH_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, SCH_TROUBLE)
        + section("Reference", "CHEATSHEET", None, SCH_CHEAT)
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# 04 · AUTOSCALING
# ═══════════════════════════════════════════════════════════════════════════
AS_DIAGRAM = diagram([
    ("Signal", [("metrics-server (CPU/mem)", "core"),
                ("Prometheus adapter (custom)", "core"),
                ("KEDA (external: queue depth)", "core")]),
    ("Pod count", [("HPA — scales replicas", "warm")]),
    ("Pod size", [("VPA — scales requests/limits", "hot")]),
    ("Node count", [("Cluster Autoscaler / Karpenter", "calm")]),
    ("Constraint", [("PodDisruptionBudget", "go"), ("ResourceQuota", "go"),
                    ("node group min/max", "go")]),
    ("Result", [("pods fit, or stay Pending", "plain")]),
], "Three autoscalers on three different axes — HPA and VPA on CPU at once is the classic mistake")

AS_CORE = "".join([
 card(1, "HPA — replicas from a metric, and the algorithm in one line",
      "desiredReplicas = ceil(current x (currentMetric / targetMetric)). Everything else is damping.",
      ["HPA", "metrics-server", "stabilization"], """
<p>The Horizontal Pod Autoscaler adjusts <strong>replica count</strong>. The core calculation is
one line:</p>
<p><code>desiredReplicas = ceil(currentReplicas × (currentMetricValue / desiredMetricValue))</code></p>
<p>At 4 replicas averaging 80% CPU against a 50% target: <code>ceil(4 × 1.6) = 7</code>. There
is no mystery in the arithmetic — the surprises are all in the inputs and the damping.</p>
<h3>The three things that stop it working</h3>
<ul>
<li><strong>No resource requests.</strong> CPU-percentage targets are a percentage
<em>of the request</em>. A container with no <code>requests.cpu</code> has no denominator, the
HPA reports <code>&lt;unknown&gt;</code>, and it never scales. This is the single most common
cause.</li>
<li><strong>No metrics-server.</strong> Same symptom, different reason. <code>kubectl top</code>
failing and the HPA showing <code>&lt;unknown&gt;</code> together point here.</li>
<li><strong>Scale-down stabilization.</strong> The default 300-second window means scale-down
looks "broken" for five minutes after load drops. It is deliberate — it stops flapping.</li>
</ul>
<h3>CPU is often the wrong signal</h3>
<p>For a queue consumer, the honest metric is queue depth, not CPU: a worker blocked on I/O sits
at 5% CPU with a backlog of 50,000. That is what custom metrics (via the Prometheus adapter) and
external metrics (via KEDA) exist for, and it is usually the difference between autoscaling that
works and autoscaling that is decorative.</p>
""" + term("an HPA that reports unknown", [
    ("$", "kubectl get hpa api"),
    ("", "NAME   REFERENCE        TARGETS         MINPODS  MAXPODS  REPLICAS"),
    ("", "api    Deployment/api   <unknown>/50%   2        10       2"),
    ("#", "two candidates. Check metrics-server first:"),
    ("$", "kubectl top pods -l app=api"),
    ("", "error: Metrics API not available          <- metrics-server"),
    ("#", "if top works, it is the missing request:"),
    ("$", "kubectl get deploy api -o jsonpath='{.spec.template.spec.containers[0].resources}'"),
    ("", "{}                                        <- no requests, no denominator"),
    ("$", "kubectl set resources deploy/api --requests=cpu=200m,memory=256Mi"),
    ("#", "and the behaviour block that stops flapping while still reacting fast:"),
    ("", "behavior:"),
    ("", "  scaleDown: { stabilizationWindowSeconds: 300 }"),
    ("", "  scaleUp:   { stabilizationWindowSeconds: 0,"),
    ("", "               policies: [{type: Percent, value: 100, periodSeconds: 30}] }"),
]) + refs([
    ("Horizontal Pod Autoscaling", K8S + "concepts/workloads/autoscaling/horizontal-pod-autoscale/",
     "The algorithm, tolerance, behaviour policies and multi-metric handling."),
    ("HPA Walkthrough", K8S + "tasks/run-application/horizontal-pod-autoscale-walkthrough/",
     "A worked example, including custom and external metrics."),
])),

 card(2, "VPA — right-sizing requests, and why it fights the HPA",
      "The recommender is useful on its own; the updater evicts pods to apply what it found.",
      ["VPA", "recommender", "in-place resize"], """
<p>The Vertical Pod Autoscaler adjusts <strong>requests and limits</strong> rather than replica
count. It has three parts, and they are separable — which matters more than the docs make
obvious:</p>
<ul>
<li><strong>Recommender</strong> — watches usage and computes what the requests should be.</li>
<li><strong>Updater</strong> — evicts pods whose requests are wrong.</li>
<li><strong>Admission controller</strong> — rewrites requests on pods as they are created.</li>
</ul>
<p>In <code>updateMode: "Off"</code> you get only the recommender: no evictions, just a
recommendation you can read. That is the mode most clusters should start in — it turns
"what should this request be?" from guesswork into a measured number, with no runtime risk.</p>
<h3>VPA and HPA on the same metric will fight</h3>
<p>Both react to CPU. VPA raises the request; raising the request lowers CPU-as-a-percentage-of-request;
the HPA sees lower utilisation and scales in; fewer pods means more load each; VPA raises requests
again. The documented rule is simple: <strong>do not run both on CPU or memory for the same
workload.</strong> HPA on a custom metric with VPA on CPU is fine.</p>
""" + term("using VPA as a measuring tool, safely", [
    ("", "apiVersion: autoscaling.k8s.io/v1"),
    ("", "kind: VerticalPodAutoscaler"),
    ("", "spec:"),
    ("", "  targetRef: { apiVersion: apps/v1, kind: Deployment, name: api }"),
    ("", "  updatePolicy: { updateMode: \"Off\" }     # recommend only, never evict"),
    ("$", "kubectl describe vpa api | grep -A12 'Recommendation'"),
    ("", "  Container Recommendations:"),
    ("", "    Target:  cpu: 240m   memory: 310Mi"),
    ("", "    Lower Bound: cpu: 180m"),
    ("", "    Upper Bound: cpu: 520m"),
    ("#", "compare with what is actually requested, then set it deliberately:"),
    ("$", "kubectl get deploy api -o jsonpath='{.spec.template.spec.containers[0].resources.requests}'"),
]) + refs([
    ("Vertical Pod Autoscaling", K8S + "concepts/workloads/autoscaling/vertical-pod-autoscale/",
     "Update modes, the recommender, and the explicit HPA conflict warning."),
    ("autoscaler/vertical-pod-autoscaler", "https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler",
     "The component itself — install, CRDs and known limitations."),
])),

 card(3, "Cluster Autoscaler — nodes, and the pods that pin them forever",
      "Scale-up is easy. Scale-down is blocked by a surprisingly long list.",
      ["Cluster Autoscaler", "scale-down", "Karpenter"], """
<p>The Cluster Autoscaler adds nodes when pods are <code>Pending</code> for want of capacity, and
removes nodes that have been underused for a while. Scale-up is straightforward. Scale-down is
where the money leaks, because a single pod can pin a whole node indefinitely.</p>
<h3>What blocks a node from being removed</h3>
<ul>
<li>A pod with <strong>no controller</strong> — a bare Pod nothing would recreate.</li>
<li>A pod whose <strong>PodDisruptionBudget</strong> would be violated.</li>
<li>A pod with <strong>local storage</strong> (emptyDir or hostPath) unless annotated safe.</li>
<li>A pod in <strong>kube-system</strong> without a PDB.</li>
<li>Anything carrying
<code>cluster-autoscaler.kubernetes.io/safe-to-evict: "false"</code>.</li>
</ul>
<p>The autoscaler logs its reason for every node it declined to remove, which turns "why are we
paying for twelve nodes at 20% utilisation" into a five-minute answer rather than a theory.</p>
<p><strong>Karpenter</strong> takes a different approach — instead of scaling fixed node groups
it provisions the instance shape that fits the pending pods, and consolidates aggressively. On
AWS it is usually the better answer now; the mental model shifts from "which group do I grow" to
"what shape does this workload need".</p>
""" + term("why the cluster will not scale down", [
    ("$", "kubectl logs -n kube-system deploy/cluster-autoscaler | grep -i 'scale.down' | tail -20"),
    ("", "node worker-07 cannot be removed: pod kube-system/metrics-server-x is"),
    ("", "  not replicated and has no PodDisruptionBudget"),
    ("", "node worker-09 cannot be removed: pod prod/batch-1 has local storage"),
    ("#", "the summary the autoscaler maintains for itself:"),
    ("$", "kubectl get cm -n kube-system cluster-autoscaler-status -o yaml | head -40"),
    ("#", "allow a pod with scratch space to be moved:"),
    ("$", "kubectl annotate pod batch-1 \\"),
    ("", "  cluster-autoscaler.kubernetes.io/safe-to-evict=true"),
]) + note("warn", "min replicas 1 plus a strict PDB is a permanent node",
          "<p>A single-replica Deployment with <code>minAvailable: 1</code> can never be "
          "evicted, so its node can never be drained — not by the autoscaler, and not by an "
          "upgrade either. Two replicas, or <code>maxUnavailable: 1</code> instead, costs less "
          "than the node you are pinning.</p>")
   + refs([
    ("Autoscaling Workloads", K8S + "concepts/workloads/autoscaling/",
     "How the three autoscalers relate, from upstream."),
    ("autoscaler/cluster-autoscaler", "https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler",
     "Scale-down conditions, the safe-to-evict annotation, and per-cloud behaviour."),
    ("Disruptions", K8S + "concepts/workloads/pods/disruptions/",
     "PodDisruptionBudget semantics — the thing that blocks both scale-down and upgrades."),
])),
])

AS_TROUBLE = """
<p>Autoscaling failures are quiet: nothing errors, the thing just does not scale. Each of the
three has one dominant cause, so check that first rather than reading configuration.</p>
""" + table(
    ["Symptom", "Most likely cause", "Check"],
    [["HPA target <code>&lt;unknown&gt;</code>", "No resource requests, or no metrics-server",
      "<code>kubectl top pods</code>; then the container's <code>resources.requests</code>"],
     ["HPA at max, still slow", "Bottleneck is downstream, not replicas",
      "Database connections, a queue, a rate limit"],
     ["Scales up, never down", "300s stabilization, or one busy replica in the average",
      "<code>kubectl describe hpa</code> — the conditions explain each decision"],
     ["Replicas flapping", "scaleUp and scaleDown both aggressive",
      "Set a <code>behavior</code> block"],
     ["Pods Pending, no new nodes", "Node group at max, or no shape fits",
      "Cluster Autoscaler logs; the group's max size"],
     ["Nodes never removed", "A pod pinning each one",
      "<code>cluster-autoscaler-status</code> ConfigMap"],
     ["VPA and HPA both acting", "Both on CPU — they fight by design",
      "Move HPA to a custom metric, or VPA to Off"],
     ]) + """
<h3>Read the HPA's own reasoning</h3>
<p><code>kubectl describe hpa</code> carries conditions — <code>AbleToScale</code>,
<code>ScalingActive</code>, <code>ScalingLimited</code> — each with a message stating exactly
what the controller decided and why. It is the autoscaling equivalent of the scheduler's Events
line, and equally underused.</p>
""" + term("the HPA explaining itself", [
    ("$", "kubectl describe hpa api | grep -A10 Conditions"),
    ("", "  AbleToScale     True    ReadyForNewScale"),
    ("", "  ScalingActive   True    ValidMetricFound"),
    ("", "  ScalingLimited  True    TooManyReplicas"),
    ("", "    the desired replica count is more than the maximum replica count"),
    ("#", "-> it WANTS more and maxReplicas is the ceiling. Raise it, or accept the limit."),
    ("$", "kubectl get hpa -A -o custom-columns=\\"),
    ("", "  NS:.metadata.namespace,NAME:.metadata.name,MIN:.spec.minReplicas,MAX:.spec.maxReplicas,CUR:.status.currentReplicas"),
    ("#", "every HPA currently pinned at its ceiling — the ones to look at:"),
    ("$", "kubectl get hpa -A -o json | jq -r '.items[]"),
    ("", "  | select(.status.currentReplicas==.spec.maxReplicas)"),
    ("", "  | \"\\(.metadata.namespace)/\\(.metadata.name)\"'"),
])

AS_CHEAT = table(["Command", "What it answers"], [
    ["<code>kubectl get hpa -A</code>", "Targets, current versus desired, everywhere"],
    ["<code>kubectl describe hpa &lt;x&gt;</code>", "The controller's own reasoning, in conditions"],
    ["<code>kubectl top pods</code> / <code>nodes</code>", "Whether metrics-server works at all"],
    ["<code>kubectl set resources deploy/&lt;x&gt; --requests=cpu=200m</code>", "Give the HPA a denominator"],
    ["<code>kubectl describe vpa &lt;x&gt;</code>", "Recommended requests, measured not guessed"],
    ["<code>kubectl logs -n kube-system deploy/cluster-autoscaler</code>", "Why a node was not removed"],
    ["<code>kubectl get cm -n kube-system cluster-autoscaler-status -o yaml</code>", "Node group state at a glance"],
    ["<code>kubectl get pdb -A</code>", "What blocks eviction, scale-down and upgrades"],
    ["<code>kubectl get pods --field-selector status.phase=Pending -A</code>", "What should be triggering scale-up"],
    ["<code>kubectl annotate pod &lt;p&gt; cluster-autoscaler.kubernetes.io/safe-to-evict=true</code>", "Unpin a node"],
], "mono")

KUBERNETES_AUTOSCALING = dict(
    slug="kubernetes-autoscaling",
    title="Kubernetes Autoscaling",
    tagline=("The HPA algorithm in one line and the missing resource request that silently "
             "disables it, VPA as a measuring tool before it is an actuator, why the two fight "
             "on CPU, and the single pod that pins a node against every scale-down."),
    eyebrow="Kubernetes · Core",
    meta=["<b>24 min</b> read", "Level: <b>core → advanced</b>", "Kubernetes <b>04 / 05</b>"],
    sections=(
        section("The model", "THREE AUTOSCALERS, THREE AXES",
                "Count, size and capacity. They interact, and two of them actively conflict.",
                f'<div class="dg-scroll">{AS_DIAGRAM}</div>'
                '<p class="dg-cap">The constraint row is what makes autoscaling fail quietly: a '
                'PodDisruptionBudget or a node-group maximum stops the whole chain without '
                'anything reporting an error.</p>')
        + section("Core", "THE THREE AUTOSCALERS",
                  "What each one moves, and the one thing that stops each from working.", AS_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, AS_TROUBLE)
        + section("Reference", "CHEATSHEET", None, AS_CHEAT)
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# 05 · CLUSTER OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════
OPS_DIAGRAM = diagram([
    ("Harden", [("Pod Security Admission", "core"), ("NetworkPolicy", "core"),
                ("RBAC least privilege", "core"), ("Encryption at rest", "core")]),
    ("Version", [("control plane first", "warm"), ("kubelet within skew", "warm"),
                 ("deprecated API check", "warm")]),
    ("Drain", [("cordon → evict → reboot", "hot"), ("PDB gates every eviction", "hot")]),
    ("Back up", [("etcd snapshot (cluster state)", "calm"),
                 ("Velero (namespaces + PV data)", "calm")]),
    ("Spread", [("multi-cluster: fleet, not one big cluster", "go")]),
    ("Prove", [("restore rehearsal = your real RTO", "plain")]),
], "The order matters: harden before you upgrade, and rehearse the restore before you need it")

OPS_CORE = "".join([
 card(1, "Cluster security — four controls that do most of the work",
      "Pod Security Admission, NetworkPolicy, RBAC and encryption at rest.",
      ["PSA", "NetworkPolicy", "hardening"], """
<p>Cluster hardening is a long subject with a short high-value core. Four controls, each one
label or object, each closing a category of problem:</p>
<ul>
<li><strong>Pod Security Admission.</strong> Replaced PodSecurityPolicy in v1.25. Three levels —
<code>privileged</code>, <code>baseline</code>, <code>restricted</code> — applied as a namespace
label. <code>restricted</code> blocks running as root, privilege escalation, host namespaces and
most capabilities.</li>
<li><strong>NetworkPolicy.</strong> Without one, every pod reaches every pod in every namespace.
Default-deny per namespace, then allow what is needed.</li>
<li><strong>RBAC least privilege.</strong> Covered in Config &amp; Access — the short version is
that <code>create pods</code> and <code>get secrets</code> are both effectively privileged.</li>
<li><strong>Encryption at rest.</strong> Secrets sit in etcd in the clear by default.</li>
</ul>
<h3>Use warn before enforce</h3>
<p>PSA can warn and audit without blocking. Labelling a namespace
<code>warn=restricted</code> first tells you exactly which workloads would break, from real
traffic, before anything is refused. Going straight to <code>enforce</code> on a live namespace
is how you find out during an incident.</p>
""" + term("rolling out Pod Security without breaking production", [
    ("#", "1. warn only — nothing is blocked, violations are reported"),
    ("$", "kubectl label ns prod pod-security.kubernetes.io/warn=restricted \\"),
    ("", "  pod-security.kubernetes.io/audit=restricted"),
    ("#", "2. redeploy something and read the warnings it prints"),
    ("$", "kubectl rollout restart deploy -n prod"),
    ("", "Warning: would violate \"restricted\": allowPrivilegeEscalation != false,"),
    ("", "  unrestricted capabilities, runAsNonRoot != true, seccompProfile"),
    ("#", "3. fix the workloads, THEN enforce"),
    ("$", "kubectl label ns prod pod-security.kubernetes.io/enforce=restricted --overwrite"),
    ("#", "what is enforced across the fleet right now:"),
    ("$", "kubectl get ns -o custom-columns=\\"),
    ("", "  NAME:.metadata.name,ENFORCE:.metadata.labels.pod-security\\\\.kubernetes\\\\.io/enforce"),
]) + refs([
    ("Pod Security Standards", K8S + "concepts/security/pod-security-standards/",
     "What privileged, baseline and restricted each permit, field by field."),
    ("Pod Security Admission", K8S + "concepts/security/pod-security-admission/",
     "The labels, the warn/audit/enforce modes and version pinning."),
    ("Network Policies", K8S + "concepts/services-networking/network-policies/",
     "The isolation model, and the default-deny recipes."),
])),

 card(2, "Upgrades — version skew, and the API that disappears under you",
      "Control plane first, one minor at a time, and check what is still calling the removed API.",
      ["upgrade", "version skew", "deprecated API"], """
<p>Two rules govern every Kubernetes upgrade:</p>
<ul>
<li><strong>Control plane first</strong>, then nodes. kubelet may be up to three minor versions
behind the API server, never ahead.</li>
<li><strong>One minor version at a time.</strong> 1.28 → 1.30 is two upgrades, not one.</li>
</ul>
<p>The thing that actually breaks workloads is <strong>API removal</strong>. A deprecated API is
removed on a schedule, and a manifest or controller still calling it starts failing the moment
the control plane moves. The cluster knows who is calling what, which turns this from an audit
into a query.</p>
<h3>The pre-upgrade sequence</h3>
<p>Check for removed APIs, take an etcd snapshot, confirm PDBs will not deadlock the drain,
upgrade the control plane, then the nodes one pool at a time.</p>
""" + term("finding what will break before it breaks", [
    ("#", "1. what is still calling a deprecated API, and who"),
    ("$", "kubectl get --raw /metrics | grep apiserver_requested_deprecated_apis"),
    ("$", "kubectl get apirequestcount -o json | jq -r '.items[]"),
    ("", "  | select(.status.removedInRelease != null)"),
    ("", "  | \"\\(.metadata.name) removed in \\(.status.removedInRelease)\"'"),
    ("#", "2. snapshot etcd BEFORE touching anything"),
    ("$", "ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-$(date +%F).db \\"),
    ("", "  --endpoints=https://127.0.0.1:2379 \\"),
    ("", "  --cacert=/etc/kubernetes/pki/etcd/ca.crt \\"),
    ("", "  --cert=/etc/kubernetes/pki/etcd/server.crt \\"),
    ("", "  --key=/etc/kubernetes/pki/etcd/server.key"),
    ("$", "ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-$(date +%F).db -w table"),
    ("#", "3. will the drain deadlock? any PDB with 0 allowed is a stop sign"),
    ("$", "kubectl get pdb -A -o json | jq -r '.items[]"),
    ("", "  | select(.status.disruptionsAllowed==0)"),
    ("", "  | \"\\(.metadata.namespace)/\\(.metadata.name)\"'"),
    ("#", "4. then, per node"),
    ("$", "kubectl drain worker-04 --ignore-daemonsets --delete-emptydir-data --timeout=10m"),
]) + refs([
    ("Upgrading kubeadm clusters", K8S + "tasks/administer-cluster/kubeadm/kubeadm-upgrade/",
     "The supported sequence, and the skew rules restated per component."),
    ("Safely Drain a Node", K8S + "tasks/administer-cluster/safely-drain-node/",
     "How eviction interacts with PodDisruptionBudgets."),
])),

 card(3, "Backup — two different things, and only one has your data",
      "An etcd snapshot is the cluster. Velero is the namespaces and the volumes.",
      ["etcd", "Velero", "RTO"], """
<table class="tbl"><thead><tr><th></th><th>etcd snapshot</th><th>Velero</th></tr></thead>
<tbody>
<tr><td>Contains</td><td>Every API object</td><td>Selected namespaces + PV contents</td></tr>
<tr><td>Restores</td><td>The whole cluster to that instant</td><td>Namespaces, into this or another cluster</td></tr>
<tr><td>Granularity</td><td>All or nothing</td><td>Per namespace, per label</td></tr>
<tr><td>PV data</td><td><strong>No</strong></td><td>Yes — snapshots or file-level copy</td></tr>
<tr><td>Right for</td><td>Lost quorum, corrupted control plane</td><td>Deleted namespace, migration, real DR</td></tr>
</tbody></table>
<p>Conflating the two is how a DR test fails. "We back up etcd nightly" does not protect against
someone deleting the prod namespace with Delete-policy PVCs — the objects come back from a
cluster-wide restore, the <em>volume contents</em> do not, because they were never in etcd.</p>
<h3>Your RTO is a measured number or it is fiction</h3>
<p>An etcd restore stops the control plane, restores on one member and rebuilds the others. It is
documented, disruptive, and takes as long as it takes. The only way to know that number is to do
it once on a cluster you can afford to break — and the first rehearsal always takes longer than
anyone predicted.</p>
""" + term("both, and the check that they actually ran", [
    ("$", "velero backup create prod-$(date +%F) --include-namespaces prod \\"),
    ("", "  --snapshot-volumes --ttl 720h"),
    ("$", "velero backup describe prod-$(date +%F) --details"),
    ("$", "velero backup get"),
    ("", "NAME           STATUS      ERRORS   WARNINGS   CREATED"),
    ("", "prod-2026-09-15 Completed   0        0          2h ago"),
    ("#", "restore ONE namespace, without touching the rest of the cluster:"),
    ("$", "velero restore create --from-backup prod-2026-09-15 --include-namespaces prod"),
    ("#", "a backup that has never been restored is a hypothesis. Prove it somewhere safe:"),
    ("$", "velero restore create drill --from-backup prod-2026-09-15 \\"),
    ("", "  --namespace-mappings prod:prod-restore-drill"),
]) + note("bad", "The reclaim policy decides whether the data survives at all",
          "<p>On a <code>Delete</code>-policy StorageClass, removing a PVC destroys the backing "
          "volume immediately — including when the PVC goes as a side effect of deleting a "
          "namespace or a Helm release. <code>Retain</code> turns irreversible loss into "
          "orphaned volumes you clean up deliberately, which is a far better problem.</p>")
   + refs([
    ("Operating etcd clusters for Kubernetes", K8S + "tasks/administer-cluster/configure-upgrade-etcd/",
     "Snapshot, restore, defragmentation and the sizing limits."),
])),

 card(4, "Multi-cluster and DR — a fleet, not one big cluster",
      "What a second cluster buys you, what it costs, and the failure domain you actually care about.",
      ["multi-cluster", "DR", "failure domain"], """
<p>Past a certain size the question stops being "how big can this cluster get" and becomes "how
many clusters, split how". The honest reasons to run more than one:</p>
<ul>
<li><strong>Blast radius.</strong> A cluster is a failure domain. A bad CRD, a broken webhook or
a control-plane upgrade takes out everything in it.</li>
<li><strong>Region.</strong> A cluster does not span regions well — etcd needs low latency
between members.</li>
<li><strong>Hard tenancy.</strong> Namespaces are not a security boundary; separate clusters
are.</li>
<li><strong>Upgrade staging.</strong> Somewhere real to land a new version first.</li>
</ul>
<p>And the costs, which are consistently underestimated: every platform component installed N
times, N sets of credentials and policy to keep consistent, cross-cluster service discovery to
solve, and a fleet-management story (Argo CD ApplicationSets, Cluster API, Fleet) that is now
itself production infrastructure.</p>
<h3>The DR question that actually matters</h3>
<p>Not "do we have a second cluster" but <strong>"what is our RPO and RTO, and have we measured
them"</strong>. Active-passive with Velero restore is hours. Active-active with replicated data
is minutes, and a much larger standing bill. Both are defensible; only one is usually what people
have while believing they have the other.</p>
""" + term("the fleet-wide checks worth having", [
    ("#", "version drift across the fleet"),
    ("$", "for c in $(kubectl config get-contexts -o name); do"),
    ("", "  printf '%-28s %s\\n' \"$c\" \"$(kubectl --context=$c version -o json \\"),
    ("", "    | jq -r .serverVersion.gitVersion)\"; done"),
    ("#", "does every cluster have a backup that completed recently?"),
    ("$", "for c in $(kubectl config get-contexts -o name); do"),
    ("", "  echo \"== $c\"; kubectl --context=$c get backup -n velero \\"),
    ("", "    --sort-by=.metadata.creationTimestamp | tail -2; done"),
    ("#", "and the one that catches real drift — what is NOT in git"),
    ("$", "kubectl --context=$c diff -f manifests/ || true"),
]) + refs([
    ("High Availability with kubeadm", K8S + "setup/production-environment/tools/kubeadm/high-availability/",
     "Stacked versus external etcd, and what HA does and does not cover."),
    ("PKI certificates and requirements", K8S + "concepts/cluster-administration/certificates/",
     "The certificates a cluster depends on — and the expiry that takes one down quietly."),
])),
])

OPS_TROUBLE = """
<p>Cluster-level failures differ from workload failures in one way that matters: they are rarely
loud. A certificate that expires in 30 days, a backup that has silently failed for a month, an
etcd database approaching its quota — each is invisible until it is an outage.</p>
""" + table(
    ["Symptom", "Cause", "Check"],
    [["API server suddenly refuses everything", "Certificate expired",
      "<code>kubeadm certs check-expiration</code>"],
     ["Writes fail, reads work", "etcd lost quorum, or hit its DB quota",
      "<code>etcdctl endpoint status -w table</code>"],
     ["Everything slow, nothing down", "etcd fsync latency / leader elections",
      "<code>etcd_disk_wal_fsync_duration_seconds</code> p99 &gt; 10 ms"],
     ["Upgrade drain hangs on one node", "A PDB that allows zero disruptions",
      "<code>kubectl get pdb -A</code>"],
     ["Workloads vanish after upgrade", "A removed API their manifests used",
      "<code>kubectl get apirequestcount</code> — before, not after"],
     ["Restore produces empty volumes", "etcd snapshot, not an application backup",
      "Velero with <code>--snapshot-volumes</code>"],
     ["Node NotReady, kubelet fine", "CNI or the container runtime",
      "<code>journalctl -u kubelet -u containerd</code> on the node"],
     ]) + """
<h3>The three that should be alerts, not discoveries</h3>
""" + term("certificate expiry, etcd size, backup age", [
    ("#", "1. certificates — silent until the day everything stops"),
    ("$", "kubeadm certs check-expiration"),
    ("", "CERTIFICATE                EXPIRES                  RESIDUAL TIME"),
    ("", "apiserver                  Nov 02, 2026 09:14 UTC   48d"),
    ("", "etcd-server                Nov 02, 2026 09:14 UTC   48d"),
    ("#", "2. etcd DB size against its quota (default 8 GB)"),
    ("$", "kubectl -n kube-system exec etcd-master-0 -- etcdctl endpoint status -w table"),
    ("#", "   growing steadily? compact and defrag, do not just raise the quota:"),
    ("$", "etcdctl compact $(etcdctl endpoint status -w json | jq -r '.[0].Status.header.revision')"),
    ("$", "etcdctl defrag --cluster"),
    ("#", "3. backup age — a job that has failed quietly for a month looks like nothing"),
    ("$", "velero backup get --output json | jq -r '.items[]"),
    ("", "  | \"\\(.metadata.name)\\t\\(.status.phase)\\t\\(.status.completionTimestamp)\"' | tail -5"),
]) + note("good", "Alert on the absence, not the error",
          "<p>Each of these three fails by <em>not happening</em>: the backup does not run, the "
          "certificate does not renew, the compaction does not occur. None produces an error to "
          "alert on. The alert has to be on the age of the last success — which is a different "
          "kind of rule, and the one most clusters are missing.</p>")

OPS_CHEAT = table(["Command", "What it answers"], [
    ["<code>kubeadm certs check-expiration</code>", "The silent outage 30 days out"],
    ["<code>etcdctl endpoint status -w table</code>", "Quorum, leader and DB size"],
    ["<code>kubectl get apirequestcount</code>", "Who still calls an API about to be removed"],
    ["<code>kubectl get pdb -A</code>", "What will deadlock the next drain"],
    ["<code>kubectl drain &lt;n&gt; --ignore-daemonsets --delete-emptydir-data</code>", "Evacuate a node properly"],
    ["<code>kubectl get ns -o custom-columns=...enforce</code>", "Which namespaces enforce Pod Security"],
    ["<code>kubectl get networkpolicy -A</code>", "Which namespaces are actually isolated"],
    ["<code>velero backup get</code>", "Whether the backup ran, and when it last succeeded"],
    ["<code>velero restore create --from-backup &lt;b&gt;</code>", "Bring a namespace back"],
    ["<code>kubectl version -o json | jq .serverVersion</code>", "Where this cluster sits in the skew"],
    ["<code>kubectl get nodes -o wide</code>", "kubelet and runtime versions per node"],
    ["<code>kubectl diff -f manifests/</code>", "Drift between git and the cluster"],
], "mono")

KUBERNETES_CLUSTER_OPS = dict(
    slug="kubernetes-cluster-operations",
    title="Kubernetes Cluster Operations",
    tagline=("Pod Security rolled out with warn before enforce, the removed API that takes "
             "workloads with it on upgrade, the difference between an etcd snapshot and a real "
             "backup, and the three cluster failures that are silent until they are outages."),
    eyebrow="Kubernetes · Advanced",
    meta=["<b>28 min</b> read", "Level: <b>advanced</b>", "Kubernetes <b>05 / 05</b>"],
    sections=(
        section("The model", "THE LIFECYCLE OF A CLUSTER YOU OPERATE",
                "Harden, upgrade, drain, back up, spread — and prove the restore works before "
                "you need it to.",
                f'<div class="dg-scroll">{OPS_DIAGRAM}</div>'
                '<p class="dg-cap">PodDisruptionBudget appears in the drain row for a reason: '
                'the same object that protects availability is what stops an upgrade and what '
                'pins a node against scale-down.</p>')
        + section("Core", "SECURITY, UPGRADES, BACKUP AND FLEET",
                  "The four operational concerns that are nobody's feature work until the day "
                  "they are the incident.", OPS_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, OPS_TROUBLE)
        + section("Reference", "CHEATSHEET", None, OPS_CHEAT)
    ),
)

TOPICS = [KUBERNETES_SCHEDULING, KUBERNETES_AUTOSCALING, KUBERNETES_CLUSTER_OPS]
