#!/usr/bin/env python3
"""The low-level and connection diagrams, one pair per deep-dive topic.

CONTENT, NOT CODE — the renderers live in diagrams.py. This file is the part
you edit when a diagram is wrong, and it is meant to be readable as prose.

Each topic gets two pictures the high-level layered diagram cannot give:

  detail   one box from the high-level view, opened up, with its interfaces
           named on the edges. "What is actually inside this thing."
  flow     one request or one piece of data, hop by hop, with the protocol or
           port on each hop. "Where does it go, and which hop dropped it."

A RULE FOR WRITING THESE
------------------------
Every edge label earns its place by being something you could act on — a port
you could tcpdump, a syscall you could strace, a table you could dump. "sends
request" is not a label; ":8080 HTTP" and "DNAT" are. If a hop has no such
label, it is usually two hops pretending to be one.

Roles colour the boxes and mean the same thing across every diagram on the
site: core = the thing under discussion, warm = machinery that acts on it,
hot = where it goes wrong, go = the success path, calm = storage or state,
plain = context that is not the topic.
"""
import os
import pathlib as _pl
import sys

ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT / "tools"))

from diagrams import detail, flow                    # noqa: E402

# ═══════════════════════════════════════════════════════════════════════════
# FOUNDATION
# ═══════════════════════════════════════════════════════════════════════════
SPEC = {}

SPEC["computer-fundamentals"] = [
    ("Low level", "What is inside one core, between the instruction and the data?",
     detail("ONE CPU CORE", [
         ("Fetch and decode", [
             ("L1 instruction cache", "core", "~32 KB, ~4 cycles"),
             ("branch predictor", "warm", "a miss costs ~15 cycles"),
             ("decoder → µops", "plain", None)]),
         ("Address translation", [
             ("TLB", "core", "virtual → physical"),
             ("page walk on a miss", "hot", "~100+ cycles"),
             ("MMU", "plain", None)]),
         ("Data path", [
             ("L1 data cache", "core", "~32 KB, ~4 cycles"),
             ("L2", "warm", "~1 MB, ~14 cycles"),
             ("L3 shared", "warm", "~32 MB, ~40 cycles"),
             ("prefetcher", "go", "guesses the next line")]),
     ], inputs=["instruction stream", "load / store"],
        outputs=["L3 miss → memory", "coherency traffic"]),
     "Nothing here is optional. Every line of your code goes through all of it, "
     "and the only part you can influence from a high-level language is whether "
     "the data you touch next is already in the line you just pulled in."),

    ("Connection", "What does one memory read actually cost?",
     flow([("load instruction", "plain"),
           ("L1d", "core", "~1 ns"),
           ("L2", "warm", "miss"),
           ("L3", "warm", "miss"),
           ("memory controller", "hot", "miss"),
           ("DRAM row", "calm", "~80 ns"),
           ("cache line filled", "go", "64 bytes")]),
     "Six orders of magnitude separate the first hop from the last. This is why "
     "an array beats a linked list with identical Big-O: the array's next element "
     "arrived in the same 64-byte line, and the list's is a fresh trip to DRAM."),
]

SPEC["operating-systems"] = [
    ("Low level", "What does the kernel do between your read() and the disk?",
     detail("KERNEL, ON ONE read()", [
         ("Entry", [("syscall boundary", "core", "user → kernel mode"),
                    ("fd table lookup", "core", "per-process"),
                    ("permission check", "warm", None)]),
         ("Filesystem", [("VFS", "core", "one API, many filesystems"),
                         ("page cache", "calm", "hit means no disk at all"),
                         ("filesystem driver", "warm", "ext4 / xfs")]),
         ("Block", [("block layer + I/O scheduler", "warm", "merge and reorder"),
                    ("device driver", "plain", None),
                    ("the actual device", "plain", None)]),
     ], inputs=["read(fd, buf, n)", "process context"],
        outputs=["bytes into buf", "blocked → scheduler"]),
     "The page cache is the hop that decides everything. A hit returns in "
     "microseconds and never reaches the block layer; a miss parks your process "
     "in D state where even kill -9 will not touch it."),

    ("Connection", "How does a process get to run, and how does it stop running?",
     flow([("process created", "plain"),
           ("run queue", "core", "fork / clone"),
           ("scheduler picks it", "core", "CFS vEFT"),
           ("running on a CPU", "go", "context switch"),
           ("blocks on I/O", "hot", "syscall sleeps"),
           ("wait queue", "calm", "D state"),
           ("woken by completion", "warm", "IRQ"),
           ("back to run queue", "core", None)]),
     "Load average counts the boxes in the run queue AND the ones in D state, "
     "which is why a machine with idle CPUs can show a load of 40: nothing is "
     "computing, everything is waiting on a disk."),
]

