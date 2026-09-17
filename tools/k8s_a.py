#!/usr/bin/env python3
"""Kubernetes content, batch A: Workloads (#061), Config & Access (#062).

Topics covered:
  #061  ReplicaSets, DaemonSets, Jobs / CronJobs, Probes
  #062  ConfigMaps, Secrets, Namespaces, RBAC
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
# TOOLS is the real tools/ directory — derived from this file's own
# location, never from ROOT. ROOT is the OUTPUT root (dist/) and source
# must never be looked up underneath it.
TOOLS = _pl.Path(__file__).resolve().parent

from content_page import card, term, table, note, diagram, section, refs

K8S = "https://kubernetes.io/docs/"

# ═══════════════════════════════════════════════════════════════════════════
# 01 · WORKLOADS
# ═══════════════════════════════════════════════════════════════════════════
WL_DIAGRAM = diagram([
    ("You apply", [("Deployment", "core"), ("DaemonSet", "core"),
                   ("Job / CronJob", "core"), ("StatefulSet", "core")]),
    ("Controller", [("deployment-controller", "warm"), ("daemonset-controller", "warm"),
                    ("job-controller", "warm"), ("cronjob-controller", "warm")]),
    ("Owns", [("ReplicaSet (one per revision)", "hot")]),
    ("Creates", [("Pod", "calm")]),
    ("Scheduled", [("kube-scheduler → node", "go")]),
    ("Run by", [("kubelet", "plain"), ("container runtime", "plain")]),
    ("Gated by", [("startupProbe", "plain"), ("readinessProbe → Endpoints", "plain"),
                  ("livenessProbe → restart", "plain")]),
], "You never create a Pod directly — you declare intent and a controller reconciles towards it")

WL_CORE = "".join([
 card(1, "ReplicaSets — the object you never write and always debug",
      "One per Deployment revision, and that is what makes rollbacks and stuck rollouts legible.",
      ["ReplicaSet", "revision", "rollout"], """
<p>You write a <code>Deployment</code>; the deployment controller creates a
<strong>ReplicaSet</strong> per revision and scales them against each other. The Deployment is
the rollout strategy. The ReplicaSet is the thing that actually keeps N pods alive.</p>
<p>That two-layer split is why <code>kubectl get rs</code> is one of the most informative
commands during a bad deploy. A rollout that is stuck shows it plainly: the new ReplicaSet has
desired=3 current=1 ready=0 while the old one still has 3 ready. The Deployment just says
"progressing".</p>
<h3>The bits that surprise people</h3>
<ul>
<li><strong>Old ReplicaSets are kept, scaled to zero.</strong> That is the rollback target.
<code>revisionHistoryLimit</code> (default 10) decides how many, and setting it to 0 means you
cannot <code>rollout undo</code> at all.</li>
<li><strong>The selector is immutable.</strong> Change <code>spec.selector</code> on a live
Deployment and the API rejects it — you delete and recreate, which is a real outage if you did
not plan it.</li>
<li><strong>Adoption is by label.</strong> A ReplicaSet adopts any matching pod without an
owner. Two controllers with overlapping selectors will fight over the same pods indefinitely.</li>
</ul>
""" + term("reading a stuck rollout properly", [
    ("$", "kubectl get rs -l app=api"),
    ("", "NAME             DESIRED   CURRENT   READY   AGE"),
    ("", "api-7d9f4b8c6d   3         1         0       6m      <- new, not coming up"),
    ("", "api-5c8a1f2e9b   3         3         3       9d      <- old, still serving"),
    ("#", "the Deployment alone would only say 'ReplicaSetUpdated'. The rs tells you"),
    ("#", "that one new pod was created and never became ready — so look at THAT pod:"),
    ("$", "kubectl describe pod -l pod-template-hash=7d9f4b8c6d | tail -20"),
    ("$", "kubectl rollout undo deploy/api --to-revision=2"),
]) + refs([
    ("ReplicaSet", K8S + "concepts/workloads/controllers/replicaset/",
     "The controller contract, adoption rules and why the selector is immutable."),
])),

 card(2, "DaemonSets — one per node, and the scheduling rules are different",
      "Node agents, tolerations, and the update strategy that will not roll itself.",
      ["DaemonSet", "tolerations", "node agent"], """
