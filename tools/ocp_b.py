#!/usr/bin/env python3
"""OpenShift content, batch B: Networking & Storage (issue #059).

Covers three taxonomy topics: Routes, OpenShift Networking, OpenShift Storage.
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section

# ═══════════════════════════════════════════════════════════════════════════
# 02 · OPENSHIFT NETWORKING & STORAGE
# ═══════════════════════════════════════════════════════════════════════════
NET_DIAGRAM = diagram([
    ("Client", [("Browser / API client", "core")]),
    ("DNS", [("*.apps.<cluster>.<domain>", "core")]),
    ("Edge", [("Load balancer / VIP", "warm")]),
    ("Ingress", [("Router pods (HAProxy)", "hot"), ("Route object", "hot"),
                 ("TLS termination", "hot")]),
    ("Service", [("ClusterIP", "calm"), ("EndpointSlice", "calm")]),
    ("Overlay", [("OVN-Kubernetes", "go"), ("Geneve tunnel", "go"),
                 ("NetworkPolicy / ACL", "go")]),
    ("Node", [("br-int (OVS)", "plain"), ("veth pair", "plain")]),
    ("Pod", [("Container netns", "plain"), ("eth0", "plain")]),
], "A request crosses eight layers; the one that dropped it is almost never the one you suspect")

STO_DIAGRAM = diagram([
    ("Workload", [("Pod", "core"), ("StatefulSet volumeClaimTemplate", "core")]),
    ("Claim", [("PersistentVolumeClaim", "warm")]),
    ("Policy", [("StorageClass", "hot"), ("reclaimPolicy", "hot"),
                ("volumeBindingMode", "hot"), ("allowVolumeExpansion", "hot")]),
    ("Control", [("external-provisioner", "calm"), ("external-attacher", "calm"),
                 ("external-resizer", "calm")]),
    ("Driver", [("CSI driver (controller)", "go"), ("CSI driver (node)", "go")]),
    ("Volume", [("PersistentVolume", "plain")]),
    ("Backend", [("Ceph / NetApp / EBS / vSphere", "plain")]),
], "Every PVC failure is one of these arrows not completing — and each arrow logs in a different place")

NET_CORE = "".join([
 card(1, "Routes — the object that predates Ingress",
      "What a Route does that an Ingress does not, and the four TLS modes.",
      ["Route", "HAProxy", "TLS"], """
<p>A <code>Route</code> is OpenShift's ingress object. It predates the Kubernetes
<code>Ingress</code> API, and OpenShift supports both — an Ingress is silently converted into
a Route by the ingress operator, which is worth knowing because the object you debug is the
Route even when the object you created was an Ingress.</p>
<p>What a Route gives you that plain Ingress does not: <strong>per-route TLS policy</strong>,
weighted backends for canary splits, and configuration knobs (timeouts, balance algorithm,
rate limits) as annotations that the router actually honours.</p>
<h3>The four TLS modes, and which one you want</h3>
<table class="tbl"><thead><tr><th>Mode</th><th>Router does</th><th>Pod receives</th><th>Use when</th></tr></thead>
<tbody>
<tr><td><strong>edge</strong></td><td>Terminates TLS</td><td>Plain HTTP</td><td>Default. Traffic inside the cluster is on the overlay.</td></tr>
<tr><td><strong>passthrough</strong></td><td>Forwards bytes, does not decrypt</td><td>TLS</td><td>The app must see the client cert (mTLS), or does its own TLS.</td></tr>
<tr><td><strong>reencrypt</strong></td><td>Terminates, then opens a new TLS connection</td><td>TLS</td><td>You need the router's cert externally and encryption internally.</td></tr>
<tr><td><strong>none</strong></td><td>Plain HTTP end to end</td><td>HTTP</td><td>Essentially never in production.</td></tr>
</tbody></table>
<p><strong>passthrough cannot do path-based routing.</strong> The router never decrypts, so it
cannot read the path — it routes on SNI alone. A passthrough Route with a <code>path:</code>
set is a configuration that silently does not do what it says.</p>
""" + term("what the router actually did with your route", [
    ("$", "oc get route app -o jsonpath='{.status.ingress[*].conditions[*]}' | jq"),
    ("", "{ \"type\": \"Admitted\", \"status\": \"False\","),
    ("", "  \"reason\": \"HostAlreadyClaimed\","),
    ("", "  \"message\": \"route app already exposes app.apps.ocp.example.com and is older\" }"),
    ("#", "Admitted=False is the single most useful field on a Route. A route that is not"),
    ("#", "admitted returns 503 from the router and looks exactly like a broken backend."),
    ("$", "oc -n openshift-ingress rsh deploy/router-default cat haproxy.config | grep -A6 app"),
])),

 card(2, "The cluster network — OVN-Kubernetes end to end",
      "Overlay, node subnets, and why the packet is fine until it is not.",
      ["OVN", "Geneve", "CNI"], """