SPEC["shell-and-bash"] = [
    ("Low level", "What does bash do to your line before anything runs?",
     detail("ONE COMMAND LINE, EXPANDED", [
         ("Parse", [("tokenise", "plain", None),
                    ("alias expansion", "warm", "first word only"),
                    ("quote removal is LAST", "hot", "after every expansion")]),
         ("Expand, in this order", [
             ("brace {a,b}", "core", "before variables"),
             ("tilde ~", "core", None),
             ("parameter $var", "core", "unquoted → splits"),
             ("command $( )", "core", None)]),
         ("Then", [("arithmetic $(( ))", "warm", None),
                   ("word splitting on IFS", "hot", "the classic bug"),
                   ("pathname globbing *", "hot", "can match nothing"),
                   ("redirection", "go", "before exec")]),
     ], inputs=["the line you typed", "IFS, shopt, set -f"],
        outputs=["argv[] for execve", "fds 0/1/2"]),
     "The order is the whole lesson. Word splitting happens AFTER variable "
     "expansion and BEFORE quote removal, which is exactly why $file breaks on "
     "a space and \"$file\" does not."),

    ("Connection", "What actually happens when you type a | b > out?",
     flow([("bash reads the line", "plain"),
           ("pipe(2)", "core", "two fds"),
           ("fork for 'a'", "warm", "child 1"),
           ("dup2 → stdout", "core", "fd 1 = pipe write"),
           ("fork for 'b'", "warm", "child 2"),
           ("open 'out', dup2", "core", "fd 1 = file"),
           ("execve both", "go", "argv from expansion"),
           ("wait, $? = last", "calm", "PIPESTATUS has all")]),
     "Both children are forked before either runs, which is why a pipeline's "
     "exit status is the LAST command's — and why set -o pipefail exists at all."),
]

SPEC["python"] = [
    ("Low level", "What is inside CPython while your function runs?",
     detail("CPYTHON RUNTIME", [
         ("Compile, once", [("source → AST", "plain", None),
                            ("AST → bytecode", "core", "cached in __pycache__"),
                            ("code object", "calm", "co_consts, co_names")]),
         ("Execute, always", [("eval loop (ceval)", "core", "one bytecode at a time"),
                              ("the GIL", "hot", "one thread executes bytecode"),
                              ("frame stack", "calm", None)]),
         ("Memory", [("reference counting", "warm", "frees most objects"),
                     ("cycle GC, generational", "warm", "for the rest"),
                     ("object allocator", "plain", "pymalloc arenas")]),
     ], inputs=["your module", "C extension calls"],
        outputs=["syscalls", "GIL released on I/O"]),
     "The GIL protects the interpreter's own state, not yours. It is released "
     "around blocking I/O and inside well-behaved C extensions — which is the "
     "entire basis for choosing between threads, processes and asyncio."),

    ("Connection", "Where does the GIL actually bite?",
     flow([("request arrives", "plain"),
           ("thread wakes", "core", "acquires GIL"),
           ("parse / branch", "hot", "GIL held — serialised"),
           ("db call", "go", "GIL RELEASED"),
           ("other threads run", "go", "real concurrency here"),
           ("response built", "hot", "GIL held again"),
           ("bytes written", "calm", "GIL released")]),
     "Threads give you real concurrency on the green hops and none at all on the "
     "red ones. If your workload is mostly red, threads will not help and "
     "multiprocessing will."),
]