<p>A <code>DaemonSet</code> runs one pod per matching node, and adds one automatically when a
node joins. It is the shape for anything that is <em>about the node</em>: log collectors, CNI
agents, node exporters, storage drivers.</p>
<p>Two behaviours differ from every other workload:</p>
<ul>
<li><strong>It tolerates more by default.</strong> DaemonSet pods get tolerations for
<code>node.kubernetes.io/not-ready</code>, <code>unreachable</code>, <code>disk-pressure</code>
and others automatically — because a node agent that evacuates itself the moment the node is
unhealthy is useless precisely when you need it.</li>
<li><strong>It ignores <code>kubectl drain</code>.</strong> Drain skips DaemonSet pods, which
is why <code>--ignore-daemonsets</code> exists and why you pass it every time.</li>
</ul>
<h3>The update trap</h3>
<p><code>updateStrategy: OnDelete</code> means the DaemonSet will <strong>never</strong> roll a
new image — it waits for you to delete each pod by hand. It is a legitimate choice for a
storage driver you want to reboot deliberately, and a silent "our agent has been on the old
version for eight months" for everything else.</p>
""" + term("why the agent did not update", [
    ("$", "kubectl get ds -n monitoring node-exporter -o jsonpath='{.spec.updateStrategy.type}'"),
    ("", "OnDelete"),
    ("#", "there it is. RollingUpdate is what you almost always want:"),
    ("$", "kubectl patch ds node-exporter -n monitoring --type=merge \\"),
    ("", "  -p '{\"spec\":{\"updateStrategy\":{\"type\":\"RollingUpdate\","),
    ("", "       \"rollingUpdate\":{\"maxUnavailable\":1}}}}'"),
    ("$", "kubectl rollout status ds/node-exporter -n monitoring"),
    ("#", "and to confirm it is genuinely on every node it should be:"),
    ("$", "kubectl get ds -A -o custom-columns=\\"),
    ("", "  NS:.metadata.namespace,NAME:.metadata.name,DESIRED:.status.desiredNumberScheduled,READY:.status.numberReady"),
]) + refs([
    ("DaemonSet", K8S + "concepts/workloads/controllers/daemonset/",
     "Default tolerations, update strategies and how nodes are matched."),
])),

 card(3, "Jobs and CronJobs — the workload that is allowed to finish",
      "Completions, parallelism, backoff, and the concurrency policy that causes pile-ups.",
      ["Job", "CronJob", "backoffLimit"], """
<p>A <code>Job</code> runs pods until a target number <strong>succeed</strong>. A
<code>CronJob</code> creates Jobs on a schedule. Everything that goes wrong with them comes from
four fields.</p>
<table class="tbl"><thead><tr><th>Field</th><th>Means</th><th>Gets you when</th></tr></thead>
<tbody>
<tr><td><code>completions</code></td><td>How many successes end the Job</td><td>Unset = 1, so a "batch" silently processes once</td></tr>
<tr><td><code>parallelism</code></td><td>How many pods at once</td><td>Unset = 1; your 6-hour job could have been 20 minutes</td></tr>
<tr><td><code>backoffLimit</code></td><td>Retries before Failed</td><td>Default 6, with exponential backoff to 6 minutes — a fast-failing job takes ~20 min to give up</td></tr>
<tr><td><code>activeDeadlineSeconds</code></td><td>Wall-clock cap</td><td>Unset = a hung job runs forever, holding its resources</td></tr>
</tbody></table>
<h3>concurrencyPolicy is the CronJob field that causes incidents</h3>
<p>The default is <code>Allow</code>. If a run takes longer than the interval, the next one
starts anyway — and on a five-minute schedule with a run that has started taking eight minutes,
you accumulate overlapping jobs until something saturates. <code>Forbid</code> skips the new run;
<code>Replace</code> kills the old one. Both are usually more correct than the default.</p>
<p>Also: <code>startingDeadlineSeconds</code>. If the controller is down past that window the
run is <em>skipped</em>, not queued — and if it is unset and the controller was down a long
time, the CronJob can fire every missed run at once on recovery.</p>
""" + term("a CronJob that cannot pile up", [
    ("", "spec:"),
    ("", "  schedule: \"*/5 * * * *\""),
    ("", "  concurrencyPolicy: Forbid          # skip if the last one still runs"),
    ("", "  startingDeadlineSeconds: 120       # give up rather than stampede on recovery"),
    ("", "  successfulJobsHistoryLimit: 3      # default 3; 0 makes debugging impossible"),
    ("", "  failedJobsHistoryLimit: 3"),
    ("", "  jobTemplate:"),
    ("", "    spec:"),
    ("", "      activeDeadlineSeconds: 240     # hard stop, shorter than the interval"),
    ("", "      backoffLimit: 2"),
    ("#", "finding the pile-up you already have:"),
    ("$", "kubectl get jobs -A --sort-by=.metadata.creationTimestamp | tail -20"),
    ("$", "kubectl get jobs -A --field-selector status.successful=0"),
]) + refs([
    ("Job", K8S + "concepts/workloads/controllers/job/",
     "Completion modes, parallelism, backoff and the pod failure policy."),
    ("CronJob", K8S + "concepts/workloads/controllers/cron-jobs/",
     "Schedule syntax, concurrency policy and the missed-schedule rules."),
])),

 card(4, "Probes — three of them, and only one restarts anything",
      "The difference between 'not ready' and 'restart me' is the difference between a blip and an outage.",
      ["liveness", "readiness", "startup"], """
