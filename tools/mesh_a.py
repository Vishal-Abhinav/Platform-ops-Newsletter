#!/usr/bin/env python3
"""Service Mesh content: Fundamentals (#066), Operations (#067).

Topics covered:
  #066  Service Mesh, Istio, Envoy, Linkerd, Service Discovery
  #067  Traffic Management, mTLS, Service-to-Service Security,
        Observability in Service Mesh, Multi-Cluster Service Mesh
"""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
# TOOLS is the real tools/ directory — derived from this file's own
# location, never from ROOT. ROOT is the OUTPUT root (dist/) and source
# must never be looked up underneath it.
TOOLS = _pl.Path(__file__).resolve().parent

from content_page import card, term, table, note, diagram, section, refs

ISTIO = "https://istio.io/latest/docs/"
K8S = "https://kubernetes.io/docs/"

# ═══════════════════════════════════════════════════════════════════════════
# 06 · SERVICE MESH FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════════════════
SM_DIAGRAM = diagram([
    ("Control plane", [("istiod / linkerd-destination", "core"),
                       ("config → xDS", "core"), ("CA issues workload certs", "core")]),
    ("Injection", [("webhook adds the sidecar at admission", "warm")]),
    ("Pod A", [("app container", "hot"), ("sidecar proxy", "hot")]),
    ("Capture", [("iptables / CNI plugin redirects all traffic", "calm")]),
    ("Wire", [("mTLS, identity = SPIFFE ID", "go")]),
    ("Pod B", [("sidecar proxy", "plain"), ("app container", "plain")]),
    ("Telemetry", [("every hop reported: latency, code, identity", "plain")]),
], "The app opens a plain connection to a Service; iptables redirects it into the proxy, which does the rest")