SPEC["git-version-control"] = [
    ("Low level", "What is actually in .git?",
     detail(".GIT", [
         ("Objects, content-addressed", [
             ("blob", "core", "file contents, no name"),
             ("tree", "core", "names + modes → blobs"),
             ("commit", "core", "one tree + parents"),
             ("tag", "plain", "annotated only")]),
         ("Pointers", [("refs/heads/*", "warm", "branches"),
                       ("HEAD", "warm", "where you are"),
                       ("refs/remotes/*", "warm", "last known remote"),
                       ("reflog", "go", "where HEAD has been")]),
         ("Working state", [("index (.git/index)", "calm", "the staging area"),
                            ("packfiles", "calm", "deltas, after gc"),
                            ("loose objects", "plain", "before gc")]),
     ], inputs=["working tree", "fetch from remote"],
        outputs=["checkout → working tree", "push → remote refs"]),
     "A blob has no filename — the tree supplies it. That is why moving a file "
     "costs nothing, why git cannot track a rename as such, and why identical "
     "files anywhere in history are stored exactly once."),

    ("Connection", "Where does a change live at each step?",
     flow([("edit a file", "plain"),
           ("working tree", "core", "untracked change"),
           ("git add", "warm", "blob written NOW"),
           ("index", "calm", "tree staged"),
           ("git commit", "warm", "tree + parent"),
           ("object store", "calm", "commit written"),
           ("branch ref moves", "go", "reflog records it"),
           ("git push", "go", "remote ref updated")]),
     "The blob is written at `git add`, not at commit. That is why a change you "
     "staged and then overwrote is still recoverable, and why reflog can bring "
     "back a commit you have 'lost' for up to ninety days."),
]

# ═══════════════════════════════════════════════════════════════════════════
# KUBERNETES
# ═══════════════════════════════════════════════════════════════════════════
SPEC["kubernetes-workloads"] = [
    ("Low level", "What is inside the kubelet, the thing that actually starts containers?",
     detail("KUBELET", [
         ("Sources of truth", [("apiserver watch", "core", "pods bound to this node"),
                               ("static manifests", "plain", "/etc/kubernetes/manifests"),
                               ("PLEG", "warm", "relists the runtime")]),
         ("The sync loop", [("syncPod per pod", "core", "desired vs actual"),
                            ("probe workers", "warm", "startup / readiness / liveness"),
                            ("eviction manager", "hot", "on disk or memory pressure")]),
         ("Plugins it drives", [("CRI → containerd", "go", "create / start / kill"),
                                ("CNI", "go", "pod gets an IP"),
                                ("CSI", "calm", "mount volumes")]),
     ], inputs=["bound Pod spec", "node conditions"],
        outputs=["container lifecycle", "status back to apiserver"]),
     "The kubelet owns exactly one node and reconciles only the pods bound to it. "
     "Nothing here knows about Deployments — by the time the kubelet sees it, a "
     "workload is just a Pod with a node name on it."),

    ("Connection", "What happens between kubectl apply and a running container?",
     flow([("kubectl apply", "plain"),
           ("apiserver", "core", "HTTPS :6443"),
           ("etcd", "calm", "write, then watch fires"),
           ("deployment controller", "warm", "creates ReplicaSet"),
           ("replicaset controller", "warm", "creates Pod"),
           ("scheduler", "core", "sets spec.nodeName"),
           ("kubelet on that node", "go", "watch match"),
           ("containerd → container", "go", "CRI")]),
     "Eight hops, each one a separate controller reading and writing the same "
     "store. A pod stuck Pending has not reached the scheduler's binding hop; a "
     "pod stuck ContainerCreating is past it and stuck in CNI or CSI."),
]