<p>Three probes, three jobs, and conflating them is the most common self-inflicted Kubernetes
outage there is:</p>
<table class="tbl"><thead><tr><th>Probe</th><th>On failure</th><th>Question it answers</th></tr></thead>
<tbody>
<tr><td><strong>startupProbe</strong></td><td>Keeps the others waiting</td><td>Has it finished booting?</td></tr>
<tr><td><strong>readinessProbe</strong></td><td>Removed from Endpoints</td><td>Should it get traffic right now?</td></tr>
<tr><td><strong>livenessProbe</strong></td><td><strong>Container is killed</strong></td><td>Is it wedged beyond recovery?</td></tr>
</tbody></table>
<h3>Why a liveness probe on a dependency is dangerous</h3>
<p>Point liveness at a <code>/health</code> that checks the database, and the moment the database
has a bad thirty seconds every replica fails liveness and gets killed — simultaneously. You have
converted a recoverable dependency blip into a full restart storm, and the restarts add load to
the thing that was already struggling.</p>
<p>The rule that avoids it: <strong>liveness checks only what a restart can fix.</strong> A
deadlocked event loop, yes. A database you do not own, never — that belongs in readiness, where
failing simply takes the pod out of rotation until the dependency returns.</p>
<h3>Slow starts belong in startupProbe, not in initialDelaySeconds</h3>
<p>A long <code>initialDelaySeconds</code> on liveness delays detection for the whole life of the
pod. A <code>startupProbe</code> with a generous <code>failureThreshold</code> gives a slow JVM
five minutes to boot and then hands over to a tight liveness probe.</p>
""" + term("probes that do not cause the outage they are meant to prevent", [
    ("", "startupProbe:                      # up to 5 min to boot, then get strict"),
    ("", "  httpGet: { path: /healthz, port: 8080 }"),
    ("", "  periodSeconds: 5"),
    ("", "  failureThreshold: 60"),
    ("", "readinessProbe:                    # dependencies live HERE"),
    ("", "  httpGet: { path: /ready, port: 8080 }"),
    ("", "  periodSeconds: 5"),
    ("", "  failureThreshold: 3"),
    ("", "livenessProbe:                     # process health ONLY"),
    ("", "  httpGet: { path: /healthz, port: 8080 }"),
    ("", "  periodSeconds: 10"),
    ("", "  failureThreshold: 3"),
    ("#", "is a restart loop actually a liveness kill? Exit 137 + this event = yes:"),
    ("$", "kubectl describe pod api-7d9f | grep -A2 'Liveness probe failed'"),
    ("$", "kubectl get pod api-7d9f -o jsonpath='{.status.containerStatuses[0].lastState.terminated.reason}'"),
]) + note("bad", "The restart-storm signature",
          "<p>Many replicas restarting within the same few seconds, all with "
          "<code>Liveness probe failed</code> and exit 137, while the application logs show "
          "nothing wrong — that is a dependency wobble being amplified by liveness. Move the "
          "dependency check to readiness before you tune any timeouts.</p>")
   + refs([
    ("Configure Liveness, Readiness and Startup Probes", K8S + "tasks/configure-pod-container/configure-liveness-readiness-startup-probes/",
     "Every probe field, the handler types, and the interaction between the three."),
    ("Pod Lifecycle", K8S + "concepts/workloads/pods/pod-lifecycle/",
     "Phases, conditions and where probe results actually land."),
])),
])

WL_TROUBLE = """
<p>Nearly every workload symptom is one of four states, and the state tells you which object to
look at. Guessing from the Deployment alone wastes the first ten minutes.</p>
""" + table(
    ["Pod state", "What it means", "Look at"],
    [["<code>Pending</code>", "Never scheduled — no node fits, or quota refused it",
      "<code>kubectl describe pod</code>, the Events tail names the failed predicate"],
     ["<code>ContainerCreating</code> &gt; 2 min", "Image pull, volume attach or CNI",
      "Events; then the node's kubelet log"],
     ["<code>CrashLoopBackOff</code>", "It starts and exits",
      "<code>kubectl logs -p</code> — the PREVIOUS container is the one that failed"],
     ["<code>Running</code> but <code>0/1</code>", "Readiness failing — no traffic reaches it",
      "<code>describe</code> for the probe message; the Service has no endpoint"],
     ["<code>Running</code>, restarts climbing", "Liveness killing it, or OOM",
      "<code>lastState.terminated.reason</code> — <code>Error</code> vs <code>OOMKilled</code>"],
     ["<code>Completed</code> but rerun", "A Job that succeeded and the CronJob fired again",
      "<code>concurrencyPolicy</code> and the job history"],
     ]) + """