SM_CORE = "".join([
 card(1, "What a mesh actually is, and when it earns its place",
      "A proxy beside every pod, and one control plane configuring all of them.",
      ["sidecar", "data plane", "control plane"], """
<p>A service mesh is two things: a <strong>data plane</strong> of proxies — one per pod, or one
per node — that every request passes through, and a <strong>control plane</strong> that
configures them. The application is not modified and usually does not know the proxy is there.</p>
<p>What you get, and the reason it is worth the weight: <strong>mTLS everywhere without touching
application code</strong>, retries and timeouts and circuit breaking as policy rather than as
library code in six languages, traffic splitting for canaries, and uniform golden-signal
telemetry for every hop in the system.</p>
<h3>The honest costs</h3>
<ul>
<li><strong>Latency.</strong> Two extra proxy hops per request. Single-digit milliseconds, but
not zero, and it compounds across a deep call graph.</li>
<li><strong>Resources.</strong> A sidecar per pod. At a thousand pods that is a meaningful slice
of the cluster spent on proxies.</li>
<li><strong>A new failure domain.</strong> The mesh can now break your traffic in ways that have
nothing to do with your code, and debugging moves from "read the app log" to "read the proxy
config".</li>
</ul>
<h3>When you do not need one</h3>
<p>Ten services, one language, one team: a shared HTTP client library with retries and timeouts
gets most of the benefit at none of the cost. The mesh wins when the count of services and
languages is high enough that "put it in the library" stops being one change and becomes six.</p>
<p><strong>Ambient / sidecar-less modes</strong> change this calculation. Istio's ambient mode
moves mTLS and L4 telemetry to a per-node component and makes the L7 proxy opt-in per namespace,
which removes the per-pod sidecar cost for workloads that only need encryption and metrics.</p>
""" + refs([
    ("What is Istio?", ISTIO + "concepts/what-is-istio/",
     "The data-plane / control-plane split, and what the project sets out to solve."),
    ("Linkerd Overview", "https://linkerd.io/2.18/overview/",
     "The same model with a deliberately smaller surface — a useful contrast."),
])),

 card(2, "Envoy — the proxy under most of it",
      "Listeners, routes, clusters, endpoints — and xDS, which is how they arrive.",
      ["Envoy", "xDS", "listener"], """
<p>Istio, Gloo, Consul, Gateway API implementations and most of the ecosystem use
<strong>Envoy</strong> as the data plane. Understanding four of its objects makes mesh debugging
tractable, because every mesh CRD ultimately renders into them:</p>
<table class="tbl"><thead><tr><th>Object</th><th>Answers</th></tr></thead>
<tbody>
<tr><td><strong>Listener</strong></td><td>What port am I accepting on?</td></tr>
<tr><td><strong>Route</strong></td><td>Given this request, which cluster?</td></tr>
<tr><td><strong>Cluster</strong></td><td>A named upstream, with its load-balancing and outlier policy</td></tr>
<tr><td><strong>Endpoint</strong></td><td>The actual pod IPs behind that cluster</td></tr>
</tbody></table>
<p><strong>xDS</strong> is the protocol that streams these from the control plane to every proxy.
When someone says "the config has not propagated", they mean a proxy's xDS state is stale — and
that is directly observable rather than a matter of opinion.</p>
<h3>The debugging move that skips all the guessing</h3>
<p>Do not reason about what the CRDs should have produced. Ask the proxy what it actually has.</p>
""" + term("asking the proxy instead of theorising", [
    ("$", "istioctl proxy-status"),
    ("", "NAME                 CDS       LDS       EDS       RDS"),
    ("", "api-7d9f.prod        SYNCED    SYNCED    SYNCED    SYNCED"),
    ("", "web-5c8a.prod        SYNCED    STALE     SYNCED    SYNCED   <- here"),
    ("#", "what does this proxy think the routes are?"),
    ("$", "istioctl proxy-config route api-7d9f.prod --name 8080 -o json | jq '.[0].virtualHosts'"),
    ("$", "istioctl proxy-config cluster api-7d9f.prod --fqdn payments.prod.svc.cluster.local"),
    ("$", "istioctl proxy-config endpoint api-7d9f.prod --cluster 'outbound|8080||payments.prod.svc.cluster.local'"),
    ("#", "and the single most useful command in the whole toolkit:"),
    ("$", "istioctl analyze -n prod"),
    ("", "Warning [IST0101] (VirtualService prod/api) Referenced host not found: \"paymnets\""),
]) + refs([
    ("Envoy architecture overview", "https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/intro",
     "Listeners, filters, clusters and the threading model."),
    ("Life of a Request", "https://www.envoyproxy.io/docs/envoy/latest/intro/life_of_a_request",
     "Exactly what happens between accept and upstream — worth reading once, properly."),
])),

 card(3, "Service discovery — what the mesh adds to kube-dns",
      "Kubernetes already resolves names. The mesh changes what happens after resolution.",
      ["discovery", "EndpointSlice", "locality"], """
<p>Kubernetes service discovery is already complete: CoreDNS resolves
<code>svc.ns.svc.cluster.local</code> to a ClusterIP, and kube-proxy load-balances to the
EndpointSlice. A mesh does not replace that — it <em>intercepts</em> after it.</p>
<p>What changes: the proxy has the full endpoint list rather than an iptables rule, so it can do
things kube-proxy cannot — least-request instead of random, <strong>locality-aware</strong>
routing that prefers same-zone endpoints and fails over to another zone only when the local ones
are unhealthy, <strong>outlier detection</strong> that ejects an endpoint returning 5xx, and
per-request retries with a budget.</p>
<h3>Locality routing is usually the biggest single win</h3>
<p>Cross-zone traffic costs money and latency in every cloud. With zone labels on the nodes and
locality load balancing on, same-zone requests stay in-zone — often a double-digit percentage of
inter-AZ transfer removed for one config change.</p>
""" + term("locality-aware routing with automatic failover", [
    ("", "apiVersion: networking.istio.io/v1"),
    ("", "kind: DestinationRule"),
    ("", "spec:"),
    ("", "  host: payments.prod.svc.cluster.local"),
    ("", "  trafficPolicy:"),
    ("", "    loadBalancer:"),
    ("", "      localityLbSetting:"),
    ("", "        enabled: true"),
    ("", "        failover: [{from: us-east-1a, to: us-east-1b}]"),
    ("", "    outlierDetection:            # eject endpoints that start failing"),
    ("", "      consecutive5xxErrors: 5"),
    ("", "      interval: 10s"),
    ("", "      baseEjectionTime: 30s"),
    ("#", "verify the proxy has endpoints in more than one locality:"),
    ("$", "istioctl proxy-config endpoint api-7d9f.prod \\"),
    ("", "  --cluster 'outbound|8080||payments.prod.svc.cluster.local' -o json \\"),
    ("", "  | jq -r '.[].hostStatuses[].locality'"),
]) + refs([
    ("Service", K8S + "concepts/services-networking/service/",
     "What Kubernetes already gives you, before any mesh."),
    ("Istio traffic management", ISTIO + "concepts/traffic-management/",
     "DestinationRule, VirtualService, and where discovery fits."),
])),

 card(4, "Istio or Linkerd — and how to decide without a bake-off",
      "Scope versus simplicity. Both are CNCF-graduated and production-grade.",
      ["Istio", "Linkerd", "Gateway API"], """
<table class="tbl"><thead><tr><th></th><th>Istio</th><th>Linkerd</th></tr></thead>
<tbody>
<tr><td>Proxy</td><td>Envoy (C++), very configurable</td><td>linkerd2-proxy (Rust), purpose-built, small</td></tr>
<tr><td>Surface</td><td>Large — many CRDs, many knobs</td><td>Deliberately small</td></tr>
<tr><td>Resource cost</td><td>Higher per sidecar</td><td>Notably lower</td></tr>
<tr><td>Sidecar-less</td><td>Ambient mode</td><td>—</td></tr>
<tr><td>Strength</td><td>Anything you can express, you can configure</td><td>Fewer ways to get it wrong</td></tr>
</tbody></table>
<p>The decision is rarely about capability, because both do the core job. It is about whether you
want the configurability and will staff for it, or want the smallest thing that provides mTLS,
retries and golden signals.</p>
<h3>Gateway API is where both are heading</h3>
<p>The Kubernetes <strong>Gateway API</strong> is the successor to Ingress and now has a
service-mesh profile (GAMMA). Both Istio and Linkerd implement it. For new configuration it is
worth preferring Gateway API resources over vendor CRDs where they cover your case — the config
outlives the mesh you picked.</p>
""" + refs([
    ("Gateway API", "https://gateway-api.sigs.k8s.io/",
     "The standard replacing Ingress, and the mesh profile both projects implement."),
    ("Istio security concepts", ISTIO + "concepts/security/",
     "Identity, certificates and the policy model."),
])),
])