SPEC["kubernetes-config-and-access"] = [
    ("Low level", "What does the API server do to every single request?",
     detail("APISERVER REQUEST PIPELINE", [
         ("Who are you", [("authentication", "core", "cert, token, OIDC"),
                          ("→ user + groups", "plain", "no user objects exist")]),
         ("May you", [("RBAC authorisation", "core", "purely additive, no deny"),
                      ("→ allow or 403", "hot", "first matching rule wins")]),
         ("Mutate then validate", [
             ("mutating admission", "warm", "webhooks, defaulting"),
             ("schema validation", "warm", "OpenAPI"),
             ("validating admission", "warm", "Pod Security, policy"),
             ("quota", "hot", "the last gate")]),
         ("Persist", [("etcd write", "calm", "serialised, encrypted at rest if configured"),
                      ("watch fan-out", "go", "every controller sees it")]),
     ], inputs=["kubectl / controller", "kubeconfig identity"],
        outputs=["201 + object", "watch event to all"]),
     "Four gates, in this order, on every request including a controller's. A "
     "403 came from gate two and mentions the verb and resource; a 422 came from "
     "gate three and mentions the field."),

    ("Connection", "Why can a Secret be read by someone you never granted it to?",
     flow([("ServiceAccount token", "plain"),
           ("authentication", "core", "identity established"),
           ("RoleBindings in ns", "warm", "namespace-scoped"),
           ("ClusterRoleBindings", "hot", "cluster-wide, easy to miss"),
           ("union of all rules", "hot", "additive — no deny exists"),
           ("get secrets → allowed", "go", "base64, not encrypted"),
           ("mounted in a pod", "calm", "readable by the process")]),
     "RBAC has no deny rule. Access is the union of every binding that matches, "
     "so auditing 'who can read this Secret' means enumerating bindings, not "
     "reading one policy."),
]

SPEC["kubernetes-scheduling"] = [
    ("Low level", "What is inside one scheduling cycle?",
     detail("KUBE-SCHEDULER", [
         ("Queue", [("activeQ", "core", "ready to try"),
                    ("unschedulableQ", "hot", "failed, waiting for a cluster change"),
                    ("backoffQ", "warm", "exponential retry")]),
         ("Filter — can it fit", [("NodeResourcesFit", "core", "requests, not limits"),
                                  ("TaintToleration", "core", "the node's veto"),
                                  ("NodeAffinity", "core", "the pod's requirement"),
                                  ("VolumeBinding", "warm", "zone of the PV")]),
         ("Score — where is best", [("LeastAllocated", "warm", None),
                                    ("PodTopologySpread", "warm", "even across zones"),
                                    ("InterPodAffinity", "warm", "topologyKey"),
                                    ("ImageLocality", "plain", "image already there")]),
         ("Commit", [("Reserve → Permit", "go", None),
                     ("Bind: set spec.nodeName", "go", "one API write")]),
     ], inputs=["Pod with no nodeName", "node + PV state"],
        outputs=["Binding object", "FailedScheduling event"]),
     "Filter is a yes/no over every node and score only ranks the survivors. A "
     "Pending pod means filter returned an empty set, and the event tells you "
     "which predicate rejected how many nodes — read it verbatim."),

    ("Connection", "Why is my pod Pending?",
     flow([("Pod created", "plain"),
           ("activeQ", "core", "no nodeName"),
           ("filter over N nodes", "warm", "each plugin votes"),
           ("0 nodes survive", "hot", "FailedScheduling"),
           ("unschedulableQ", "hot", "parked, not retried"),
           ("cluster changes", "warm", "node added, pod deleted"),
           ("requeued → bound", "go", "spec.nodeName set")]),
     "A pod in unschedulableQ is not being retried on a timer — it waits for a "
     "cluster event that could plausibly change the answer. That is why adding a "
     "node fixes it instantly and waiting does not."),
]

SPEC["kubernetes-autoscaling"] = [
    ("Low level", "What is inside the HPA's control loop?",
     detail("HPA CONTROLLER, EVERY 15s", [
         ("Read", [("metrics.k8s.io", "core", "from metrics-server"),
                   ("current replicas", "core", "scale subresource"),
                   ("resource requests", "hot", "MISSING → no CPU target at all")]),
         ("Decide", [("ratio = current / target", "core", "per metric"),
                     ("tolerance 10%", "warm", "inside it, do nothing"),
                     ("take the MAX across metrics", "warm", None)]),
         ("Damp", [("scale-up: no delay by default", "go", None),
                   ("scale-down stabilisation 5m", "calm", "uses the window's max"),
                   ("min / maxReplicas clamp", "plain", None)]),
     ], inputs=["metrics-server", "Deployment /scale"],
        outputs=["replica count written", "ScalingActive condition"]),
     "The CPU target is a percentage OF THE REQUEST. With no resources.requests "
     "on the container there is no denominator, the HPA reports "
     "ScalingActive=False, and it silently never scales."),

    ("Connection", "What has to happen for load to turn into a new node?",
     flow([("load rises", "plain"),
           ("kubelet cAdvisor", "core", "10s"),
           ("metrics-server", "core", "15s scrape"),
           ("HPA loop", "warm", "15s, +10% tolerance"),
           ("Deployment /scale", "go", "replicas++"),
           ("new Pod → Pending", "hot", "no room"),
           ("cluster-autoscaler", "warm", "10s scan"),
           ("node joins, pod binds", "go", "30s–5m")]),
     "Add the hops up before blaming the HPA: roughly a minute of pure "
     "measurement latency before the first new pod, and minutes more if a node "
     "has to be provisioned. Autoscaling is not a latency control."),
]