<h3>The one command that answers most of it</h3>
""" + term("state, reason and exit code for everything unhealthy", [
    ("$", "kubectl get pods -A -o json | jq -r '.items[]"),
    ("", "  | select(.status.phase!=\"Running\" and .status.phase!=\"Succeeded\")"),
    ("", "  | \"\\(.metadata.namespace)/\\(.metadata.name)\\t\\(.status.phase)\"'"),
    ("#", "restart reasons across the cluster, which is where OOM hides:"),
    ("$", "kubectl get pods -A -o json | jq -r '.items[].status.containerStatuses[]?"),
    ("", "  | select(.restartCount>0)"),
    ("", "  | \"\\(.name)\\t\\(.restartCount)\\t\\(.lastState.terminated.reason // \"-\")\"'"),
    ("#", "events are the real story and they expire in an hour — grab them first:"),
    ("$", "kubectl get events -A --sort-by=.lastTimestamp | tail -40"),
]) + note("good", "logs -p is the whole trick for CrashLoopBackOff",
          "<p><code>kubectl logs</code> on a crash-looping pod shows the container that is "
          "starting <em>now</em> and usually prints nothing useful. <code>kubectl logs -p</code> "
          "shows the one that already died, which is the one holding the stack trace.</p>")

WL_CHEAT = table(["Command", "What it answers"], [
    ["<code>kubectl get rs -l app=&lt;x&gt;</code>", "Which revision is stuck, old versus new"],
    ["<code>kubectl rollout status deploy/&lt;x&gt; --timeout=5m</code>", "Block until it lands or fails"],
    ["<code>kubectl rollout history deploy/&lt;x&gt;</code>", "Revisions available to roll back to"],
    ["<code>kubectl rollout undo deploy/&lt;x&gt; --to-revision=N</code>", "Go back to a specific one"],
    ["<code>kubectl logs -p &lt;pod&gt;</code>", "The container that actually crashed"],
    ["<code>kubectl get pod &lt;p&gt; -o jsonpath='{.status.containerStatuses[0].lastState}'</code>", "Exit code and reason — Error vs OOMKilled"],
    ["<code>kubectl get ds -A</code>", "Desired versus ready, per node agent"],
    ["<code>kubectl get jobs -A --sort-by=.metadata.creationTimestamp</code>", "CronJob pile-ups"],
    ["<code>kubectl get cronjob -A</code>", "Schedules, last run and suspension"],
    ["<code>kubectl describe pod &lt;p&gt;</code>", "Scheduling, probe and image-pull failures"],
    ["<code>kubectl get events -A --sort-by=.lastTimestamp</code>", "What just happened — expires in an hour"],
    ["<code>kubectl debug &lt;pod&gt; -it --image=busybox --target=&lt;c&gt;</code>", "A shell beside a container with no shell"],
], "mono")

KUBERNETES_WORKLOADS = dict(
    slug="kubernetes-workloads",
    title="Kubernetes Workloads",
    tagline=("ReplicaSets and why a stuck rollout is legible, DaemonSets and the update "
             "strategy that silently never rolls, Jobs and CronJobs that pile up on their own "
             "schedule, and the liveness probe that turns a dependency blip into an outage."),
    eyebrow="Kubernetes · Core",
    meta=["<b>26 min</b> read", "Level: <b>core → advanced</b>", "Kubernetes <b>01 / 05</b>"],
    sections=(
        section("The model", "FROM INTENT TO A RUNNING CONTAINER",
                "You declare what you want; a chain of controllers argues reality towards it. "
                "Knowing which link owns what is most of debugging.",
                f'<div class="dg-scroll">{WL_DIAGRAM}</div>'
                '<p class="dg-cap">The probes at the bottom are not part of starting the pod — '
                'they decide, continuously, whether it gets traffic and whether it gets killed. '
                'That is why they cause outages disproportionate to their size.</p>')
        + section("Core", "THE FOUR WORKLOAD BEHAVIOURS",
                  "What each controller guarantees, and the field in each that causes the "
                  "incident.", WL_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, WL_TROUBLE)
        + section("Reference", "CHEATSHEET", None, WL_CHEAT)
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# 02 · CONFIG & ACCESS
# ═══════════════════════════════════════════════════════════════════════════
CFG_DIAGRAM = diagram([
    ("Identity", [("User / OIDC", "core"), ("ServiceAccount", "core"),
                  ("Group", "core")]),
    ("AuthN", [("Certificate / token / OIDC", "warm")]),
    ("AuthZ", [("RBAC: Role + RoleBinding", "hot"),
               ("ClusterRole + ClusterRoleBinding", "hot")]),
    ("Admission", [("Mutating webhooks", "calm"), ("Pod Security Admission", "calm"),
                   ("Validating webhooks", "calm"), ("ResourceQuota", "calm")]),
    ("Boundary", [("Namespace", "go")]),
    ("Config", [("ConfigMap", "plain"), ("Secret", "plain")]),
    ("Consumed as", [("env / envFrom", "plain"), ("volume mount", "plain"),
                     ("projected volume", "plain")]),
], "Four gates in order — and only the last two are namespaced, which is where most confusion starts")

CFG_CORE = "".join([
 card(1, "ConfigMaps — and why your pod did not pick up the change",
      "Mounted config updates itself; environment variables never do.",
      ["ConfigMap", "envFrom", "subPath"], """