<p>OVN-Kubernetes is the default CNI on modern OpenShift. Each node gets a slice of the cluster
CIDR; pods get an address from their node's slice; traffic between nodes is encapsulated in
<strong>Geneve</strong> over the node network.</p>
<p>Three consequences that matter operationally:</p>
<ul>
<li><strong>MTU is not negotiable.</strong> Geneve adds ~100 bytes of header. If the node
network MTU is 1500, the pod MTU must be ~1400. Get this wrong and small packets work
perfectly while large ones vanish — which presents as "TLS handshakes fine, large responses
hang", the single most misdiagnosed cluster networking fault there is.</li>
<li><strong>NetworkPolicy is enforced in OVS flows</strong>, not iptables. <code>iptables -L</code>
on the node tells you nothing about why a pod was blocked.</li>
<li><strong>The cluster CIDR cannot be changed after install.</strong> Sizing it too small is
permanent; the node subnet size caps pods per node.</li>
</ul>
""" + term("the MTU check that resolves the 'large responses hang' incident", [
    ("$", "oc get network.operator cluster -o jsonpath='{.spec.defaultNetwork.ovnKubernetesConfig.mtu}'"),
    ("", "1400"),
    ("$", "oc debug node/worker-01 -- chroot /host ip link show br-ex | grep mtu"),
    ("", "3: br-ex: <BROADCAST,MULTICAST,UP> mtu 1500"),
    ("#", "1500 - 100 (Geneve) = 1400. Correct here. If the underlay is 1450, it is not."),
    ("#", "prove it from inside a pod — DF set, so it fails rather than fragmenting:"),
    ("$", "oc rsh deploy/app ping -M do -s 1372 10.128.4.9"),
    ("", "PING 10.128.4.9 1372(1400) bytes of data."),
    ("", "1380 bytes from 10.128.4.9: icmp_seq=1 ttl=64 time=0.31 ms"),
    ("$", "oc rsh deploy/app ping -M do -s 1400 10.128.4.9"),
    ("", "ping: local error: message too long, mtu=1400   <- the ceiling, confirmed"),
])),

 card(3, "Services, EndpointSlices and DNS",
      "Where traffic is actually lost between a Service and a Pod.",
      ["Service", "EndpointSlice", "readiness"], """
<p>A Service is a stable name and VIP; the real destination list is the
<code>EndpointSlice</code>. An endpoint appears there only when the pod is <strong>Ready</strong>.
So the single most common "the service returns 503" cause is not networking at all — it is a
readiness probe failing, which silently empties the slice.</p>
<p>Cluster DNS is CoreDNS, and names resolve as
<code>&lt;service&gt;.&lt;namespace&gt;.svc.cluster.local</code>. Short names work inside the
same namespace through the search path — which is also why a pod resolving
<code>db</code> in the wrong namespace gets a confusing answer rather than an error.</p>
""" + term("service returning 503 — three commands, in this order", [
    ("$", "oc get endpointslice -l kubernetes.io/service-name=api"),
    ("", "NAME        ADDRESSTYPE   PORTS   ENDPOINTS   AGE"),
    ("", "api-x7k2n   IPv4          8080    <unset>     4d"),
    ("#", "empty ENDPOINTS = no Ready pod. This is a probe problem, not a network problem."),
    ("$", "oc get pods -l app=api -o wide"),
    ("", "NAME          READY   STATUS    RESTARTS"),
    ("", "api-7d9f-x2   0/1     Running   0          <- Running but not Ready"),
    ("$", "oc describe pod api-7d9f-x2 | grep -A3 Readiness"),
    ("", "Readiness probe failed: HTTP probe failed with statuscode: 500"),
])),

 card(4, "NetworkPolicy — default-allow is the real default",
      "Nothing is isolated until one policy selects a pod, and then everything is.",
      ["NetworkPolicy", "isolation", "default-deny"], """