SM_TROUBLE = """
<p>Mesh debugging has one rule: <strong>stop reasoning about the CRDs and ask the proxy</strong>.
The CRDs are intent; the proxy's xDS state is what is actually happening, and the gap between
them is where the bug lives.</p>
""" + table(
    ["Symptom", "Likely cause", "Command"],
    [["503 with <code>UC</code>/<code>UF</code> flags", "Upstream refused or unreachable",
      "<code>istioctl proxy-config endpoint</code> — is the list empty?"],
     ["503 <code>NR</code> (no route)", "No VirtualService matches this host/port",
      "<code>istioctl proxy-config route</code>"],
     ["Works without the sidecar, fails with it", "Port naming, or a protocol the mesh mis-detected",
      "Service port must be named <code>http</code>, <code>grpc</code>, <code>tcp</code>…"],
     ["mTLS handshake failures", "PeerAuthentication STRICT with a non-mesh client",
      "<code>istioctl x describe pod &lt;p&gt;</code>"],
     ["Config change did nothing", "Proxy has stale xDS",
      "<code>istioctl proxy-status</code> — anything not SYNCED"],
     ["Some pods not meshed", "Injection label missing, or the pod predates it",
      "<code>kubectl get ns -L istio-injection</code>; then restart"],
     ["Intermittent 503 on deploy", "No graceful drain — in-flight requests cut",
      "<code>terminationGracePeriodSeconds</code> and a preStop sleep"],
     ]) + """
<h3>Port naming is the one that wastes a whole afternoon</h3>
<p>Istio infers protocol from the <strong>Service port name</strong>. A port named
<code>web</code> is treated as plain TCP, so HTTP routing, retries, and L7 telemetry silently do
nothing — no error, just features that are quietly absent. Name it <code>http</code>, or use
<code>appProtocol</code>.</p>
""" + term("the checks, in the order worth running them", [
    ("$", "istioctl analyze -A"),
    ("#", "1. is every proxy current?"),
    ("$", "istioctl proxy-status | grep -v SYNCED"),
    ("#", "2. what does THIS pod believe about mTLS and policy?"),
    ("$", "istioctl x describe pod api-7d9f.prod"),
    ("#", "3. the actual request flags — 15 seconds of proxy log beats an hour of theory"),
    ("$", "kubectl logs api-7d9f -c istio-proxy --tail=50 | grep -v '\" 200 '"),
    ("", "[2026-09-15T09:12:44Z] \"GET /v1/charge HTTP/1.1\" 503 UF,URX"),
    ("#", "   UF = upstream connection failure. Endpoints, not routes."),
    ("#", "4. are there any endpoints at all?"),
    ("$", "istioctl proxy-config endpoint api-7d9f.prod | grep payments"),
    ("#", "5. the port-name check that explains 'L7 features do nothing'"),
    ("$", "kubectl get svc -A -o json | jq -r '.items[] | .metadata.namespace as $ns"),
    ("", "  | .metadata.name as $n | .spec.ports[]"),
    ("", "  | select((.name//\"\")|test(\"^(http|https|grpc|tcp|tls|mongo|redis)\")|not)"),
    ("", "  | \"\\($ns)/\\($n) port \\(.port) name=\\(.name // \"UNNAMED\")\"'"),
]) + note("good", "The proxy access log has the answer in two characters",
          "<p>Envoy tags every request with response flags — <code>UF</code> upstream failure, "
          "<code>UH</code> no healthy upstream, <code>NR</code> no route, <code>UO</code> "
          "outlier-ejected, <code>URX</code> retry limit. They distinguish 'nothing to send it "
          "to' from 'nowhere to route it' immediately, which is the fork you would otherwise "
          "spend twenty minutes narrowing by hand.</p>")