<p>A <code>ConfigMap</code> is a key/value object consumed in one of two ways, and the two behave
completely differently at runtime:</p>
<table class="tbl"><thead><tr><th>Consumed as</th><th>On ConfigMap update</th></tr></thead>
<tbody>
<tr><td><code>env</code> / <code>envFrom</code></td><td><strong>Never changes.</strong> Environment is set once at container start.</td></tr>
<tr><td>Volume mount</td><td>Updated in place, typically within a minute (kubelet sync period).</td></tr>
<tr><td>Volume mount with <code>subPath</code></td><td><strong>Never changes.</strong> subPath breaks the symlink swap the update relies on.</td></tr>
</tbody></table>
<p>"We updated the ConfigMap and nothing happened" is almost always row 1 or row 3. Neither is a
bug; both are documented; both are invisible unless you know to look.</p>
<h3>Making a change actually roll</h3>
<p>If the app cannot reload config itself, the honest answer is to restart it — and the tidy way
is to put a hash of the config in the pod template annotation, so changing the ConfigMap changes
the Deployment and triggers a normal rolling update.</p>
""" + term("three ways to make config changes take effect", [
    ("#", "1. immediate, manual"),
    ("$", "kubectl rollout restart deploy/api"),
    ("#", "2. automatic — annotate the POD TEMPLATE with a hash of the config"),
    ("", "spec: { template: { metadata: { annotations: {"),
    ("", "  checksum/config: \"<sha256 of the configmap>\" } } } }"),
    ("#", "   changing the ConfigMap changes the hash, which changes the template,"),
    ("#", "   which is a new revision — a normal rolling update, no special tooling"),
    ("#", "3. confirm what the container currently sees, rather than assuming:"),
    ("$", "kubectl exec deploy/api -- cat /etc/app/config.yaml"),
    ("$", "kubectl exec deploy/api -- env | grep LOG_LEVEL"),
]) + refs([
    ("ConfigMap", K8S + "concepts/configuration/configmap/",
     "Consumption modes, immutability, and the subPath caveat spelled out."),
])),

 card(2, "Secrets — base64 is not encryption, and who can read them is the real question",
      "Encryption at rest, the ServiceAccount token that is no longer mounted forever, and RBAC as the actual control.",
      ["Secret", "encryption at rest", "etcd"], """