<p>An empty cluster allows every pod to reach every other pod, in every namespace. NetworkPolicy
is <strong>additive allow-listing with an unusual trigger</strong>: a pod is unrestricted until
at least one policy selects it, and from that moment only traffic explicitly allowed by some
policy reaches it.</p>
<p>That produces the classic self-inflicted outage. You add one policy allowing frontend →
backend. The backend is now isolated, so its <em>egress to the database</em> — never mentioned
in the policy — is unaffected (egress is a separate policyType) but the <em>monitoring
scrape</em> from the openshift-monitoring namespace is now blocked, and your dashboards go
blank without a single error.</p>
""" + term("a default-deny baseline that does not break the platform", [
    ("#", "1. deny everything into this namespace"),
    ("", "kind: NetworkPolicy"),
    ("", "spec: { podSelector: {}, policyTypes: [Ingress] }"),
    ("#", "2. re-allow same-namespace traffic"),
    ("", "spec: { podSelector: {}, ingress: [{ from: [{ podSelector: {} }] }] }"),
    ("#", "3. re-allow the router, or every Route in this namespace 503s"),
    ("", "  from: [{ namespaceSelector: { matchLabels:"),
    ("", "    { policy-group.network.openshift.io/ingress: \"\" } } }]"),
    ("#", "4. re-allow monitoring, or the namespace disappears from Prometheus"),
    ("", "  from: [{ namespaceSelector: { matchLabels:"),
    ("", "    { network.openshift.io/policy-group: monitoring } } }]"),
]) + note("warn", "Test the policy against the platform, not just your app",
          "<p>Router, monitoring, and the DNS namespace all need explicit allowances once a "
          "namespace is isolated. The failure is silent in each case: a 503 from the router, "
          "a gap in Prometheus, and a DNS timeout that looks like a slow dependency.</p>")),
])

NET_ADV = "".join([
 card(5, "Storage classes and the binding mode that causes stuck pods",
      "WaitForFirstConsumer exists for a reason, and Immediate will bite you in a multi-AZ cluster.",
      ["StorageClass", "topology", "binding"], """
<p>A <code>StorageClass</code> is the policy: which provisioner, what parameters, what happens
to the volume when the claim is deleted, and — critically — <strong>when</strong> the volume
gets created.</p>
<table class="tbl"><thead><tr><th>volumeBindingMode</th><th>Volume is created</th><th>Failure mode</th></tr></thead>
<tbody>
<tr><td><code>Immediate</code></td><td>As soon as the PVC exists</td><td>Volume lands in AZ-a, pod is later scheduled to AZ-b, pod is Pending forever</td></tr>
<tr><td><code>WaitForFirstConsumer</code></td><td>Once a pod using it is scheduled</td><td>PVC sits Pending until a pod appears — which looks broken but is correct</td></tr>
</tbody></table>
<p>On any cluster whose nodes span failure domains, <code>WaitForFirstConsumer</code> is the
right default and <code>Immediate</code> is a latent scheduling bug.</p>
<p>Two other fields decide whether you can recover later, and neither can be changed on an
existing volume: <code>reclaimPolicy</code> (<code>Delete</code> destroys the backend volume
when the PVC goes; <code>Retain</code> keeps it) and <code>allowVolumeExpansion</code>
(false means you can never grow it without a migration).</p>
""" + term("the Pending PVC decision tree", [
    ("$", "oc get pvc data-0"),
    ("", "NAME     STATUS    VOLUME   CAPACITY   STORAGECLASS   AGE"),
    ("", "data-0   Pending                       gp3-csi        11m"),
    ("$", "oc describe pvc data-0 | tail -5"),
    ("", "Normal  WaitForFirstConsumer  waiting for first consumer to be created"),
    ("#", "^ correct and healthy. The pod has not been scheduled yet — look at the POD."),
    ("", "Warning  ProvisioningFailed   failed to provision volume: rpc error:"),
    ("", "  code = ResourceExhausted desc = volume quota exceeded"),
    ("#", "^ a real failure, and the message comes from the BACKEND, not Kubernetes"),
])),

 card(6, "Access modes, and the one that does not mean what people think",
      "RWO is per-node, not per-pod — and that changes how rolling updates behave.",
      ["RWO", "RWX", "ReadWriteOncePod"], """