SM_CHEAT = table(["Command", "What it answers"], [
    ["<code>istioctl analyze -A</code>", "Misconfiguration, before it becomes an incident"],
    ["<code>istioctl proxy-status</code>", "Which proxies have stale config"],
    ["<code>istioctl x describe pod &lt;p&gt;</code>", "Policies, mTLS mode and routes for one pod"],
    ["<code>istioctl proxy-config route &lt;p&gt;</code>", "The routes this proxy actually has"],
    ["<code>istioctl proxy-config cluster &lt;p&gt;</code>", "Upstreams it knows about"],
    ["<code>istioctl proxy-config endpoint &lt;p&gt;</code>", "Real pod IPs — empty means 503"],
    ["<code>istioctl proxy-config listener &lt;p&gt;</code>", "Ports it is accepting on"],
    ["<code>kubectl logs &lt;p&gt; -c istio-proxy</code>", "Response flags — the two-character diagnosis"],
    ["<code>kubectl get ns -L istio-injection</code>", "Which namespaces are meshed"],
    ["<code>linkerd check</code>", "Linkerd's equivalent end-to-end health check"],
    ["<code>linkerd viz stat deploy -n &lt;ns&gt;</code>", "Success rate, RPS and latency per workload"],
], "mono")

SERVICE_MESH_FUNDAMENTALS = dict(
    slug="service-mesh-fundamentals",
    title="Service Mesh Fundamentals",
    tagline=("What a sidecar mesh actually buys and what it costs, the four Envoy objects every "
             "mesh CRD renders into, what discovery adds on top of kube-dns, and the port name "
             "that silently disables every L7 feature."),
    eyebrow="Kubernetes · Service Mesh",
    meta=["<b>25 min</b> read", "Level: <b>core → advanced</b>", "Service Mesh <b>01 / 02</b>"],
    sections=(
        section("The model", "HOW A REQUEST GETS INTO THE MESH",
                "The application opens an ordinary connection. Everything after that is "
                "interception the app never sees.",
                f'<div class="dg-scroll">{SM_DIAGRAM}</div>'
                '<p class="dg-cap">Because capture is transparent, the app cannot tell you what '
                'the mesh did. That is why every debugging path here goes through the proxy '
                'rather than the application log.</p>')
        + section("Core", "MESH, PROXY AND DISCOVERY",
                  "What the parts are, and which decisions actually matter.", SM_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, SM_TROUBLE)
        + section("Reference", "CHEATSHEET", None, SM_CHEAT)
    ),
)

# ═══════════════════════════════════════════════════════════════════════════
# 07 · SERVICE MESH OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════
SMO_DIAGRAM = diagram([
    ("Identity", [("SPIFFE ID per ServiceAccount", "core"), ("mesh CA issues cert", "core"),
                  ("rotated hourly", "core")]),
    ("Transport", [("PeerAuthentication: STRICT | PERMISSIVE", "warm")]),
    ("AuthZ", [("AuthorizationPolicy: ALLOW / DENY / CUSTOM", "hot")]),
    ("Routing", [("VirtualService: match, split, retry, timeout", "calm")]),
    ("Upstream", [("DestinationRule: subsets, LB, outlier, circuit breaker", "go")]),
    ("Telemetry", [("metrics per hop", "plain"), ("access logs", "plain"),
                   ("trace headers — app must propagate", "plain")]),
], "Identity first: every policy below it is expressed in terms of who the caller cryptographically is")