<p>A <code>Secret</code> is a ConfigMap with a different name and base64-encoded values.
<strong>base64 is encoding, not encryption</strong> — anyone who can read the object can read the
value, and by default the bytes sit in etcd in the clear.</p>
<p>Three things actually protect a Secret, and all three are opt-in:</p>
<ul>
<li><strong>Encryption at rest.</strong> An <code>EncryptionConfiguration</code> on the API
server encrypts Secrets before they reach etcd — ideally with a KMS provider rather than a local
key that sits next to the data it protects.</li>
<li><strong>RBAC.</strong> <code>get secrets</code> in a namespace means every secret in it.
There is no per-object RBAC in core Kubernetes, so "read one secret" is really "read them all"
unless you split namespaces.</li>
<li><strong>Not mounting them.</strong> Since v1.24, ServiceAccount tokens are short-lived
projected volumes rather than permanent Secret objects — a real improvement, and worth checking
you are not still creating long-lived token Secrets by hand.</li>
</ul>
<h3>The audit question you will eventually be asked</h3>
<p>"Who can read the database password?" is an RBAC query, not a Secret query — and it has a
precise answer.</p>
""" + term("answering 'who can read this' properly", [
    ("$", "kubectl auth can-i get secrets -n prod --as=system:serviceaccount:prod:api-sa"),
    ("#", "everyone with the verb, across all subjects:"),
    ("$", "kubectl get rolebindings,clusterrolebindings -A -o json | jq -r '.items[]"),
    ("", "  | select(.roleRef.name|test(\"admin|edit|secret\";\"i\"))"),
    ("", "  | \"\\(.kind)\\t\\(.metadata.namespace // \"-\")/\\(.metadata.name)\\t-> \\(.roleRef.name)\"'"),
    ("#", "is encryption at rest actually on? read a raw value straight out of etcd:"),
    ("$", "kubectl -n kube-system exec etcd-master-0 -- etcdctl \\"),
    ("", "  get /registry/secrets/prod/db-creds | hexdump -C | head -3"),
    ("#", "plaintext you can read = not encrypted. 'k8s:enc:' prefix = encrypted."),
]) + note("warn", "A Secret in git is a Secret in git",
          "<p>Sealed Secrets, SOPS or an external store (Vault, a cloud secret manager via the "
          "Secrets Store CSI driver) all solve this. Base64 in a committed manifest solves "
          "nothing — it is a rendering choice, not a security boundary, and the repo history "
          "keeps it after you delete the file.</p>")
   + refs([
    ("Secrets", K8S + "concepts/configuration/secret/",
     "Types, projected ServiceAccount tokens, and the explicit note that Secrets are not encrypted by default."),
    ("Encrypting Confidential Data at Rest", K8S + "tasks/administer-cluster/encrypt-data/",
     "EncryptionConfiguration, providers, and rotating the key without downtime."),
])),

 card(3, "Namespaces — a boundary for names and quota, not for security",
      "What a namespace actually isolates, and the four things it does not.",
      ["Namespace", "quota", "isolation"], """
<p>A namespace scopes <strong>names</strong>, and gives you something to attach RBAC,
<code>ResourceQuota</code> and <code>LimitRange</code> to. That is genuinely useful, and it is
also the whole list.</p>
<p>What a namespace does <strong>not</strong> isolate, and each has bitten someone:</p>
<ul>
<li><strong>The network.</strong> Every pod can reach every other pod in every namespace until a
NetworkPolicy says otherwise.</li>
<li><strong>Nodes.</strong> Pods from different namespaces share hardware, page cache and
kernel.</li>
<li><strong>Cluster-scoped objects.</strong> Nodes, PersistentVolumes, StorageClasses, CRDs and
ClusterRoles belong to nobody's namespace.</li>
<li><strong>Resources, unless you say so.</strong> Without a ResourceQuota one namespace can
consume the whole cluster.</li>
</ul>
<p>So "we put the untrusted tenant in its own namespace" is not a security statement by itself.
It becomes one when you add a default-deny NetworkPolicy, a quota, a restricted Pod Security
Admission level and — for genuinely untrusted workloads — separate nodes or a separate cluster.</p>
""" + term("a namespace that actually holds a boundary", [
    ("#", "1. quota, so it cannot eat the cluster"),
    ("$", "kubectl create quota team-a --hard=cpu=20,memory=64Gi,pods=100 -n team-a"),
    ("#", "2. defaults, so pods without requests do not get unlimited"),
    ("$", "kubectl apply -n team-a -f limitrange.yaml"),
    ("#", "3. Pod Security Admission — one label, enforced at admission"),
    ("$", "kubectl label ns team-a \\"),
    ("", "  pod-security.kubernetes.io/enforce=restricted \\"),
    ("", "  pod-security.kubernetes.io/warn=restricted"),
    ("#", "4. default-deny ingress, then re-allow what is needed"),
    ("$", "kubectl apply -n team-a -f default-deny.yaml"),
    ("#", "and check what is actually enforced rather than what you intended:"),
    ("$", "kubectl get ns team-a -o jsonpath='{.metadata.labels}' | jq"),
    ("$", "kubectl describe quota -n team-a"),
]) + refs([
    ("Namespaces", K8S + "concepts/overview/working-with-objects/namespaces/",
     "Scope, DNS implications and which resources are not namespaced."),
    ("Resource Quotas", K8S + "concepts/policy/resource-quotas/",
     "Every quotable resource, and how quota interacts with requests and limits."),
])),

 card(4, "RBAC — four objects, and one rule that explains every surprise",
      "Permissions are purely additive. There is no deny, so nothing you add can ever be revoked by another rule.",
      ["RBAC", "Role", "ClusterRole", "binding"], """