SPEC["kubernetes-cluster-operations"] = [
    ("Low level", "What is inside etcd, and what makes it slow?",
     detail("ETCD MEMBER", [
         ("Consensus", [("Raft log", "core", "append-only, replicated"),
                        ("leader election", "warm", "election timeout 1000ms"),
                        ("quorum = N/2 + 1", "hot", "2 of 3; lose 2 and it is read-only")]),
         ("Durability", [("WAL fsync", "hot", "disk latency IS etcd latency"),
                         ("snapshot", "calm", "every 100k revisions"),
                         ("backend .db (bbolt)", "calm", None)]),
         ("Housekeeping", [("compaction", "warm", "drops old revisions"),
                           ("defrag", "warm", "returns free pages to disk"),
                           ("quota 2 GB default", "hot", "exceeded → NOSPACE alarm")]),
     ], inputs=["apiserver writes", "peer replication"],
        outputs=["committed revision", "watch stream"]),
     "Every write is an fsync on a quorum of members, so etcd's p99 is your "
     "disk's p99 — this is the one component where slow storage becomes a "
     "cluster-wide outage rather than a slow application."),

    ("Connection", "What breaks during an upgrade, and in what order?",
     flow([("read the release notes", "plain"),
           ("etcd snapshot", "calm", "the only real rollback"),
           ("control plane first", "core", "n+1 minor max"),
           ("removed APIs bite HERE", "hot", "workloads 404"),
           ("cordon + drain a node", "warm", "PDB gates eviction"),
           ("kubelet upgraded", "go", "rejoins"),
           ("uncordon, next node", "go", "repeat")]),
     "The control plane goes first and must never be more than one minor ahead "
     "of the kubelets. The hop that actually hurts is the removed API: your "
     "manifests stop applying at the moment the new apiserver comes up."),
]

# ═══════════════════════════════════════════════════════════════════════════
# SERVICE MESH
# ═══════════════════════════════════════════════════════════════════════════
SPEC["service-mesh-fundamentals"] = [
    ("Low level", "What is inside the sidecar, and what do the CRDs become?",
     detail("ENVOY SIDECAR", [
         ("The four objects every mesh CRD compiles to", [
             ("Listener", "core", "a port Envoy binds"),
             ("Route", "core", "match → cluster"),
             ("Cluster", "core", "a destination + policy"),
             ("Endpoint", "core", "actual pod IPs")]),
         ("Filter chain on each listener", [
             ("TLS transport socket", "warm", "mTLS terminate / originate"),
             ("HTTP connection manager", "warm", "L7 only if the port is named"),
             ("router filter", "go", None)]),
         ("Interception", [("iptables REDIRECT", "hot", "installed by istio-init"),
                           ("inbound :15006", "plain", None),
                           ("outbound :15001", "plain", None)]),
     ], inputs=["xDS from istiod", "app traffic via iptables"],
        outputs=["mTLS to peer sidecar", "metrics :15090"]),
     "VirtualService and DestinationRule are not runtime objects — istiod "
     "compiles them into these four. `istioctl proxy-config` prints what the "
     "sidecar actually got, which is the only version that matters."),

    ("Connection", "What does a pod-to-pod call really traverse?",
     flow([("app in pod A", "plain"),
           ("iptables REDIRECT", "hot", "localhost"),
           ("sidecar A outbound", "core", ":15001"),
           ("sidecar B inbound", "core", "mTLS, SPIFFE ID"),
           ("iptables → app", "hot", ":15006"),
           ("app in pod B", "go", "localhost"),
           ("metrics + trace headers", "calm", "app must forward them")]),
     "Two extra process hops per call, both localhost, both adding latency and a "
     "place to fail. mTLS identity is established between the sidecars — which is "
     "why policy can talk about services rather than subnets."),
]