<p>Access modes are a contract the <em>driver</em> enforces, not a lock Kubernetes applies:</p>
<ul>
<li><strong>ReadWriteOnce (RWO)</strong> — mountable read-write by <strong>one node</strong>.
Several pods on that same node can share it. This surprises people in both directions: they
expect exclusivity and do not get it, or they expect to scale to 2 replicas and the second pod
hangs in <code>ContainerCreating</code> because it landed elsewhere.</li>
<li><strong>ReadWriteOncePod (RWOP)</strong> — genuinely one pod. This is the one people
usually meant.</li>
<li><strong>ReadWriteMany (RWX)</strong> — many nodes at once. Needs a filesystem that supports
it (CephFS, NFS, Azure Files). Most block drivers cannot do it at all.</li>
<li><strong>ReadOnlyMany (ROX)</strong> — many nodes, read-only.</li>
</ul>
<h3>Why your Deployment rollout hangs on RWO</h3>
<p>A <code>Deployment</code> with the default <code>RollingUpdate</code> strategy starts the new
pod <em>before</em> terminating the old one. With an RWO volume and the new pod on a different
node, the new pod cannot attach until the old one releases — and the old one will not terminate
until the new one is ready. It deadlocks until the progress deadline expires.</p>
""" + term("recognising the RWO rollout deadlock", [
    ("$", "oc get pods -l app=db"),
    ("", "db-6f8-old   1/1   Running             0    9d"),
    ("", "db-7a1-new   0/1   ContainerCreating   0    6m"),
    ("$", "oc describe pod db-7a1-new | tail -3"),
    ("", "Warning  FailedAttachVolume  Multi-Attach error for volume \"pvc-3c80d\":"),
    ("", "  Volume is already exclusively attached to one node and can't be attached to another"),
    ("#", "Fix: strategy Recreate for single-writer workloads, or a StatefulSet."),
    ("", "spec: { strategy: { type: Recreate } }"),
])),

 card(7, "CSI — where a storage failure actually logs",
      "Three controllers, two places, and none of them is the kubelet.",
      ["CSI", "attacher", "provisioner"], """
<p>CSI splits the work across sidecars, and each one fails in its own log. Knowing which is
which turns a storage incident from an afternoon into ten minutes:</p>
<table class="tbl"><thead><tr><th>Stage</th><th>Component</th><th>Runs on</th><th>Symptom when it fails</th></tr></thead>
<tbody>
<tr><td>Create volume</td><td><code>external-provisioner</code></td><td>Controller pod</td><td>PVC stays Pending, <code>ProvisioningFailed</code> event</td></tr>
<tr><td>Attach to node</td><td><code>external-attacher</code></td><td>Controller pod</td><td>Pod stuck ContainerCreating, <code>FailedAttachVolume</code></td></tr>
<tr><td>Mount into pod</td><td>CSI node plugin</td><td>DaemonSet on the node</td><td><code>FailedMount</code>, timeout after 2 minutes</td></tr>
<tr><td>Grow volume</td><td><code>external-resizer</code></td><td>Controller pod</td><td>PVC capacity never changes, no error on the PVC</td></tr>
</tbody></table>
<p>The pattern to internalise: <strong>provisioning and attaching are cluster-level, mounting is
node-level.</strong> A FailedMount is a node problem — go to that node. A ProvisioningFailed is
a backend problem — go to the controller and then to the storage system itself.</p>
""" + term("following a stuck volume through the layers", [
    ("$", "oc get volumeattachment | grep pvc-3c80d"),
    ("", "csi-9f2...  ebs.csi.aws.com  pvc-3c80d  worker-04  false"),
    ("#", "ATTACHED=false and it has been minutes -> attacher, not the node"),
    ("$", "oc logs -n openshift-cluster-csi-drivers deploy/aws-ebs-csi-driver-controller \\"),
    ("", "  -c csi-attacher --tail=40 | grep pvc-3c80d"),
    ("#", "if attachment IS true but the pod still will not start, it is the node plugin:"),
    ("$", "oc logs -n openshift-cluster-csi-drivers ds/aws-ebs-csi-driver-node \\"),
    ("", "  --field-selector spec.nodeName=worker-04 -c csi-driver --tail=40"),
])),

 card(8, "Expanding, migrating and the reclaim policy you set once",
      "Growing a volume is online and easy; shrinking is impossible; Delete is forever.",
      ["expansion", "reclaimPolicy", "migration"], """