<p>Four objects, two axes. <code>Role</code> and <code>RoleBinding</code> are namespaced;
<code>ClusterRole</code> and <code>ClusterRoleBinding</code> are not:</p>
<table class="tbl"><thead><tr><th>Combination</th><th>Grants</th></tr></thead>
<tbody>
<tr><td>Role + RoleBinding</td><td>Those verbs in that one namespace</td></tr>
<tr><td><strong>ClusterRole + RoleBinding</strong></td><td>The ClusterRole's verbs, but only in the binding's namespace — the useful one people forget</td></tr>
<tr><td>ClusterRole + ClusterRoleBinding</td><td>Every namespace, plus cluster-scoped resources</td></tr>
<tr><td>Role + ClusterRoleBinding</td><td><strong>Invalid.</strong> Silently grants nothing.</td></tr>
</tbody></table>
<h3>The rule that explains the surprises</h3>
<p><strong>RBAC is purely additive and has no deny.</strong> Effective permission is the union of
every binding that matches you. So you cannot subtract a permission with another rule — you have
to find and remove the binding that granted it. And a user in three groups has all three groups'
permissions, which is why "I thought we removed their access" is usually a second binding nobody
looked for.</p>
<h3>Escalation paths that do not look like admin</h3>
<p>Several innocuous-looking verbs are effectively cluster-admin:
<code>create pods</code> (mount any secret, or a hostPath),
<code>escalate</code>/<code>bind</code> (grant yourself more),
<code>impersonate</code> (become anyone), and
<code>get secrets</code> where a privileged ServiceAccount token lives.</p>
""" + term("stop reading bindings and ask the API", [
    ("$", "kubectl auth can-i --list -n prod --as=jane"),
    ("$", "kubectl auth can-i create pods -n prod --as=jane"),
    ("#", "the service-account form, which is where this usually matters:"),
    ("$", "kubectl auth can-i list secrets -A \\"),
    ("", "  --as=system:serviceaccount:prod:api-sa"),
    ("#", "every binding that mentions a subject — the 'second binding' problem:"),
    ("$", "kubectl get rolebindings,clusterrolebindings -A -o json \\"),
    ("", "  | jq -r --arg who jane '.items[] | select(.subjects[]?.name==$who)"),
    ("", "    | \"\\(.kind) \\(.metadata.namespace // \"cluster\")/\\(.metadata.name) -> \\(.roleRef.name)\"'"),
    ("#", "who holds cluster-admin, which should be a very short list:"),
    ("$", "kubectl get clusterrolebindings -o json | jq -r '.items[]"),
    ("", "  | select(.roleRef.name==\"cluster-admin\") | .subjects[]?.name'"),
]) + refs([
    ("Using RBAC Authorization", K8S + "reference/access-authn-authz/rbac/",
     "The full object model, aggregation, and the default ClusterRoles the cluster ships with."),
    ("RBAC Good Practices", K8S + "concepts/security/rbac-good-practices/",
     "The escalation paths above, from upstream, with the reasoning for each."),
])),
])

CFG_TROUBLE = """
<p>Access failures and config failures look identical from the outside — the pod does not work —
and are diagnosed completely differently. The refusal wording tells you which gate said no.</p>
""" + table(
    ["What you see", "Which gate", "Next command"],
    [["<code>Unauthorized</code> / 401", "Authentication — the identity did not resolve",
      "<code>kubectl auth whoami</code>; check the kubeconfig context"],
     ["<code>Forbidden: User \"x\" cannot &lt;verb&gt;</code>", "RBAC",
      "<code>kubectl auth can-i --list --as=x</code>"],
     ["<code>violates PodSecurity \"restricted\"</code>", "Pod Security Admission",
      "<code>kubectl get ns &lt;n&gt; -o jsonpath='{.metadata.labels}'</code>"],
     ["<code>exceeded quota</code>", "ResourceQuota",
      "<code>kubectl describe quota -n &lt;n&gt;</code>"],
     ["<code>admission webhook ... denied</code>", "A validating webhook",
      "<code>kubectl get validatingwebhookconfigurations</code>"],
     ["Pod runs, config is stale", "env vars or a subPath mount",
      "<code>kubectl exec -- env</code>; then the volume's <code>subPath</code>"],
     ["<code>CreateContainerConfigError</code>", "A referenced ConfigMap or Secret is missing",
      "<code>kubectl describe pod</code> names the key it could not find"],
     ]) + """