SMO_CORE = "".join([
 card(1, "mTLS — identity you did not have to write code for",
      "PERMISSIVE during migration, STRICT afterwards, and the SPIFFE ID that makes policy possible.",
      ["mTLS", "SPIFFE", "PeerAuthentication"], """
<p>The mesh issues every workload a short-lived X.509 certificate whose identity is a
<strong>SPIFFE ID</strong> derived from its ServiceAccount:</p>
<p><code>spiffe://cluster.local/ns/prod/sa/payments-sa</code></p>
<p>Both ends present one, both verify, and rotation is automatic and frequent — typically hourly.
That is the part worth appreciating: certificate rotation, the thing that causes outages
everywhere else, becomes invisible infrastructure.</p>
<p>And crucially, this identity is <strong>cryptographic, not network-based</strong>. Policy can
now say "payments may call ledger" rather than "10.4.0.0/16 may reach port 8080" — which
survives pods moving, IPs changing and namespaces being recreated.</p>
<h3>PERMISSIVE is the migration mode, and the trap</h3>
<p><code>PERMISSIVE</code> accepts both mTLS and plaintext, which is what makes incremental
adoption possible. It is also indistinguishable from STRICT when everything happens to be
meshed — so clusters sit in PERMISSIVE for years believing they have mutual TLS, while any
unmeshed pod can still connect in plaintext.</p>
""" + term("moving to STRICT, and proving it took", [
    ("#", "namespace-wide, after everything in it is meshed"),
    ("", "apiVersion: security.istio.io/v1"),
    ("", "kind: PeerAuthentication"),
    ("", "metadata: { name: default, namespace: prod }"),
    ("", "spec: { mtls: { mode: STRICT } }"),
    ("#", "what is each workload ACTUALLY doing right now?"),
    ("$", "istioctl x describe pod api-7d9f.prod | grep -i mtls"),
    ("#", "the honest test — a plaintext client from outside the mesh:"),
    ("$", "kubectl run probe --rm -it --image=curlimages/curl \\"),
    ("", "  --annotations sidecar.istio.io/inject=false -- \\"),
    ("", "  curl -sS -m 5 http://payments.prod.svc.cluster.local:8080/health"),
    ("", "curl: (56) Recv failure: Connection reset by peer    <- STRICT is real"),
    ("#", "any namespace still permissive:"),
    ("$", "kubectl get peerauthentication -A -o json | jq -r '.items[]"),
    ("", "  | \"\\(.metadata.namespace)/\\(.metadata.name)\\t\\(.spec.mtls.mode // \"unset\")\"'"),
]) + refs([
    ("Istio security concepts", ISTIO + "concepts/security/",
     "Identity, certificate issuance and rotation, PeerAuthentication and AuthorizationPolicy."),
    ("Istio security best practices", ISTIO + "ops/best-practices/security/",
     "Where policy can be bypassed, and how to close each gap."),
])),

 card(2, "AuthorizationPolicy — who may call whom",
      "DENY wins over ALLOW, and an empty rule means something different from no rule.",
      ["AuthorizationPolicy", "least privilege", "deny"], """
<p>With identity established, authorization becomes a statement about services rather than
addresses. The evaluation order is worth committing to memory, because it is where surprises
come from:</p>
<ol>
<li><strong>CUSTOM</strong> policies (external authz) evaluate first.</li>
<li><strong>DENY</strong> policies — if any matches, the request is refused.</li>
<li>If any <strong>ALLOW</strong> policy applies to the workload, the request must match one.</li>
<li>If no ALLOW policy applies to the workload at all, the request is <strong>allowed</strong>.</li>
</ol>
<p>Point 4 is the one that catches people. A namespace with no AuthorizationPolicy is fully open.
Adding one ALLOW policy to a single workload flips <em>that workload</em> to default-deny while
everything beside it stays open — which is usually intended, and rarely realised.</p>
<h3>The default-deny baseline</h3>
<p>An ALLOW policy with an empty <code>spec: {}</code> matches nothing and therefore denies
everything in its namespace. That is the idiom for a default-deny floor, and it reads as a typo
if you have not seen it before.</p>
""" + term("default-deny, then allow exactly what should exist", [
    ("#", "1. the floor: allow nothing (empty spec matches no request)"),
    ("", "apiVersion: security.istio.io/v1"),
    ("", "kind: AuthorizationPolicy"),
    ("", "metadata: { name: deny-all, namespace: prod }"),
    ("", "spec: {}"),
    ("#", "2. one allowance, by IDENTITY not by IP"),
    ("", "spec:"),
    ("", "  selector: { matchLabels: { app: ledger } }"),
    ("", "  action: ALLOW"),
    ("", "  rules:"),
    ("", "  - from: [{ source: { principals:"),
    ("", "      [\"cluster.local/ns/prod/sa/payments-sa\"] } }]"),
    ("", "    to:   [{ operation: { methods: [\"POST\"], paths: [\"/v1/entries\"] } }]"),
    ("#", "a refusal is RBAC: access denied, and the proxy log names the policy:"),
    ("$", "kubectl logs ledger-6f8 -c istio-proxy | grep -i rbac | tail -5"),
]) + note("warn", "Test policy from a real caller, not from curl in a debug pod",
          "<p>A debug pod carries its own ServiceAccount, so it has a different SPIFFE ID and "
          "will be refused for reasons that have nothing to do with the policy you are testing. "
          "Exec into an actual client pod, or run the probe with the same ServiceAccount.</p>")),

 card(3, "Traffic management — canaries, retries and the timeout budget",
      "Weighted splits are the easy part; retries are where meshes amplify an outage.",
      ["VirtualService", "canary", "retry"], """
<p><code>VirtualService</code> decides routing — match on header, path or weight;
<code>DestinationRule</code> defines the subsets and the upstream policy. A canary is a weight
change, and a header-matched route lets you send only your own traffic to the new version first,
which is a better first step than 1% of everyone.</p>
<h3>Retries are the dangerous feature</h3>
<p>Mesh retries are per-hop, and they multiply through a call graph. Three retries at each of
three hops is up to 27 requests hitting the service at the bottom — so a service that is
struggling receives an order of magnitude <em>more</em> load precisely because it started
failing. This is the mechanism behind a large share of mesh-amplified outages.</p>
<p>Three rules keep it safe: retry only <strong>idempotent</strong> operations, keep
<code>perTryTimeout × attempts</code> under the overall timeout, and pair retries with
<strong>outlier detection</strong> so a consistently failing endpoint is ejected rather than
retried at.</p>
""" + term("a canary and a retry policy that will not amplify", [
    ("", "kind: VirtualService"),
    ("", "spec:"),
    ("", "  hosts: [payments]"),
    ("", "  http:"),
    ("", "  - match: [{ headers: { x-canary: { exact: \"true\" } } }]   # opt-in first"),
    ("", "    route: [{ destination: { host: payments, subset: v2 } }]"),
    ("", "  - route:                                                   # then weight"),
    ("", "    - { destination: { host: payments, subset: v1 }, weight: 95 }"),
    ("", "    - { destination: { host: payments, subset: v2 }, weight: 5 }"),
    ("", "    timeout: 3s"),
    ("", "    retries:"),
    ("", "      attempts: 2                     # 2, not 5"),
    ("", "      perTryTimeout: 1s               # 2 x 1s < 3s overall"),
    ("", "      retryOn: 5xx,reset,connect-failure"),
    ("#", "and the circuit breaker that stops you retrying at a dead endpoint:"),
    ("", "kind: DestinationRule"),
    ("", "spec:"),
    ("", "  trafficPolicy:"),
    ("", "    outlierDetection: { consecutive5xxErrors: 5, interval: 10s,"),
    ("", "                        baseEjectionTime: 30s, maxEjectionPercent: 50 }"),
    ("", "    connectionPool: { http: { http2MaxRequests: 100,"),
    ("", "                              maxRequestsPerConnection: 10 } }"),
]) + refs([
    ("Istio traffic management", ISTIO + "concepts/traffic-management/",
     "VirtualService, DestinationRule, subsets, retries, timeouts and circuit breaking."),
])),

 card(4, "Observability and multi-cluster",
      "Free golden signals, the tracing caveat nobody mentions, and what a second cluster costs.",
      ["telemetry", "tracing", "multi-cluster"], """
<p>Because every request crosses a proxy, the mesh reports request rate, error rate and latency
distribution for <em>every</em> service-to-service hop, labelled with both identities, with no
application instrumentation at all. That is the fastest observability win available in a
Kubernetes estate, and it arrives the day you install the mesh.</p>
<h3>The tracing caveat</h3>
<p>Distributed tracing is <strong>not</strong> free. The mesh generates and forwards span
context, but the application must <strong>propagate the trace headers</strong>
(<code>traceparent</code>, or the <code>x-b3-*</code> family) from the incoming request to its
outgoing calls. An app that does not becomes a wall: every trace stops there and you get
disconnected fragments rather than a call graph. It is a handful of lines in most frameworks, and
it is the single most common reason mesh tracing "does not work".</p>
<h3>Multi-cluster mesh</h3>
<p>Two shapes. <strong>Multi-primary</strong> puts a control plane in each cluster — no
cross-cluster control dependency, more to keep consistent. <strong>Primary-remote</strong> has
one control plane serving several clusters — simpler config, and a hard dependency on the primary.
Either way the prerequisites are the same and are the actual work: a shared trust root so
identities verify across clusters, pod-to-pod reachability or east-west gateways, and consistent
namespace and ServiceAccount naming, because identity is derived from those names.</p>
""" + term("what the mesh already knows, without app changes", [
    ("#", "success rate and latency per hop — no instrumentation"),
    ("$", "kubectl exec -n istio-system deploy/prometheus -c prometheus -- \\"),
    ("", "  curl -sG localhost:9090/api/v1/query --data-urlencode 'query='\\"),
    ("", "'sum by (destination_service_name) ("),
    ("", "  rate(istio_requests_total{response_code=~\"5..\"}[5m]))'"),
    ("#", "p99 per service pair"),
    ("", "histogram_quantile(0.99, sum by (le, source_workload, destination_service_name)("),
    ("", "  rate(istio_request_duration_milliseconds_bucket[5m])))"),
    ("#", "linkerd states it directly:"),
    ("$", "linkerd viz stat deploy -n prod"),
    ("", "NAME      MESHED   SUCCESS   RPS   LATENCY_P99"),
    ("", "payments  3/3       99.82%    412   184ms"),
    ("#", "is the app actually propagating trace context? look for it downstream:"),
    ("$", "kubectl logs payments-6f8 -c istio-proxy | grep -o 'traceparent[^ ]*' | head -3"),
]) + refs([
    ("Istio observability", ISTIO + "concepts/observability/",
     "The metrics the mesh emits, and the explicit note that apps must forward trace headers."),
    ("Istio multicluster installation", ISTIO + "setup/install/multicluster/",
     "Multi-primary versus primary-remote, trust roots and east-west gateways."),
    ("Linkerd automatic mTLS", "https://linkerd.io/2.18/features/automatic-mtls/",
     "How the same identity model looks with fewer moving parts."),
])),
])