<p><strong>Expansion</strong> works if <code>allowVolumeExpansion: true</code> was on the
StorageClass at creation time. Edit the PVC's requested size and the resizer grows the backend
volume, then the filesystem — online, for most drivers. Some need a pod restart to finish the
filesystem step, which shows as capacity updated on the PV but not inside the container.</p>
<p><strong>Shrinking is not supported.</strong> Not by Kubernetes, not by any CSI driver. The
only route is create-new, copy, swap.</p>
<p><strong>reclaimPolicy</strong> is the one that ends careers. With <code>Delete</code>, removing
a PVC destroys the backing volume immediately and irreversibly — including when the PVC is
removed as a side effect of deleting a namespace or a Helm release. With <code>Retain</code>,
the PV survives in <code>Released</code> state holding the data, and you can rebind it.</p>
""" + term("rebinding a Retained volume to a new claim", [
    ("$", "oc get pv | grep Released"),
    ("", "pvc-3c80d   50Gi   RWO   Retain   Released   prod/data-0   gp3-csi"),
    ("#", "claimRef still points at the deleted PVC — that is what blocks rebinding"),
    ("$", "oc patch pv pvc-3c80d --type=json \\"),
    ("", "  -p '[{\"op\":\"remove\",\"path\":\"/spec/claimRef\"}]'"),
    ("#", "PV goes Available; a new PVC with matching size and class will bind to it"),
]) + note("bad", "Check reclaimPolicy before you delete a namespace",
          "<p><code>oc delete project</code> deletes the PVCs in it. On a Delete-policy class "
          "that is an irreversible data loss with no confirmation prompt and no undo. For any "
          "class holding real data, set <code>Retain</code> — the cost is orphaned volumes you "
          "clean up deliberately, which is a much better problem.</p>")),
])

NET_TROUBLE = """
<p>Networking and storage failures both present as "the pod is not working", and both have a
layered path where the failing layer is rarely the one the symptom points at. Walk the path.</p>
<h3>A request that does not arrive</h3>
""" + table(
    ["Test", "Command", "If this works, the fault is above"],
    [["Is the Route admitted?", "<code>oc get route app -o yaml | grep -A4 conditions</code>", "DNS or the load balancer"],
     ["Does the router know about it?", "<code>oc -n openshift-ingress rsh deploy/router-default cat haproxy.config | grep app</code>", "The Route object"],
     ["Does the Service have endpoints?", "<code>oc get endpointslice -l kubernetes.io/service-name=app</code>", "The router"],
     ["Is the pod Ready?", "<code>oc get pod -l app=app</code>", "The Service selector"],
     ["Does the pod answer directly?", "<code>oc rsh deploy/app curl -s localhost:8080/health</code>", "The readiness probe"],
     ["Does another pod reach it?", "<code>oc run t --rm -it --image=curlimages/curl -- curl app.ns.svc:8080</code>", "NetworkPolicy or DNS"],
     ]) + """