<h3>The webhook that takes the cluster down with it</h3>
<p>A validating or mutating webhook with <code>failurePolicy: Fail</code> whose backing service
is unavailable rejects <em>every</em> matching API write. If its own namespace is in scope, you
cannot deploy the fix — including the webhook itself. This is a genuine "cannot deploy anything"
outage and the escape is to delete the webhook configuration.</p>
""" + term("when the cluster refuses every write", [
    ("$", "kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations"),
    ("$", "kubectl get validatingwebhookconfiguration <name> -o json \\"),
    ("", "  | jq '.webhooks[] | {name, failurePolicy, namespaceSelector}'"),
    ("#", "if the backing service is down and failurePolicy is Fail, remove the config."),
    ("#", "back it up first — this IS the emergency brake, not a fix:"),
    ("$", "kubectl get validatingwebhookconfiguration <name> -o yaml > /tmp/whc.yaml"),
    ("$", "kubectl delete validatingwebhookconfiguration <name>"),
]) + note("good", "auth can-i --as is the whole debugging story for RBAC",
          "<p>Reading Roles and bindings by hand gets the answer wrong, because effective "
          "permission is the union of every matching binding including ones granted through "
          "groups. <code>kubectl auth can-i --list --as=&lt;subject&gt;</code> asks the API "
          "server to do the resolution it will actually do.</p>")

CFG_CHEAT = table(["Command", "What it answers"], [
    ["<code>kubectl auth can-i --list -n &lt;ns&gt; --as=&lt;user&gt;</code>", "Effective permissions, resolved by the API server"],
    ["<code>kubectl auth can-i &lt;verb&gt; &lt;res&gt; --as=system:serviceaccount:&lt;ns&gt;:&lt;sa&gt;</code>", "The service-account form"],
    ["<code>kubectl auth whoami</code>", "Which identity this kubeconfig presents"],
    ["<code>kubectl get clusterrolebindings -o json | jq ... cluster-admin</code>", "Who holds the keys"],
    ["<code>kubectl describe quota -n &lt;ns&gt;</code>", "Used versus hard, per resource"],
    ["<code>kubectl get ns &lt;n&gt; -o jsonpath='{.metadata.labels}'</code>", "Which Pod Security level is enforced"],
    ["<code>kubectl exec deploy/&lt;x&gt; -- env</code>", "What the container actually received"],
    ["<code>kubectl get cm,secret -n &lt;ns&gt;</code>", "What exists to be referenced"],
    ["<code>kubectl create secret generic x --from-literal=k=v --dry-run=client -o yaml</code>", "Generate without applying"],
    ["<code>kubectl get validatingwebhookconfigurations</code>", "What can reject your writes"],
    ["<code>kubectl rollout restart deploy/&lt;x&gt;</code>", "Pick up changed env-var config"],
], "mono")

KUBERNETES_CONFIG_ACCESS = dict(
    slug="kubernetes-config-and-access",
    title="Kubernetes Config & Access",
    tagline=("ConfigMaps that update in place except when they do not, Secrets that are encoded "
             "rather than encrypted, namespaces that isolate less than people assume, and RBAC's "
             "one rule — purely additive, no deny — that explains every access surprise."),
    eyebrow="Kubernetes · Core",
    meta=["<b>27 min</b> read", "Level: <b>core → advanced</b>", "Kubernetes <b>02 / 05</b>"],
    sections=(
        section("The model", "FOUR GATES BETWEEN A REQUEST AND A RUNNING POD",
                "Authentication, authorisation, admission, then quota — in that order, each "
                "refusing in its own words.",
                f'<div class="dg-scroll">{CFG_DIAGRAM}</div>'
                '<p class="dg-cap">Only the bottom half is namespaced. ClusterRoles, nodes and '
                'PersistentVolumes sit outside any namespace, which is the source of most '
                '"but I gave them access" confusion.</p>')
        + section("Core", "CONFIG, SECRETS, BOUNDARIES AND PERMISSIONS",
                  "The four objects every cluster uses, and the property of each that is not "
                  "what people assume.", CFG_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, CFG_TROUBLE)
        + section("Reference", "CHEATSHEET", None, CFG_CHEAT)
    ),
)

TOPICS = [KUBERNETES_WORKLOADS, KUBERNETES_CONFIG_ACCESS]
