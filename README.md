<div align="center">

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗ ██╗      █████╗ ████████╗███████╗ ██████╗ ██████╗ ███╗   ███╗   ║
║   ██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗████╗ ████║   ║
║   ██████╔╝██║     ███████║   ██║   █████╗  ██║   ██║██████╔╝██╔████╔██║   ║
║   ██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║   ║
║   ██║     ███████╗██║  ██║   ██║   ██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║   ║
║   ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝   ║
║                                                                           ║
║                      O P S   ×   N E W S L E T T E R                      ║
║                  Tech with Vishal Abhinav  ·  Open Source                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

![Live Issues](https://img.shields.io/badge/Live%20Issues-11-e53935?style=for-the-badge&logo=gitbook&logoColor=white)
![Glossary](https://img.shields.io/badge/Glossary-190%20Terms-f59e0b?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/Vishal-Abhinav/Platform-ops-Newsletter?style=for-the-badge&logo=github&color=00c2d4)
![License](https://img.shields.io/badge/License-MIT-84cc16?style=for-the-badge)
![Pages](https://img.shields.io/badge/GitHub%20Pages-Deployed-0a66c2?style=for-the-badge&logo=githubpages&logoColor=white)

<br/>

**A free, open-source knowledge base for DevOps Engineers, SREs, and Platform Builders.**
*Deep-dive issues · Architecture diagrams · Runbooks · A 190-term Linux & Unix glossary.*

### 🌐 **[Read it live → vishal-abhinav.github.io/Platform-ops-Newsletter](https://vishal-abhinav.github.io/Platform-ops-Newsletter/)**

[📚 Issues](#-published-issues) · [🗺️ Knowledge Map](#️-knowledge-map) · [🗂️ Structure](#️-repository-structure) · [🚀 Run Locally](#-quick-start)

</div>

---

## 🧭 What is This?

> *"I write the runbooks I wish existed the first time something broke at 2 AM."*

**Platform Ops** is a monthly technical newsletter covering the **Platform Engineering, Kubernetes, SRE and Infrastructure** stack — written by one practitioner working in production, not slideware.

This repository *is* the newsletter. Every issue is a self-contained HTML page served straight from GitHub Pages — no build step, no framework, no tracking. Fork it, read it offline, or lift a diagram for your own docs.

**Currently in this repo:** 11 monthly issue pages, 5 Foundation reference deep-dives, a 190-term Linux & Unix glossary with 12 standalone term pages, 34 category pages, 2 section hubs and a homepage index — 65 pages in total.

---

## 🗺️ Knowledge Map

The **2026 master map** — every subject this newsletter intends to cover, in one place.
521 topics, grouped into 33 categories and 10 pillars. The homepage renders
this same map with search and status filters; both are generated from one source
of truth, so the numbers here and there can never disagree.

| | Pillar | Categories | ✅ Live | 🔸 Pipeline | · Planned | Total |
|:--|:--|--:|--:|--:|--:|--:|
| `01` | **Foundation** | 1 | 7 | 0 | 3 | 10 |
| `02` | **Infrastructure** | 3 | 1 | 8 | 29 | 38 |
| `03` | **Networking** | 1 | 1 | 4 | 26 | 31 |
| `04` | **Cloud** | 1 | 0 | 4 | 13 | 17 |
| `05` | **Delivery** | 6 | 12 | 22 | 42 | 76 |
| `06` | **Kubernetes** | 3 | 18 | 17 | 23 | 58 |
| `07` | **Reliability** | 7 | 27 | 25 | 64 | 116 |
| `08` | **Security** | 2 | 0 | 18 | 28 | 46 |
| `09` | **Data & Applications** | 4 | 1 | 12 | 47 | 60 |
| `10` | **Modern Ops** | 5 | 3 | 21 | 45 | 69 |
| | **Total** | **33** | **70** | **131** | **320** | **521** |

**Status meanings**

| | Meaning |
|:--|:--|
| ✅ **Live** | A published issue covers it, and the topic links straight to that page. |
| 🔸 **Pipeline** | Next up — adjacent to a series already running, so it's queued rather than hypothetical. |
| · **Planned** | On the backlog. No date attached; it moves to pipeline when the series in front of it lands. |

Live topics point at the 16 deep-dives already in this repo — 11 monthly issues plus the
Foundation reference pages — so one page can light up several topics at once. Issue #051 alone
covers Prometheus, Grafana, Loki, Jaeger and distributed tracing.

<br>

<details>
<summary><b>01 · Foundation</b> — 1 category · 7 live · 0 pipeline · 3 planned</summary>

**🧱 Foundation** — 7 live · 0 pipeline · 3 planned  
✅ [Computer Fundamentals](./Foundation/COMPUTER-FUNDAMENTALS/computer-fundamentals.html) &nbsp;
✅ [Operating Systems](./Foundation/OPERATING-SYSTEMS/operating-systems.html) &nbsp;
✅ [Linux](./Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html) &nbsp;
✅ [Unix](./Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html) &nbsp;
· Windows Server &nbsp;
✅ [Shell & Bash](./Foundation/SHELL-AND-BASH/shell-and-bash.html) &nbsp;
✅ [Python](./Foundation/PYTHON/python.html) &nbsp;
· Programming Fundamentals &nbsp;
· Data Structures & Algorithms &nbsp;
✅ [Git & Version Control](./Foundation/GIT-VERSION-CONTROL/git-version-control.html) &nbsp;

</details>

<details>
<summary><b>02 · Infrastructure</b> — 3 categories · 1 live · 8 pipeline · 29 planned</summary>

**🏗️ IT Infrastructure** — 0 live · 5 pipeline · 7 planned  
🔸 IT Infrastructure &nbsp;
🔸 Server Administration &nbsp;
· Hardware &nbsp;
· Data Center &nbsp;
· Rack / Power / Cooling &nbsp;
🔸 Capacity Planning &nbsp;
🔸 High Availability &nbsp;
· Fault Tolerance &nbsp;
🔸 Disaster Recovery &nbsp;
· Business Continuity &nbsp;
· Infrastructure Architecture &nbsp;
· Enterprise Infrastructure &nbsp;

**💽 Storage** — 1 live · 2 pipeline · 12 planned  
🔸 Storage Fundamentals &nbsp;
· Local Storage &nbsp;
· RAID &nbsp;
✅ [LVM](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) &nbsp;
· SAN &nbsp;
· NAS &nbsp;
· NFS &nbsp;
· SMB / CIFS &nbsp;
· Object Storage &nbsp;
· Block Storage &nbsp;
· File Storage &nbsp;
· Storage Replication &nbsp;
· Storage Performance &nbsp;
· Storage Backup &nbsp;
🔸 Storage Troubleshooting &nbsp;

**🖥️ Virtualization** — 0 live · 1 pipeline · 10 planned  
🔸 Virtualization Fundamentals &nbsp;
· VMware &nbsp;
· ESXi &nbsp;
· vCenter &nbsp;
· KVM &nbsp;
· QEMU &nbsp;
· Hyper-V &nbsp;
· Virtual Networking &nbsp;
· Virtual Storage &nbsp;
· VM Lifecycle &nbsp;
· VM HA / DR &nbsp;

</details>

<details>
<summary><b>03 · Networking</b> — 1 category · 1 live · 4 pipeline · 26 planned</summary>

**🌐 Networking** — 1 live · 4 pipeline · 26 planned  
🔸 Networking Fundamentals &nbsp;
🔸 OSI Model &nbsp;
🔸 TCP/IP &nbsp;
· IPv4 &nbsp;
· IPv6 &nbsp;
· Subnetting &nbsp;
· VLAN &nbsp;
· Switching &nbsp;
· Routing &nbsp;
· BGP &nbsp;
· OSPF &nbsp;
· EIGRP &nbsp;
· MPLS &nbsp;
· ARP &nbsp;
· ICMP &nbsp;
· TCP &nbsp;
· UDP &nbsp;
✅ [DNS](./DevOps/K8/Networking/k8-networking.html) &nbsp;
· DHCP &nbsp;
· NAT &nbsp;
· Proxy &nbsp;
· VPN &nbsp;
· IPSec &nbsp;
🔸 Load Balancing &nbsp;
· Network Security &nbsp;
· Firewall &nbsp;
· WAF &nbsp;
· SDN &nbsp;
· SD-WAN &nbsp;
· Network Automation &nbsp;
· Network Monitoring &nbsp;

</details>

<details>
<summary><b>04 · Cloud</b> — 1 category · 0 live · 4 pipeline · 13 planned</summary>

**☁️ Cloud** — 0 live · 4 pipeline · 13 planned  
🔸 Cloud Fundamentals &nbsp;
🔸 AWS &nbsp;
🔸 Microsoft Azure &nbsp;
· Google Cloud &nbsp;
· Cloud Networking &nbsp;
· Cloud Compute &nbsp;
· Cloud Storage &nbsp;
· Cloud Databases &nbsp;
· Cloud IAM &nbsp;
· Cloud Security &nbsp;
· Cloud Monitoring &nbsp;
· Cloud Backup &nbsp;
· Cloud DR &nbsp;
🔸 Hybrid Cloud &nbsp;
· Multi-Cloud &nbsp;
· Cloud Migration &nbsp;
· Cloud Architecture &nbsp;

</details>

<details>
<summary><b>05 · Delivery</b> — 6 categories · 12 live · 22 pipeline · 42 planned</summary>

**⚙️ DevOps** — 9 live · 5 pipeline · 7 planned  
🔸 DevOps Fundamentals &nbsp;
· DevOps Culture &nbsp;
✅ [CI/CD](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Continuous Integration](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Continuous Delivery](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Continuous Deployment](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Jenkins](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [GitLab CI/CD](./DevOps/CICD/cicd-pipelines.html) &nbsp;
🔸 GitHub Actions &nbsp;
· Azure DevOps &nbsp;
· Build Automation &nbsp;
· Artifact Management &nbsp;
· Release Automation &nbsp;
✅ [Deployment Strategies](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Blue/Green Deployment](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Canary Deployment](./DevOps/CICD/cicd-pipelines.html) &nbsp;
🔸 Rolling Deployment &nbsp;
🔸 Rollback &nbsp;
· Feature Flags &nbsp;
🔸 Pipeline Security &nbsp;
· Pipeline Optimization &nbsp;

**📦 Containers** — 0 live · 6 pipeline · 6 planned  
🔸 Containers &nbsp;
🔸 Docker &nbsp;
· Podman &nbsp;
· Containerd &nbsp;
· CRI &nbsp;
· OCI &nbsp;
🔸 Container Images &nbsp;
· Container Registries &nbsp;
🔸 Container Networking &nbsp;
· Container Storage &nbsp;
🔸 Container Security &nbsp;
🔸 Container Troubleshooting &nbsp;

**📐 Infrastructure as Code** — 0 live · 3 pipeline · 8 planned  
🔸 Infrastructure as Code &nbsp;
🔸 Terraform &nbsp;
· OpenTofu &nbsp;
· Pulumi &nbsp;
· Terraform Modules &nbsp;
🔸 Terraform State &nbsp;
· Remote State &nbsp;
· Terraform Providers &nbsp;
· IaC Security &nbsp;
· IaC Testing &nbsp;
· IaC Drift Management &nbsp;

**🔧 Configuration Management** — 0 live · 3 pipeline · 9 planned  
🔸 Configuration Management &nbsp;
🔸 Ansible &nbsp;
🔸 Ansible Playbooks &nbsp;
· Roles &nbsp;
· Inventories &nbsp;
· Variables &nbsp;
· Templates &nbsp;
· Ansible Vault &nbsp;
· AWX / Automation Platform &nbsp;
· Puppet &nbsp;
· Chef &nbsp;
· Salt &nbsp;

**🔀 GitOps** — 3 live · 2 pipeline · 3 planned  
✅ [GitOps](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Argo CD](./DevOps/CICD/cicd-pipelines.html) &nbsp;
✅ [Flux](./DevOps/CICD/cicd-pipelines.html) &nbsp;
🔸 Git-based Infrastructure &nbsp;
🔸 Declarative Deployment &nbsp;
· Drift Detection &nbsp;
· Progressive Delivery &nbsp;
· GitOps Security &nbsp;

**🛠️ Platform Engineering** — 0 live · 3 pipeline · 9 planned  
🔸 Platform Engineering &nbsp;
🔸 Internal Developer Platform &nbsp;
· Developer Experience &nbsp;
· Self-Service Infrastructure &nbsp;
· Golden Paths &nbsp;
· Platform-as-a-Product &nbsp;
🔸 Backstage &nbsp;
· Developer Portals &nbsp;
· Platform APIs &nbsp;
· Platform Governance &nbsp;
· Platform Automation &nbsp;
· Platform Security &nbsp;

</details>

<details>
<summary><b>06 · Kubernetes</b> — 3 categories · 18 live · 17 pipeline · 23 planned</summary>

**☸️ Kubernetes** — 16 live · 13 pipeline · 6 planned  
✅ [Kubernetes Fundamentals](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
✅ [Kubernetes Architecture](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
✅ [Pods](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
✅ [Deployments](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
🔸 ReplicaSets &nbsp;
🔸 DaemonSets &nbsp;
✅ [StatefulSets](./DevOps/K8/STORAGE/k8-storage.html) &nbsp;
· Jobs / CronJobs &nbsp;
✅ [Services](./DevOps/K8/Networking/k8-networking.html) &nbsp;
✅ [Ingress](./DevOps/K8/Networking/k8-networking.html) &nbsp;
🔸 ConfigMaps &nbsp;
🔸 Secrets &nbsp;
✅ [Volumes](./DevOps/K8/STORAGE/k8-storage.html) &nbsp;
✅ [Persistent Volumes](./DevOps/K8/STORAGE/k8-storage.html) &nbsp;
✅ [Storage Classes](./DevOps/K8/STORAGE/k8-storage.html) &nbsp;
🔸 RBAC &nbsp;
🔸 Namespaces &nbsp;
✅ [Resource Requests/Limits](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
🔸 Probes &nbsp;
✅ [Scheduling](./DevOps/K8/ARCHITECTURE/k8-architecture.html) &nbsp;
🔸 Taints / Tolerations &nbsp;
🔸 Affinity / Anti-Affinity &nbsp;
🔸 Autoscaling &nbsp;
🔸 HPA &nbsp;
🔸 VPA &nbsp;
· Cluster Autoscaling &nbsp;
✅ [Kubernetes Networking](./DevOps/K8/Networking/k8-networking.html) &nbsp;
✅ [CNI](./DevOps/K8/Networking/k8-networking.html) &nbsp;
✅ [CSI](./DevOps/K8/STORAGE/k8-storage.html) &nbsp;
🔸 Kubernetes Security &nbsp;
✅ [Kubernetes Troubleshooting](./DevOps/K8/ERROR/K8-error.html) &nbsp;
· Kubernetes Upgrade &nbsp;
· Kubernetes Backup &nbsp;
· Multi-Cluster Kubernetes &nbsp;
· Kubernetes Disaster Recovery &nbsp;

**🔴 OpenShift** — 2 live · 2 pipeline · 9 planned  
🔸 OpenShift Fundamentals &nbsp;
🔸 OpenShift Architecture &nbsp;
· Projects &nbsp;
· Routes &nbsp;
· Operators &nbsp;
✅ [SCC](./DevOps/K8/ERROR/K8-error.html) &nbsp;
· OpenShift Networking &nbsp;
· OpenShift Storage &nbsp;
· OpenShift Monitoring &nbsp;
· OpenShift Logging &nbsp;
· OpenShift Security &nbsp;
✅ [OpenShift Troubleshooting](./DevOps/K8/ERROR/K8-error.html) &nbsp;
· OpenShift Upgrades &nbsp;

**🕸️ Service Mesh** — 0 live · 2 pipeline · 8 planned  
🔸 Service Mesh &nbsp;
🔸 Istio &nbsp;
· Envoy &nbsp;
· Linkerd &nbsp;
· Traffic Management &nbsp;
· mTLS &nbsp;
· Service-to-Service Security &nbsp;
· Service Discovery &nbsp;
· Observability in Service Mesh &nbsp;
· Multi-Cluster Service Mesh &nbsp;

</details>

<details>
<summary><b>07 · Reliability</b> — 7 categories · 27 live · 25 pipeline · 64 planned</summary>

**📡 SRE** — 4 live · 8 pipeline · 13 planned  
🔸 SRE Fundamentals &nbsp;
🔸 SLI &nbsp;
🔸 SLO &nbsp;
🔸 SLA &nbsp;
🔸 Error Budget &nbsp;
🔸 Reliability Engineering &nbsp;
· Availability &nbsp;
· Reliability &nbsp;
· Scalability &nbsp;
· Latency &nbsp;
✅ [MTTR](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
· MTBF &nbsp;
✅ [Incident Management](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
🔸 Problem Management &nbsp;
✅ [RCA](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
✅ [Postmortem](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
· Toil Reduction &nbsp;
· Capacity Planning &nbsp;
· Reliability Testing &nbsp;
🔸 Chaos Engineering &nbsp;
· Resilience Engineering &nbsp;
· Service Health &nbsp;
· Production Readiness &nbsp;
· Operational Readiness &nbsp;
· SRE Automation &nbsp;

**📊 Observability** — 11 live · 4 pipeline · 7 planned  
✅ [Observability](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Monitoring](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Metrics](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Logs](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Traces](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
· Profiles &nbsp;
🔸 OpenTelemetry &nbsp;
✅ [Prometheus](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Grafana](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Alertmanager](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Loki](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
✅ [Jaeger](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
🔸 Tempo &nbsp;
🔸 ELK &nbsp;
· OpenSearch &nbsp;
✅ [Distributed Tracing](./DevOps/K8/OBSERVABILITY/k8-observability.html) &nbsp;
· Application Performance Monitoring &nbsp;
· Synthetic Monitoring &nbsp;
· Real User Monitoring &nbsp;
🔸 Alert Engineering &nbsp;
· Telemetry Pipelines &nbsp;
· Observability Architecture &nbsp;

**📜 Logging** — 2 live · 3 pipeline · 9 planned  
✅ [Linux Logging](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) &nbsp;
🔸 Syslog &nbsp;
✅ [Journald](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) &nbsp;
🔸 Log Rotation &nbsp;
🔸 Centralized Logging &nbsp;
· Logstash &nbsp;
· Fluent Bit &nbsp;
· Fluentd &nbsp;
· Elasticsearch &nbsp;
· OpenSearch &nbsp;
· Kibana &nbsp;
· Log Correlation &nbsp;
· Log Retention &nbsp;
· Log Security &nbsp;

**⚡ Performance Engineering** — 4 live · 2 pipeline · 6 planned  
✅ [CPU Performance](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;
✅ [Memory Performance](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;
✅ [Disk I/O](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;
🔸 Network Performance &nbsp;
· Application Performance &nbsp;
· Database Performance &nbsp;
· Load Testing &nbsp;
· Stress Testing &nbsp;
· Benchmarking &nbsp;
🔸 Profiling &nbsp;
· Capacity Modeling &nbsp;
✅ [Performance Troubleshooting](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;

**🔍 Troubleshooting** — 5 live · 2 pipeline · 5 planned  
✅ [Linux Troubleshooting](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;
🔸 Network Troubleshooting &nbsp;
🔸 Storage Troubleshooting &nbsp;
· Database Troubleshooting &nbsp;
· Application Troubleshooting &nbsp;
✅ [Kubernetes Troubleshooting](./DevOps/K8/ERROR/K8-error.html) &nbsp;
· Cloud Troubleshooting &nbsp;
✅ [Performance Troubleshooting](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) &nbsp;
· Security Troubleshooting &nbsp;
✅ [Production Incident Troubleshooting](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
✅ [Root Cause Analysis](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
· Failure Analysis &nbsp;

**🗄️ Backup & DR** — 0 live · 4 pipeline · 12 planned  
🔸 Backup Fundamentals &nbsp;
· Full Backup &nbsp;
· Incremental Backup &nbsp;
· Differential Backup &nbsp;
· Snapshot &nbsp;
· Replication &nbsp;
🔸 RPO &nbsp;
🔸 RTO &nbsp;
🔸 DR Architecture &nbsp;
· Active/Active &nbsp;
· Active/Passive &nbsp;
· Backup Validation &nbsp;
· Restore Testing &nbsp;
· DR Drill &nbsp;
· Failover &nbsp;
· Failback &nbsp;

**🎫 ITSM & Operations** — 1 live · 2 pipeline · 12 planned  
· ITIL &nbsp;
✅ [Incident Management](./SRE/INCIDENT-MANAGEMENT/incident-management.html) &nbsp;
🔸 Problem Management &nbsp;
🔸 Change Management &nbsp;
· Release Management &nbsp;
· Service Request &nbsp;
· Event Management &nbsp;
· CMDB &nbsp;
· Asset Management &nbsp;
· Configuration Management &nbsp;
· ServiceNow &nbsp;
· Remedy &nbsp;
· CAB &nbsp;
· Change Windows &nbsp;
· Operational Documentation &nbsp;

</details>

<details>
<summary><b>08 · Security</b> — 2 categories · 0 live · 18 pipeline · 28 planned</summary>

**🛡️ Security** — 0 live · 11 pipeline · 20 planned  
🔸 Cybersecurity Fundamentals &nbsp;
🔸 Infrastructure Security &nbsp;
· Network Security &nbsp;
🔸 Linux Security &nbsp;
· Cloud Security &nbsp;
🔸 Container Security &nbsp;
🔸 Kubernetes Security &nbsp;
· Application Security &nbsp;
🔸 DevSecOps &nbsp;
· Zero Trust &nbsp;
· IAM &nbsp;
🔸 RBAC &nbsp;
· PAM &nbsp;
· LDAP &nbsp;
· Active Directory &nbsp;
· SSO &nbsp;
· OAuth &nbsp;
· OIDC &nbsp;
· SAML &nbsp;
· PKI &nbsp;
🔸 TLS/SSL &nbsp;
🔸 Certificates &nbsp;
🔸 Secrets Management &nbsp;
🔸 HashiCorp Vault &nbsp;
· Vulnerability Management &nbsp;
· Security Scanning &nbsp;
· SIEM &nbsp;
· SOC &nbsp;
· Threat Detection &nbsp;
· Compliance &nbsp;
· Security Auditing &nbsp;

**🔗 Supply Chain Security** — 0 live · 7 pipeline · 8 planned  
🔸 Software Supply Chain Security &nbsp;
🔸 SBOM &nbsp;
· SLSA &nbsp;
· Artifact Signing &nbsp;
🔸 Image Signing &nbsp;
· Cosign &nbsp;
🔸 Admission Control &nbsp;
🔸 Policy as Code &nbsp;
· OPA &nbsp;
· Gatekeeper &nbsp;
· Kyverno &nbsp;
· Dependency Security &nbsp;
🔸 Container Image Scanning &nbsp;
· Secrets Scanning &nbsp;
🔸 CI/CD Security &nbsp;

</details>

<details>
<summary><b>09 · Data & Applications</b> — 4 categories · 1 live · 12 pipeline · 47 planned</summary>

**🗃️ Database** — 0 live · 3 pipeline · 13 planned  
🔸 Database Fundamentals &nbsp;
· MySQL &nbsp;
🔸 PostgreSQL &nbsp;
· Oracle &nbsp;
· SQL Server &nbsp;
· MongoDB &nbsp;
· Redis &nbsp;
· Database Replication &nbsp;
🔸 Database HA &nbsp;
· Database Backup &nbsp;
· Database Recovery &nbsp;
· Database Performance &nbsp;
· Connection Management &nbsp;
· Query Optimization &nbsp;
· Database Monitoring &nbsp;
· Database Security &nbsp;

**🧩 Middleware** — 0 live · 3 pipeline · 11 planned  
· Application Servers &nbsp;
🔸 Nginx &nbsp;
· Apache &nbsp;
· Tomcat &nbsp;
· WildFly &nbsp;
· JBoss &nbsp;
· RabbitMQ &nbsp;
🔸 Apache Kafka &nbsp;
· Redis &nbsp;
🔸 Message Queues &nbsp;
· Event Streaming &nbsp;
· Event-Driven Architecture &nbsp;
· Middleware HA &nbsp;
· Middleware Troubleshooting &nbsp;

**🔌 API & Microservices** — 0 live · 4 pipeline · 12 planned  
🔸 REST APIs &nbsp;
🔸 HTTP/HTTPS &nbsp;
🔸 API Gateway &nbsp;
· API Management &nbsp;
· API Security &nbsp;
· Authentication &nbsp;
· Authorization &nbsp;
· Rate Limiting &nbsp;
🔸 Microservices &nbsp;
· Service Discovery &nbsp;
· Circuit Breaker &nbsp;
· Retry &nbsp;
· Timeout &nbsp;
· Bulkhead &nbsp;
· Distributed Transactions &nbsp;
· Event-Driven Microservices &nbsp;

**🕮 Distributed Systems** — 1 live · 2 pipeline · 11 planned  
🔸 Distributed Systems &nbsp;
· Consensus &nbsp;
· Leader Election &nbsp;
· Replication &nbsp;
· Consistency &nbsp;
· Eventual Consistency &nbsp;
· Distributed Transactions &nbsp;
· Caching &nbsp;
· Distributed Locking &nbsp;
· Partition Tolerance &nbsp;
🔸 CAP Theorem &nbsp;
· Failure Domains &nbsp;
✅ [Quorum](./DevOps/K8/ERROR/K8-error.html) &nbsp;
· Distributed Coordination &nbsp;

</details>

<details>
<summary><b>10 · Modern Ops</b> — 5 categories · 3 live · 21 pipeline · 45 planned</summary>

**🤖 AI Infrastructure** — 0 live · 6 pipeline · 14 planned  
🔸 AI Infrastructure &nbsp;
🔸 GPU Infrastructure &nbsp;
🔸 GPU Scheduling &nbsp;
🔸 GPU Kubernetes &nbsp;
🔸 AI Workloads on Kubernetes &nbsp;
🔸 Model Serving &nbsp;
· Inference Infrastructure &nbsp;
· LLMOps &nbsp;
· MLOps &nbsp;
· Model Monitoring &nbsp;
· Model Observability &nbsp;
· AI Cost Management &nbsp;
· AI Reliability &nbsp;
· AI Security &nbsp;
· AI Governance &nbsp;
· RAG Infrastructure &nbsp;
· Vector Databases &nbsp;
· Model Gateways &nbsp;
· AI CI/CD &nbsp;
· AI Infrastructure Automation &nbsp;

**🧠 AIOps** — 0 live · 4 pipeline · 10 planned  
🔸 AIOps &nbsp;
· AI Incident Detection &nbsp;
🔸 AI Root Cause Analysis &nbsp;
· AI Alert Correlation &nbsp;
· AI Log Analysis &nbsp;
· AI Capacity Forecasting &nbsp;
· AI Remediation &nbsp;
· AI-assisted Troubleshooting &nbsp;
· AI Operations Agents &nbsp;
🔸 Agentic DevOps &nbsp;
🔸 Agentic SRE &nbsp;
· Agentic CloudOps &nbsp;
· Human-in-the-loop Automation &nbsp;
· AI Operational Guardrails &nbsp;

**💰 FinOps** — 0 live · 5 pipeline · 6 planned  
🔸 FinOps &nbsp;
🔸 Cloud Cost Management &nbsp;
· Cost Allocation &nbsp;
· Tagging &nbsp;
· Resource Optimization &nbsp;
🔸 Rightsizing &nbsp;
· Reserved Capacity &nbsp;
🔸 Spot / Preemptible Instances &nbsp;
🔸 Kubernetes Cost Management &nbsp;
· Cloud Waste Management &nbsp;
· Cost Governance &nbsp;

**🔁 Automation** — 3 live · 3 pipeline · 6 planned  
✅ [Shell Automation](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) &nbsp;
✅ [Bash Automation](./Foundation/SHELL-AND-BASH/shell-and-bash.html) &nbsp;
✅ [Python Automation](./Foundation/PYTHON/python.html) &nbsp;
🔸 Ansible Automation &nbsp;
· Terraform Automation &nbsp;
· API Automation &nbsp;
· Cloud Automation &nbsp;
🔸 Kubernetes Automation &nbsp;
· Network Automation &nbsp;
· Database Automation &nbsp;
· Monitoring Automation &nbsp;
🔸 Self-Healing Infrastructure &nbsp;

**🏛️ Architecture** — 0 live · 3 pipeline · 9 planned  
🔸 System Architecture &nbsp;
· Cloud Architecture &nbsp;
🔸 Microservice Architecture &nbsp;
· Distributed Architecture &nbsp;
· Event-Driven Architecture &nbsp;
· Multi-Tenant Architecture &nbsp;
· Scalable Architecture &nbsp;
· Resilient Architecture &nbsp;
🔸 Zero-Downtime Architecture &nbsp;
· Multi-Region Architecture &nbsp;
· Multi-Cloud Architecture &nbsp;
· Hybrid Architecture &nbsp;

</details>


---

## 📚 Published Issues

Issues with a link below have a full page in this repo. The rest are archive listings from earlier
editions of the newsletter that have not been migrated here yet.

| Issue | Date | Topic | Page |
|:-----:|:-----|:------|:-----|
| **#057** | Sep 2026 | [**Linux & Unix Glossary**](./Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html) — 190 terms, 15 categories, searchable | ✅ Live |
| **#056** | Sep 2026 | [**Linux Troubleshooting**](./Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html) — load, OOM, disk/IO, network, boot failures | ✅ Live |
| **#055** | Sep 2026 | [**Linux Advanced**](./Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html) — systemd, sysctl, namespaces, cgroups, LVM | ✅ Live |
| **#054** | Sep 2026 | [**Linux Fundamentals**](./Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html) — FHS, permissions, packages, shell | ✅ Live |
| **#053** | Sep 2026 | [**Incident Management & Postmortems**](./SRE/INCIDENT-MANAGEMENT/incident-management.html) — severity, IC role, blameless writeups | ✅ Live |
| **#052** | Aug 2026 | [**CI/CD & GitOps Deep-Dive**](./DevOps/CICD/cicd-pipelines.html) — Jenkins, GitLab CI, ArgoCD/Flux, canary | ✅ Live |
| **#051** | Jul 2026 | [**Observability Stack**](./DevOps/K8/OBSERVABILITY/k8-observability.html) — Prometheus, Grafana, Loki, Jaeger, SLO alerting | ✅ Live |
| **#050** | Jun 2026 | [**Kubernetes Storage**](./DevOps/K8/STORAGE/k8-storage.html) — PV/PVC, StorageClasses, CSI, StatefulSets, DR | ✅ Live |
| **#049** | May 2026 | [**K8s & OpenShift Error Runbook**](./DevOps/K8/ERROR/K8-error.html) — 32 error types across 5 layers | ✅ Live |
| **#048** | Apr 2026 | [**Kubernetes Architecture**](./DevOps/K8/ARCHITECTURE/k8-architecture.html) — control plane, nodes, QoS, scheduling | ✅ Live |
| **#047** | Mar 2026 | [**Kubernetes Networking Decoded**](./DevOps/K8/Networking/k8-networking.html) — CNI, Ingress, NetworkPolicy, CoreDNS | ✅ Live |
| #045 | Jan 2026 | AI/ML Workloads on Kubernetes | 🗄️ Archive listing |
| #044 | Dec 2025 | Platform Engineering & Backstage | 🗄️ Archive listing |
| #043 | Nov 2025 | GitOps at Scale with ArgoCD & Flux | 🗄️ Archive listing |
| #042 | Oct 2025 | Observability: Prometheus + Loki + Tempo | 🗄️ Archive listing |

**Section hubs:** [DevOps / Kubernetes](./DevOps/K8/index.html) · [Infrastructure / OS](./Infrastructure/OS/index.html)

---

## 🗂️ Repository Structure

Content is organised by **topic**, not by date — the folder path is the taxonomy.

```
Platform-ops-Newsletter/
│
├── index.html                          ← Homepage: hero, knowledge map, archive, author
├── README.md                           ← You are here
├── LICENSE                             ← MIT
│
├── .github/workflows/
│   └── static.yml                      ← Deploys the whole repo to GitHub Pages
│
├── DevOps/
│   ├── CICD/cicd-pipelines.html                        #052
│   └── K8/
│       ├── index.html                                  ← Kubernetes hub
│       ├── ARCHITECTURE/k8-architecture.html           #048
│       ├── ERROR/K8-error.html                         #049
│       ├── Networking/k8-networking.html               #047
│       ├── OBSERVABILITY/k8-observability.html         #051
│       └── STORAGE/k8-storage.html                     #050
│
├── Infrastructure/
│   └── OS/
│       ├── index.html                                  ← OS / Linux hub
│       └── LINUX/
│           ├── FUNDAMENTALS/linux-fundamentals.html    #054
│           ├── ADVANCED/linux-advanced.html            #055
│           ├── TROUBLESHOOTING/linux-troubleshooting.html  #056
│           └── GLOSSARY/
│               ├── linux-unix-glossary.html            #057 — 190 terms
│               └── TERMS/fundamentals/                 ← 12 standalone term pages
│                   ├── bash.html          ├── proc.html
│                   ├── init.html          ├── shell.html
│                   ├── kernel-modules.html├── sys.html
│                   ├── linux-commands.html├── sysctl.html
│                   ├── linux-distributions.html
│                   ├── linux-kernel.html  ├── terminal-cli.html
│                   └── linux-unix-fundamentals.html
│
└── SRE/
    └── INCIDENT-MANAGEMENT/incident-management.html    #053
```

**Convention:** each issue is one self-contained `.html` file — inline CSS, inline JS, no external
dependencies beyond Google Fonts. Links between pages are **relative**, so the site works when
opened from disk, from a local server, or from GitHub Pages.

---

## ✨ Site Features

The homepage is a single hand-written HTML file with no framework behind it:

| Feature | What it does |
|:--------|:-------------|
| 🌓 **Dark / light toggle** | Theme switch in the nav, remembered via `localStorage`, applied before first paint so there's no flash |
| ♾️ **Animated DevOps loop** | SVG infinity loop with the eight lifecycle stages and a light pulse racing the path |
| 🗺️ **Knowledge map** | All 521 topics, grouped into 33 categories under 10 pillars — search by name, filter by status, expand a pillar to see what's shipped and what's queued |
| 🖥️ **Coverage terminal** | Terminal-style `tree` view of the ten pillars with live-vs-total counts, and a `ls published/` listing that links straight into every issue |
| 🔔 **Topic requests** | Clicking a pipeline or planned topic queues it; the signup then tells Kit which topics that reader is waiting for |
| 📡 **RSS** | `feed.xml` carries all 11 issues, and every page advertises it in its `<head>` |
| 📜 **Scrollable archive** | Latest Issues is an internal scroll panel that stays height-matched to the topics column |
| 🔍 **Searchable glossary** | 190 terms across 15 categories, with standalone deep-dive pages for the terms that need one |
| 🦶 **Shared footer** | One footer across all 26 pages, with links rebuilt per directory depth |

---

## 🔔 Topic Requests

456 of the 521 topics have no page yet, so a reader who finds one has nowhere to go.
Clicking a pipeline or planned topic queues it instead. The queue rides along with
the signup as a Kit custom field, which turns the backlog into a ranked list of what
people are actually waiting for.

**One-time Kit setup:** create a custom field named `topic_request`
(Grow → Subscribers → the gear icon → Custom fields). Without it Kit silently drops
the value — signups still work, you just don't see the topics. Sort your subscriber
list by that column to see which topics come up most.

---

## 📊 Analytics

Every page carries a [GoatCounter](https://www.goatcounter.com/) loader — cookieless,
open-source, free for personal sites, and no consent banner. It is **inert until you
set a site code**, so the repo ships sending nothing.

```bash
# after signing up, from the repo root — sets the code in all 26 pages
git grep -l "var PO_GC" | xargs sed -i "s/var PO_GC='[^']*'/var PO_GC='yourcode'/"
```

Beyond page views, the homepage reports four events, so you can see intent and not
just traffic:

| Event path | Fires when |
|:--|:--|
| `kmap-search/<query>` | someone searches the knowledge map (3+ characters, once they stop typing) |
| `topic-request/<topic>` | someone queues a topic for notification |
| `kmap-filter/<status>` | someone filters to live / pipeline / planned |
| `subscribe/success` | a signup completes |

`kmap-search` is the useful one: it is a live list of what people came looking for
and, when it names a topic that isn't live yet, what to write next.

---

## 📡 RSS

`feed.xml` is RSS 2.0 with all 11 published issues, newest first, and every page
advertises it via `<link rel="alternate">`. It regenerates from the issue list — add
a new item at the top when you publish, and bump `<lastBuildDate>`.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Vishal-Abhinav/Platform-ops-Newsletter.git
cd Platform-ops-Newsletter

# Open the homepage directly — no build step needed
open index.html          # macOS
xdg-open index.html      # Linux
start index.html         # Windows
```

### Run with a local server

Relative links work from the filesystem, but a server matches production more closely:

```bash
python3 -m http.server 8080     # → http://localhost:8080
# or
npx serve .                     # → http://localhost:3000
```

### Check every internal link

Because every page cross-links by relative path, it's worth verifying after any move:

```bash
# lists any href/src that doesn't resolve to a tracked file
python3 - <<'EOF'
import subprocess, re, posixpath
tree = subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
tset, broken = set(tree), []
for f in [x for x in tree if x.endswith(".html")]:
    base = posixpath.dirname(f)
    for link in re.findall(r'(?:href|src)="([^"]+)"', open(f, encoding="utf-8").read()):
        if link.startswith(("http","mailto:","#","//","data:")): continue
        t = posixpath.normpath(posixpath.join(base, link.split("#")[0].split("?")[0]))
        if t and t not in tset: broken.append((f, link))
print(f"{len(broken)} broken links")
[print(" ", f, "->", l) for f, l in broken]
EOF
```

---

## 🤖 Deployment

Pushing to `main` triggers `.github/workflows/static.yml`, which uploads the **entire repository**
as the Pages artifact and deploys it — so a new issue goes live as soon as it's merged.

```yaml
on:
  push:
    branches: ["main"]
  workflow_dispatch:        # or deploy manually from the Actions tab
```

No build, no bundler, no `node_modules`. What's in the repo is what's on the site.

---

## ➕ Adding a New Issue

```bash
# 1. Branch
git checkout -b issue/058-gateway-api

# 2. Create the page in its topic folder (not a date folder)
mkdir -p Networking/GATEWAY-API
$EDITOR Networking/GATEWAY-API/gateway-api.html

# 3. Flip every topic the issue covers to live in the knowledge map.
#    One issue usually lights up several topics — mark all of them.
#    In index.html, find the topic inside its pillar and swap
#      <span class="km-t plan">Gateway API</span>
#    for
#      <a class="km-t live" data-s="live" href="Networking/GATEWAY-API/gateway-api.html">Gateway API</a>
#    Then update, in the same file:
#      - that category's  km-c-counts  line
#      - that pillar's    km-p-counts  line and its km-p-mini flex values
#      - the five km-stat numbers and the km-bar flex values
#      - the pillar row and the published/ list in the terminal tree
#      - the two ✓ summary lines under the tree

# 4. Add an .issue-card entry in the Latest Issues archive, then update this
#    README's Knowledge Map table and the matching <details> block.

# 5. Add the issue to feed.xml as the newest <item> and bump <lastBuildDate>.
#    Add the GoatCounter loader + RSS <link> to the new page's <head>, with
#    the right number of ../ for its depth (copy them from a sibling page).

# 6. Verify, commit, push
#    (run the link checker above — it catches wrong ../ depth immediately)
git add Networking/ index.html README.md feed.xml
git commit -m "Issue #058: Gateway API — the future of Ingress"
git push origin issue/058-gateway-api
```

> **Keep the counts honest.** Every number on the homepage is derived from topic
> statuses. Flip a topic to live without updating the counts and the map starts
> lying — search index.html for `km-stat-n` and work outward from there.

> **Relative-path gotcha:** a page three folders deep needs `../../../index.html` to reach home.
> Getting this wrong is the single most common break — always run the link checker before pushing.

---

## 🔧 Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Hosting** | GitHub Pages, auto-deployed via GitHub Actions |
| **Pages** | Self-contained HTML — inline CSS + JS, zero runtime dependencies |
| **Diagrams** | Hand-written inline SVG and CSS |
| **Fonts** | Bebas Neue · DM Mono · Instrument Serif · Manrope (Google Fonts) |
| **Build** | None. That's the point. |
| **License** | MIT |

---

## ✍️ Author

<table>
  <tr>
    <td align="center">
      <b>Vishal Abhinav</b><br/>
      <sub>Platform Ops · Kubernetes · Platform Engineering · Cloud Architecture · DevOps · SRE · Infrastructure Automation</sub><br/>
      <sub>OCI Certified · CISSP Certified · AWS Certified · Cloud Native (in progress)</sub><br/><br/>
      <a href="https://github.com/Vishal-Abhinav">@Vishal-Abhinav</a> ·
      <a href="https://www.linkedin.com/in/vishal-abhinav/">LinkedIn</a>
    </td>
  </tr>
</table>

Platform Ops Engineer with 4+ years across Kubernetes, infrastructure and SRE-engineered systems —
designing for failure, automating the boring parts, and specialising in notification engine
architecture on SMPP and PDU session handling.

---

## 🤝 Contributing

Corrections and additions are welcome — this is a knowledge base, and knowledge bases rot.

```
🐛  Broken link or typo       → open a PR directly
📝  Technical correction      → open a PR, cite the source
💡  Suggest a topic           → open a GitHub Issue
🖼️  Contribute a diagram      → inline SVG please, no binaries
⭐  Star the repo             → helps other engineers find it
```

**Before opening a PR:** run the link checker above, and open your page in a browser at both
desktop and mobile widths.

---

## 📄 License

**MIT** — Copyright © 2026 Vishal Abhinav. See [LICENSE](./LICENSE).

Use it, fork it, quote it, build on it. Attribution appreciated, not required.

---

<div align="center">

**Platform Ops · Tech with Vishal Abhinav**

*Built for engineers, by an engineer.*

**[Read the latest issue →](https://vishal-abhinav.github.io/Platform-ops-Newsletter/)**

</div>