SMO_TROUBLE = """
<p>Operational mesh failures split cleanly in two: <strong>policy refused it</strong>, which is
loud and precise, or <strong>routing sent it nowhere</strong>, which shows as a 503 with a
two-character flag. Identify which before touching any YAML.</p>
""" + table(
    ["What you see", "Meaning", "Where to look"],
    [["<code>RBAC: access denied</code>", "AuthorizationPolicy refused it",
      "Proxy log names the policy; check the caller's SPIFFE ID"],
     ["503 <code>UF</code>", "Could not connect upstream", "Endpoints, and mTLS mode mismatch"],
     ["503 <code>UH</code>", "No healthy upstream — all ejected", "Outlier detection is doing its job"],
     ["503 <code>NR</code>", "No route matched", "VirtualService hosts and ports"],
     ["503 <code>UO</code>", "Circuit breaker open", "<code>connectionPool</code> limits"],
     ["Load spike on a failing service", "Retries amplifying through the graph",
      "<code>attempts</code> per hop, multiplied"],
     ["Traces stop at one service", "That app does not forward trace headers",
      "Its outgoing request headers"],
     ["Cross-cluster calls fail", "Trust root or gateway",
      "<code>istioctl proxy-config endpoint</code> — remote endpoints present?"],
     ]) + """
<h3>The mTLS mismatch that presents as a connection reset</h3>
<p>A STRICT namespace and an unmeshed caller produce a reset with no useful application-level
error. It is easy to misread as a network problem. The tell: it works from inside the mesh and
fails from outside, and the server-side proxy log shows the connection being closed before any
request line.</p>
""" + term("narrowing a mesh 503 in four commands", [
    ("$", "kubectl logs api-7d9f -c istio-proxy --tail=100 | grep ' 503 '"),
    ("", "[...] \"POST /v1/charge HTTP/1.1\" 503 UF,URX \"-\" 0 91 1001 - \"-\" ..."),
    ("#", "UF -> connection failure. Is there anything to connect TO?"),
    ("$", "istioctl proxy-config endpoint api-7d9f.prod --cluster \\"),
    ("", "  'outbound|8080||payments.prod.svc.cluster.local'"),
    ("#", "endpoints present -> mTLS mismatch. Compare both sides:"),
    ("$", "istioctl x describe pod payments-6f8.prod | grep -iA2 mtls"),
    ("#", "and confirm the policy set actually in force for that workload:"),
    ("$", "kubectl get peerauthentication,authorizationpolicy -n prod"),
]) + note("good", "istioctl analyze before anything else",
          "<p>It catches the majority of real-world mesh misconfiguration statically — hosts "
          "that do not resolve, conflicting policies, subsets with no matching DestinationRule, "
          "gateways selecting nothing. Running it in CI against your manifests catches these "
          "before they reach a cluster at all.</p>")