SPEC["service-mesh-operations"] = [
    ("Low level", "What is inside istiod?",
     detail("ISTIOD", [
         ("Config", [("watch CRDs", "core", "VirtualService, DestinationRule"),
                     ("watch Services + Endpoints", "core", "from Kubernetes"),
                     ("push context", "calm", "one snapshot per revision")]),
         ("Distribute", [("xDS server", "core", "gRPC :15012"),
                         ("debounce + throttle", "warm", "100ms, batched"),
                         ("per-proxy scoping", "warm", "Sidecar resource narrows it")]),
         ("Identity", [("CA", "go", "signs workload certs"),
                       ("SPIFFE ID per SA", "go", "spiffe://td/ns/<ns>/sa/<sa>"),
                       ("cert rotation 24h", "calm", None)]),
     ], inputs=["kube-apiserver", "CSR from sidecars"],
        outputs=["xDS config push", "signed certs"]),
     "Every sidecar gets the whole mesh's config unless a Sidecar resource "
     "narrows it. On a large mesh that is the difference between a 2 MB push and "
     "a 200 KB one, and it is the first thing to fix when istiod burns CPU."),

    ("Connection", "You applied an AuthorizationPolicy — what happens next?",
     flow([("kubectl apply", "plain"),
           ("apiserver", "core", "CRD stored"),
           ("istiod watch", "warm", "~100ms debounce"),
           ("xDS push", "core", "gRPC :15012"),
           ("sidecars update", "go", "no restart"),
           ("first matching workload", "hot", "now DEFAULT DENY"),
           ("its neighbours", "plain", "unchanged")]),
     "The trap is the last two hops. An AuthorizationPolicy that selects a "
     "workload flips that workload to deny-by-default; workloads it does not "
     "select stay wide open. One policy does not secure a namespace."),
]

# ═══════════════════════════════════════════════════════════════════════════
# OPENSHIFT
# ═══════════════════════════════════════════════════════════════════════════
SPEC["openshift-architecture"] = [
    ("Low level", "What is an operator actually doing in an OpenShift cluster?",
     detail("CLUSTER VERSION OPERATOR AND ITS OPERANDS", [
         ("CVO", [("reads the release image", "core", "a manifest of manifests"),
                  ("reconciles ~30 ClusterOperators", "core", None),
                  ("blocks on Degraded", "hot", "upgrade stops here")]),
         ("Each ClusterOperator", [("owns its operand", "warm", "e.g. the router, etcd"),
                                   ("reports Available / Progressing / Degraded", "warm", None),
                                   ("owns its CRDs", "plain", None)]),
         ("Machine layer", [("MachineConfigOperator", "warm", "node OS config"),
                            ("renders MachineConfig", "calm", "per pool"),
                            ("reboots nodes to apply", "hot", "one pool at a time")]),
     ], inputs=["release payload", "cluster state"],
        outputs=["operands reconciled", "cluster version status"]),
     "This is the real difference from vanilla Kubernetes: the cluster's own "
     "components are workloads managed by operators, so `oc get clusteroperators` "
     "is the single most useful command for 'is the cluster healthy'."),

    ("Connection", "What does oc new-app actually set in motion?",
     flow([("oc new-app <repo>", "plain"),
           ("BuildConfig created", "core", "S2I strategy"),
           ("build pod runs", "warm", "clones, builds"),
           ("image pushed", "go", "internal registry"),
           ("ImageStream tag", "calm", "records the digest"),
           ("trigger fires", "warm", "on tag change"),
           ("Deployment rolls", "go", "new pods"),
           ("Service + Route", "go", "reachable")]),
     "The ImageStream is the hop with no Kubernetes equivalent. It pins a digest "
     "and fires triggers on change, which is how a rebuild redeploys without "
     "anything editing the Deployment."),
]