<h3>A volume that does not mount</h3>
""" + table(
    ["Event on the pod", "Layer", "Go to"],
    [["<code>WaitForFirstConsumer</code>", "Normal — not a failure", "The pod's scheduling, not the PVC"],
     ["<code>ProvisioningFailed</code>", "Backend refused to create it", "external-provisioner logs, then the storage system"],
     ["<code>FailedAttachVolume</code> / Multi-Attach", "Still attached elsewhere", "<code>oc get volumeattachment</code>; likely an RWO rollout"],
     ["<code>FailedMount</code> after ~2 min", "Node-level mount", "CSI node DaemonSet on that node"],
     ["Mounted but read-only", "SCC / fsGroup / filesystem", "The pod's securityContext and the image's ownership"],
     ]) + term("the one-shot triage script", [
    ("#", "everything unhealthy, in one pass"),
    ("$", "oc get co | grep -v 'True.*False.*False'"),
    ("$", "oc get route -A -o json | jq -r '.items[] | select(.status.ingress[]?.conditions[]?"),
    ("", "  | select(.type==\"Admitted\" and .status!=\"True\")) | \"\\(.metadata.namespace)/\\(.metadata.name)\"'"),
    ("$", "oc get pvc -A --field-selector=status.phase=Pending"),
    ("$", "oc get volumeattachment -o json | jq -r '.items[]"),
    ("", "  | select(.status.attached!=true) | .metadata.name'"),
    ("$", "oc get endpointslice -A -o json | jq -r '.items[]"),
    ("", "  | select((.endpoints|length)==0) | \"\\(.metadata.namespace)/\\(.metadata.name)\"'"),
]) + note("good", "The MTU test first, when it is 'intermittent'",
          "<p>If the report is 'some requests work, big ones hang', 'it works from inside the "
          "cluster but not from outside', or 'TLS connects then stalls' — check MTU before "
          "anything else. It costs one <code>ping -M do</code> and it is the answer far more "
          "often than its reputation suggests.</p>")

NET_CHEAT = table(["Command", "What it answers"], [
    ["<code>oc get route -A</code>", "Every route and the host it claims"],
    ["<code>oc get route r -o yaml | grep -A5 conditions</code>", "Whether the router admitted it — a 503's real cause"],
    ["<code>oc -n openshift-ingress get pods -o wide</code>", "Where the routers run"],
    ["<code>oc -n openshift-ingress rsh deploy/router-default cat haproxy.config</code>", "What the router actually configured"],
    ["<code>oc get endpointslice -l kubernetes.io/service-name=&lt;s&gt;</code>", "Whether a Service has any Ready backend"],
    ["<code>oc get networkpolicy -A</code>", "Which namespaces are isolated"],
    ["<code>oc get network.operator cluster -o yaml</code>", "CNI, cluster CIDR and MTU"],
    ["<code>oc rsh &lt;pod&gt; ping -M do -s 1372 &lt;ip&gt;</code>", "The real path MTU"],
    ["<code>oc get pvc -A --field-selector=status.phase=Pending</code>", "Every stuck claim in the cluster"],
    ["<code>oc get sc</code>", "Binding mode, reclaim policy, expansion — before you commit"],
    ["<code>oc get volumeattachment</code>", "Whether a volume is attached and to which node"],
    ["<code>oc describe pvc &lt;c&gt;</code>", "The provisioner's own error message"],
    ["<code>oc get pv | grep Released</code>", "Retained volumes waiting to be rebound"],
    ["<code>oc adm must-gather -- /usr/bin/gather_network_logs</code>", "The supported network dump"],
], "mono")

OPENSHIFT_NETWORKING_STORAGE = dict(
    slug="openshift-networking-storage",
    title="OpenShift Networking & Storage",
    tagline=("Routes and the four TLS modes, OVN-Kubernetes and the MTU fault everybody "
             "misdiagnoses, NetworkPolicy isolation that silently blinds monitoring, and the "
             "CSI chain where each stage fails in a different log."),
    eyebrow="Kubernetes · OpenShift",
    meta=["<b>26 min</b> read", "Level: <b>core → advanced</b>", "OpenShift <b>02 / 03</b>"],
    sections=(
        section("The model", "HOW A REQUEST REACHES A POD",
                "Eight layers between the browser and the container, each able to drop the "
                "packet for its own reason.",
                f'<div class="dg-scroll">{NET_DIAGRAM}</div>'
                '<p class="dg-cap">The router is the only layer that returns a useful status '
                'code. Everything below it fails by dropping, which is why the triage table '
                'later works upwards from the pod rather than down from the client.</p>')
        + section("Core", "NETWORKING",
                  "Routes, the overlay, service endpoints and the policy model.", NET_CORE)
        + section("Advanced", "STORAGE",
                  "Binding modes, access modes, the CSI chain, and the two settings you cannot "
                  "change after creation.",
                  f'<div class="dg-scroll">{STO_DIAGRAM}</div>'
                  '<p class="dg-cap">A PVC that never binds is one of these arrows not '
                  'completing. Which arrow tells you which log to open.</p>' + NET_ADV)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, NET_TROUBLE)
        + section("Reference", "CHEATSHEET", None, NET_CHEAT)
    ),
)

TOPICS = [OPENSHIFT_NETWORKING_STORAGE]
