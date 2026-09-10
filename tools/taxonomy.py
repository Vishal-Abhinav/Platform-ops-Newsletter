import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

# Platform Ops — 2026 master taxonomy.
# Single source of truth. Counts in index.html and README are DERIVED from this,
# never hand-maintained.
#
#   L = live      — a published page genuinely covers this; must carry a link
#   P = pipeline  — next up, adjacent to work already published
#   -  = planned  — backlog
#
# Live links, by page:
K8A = "DevOps/K8/ARCHITECTURE/k8-architecture.html"
K8N = "DevOps/K8/Networking/k8-networking.html"
K8E = "DevOps/K8/ERROR/K8-error.html"
K8S = "DevOps/K8/STORAGE/k8-storage.html"
K8O = "DevOps/K8/OBSERVABILITY/k8-observability.html"
CICD = "DevOps/CICD/cicd-pipelines.html"
INC = "SRE/INCIDENT-MANAGEMENT/incident-management.html"
LXF = "Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html"
LXA = "Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html"
LXT = "Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html"
GLO = "Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html"
CFU = "Foundation/COMPUTER-FUNDAMENTALS/computer-fundamentals.html"
OSY = "Foundation/OPERATING-SYSTEMS/operating-systems.html"
SHB = "Foundation/SHELL-AND-BASH/shell-and-bash.html"
PYT = "Foundation/PYTHON/python.html"
GIT = "Foundation/GIT-VERSION-CONTROL/git-version-control.html"
CLX = "Commands/LINUX-COMMANDS/linux-commands.html"
CK8 = "Commands/KUBERNETES-COMMANDS/kubernetes-commands.html"
CDK = "Commands/DOCKER-COMMANDS/docker-commands.html"