SPEC["openshift-networking-storage"] = [
    ("Low level", "What is OVN-Kubernetes doing on each node?",
     detail("OVN-KUBERNETES, ONE NODE", [
         ("Control", [("ovnkube-master", "core", "watches pods and policy"),
                      ("northbound DB", "calm", "logical intent"),
                      ("southbound DB", "calm", "physical flows")]),
         ("On the node", [("ovnkube-node", "warm", "programs the bridge"),
                          ("br-int (OVS)", "core", "every pod veth lands here"),
                          ("OpenFlow rules", "warm", "the actual dataplane")]),
         ("Policy", [("NetworkPolicy → ACLs", "hot", "default allow until the first policy"),
                     ("EgressIP / EgressFirewall", "warm", "OpenShift extras"),
                     ("geneve tunnels", "plain", "node to node")]),
     ], inputs=["Pod created (CNI ADD)", "NetworkPolicy"],
        outputs=["pod veth + IP", "flows in br-int"]),
     "NetworkPolicy is translated to OVS ACLs, and the translation is where the "
     "default flips: a namespace with no policy allows everything, and the first "
     "policy selecting a pod denies everything else to it."),

    ("Connection", "How does outside traffic reach a pod, and how does a pod reach its disk?",
     flow([("external client", "plain"),
           ("DNS → *.apps wildcard", "core", None),
           ("HAProxy router pod", "core", ":443 TLS"),
           ("Route → Service", "warm", "edge / passthrough"),
           ("EndpointSlice → pod IP", "warm", None),
           ("br-int flows", "go", "geneve if cross-node"),
           ("pod :8080", "go", None),
           ("PVC → CSI mount", "calm", "attach, then mount")]),
     "The Route is OpenShift's own object and terminates TLS in the router by "
     "default, which is why a passthrough Route behaves so differently: the pod "
     "must then serve TLS itself."),
]

SPEC["openshift-operations"] = [
    ("Low level", "What is inside the cluster monitoring stack?",
     detail("CLUSTER MONITORING", [
         ("Collect", [("Prometheus (platform)", "core", "cluster components"),
                      ("Prometheus (user workload)", "core", "opt-in, separate"),
                      ("node-exporter", "warm", "per node"),
                      ("kube-state-metrics", "warm", "object state")]),
         ("Route", [("Alertmanager", "hot", "dedupe, silence, route"),
                    ("Thanos Querier", "warm", "one query view"),
                    ("retention 15d default", "calm", "not long-term storage")]),
         ("Surface", [("console dashboards", "plain", None),
                      ("PrometheusRule CRs", "warm", "alerts as objects"),
                      ("remote-write", "plain", "for anything longer")]),
     ], inputs=["ServiceMonitor", "cluster operators"],
        outputs=["alerts to receivers", "metrics API"]),
     "Platform and user-workload monitoring are two separate Prometheus "
     "instances on purpose. Your application's ServiceMonitor is ignored by the "
     "platform one, which is the usual reason a metric never appears."),

    ("Connection", "What does an upgrade traverse?",
     flow([("pick a channel", "plain"),
           ("CVO checks the graph", "core", "signed release"),
           ("release image verified", "warm", "signature"),
           ("ClusterOperators, in order", "core", "one at a time"),
           ("any Degraded → stop", "hot", "upgrade parks here"),
           ("MachineConfig rendered", "warm", "per pool"),
           ("nodes drain + reboot", "hot", "PDB gates it"),
           ("version reported", "go", "complete")]),
     "The upgrade stops on the first Degraded ClusterOperator, which is a "
     "feature: it parks rather than proceeding into a broken cluster. A PDB that "
     "can never be satisfied parks it just as effectively at the drain hop."),
]


def for_slug(slug):
    """The (kind, question, svg, caption) tuples for a topic, or ()."""
    return SPEC.get(slug, ())


if __name__ == "__main__":
    print(f"{len(SPEC)} topics with low-level + connection diagrams:")
    for k, v in sorted(SPEC.items()):
        print(f"  {k:<36} {len(v)} diagram(s)")