SMO_CHEAT = table(["Command", "What it answers"], [
    ["<code>istioctl analyze -A</code>", "Static misconfiguration across the mesh"],
    ["<code>istioctl x describe pod &lt;p&gt;</code>", "Every policy in force for one workload"],
    ["<code>kubectl get peerauthentication -A</code>", "Which namespaces are actually STRICT"],
    ["<code>kubectl get authorizationpolicy -A</code>", "Who may call whom"],
    ["<code>kubectl logs &lt;p&gt; -c istio-proxy | grep rbac</code>", "Which policy refused a request"],
    ["<code>kubectl logs &lt;p&gt; -c istio-proxy | grep ' 503 '</code>", "The response flag — the actual diagnosis"],
    ["<code>istioctl proxy-config endpoint &lt;p&gt;</code>", "Whether there is anything to route to"],
    ["<code>istioctl proxy-config route &lt;p&gt;</code>", "Whether a route matches at all"],
    ["<code>istioctl pc secret &lt;p&gt;</code>", "The workload cert and its validity"],
    ["<code>linkerd viz stat deploy -n &lt;ns&gt;</code>", "Success rate, RPS, p99 per workload"],
    ["<code>linkerd viz tap deploy/&lt;x&gt;</code>", "Live per-request stream"],
    ["<code>istioctl proxy-status</code>", "Stale config, before you debug the wrong thing"],
], "mono")