# pillar -> [ (category, icon, [ (topic, status, href|None), ... ]) ]
PILLARS = [
("Foundation", [
 ("Foundation", "🧱", [
   ("Computer Fundamentals","L",CFU),("Operating Systems","L",OSY),
   ("Linux","L",LXF),("Unix","L",GLO),("Windows Server","-",None),
   ("Shell & Bash","L",SHB),("Python","L",PYT),("Programming Fundamentals","-",None),
   ("Data Structures & Algorithms","-",None),("Git & Version Control","L",GIT)]),
]),

("Infrastructure", [
 ("IT Infrastructure", "🏗️", [
   ("IT Infrastructure","P",None),("Server Administration","P",None),("Hardware","-",None),
   ("Data Center","-",None),("Rack / Power / Cooling","-",None),("Capacity Planning","P",None),
   ("High Availability","P",None),("Fault Tolerance","-",None),("Disaster Recovery","P",None),
   ("Business Continuity","-",None),("Infrastructure Architecture","-",None),
   ("Enterprise Infrastructure","-",None)]),
 ("Storage", "💽", [
   ("Storage Fundamentals","P",None),("Local Storage","-",None),("RAID","-",None),
   ("LVM","L",LXA),("SAN","-",None),("NAS","-",None),("NFS","-",None),("SMB / CIFS","-",None),
   ("Object Storage","-",None),("Block Storage","-",None),("File Storage","-",None),
   ("Storage Replication","-",None),("Storage Performance","-",None),("Storage Backup","-",None),
   ("Storage Troubleshooting","P",None)]),
 ("Virtualization", "🖥️", [
   ("Virtualization Fundamentals","P",None),("VMware","-",None),("ESXi","-",None),
   ("vCenter","-",None),("KVM","-",None),("QEMU","-",None),("Hyper-V","-",None),
   ("Virtual Networking","-",None),("Virtual Storage","-",None),("VM Lifecycle","-",None),
   ("VM HA / DR","-",None)]),
]),

("Networking", [
 ("Networking", "🌐", [
   ("Networking Fundamentals","P",None),("OSI Model","P",None),("TCP/IP","P",None),
   ("IPv4","-",None),("IPv6","-",None),("Subnetting","-",None),("VLAN","-",None),
   ("Switching","-",None),("Routing","-",None),("BGP","-",None),("OSPF","-",None),
   ("EIGRP","-",None),("MPLS","-",None),("ARP","-",None),("ICMP","-",None),("TCP","-",None),
   ("UDP","-",None),("DNS","L",K8N),("DHCP","-",None),("NAT","-",None),("Proxy","-",None),
   ("VPN","-",None),("IPSec","-",None),("Load Balancing","P",None),("Network Security","-",None),
   ("Firewall","-",None),("WAF","-",None),("SDN","-",None),("SD-WAN","-",None),
   ("Network Automation","-",None),("Network Monitoring","-",None)]),
]),

("Cloud", [
 ("Cloud", "☁️", [
   ("Cloud Fundamentals","P",None),("AWS","P",None),("Microsoft Azure","P",None),
   ("Google Cloud","-",None),("Cloud Networking","-",None),("Cloud Compute","-",None),
   ("Cloud Storage","-",None),("Cloud Databases","-",None),("Cloud IAM","-",None),
   ("Cloud Security","-",None),("Cloud Monitoring","-",None),("Cloud Backup","-",None),
   ("Cloud DR","-",None),("Hybrid Cloud","P",None),("Multi-Cloud","-",None),
   ("Cloud Migration","-",None),("Cloud Architecture","-",None)]),
]),

("Delivery", [
 ("DevOps", "⚙️", [
   ("DevOps Fundamentals","P",None),("DevOps Culture","-",None),("CI/CD","L",CICD),
   ("Continuous Integration","L",CICD),("Continuous Delivery","L",CICD),
   ("Continuous Deployment","L",CICD),("Jenkins","L",CICD),("GitLab CI/CD","L",CICD),
   ("GitHub Actions","P",None),("Azure DevOps","-",None),("Build Automation","-",None),
   ("Artifact Management","-",None),("Release Automation","-",None),
   ("Deployment Strategies","L",CICD),("Blue/Green Deployment","L",CICD),
   ("Canary Deployment","L",CICD),("Rolling Deployment","P",None),("Rollback","P",None),
   ("Feature Flags","-",None),("Pipeline Security","P",None),("Pipeline Optimization","-",None)]),
 ("Containers", "📦", [
   ("Containers","P",None),("Docker","P",None),("Podman","-",None),("Containerd","-",None),
   ("CRI","-",None),("OCI","-",None),("Container Images","P",None),
   ("Container Registries","-",None),("Container Networking","P",None),
   ("Container Storage","-",None),("Container Security","P",None),
   ("Container Troubleshooting","P",None)]),
 ("Infrastructure as Code", "📐", [
   ("Infrastructure as Code","P",None),("Terraform","P",None),("OpenTofu","-",None),
   ("Pulumi","-",None),("Terraform Modules","-",None),("Terraform State","P",None),
   ("Remote State","-",None),("Terraform Providers","-",None),("IaC Security","-",None),
   ("IaC Testing","-",None),("IaC Drift Management","-",None)]),
 ("Configuration Management", "🔧", [
   ("Configuration Management","P",None),("Ansible","P",None),("Ansible Playbooks","P",None),
   ("Roles","-",None),("Inventories","-",None),("Variables","-",None),("Templates","-",None),
   ("Ansible Vault","-",None),("AWX / Automation Platform","-",None),("Puppet","-",None),
   ("Chef","-",None),("Salt","-",None)]),
 ("GitOps", "🔀", [
   ("GitOps","L",CICD),("Argo CD","L",CICD),("Flux","L",CICD),
   ("Git-based Infrastructure","P",None),("Declarative Deployment","P",None),
   ("Drift Detection","-",None),("Progressive Delivery","-",None),("GitOps Security","-",None)]),
 ("Platform Engineering", "🛠️", [
   ("Platform Engineering","P",None),("Internal Developer Platform","P",None),
   ("Developer Experience","-",None),("Self-Service Infrastructure","-",None),
   ("Golden Paths","-",None),("Platform-as-a-Product","-",None),("Backstage","P",None),
   ("Developer Portals","-",None),("Platform APIs","-",None),("Platform Governance","-",None),
   ("Platform Automation","-",None),("Platform Security","-",None)]),
]),

("Kubernetes", [
 ("Kubernetes", "☸️", [
   ("Kubernetes Fundamentals","L",K8A),("Kubernetes Architecture","L",K8A),("Pods","L",K8A),
   ("Deployments","L",K8A),("ReplicaSets","P",None),("DaemonSets","P",None),
   ("StatefulSets","L",K8S),("Jobs / CronJobs","-",None),("Services","L",K8N),
   ("Ingress","L",K8N),("ConfigMaps","P",None),("Secrets","P",None),("Volumes","L",K8S),
   ("Persistent Volumes","L",K8S),("Storage Classes","L",K8S),("RBAC","P",None),
   ("Namespaces","P",None),("Resource Requests/Limits","L",K8A),("Probes","P",None),
   ("Scheduling","L",K8A),("Taints / Tolerations","P",None),("Affinity / Anti-Affinity","P",None),
   ("Autoscaling","P",None),("HPA","P",None),("VPA","P",None),("Cluster Autoscaling","-",None),
   ("Kubernetes Networking","L",K8N),("CNI","L",K8N),("CSI","L",K8S),
   ("Kubernetes Security","P",None),("Kubernetes Troubleshooting","L",K8E),
   ("Kubernetes Upgrade","-",None),("Kubernetes Backup","-",None),
   ("Multi-Cluster Kubernetes","-",None),("Kubernetes Disaster Recovery","-",None)]),
 ("OpenShift", "🔴", [
   ("OpenShift Fundamentals","P",None),("OpenShift Architecture","P",None),
   ("Projects","-",None),("Routes","-",None),("Operators","-",None),("SCC","L",K8E),
   ("OpenShift Networking","-",None),("OpenShift Storage","-",None),
   ("OpenShift Monitoring","-",None),("OpenShift Logging","-",None),
   ("OpenShift Security","-",None),("OpenShift Troubleshooting","L",K8E),
   ("OpenShift Upgrades","-",None)]),
 ("Service Mesh", "🕸️", [
   ("Service Mesh","P",None),("Istio","P",None),("Envoy","-",None),("Linkerd","-",None),
   ("Traffic Management","-",None),("mTLS","-",None),("Service-to-Service Security","-",None),
   ("Service Discovery","-",None),("Observability in Service Mesh","-",None),
   ("Multi-Cluster Service Mesh","-",None)]),
]),

("Reliability", [
 ("SRE", "📡", [
   ("SRE Fundamentals","P",None),("SLI","P",None),("SLO","P",None),("SLA","P",None),
   ("Error Budget","P",None),("Reliability Engineering","P",None),("Availability","-",None),
   ("Reliability","-",None),("Scalability","-",None),("Latency","-",None),("MTTR","L",INC),
   ("MTBF","-",None),("Incident Management","L",INC),("Problem Management","P",None),
   ("RCA","L",INC),("Postmortem","L",INC),("Toil Reduction","-",None),
   ("Capacity Planning","-",None),("Reliability Testing","-",None),
   ("Chaos Engineering","P",None),("Resilience Engineering","-",None),
   ("Service Health","-",None),("Production Readiness","-",None),
   ("Operational Readiness","-",None),("SRE Automation","-",None)]),
 ("Observability", "📊", [
   ("Observability","L",K8O),("Monitoring","L",K8O),("Metrics","L",K8O),("Logs","L",K8O),
   ("Traces","L",K8O),("Profiles","-",None),("OpenTelemetry","P",None),
   ("Prometheus","L",K8O),("Grafana","L",K8O),("Alertmanager","L",K8O),("Loki","L",K8O),
   ("Jaeger","L",K8O),("Tempo","P",None),("ELK","P",None),("OpenSearch","-",None),
   ("Distributed Tracing","L",K8O),("Application Performance Monitoring","-",None),
   ("Synthetic Monitoring","-",None),("Real User Monitoring","-",None),
   ("Alert Engineering","P",None),("Telemetry Pipelines","-",None),
   ("Observability Architecture","-",None)]),
 ("Logging", "📜", [
   ("Linux Logging","L",LXA),("Syslog","P",None),("Journald","L",LXA),
   ("Log Rotation","P",None),("Centralized Logging","P",None),("Logstash","-",None),
   ("Fluent Bit","-",None),("Fluentd","-",None),("Elasticsearch","-",None),
   ("OpenSearch","-",None),("Kibana","-",None),("Log Correlation","-",None),
   ("Log Retention","-",None),("Log Security","-",None)]),
 ("Performance Engineering", "⚡", [
   ("CPU Performance","L",LXT),("Memory Performance","L",LXT),("Disk I/O","L",LXT),
   ("Network Performance","P",None),("Application Performance","-",None),
   ("Database Performance","-",None),("Load Testing","-",None),("Stress Testing","-",None),
   ("Benchmarking","-",None),("Profiling","P",None),("Capacity Modeling","-",None),
   ("Performance Troubleshooting","L",LXT)]),
 ("Troubleshooting", "🔍", [
   ("Linux Troubleshooting","L",LXT),("Network Troubleshooting","P",None),
   ("Storage Troubleshooting","P",None),("Database Troubleshooting","-",None),
   ("Application Troubleshooting","-",None),("Kubernetes Troubleshooting","L",K8E),
   ("Cloud Troubleshooting","-",None),("Performance Troubleshooting","L",LXT),
   ("Security Troubleshooting","-",None),("Production Incident Troubleshooting","L",INC),
   ("Root Cause Analysis","L",INC),("Failure Analysis","-",None)]),
 ("Backup & DR", "🗄️", [
   ("Backup Fundamentals","P",None),("Full Backup","-",None),("Incremental Backup","-",None),
   ("Differential Backup","-",None),("Snapshot","-",None),("Replication","-",None),
   ("RPO","P",None),("RTO","P",None),("DR Architecture","P",None),("Active/Active","-",None),
   ("Active/Passive","-",None),("Backup Validation","-",None),("Restore Testing","-",None),
   ("DR Drill","-",None),("Failover","-",None),("Failback","-",None)]),
 ("ITSM & Operations", "🎫", [
   ("ITIL","-",None),("Incident Management","L",INC),("Problem Management","P",None),
   ("Change Management","P",None),("Release Management","-",None),("Service Request","-",None),
   ("Event Management","-",None),("CMDB","-",None),("Asset Management","-",None),
   ("Configuration Management","-",None),("ServiceNow","-",None),("Remedy","-",None),
   ("CAB","-",None),("Change Windows","-",None),("Operational Documentation","-",None)]),
]),

("Security", [
 ("Security", "🛡️", [
   ("Cybersecurity Fundamentals","P",None),("Infrastructure Security","P",None),
   ("Network Security","-",None),("Linux Security","P",None),("Cloud Security","-",None),
   ("Container Security","P",None),("Kubernetes Security","P",None),
   ("Application Security","-",None),("DevSecOps","P",None),("Zero Trust","-",None),
   ("IAM","-",None),("RBAC","P",None),("PAM","-",None),("LDAP","-",None),
   ("Active Directory","-",None),("SSO","-",None),("OAuth","-",None),("OIDC","-",None),
   ("SAML","-",None),("PKI","-",None),("TLS/SSL","P",None),("Certificates","P",None),
   ("Secrets Management","P",None),("HashiCorp Vault","P",None),
   ("Vulnerability Management","-",None),("Security Scanning","-",None),("SIEM","-",None),
   ("SOC","-",None),("Threat Detection","-",None),("Compliance","-",None),
   ("Security Auditing","-",None)]),
 ("Supply Chain Security", "🔗", [
   ("Software Supply Chain Security","P",None),("SBOM","P",None),("SLSA","-",None),
   ("Artifact Signing","-",None),("Image Signing","P",None),("Cosign","-",None),
   ("Admission Control","P",None),("Policy as Code","P",None),("OPA","-",None),
   ("Gatekeeper","-",None),("Kyverno","-",None),("Dependency Security","-",None),
   ("Container Image Scanning","P",None),("Secrets Scanning","-",None),
   ("CI/CD Security","P",None)]),
]),

("Data & Applications", [
 ("Database", "🗃️", [
   ("Database Fundamentals","P",None),("MySQL","-",None),("PostgreSQL","P",None),
   ("Oracle","-",None),("SQL Server","-",None),("MongoDB","-",None),("Redis","-",None),
   ("Database Replication","-",None),("Database HA","P",None),("Database Backup","-",None),
   ("Database Recovery","-",None),("Database Performance","-",None),
   ("Connection Management","-",None),("Query Optimization","-",None),
   ("Database Monitoring","-",None),("Database Security","-",None)]),
 ("Middleware", "🧩", [
   ("Application Servers","-",None),("Nginx","P",None),("Apache","-",None),("Tomcat","-",None),
   ("WildFly","-",None),("JBoss","-",None),("RabbitMQ","-",None),("Apache Kafka","P",None),
   ("Redis","-",None),("Message Queues","P",None),("Event Streaming","-",None),
   ("Event-Driven Architecture","-",None),("Middleware HA","-",None),
   ("Middleware Troubleshooting","-",None)]),
 ("API & Microservices", "🔌", [
   ("REST APIs","P",None),("HTTP/HTTPS","P",None),("API Gateway","P",None),
   ("API Management","-",None),("API Security","-",None),("Authentication","-",None),
   ("Authorization","-",None),("Rate Limiting","-",None),("Microservices","P",None),
   ("Service Discovery","-",None),("Circuit Breaker","-",None),("Retry","-",None),
   ("Timeout","-",None),("Bulkhead","-",None),("Distributed Transactions","-",None),
   ("Event-Driven Microservices","-",None)]),
 ("Distributed Systems", "🕮", [
   ("Distributed Systems","P",None),("Consensus","-",None),("Leader Election","-",None),
   ("Replication","-",None),("Consistency","-",None),("Eventual Consistency","-",None),
   ("Distributed Transactions","-",None),("Caching","-",None),("Distributed Locking","-",None),
   ("Partition Tolerance","-",None),("CAP Theorem","P",None),("Failure Domains","-",None),
   ("Quorum","L",K8E),("Distributed Coordination","-",None)]),
]),

("Commands", [
 ("Linux Commands", "🐧", [
   ("Files & Navigation","L",CLX),("Permissions & Ownership","L",CLX),
   ("Text Processing","L",CLX),("Processes & Signals","L",CLX),
   ("Users & Groups","L",CLX),("Package Management","L",CLX),
   ("Disk & Filesystem","L",CLX),("Search & Locate","L",CLX),
   ("Scheduling & Boot","L",CLX),("Networking Commands","L",CLX)]),
 ("systemd Commands", "⚙️", [
   ("systemctl","P",None),("journalctl","P",None),("Unit Files","P",None),
   ("Timers","P",None),("Targets","-",None),("systemd-analyze","P",None),
   ("loginctl","-",None),("systemd-run","-",None),("Drop-ins","-",None),
   ("Service Debugging","P",None)]),
 ("Docker Commands", "🐳", [
   ("Running Containers","L",CDK),("Images & Building","L",CDK),
   ("Inspecting & Logs","L",CDK),("Networking & Volumes","L",CDK),
   ("Compose","L",CDK),("Cleanup & Pruning","L",CDK),
   ("Registry & Push","P",None),("buildx & Multi-arch","P",None),
   ("Container Debugging","P",None),("Security Scanning","-",None)]),
 ("Kubernetes Commands", "☸️", [
   ("Inspecting","L",CK8),("Applying & Deleting","L",CK8),
   ("Logs, Exec & Debug","L",CK8),("Rollouts & Scaling","L",CK8),
   ("Nodes & Scheduling","L",CK8),("Contexts & Access","L",CK8),
   ("Output & Scripting","L",CK8),("kustomize","P",None),
   ("Helm","P",None),("krew Plugins","-",None)]),
 ("OpenShift Commands", "🔴", [
   ("oc login & Projects","P",None),("oc new-app","P",None),("Routes","P",None),
   ("oc adm","P",None),("Security Context Constraints","P",None),
   ("must-gather","P",None),("Image Streams","-",None),("BuildConfigs","-",None),
   ("oc debug node","P",None),("Cluster Operators","-",None)]),
 ("Ansible Commands", "🔧", [
   ("Ad-hoc Commands","P",None),("ansible-playbook","P",None),
   ("Inventory & Limits","P",None),("ansible-vault","P",None),
   ("ansible-galaxy","-",None),("Facts & Gathering","P",None),
   ("Check & Diff Mode","P",None),("Tags","-",None),("ansible-lint","-",None),
   ("Callback Plugins","-",None)]),
 ("Terraform Commands", "📐", [
   ("init & providers","P",None),("plan","P",None),("apply","P",None),
   ("State Commands","P",None),("import","P",None),("Workspaces","-",None),
   ("fmt & validate","P",None),("Outputs","-",None),
   ("taint & replace","-",None),("destroy & targeting","-",None)]),
 ("Networking Commands", "🌐", [
   ("ip & Addressing","L",CLX),("ss & Sockets","L",CLX),("DNS Tools","L",CLX),
   ("curl & HTTP","L",CLX),("tcpdump","L",CLX),("Routing","P",None),
   ("Firewall (nft/iptables)","P",None),("ethtool","P",None),
   ("mtr & traceroute","L",CLX),("Bandwidth Testing","-",None)]),
 ("Performance Commands", "⚡", [
   ("top & htop","P",None),("vmstat","P",None),("iostat","P",None),
   ("sar & sysstat","P",None),("perf","P",None),("strace","P",None),
   ("lsof","P",None),("pidstat","P",None),("bpftrace","-",None),
   ("Flame Graphs","-",None)]),
 ("Storage Commands", "💽", [
   ("lsblk & blkid","L",CLX),("df & du","L",CLX),("mount & fstab","L",CLX),
   ("LVM Commands","L",CLX),("mkfs & fsck","L",CLX),("NFS Commands","-",None),
   ("Quotas","-",None),("Swap","-",None),("smartctl","-",None),
   ("Storage Benchmarking","-",None)]),
]),

("Modern Ops", [
 ("AI Infrastructure", "🤖", [
   ("AI Infrastructure","P",None),("GPU Infrastructure","P",None),("GPU Scheduling","P",None),
   ("GPU Kubernetes","P",None),("AI Workloads on Kubernetes","P",None),
   ("Model Serving","P",None),("Inference Infrastructure","-",None),("LLMOps","-",None),
   ("MLOps","-",None),("Model Monitoring","-",None),("Model Observability","-",None),
   ("AI Cost Management","-",None),("AI Reliability","-",None),("AI Security","-",None),
   ("AI Governance","-",None),("RAG Infrastructure","-",None),("Vector Databases","-",None),
   ("Model Gateways","-",None),("AI CI/CD","-",None),("AI Infrastructure Automation","-",None)]),
 ("AIOps", "🧠", [
   ("AIOps","P",None),("AI Incident Detection","-",None),("AI Root Cause Analysis","P",None),
   ("AI Alert Correlation","-",None),("AI Log Analysis","-",None),
   ("AI Capacity Forecasting","-",None),("AI Remediation","-",None),
   ("AI-assisted Troubleshooting","-",None),("AI Operations Agents","-",None),
   ("Agentic DevOps","P",None),("Agentic SRE","P",None),("Agentic CloudOps","-",None),
   ("Human-in-the-loop Automation","-",None),("AI Operational Guardrails","-",None)]),
 ("FinOps", "💰", [
   ("FinOps","P",None),("Cloud Cost Management","P",None),("Cost Allocation","-",None),
   ("Tagging","-",None),("Resource Optimization","-",None),("Rightsizing","P",None),
   ("Reserved Capacity","-",None),("Spot / Preemptible Instances","P",None),
   ("Kubernetes Cost Management","P",None),("Cloud Waste Management","-",None),
   ("Cost Governance","-",None)]),
 ("Automation", "🔁", [
   ("Shell Automation","L",LXA),("Bash Automation","L",SHB),("Python Automation","L",PYT),
   ("Ansible Automation","P",None),("Terraform Automation","-",None),
   ("API Automation","-",None),("Cloud Automation","-",None),
   ("Kubernetes Automation","P",None),("Network Automation","-",None),
   ("Database Automation","-",None),("Monitoring Automation","-",None),
   ("Self-Healing Infrastructure","P",None)]),
 ("Architecture", "🏛️", [
   ("System Architecture","P",None),("Cloud Architecture","-",None),
   ("Microservice Architecture","P",None),("Distributed Architecture","-",None),
   ("Event-Driven Architecture","-",None),("Multi-Tenant Architecture","-",None),
   ("Scalable Architecture","-",None),("Resilient Architecture","-",None),
   ("Zero-Downtime Architecture","P",None),("Multi-Region Architecture","-",None),
   ("Multi-Cloud Architecture","-",None),("Hybrid Architecture","-",None)]),
]),
]

def stats():
    live = pipe = plan = 0
    for _, cats in PILLARS:
        for _, _, topics in cats:
            for _, st, _ in topics:
                if st == "L": live += 1
                elif st == "P": pipe += 1
                else: plan += 1
    return live, pipe, plan

def cat_stats(topics):
    l = sum(1 for _, s, _ in topics if s == "L")
    p = sum(1 for _, s, _ in topics if s == "P")
    return l, p, len(topics) - l - p

if __name__ == "__main__":
    l, p, n = stats()
    cats = sum(len(c) for _, c in PILLARS)
    print(f"pillars={len(PILLARS)} categories={cats} topics={l+p+n}")
    print(f"live={l} pipeline={p} planned={n}")