SERVICE_MESH_OPERATIONS = dict(
    slug="service-mesh-operations",
    title="Service Mesh Operations",
    tagline=("mTLS identity that makes policy a statement about services rather than subnets, "
             "the AuthorizationPolicy default that flips one workload to deny, retries that "
             "multiply through a call graph, and the trace headers your app still has to "
             "forward itself."),
    eyebrow="Kubernetes · Service Mesh",
    meta=["<b>26 min</b> read", "Level: <b>advanced</b>", "Service Mesh <b>02 / 02</b>"],
    sections=(
        section("The model", "IDENTITY FIRST, THEN EVERY POLICY ABOVE IT",
                "Once each workload has a cryptographic identity, authorization and routing stop "
                "being about IP addresses.",
                f'<div class="dg-scroll">{SMO_DIAGRAM}</div>'
                '<p class="dg-cap">Telemetry sits at the bottom because it is a by-product: '
                'everything already passes through the proxy, so metrics come free — and traces '
                'do not, because they need the application to cooperate.</p>')
        + section("Core", "SECURITY, ROUTING AND TELEMETRY",
                  "The four things a mesh is actually run for, and where each one bites.", SMO_CORE)
        + section("In practice", "ADVANCED TROUBLESHOOTING", None, SMO_TROUBLE)
        + section("Reference", "CHEATSHEET", None, SMO_CHEAT)
    ),
)

TOPICS = [SERVICE_MESH_FUNDAMENTALS, SERVICE_MESH_OPERATIONS]
