# ClusterMAX 3.0 — Internet / WAN / North-South Coverage Research

**Product identity (verified):** ClusterMAX™ is the GPU-cloud rating system by **SemiAnalysis**. Real domain: **[clustermax.ai](https://www.clustermax.ai)**. The site also runs at [clustermax.semianalysis.com](https://clustermax.semianalysis.com/). Current release: **ClusterMAX 3.0 (Sep 2026)**. This release is still current on this research date. The site's release navigation lists only "3.0 (Sep, 2026) Current", "2.1 (Apr, 2026)", "2.0 (Nov, 2025)", "1.0 (Mar, 2025)" ([clustermax.ai](https://www.clustermax.ai)).

The latest newsletter entry on the topic is the 3.0 article ([newsletter.semianalysis.com/p/clustermax-30-the-industry-standard](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Its podcast Ep. 033 follows on Sep 23, 2026 ([semianalysis.com/weekly/latest](https://semianalysis.com/weekly/latest)). No 3.1/4.0 exists. The companion article "Most Neoclouds Suck At Security" (Sep 2, 2026) comes before that article. That companion article ships the current `cmax` CLI release ([newsletter.semianalysis.com/p/most-neoclouds-suck-at-security](https://newsletter.semianalysis.com/p/most-neoclouds-suck-at-security)).

Public tooling: the `cmax` CLI at [github.com/SemiAnalysisAI/ClusterMAX](https://github.com/SemiAnalysisAI/ClusterMAX). The PyPI package is `clustermax`, with stable release 0.2.1. SemiAnalysis publishes nightlies `0.3.0.dev…` daily through Oct 11, 2026 ([pypi.org/pypi/clustermax/json](https://pypi.org/pypi/clustermax/json)).

ClusterMAX 3.0 rates **77 providers** across **10 dimensions** and **142 total criteria**. The dimensions are Security, Lifecycle, Orchestration, Storage, Networking, Reliability, Monitoring, Pricing, Partnerships, and Availability. These counts are up from **129 criteria / 84 providers in 2.0** and 26 providers in 1.0 ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). The [2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard) article states the 129 figure verbatim. vCluster's full per-criterion scorecard supports the 142 figure: "ClusterMAX defines 142 individual criteria across ten categories" ([vcluster.com/clustermax](https://www.vcluster.com/clustermax)).

The **Networking dimension carries exactly 10 criteria** ([clustermax.ai/criteria/networking](https://www.clustermax.ai/criteria/networking)). **Zero of them concern north-south internet**; see §2. This brief is the internet/WAN sibling of our storage-side ClusterMAX brief ([storage brief](../storage-research/clustermax.md)). This brief does not re-derive the storage content of that brief.

Research date: 2026-10-11. Each claim below has a source URL. We mark a claim **[observed]** when the source states or shows it. We mark a claim **[calculated]** when it comes from our arithmetic on source numbers. We mark a claim **[inference]** when it is our interpretation.

---

## 1. Current state and what ClusterMAX actually tests on the internet/WAN side

### 1.1 Release state (verified 2026-10-11) **[observed]**
- ClusterMAX 3.0 (Sep 2026) is the current release. Previous releases stay visible as historical records ([clustermax.ai](https://www.clustermax.ai)). The 2.1 interim update (Apr 2026) says explicitly "This is not a full re-test of all providers". That update only adds providers plus the TCO/Goodput calculators ([clustermax.ai/v2.1](https://www.clustermax.ai/v2.1)).
- Counts: 77 rated providers, 323 providers in the market view, 10 dimensions, 142 criteria, 200+ user interviews. The market view is up from 209 in 2.0 and 169 in 1.0 ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Only 19 neoclouds achieve a Medallion rating in 3.0. Nebius joins CoreWeave in Platinum ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).
- The `cmax` CLI is under active nightly development. The last repo commit is on Sep 30, 2026. PyPI nightlies continue through Oct 11, 2026. But the CLI **adds no internet/WAN checks**; see §4 ([GitHub](https://github.com/SemiAnalysisAI/ClusterMAX), [PyPI](https://pypi.org/pypi/clustermax/json)).

### 1.2 What SemiAnalysis requests from providers — nothing internet-specific **[observed]**
For 3.0, SemiAnalysis requests 32 GPUs (4×8-way HGX or 8×4-way NVL72) from each provider. It also requests high-bandwidth fabric (800G RoCE or XDR InfiniBand). It requests 10TB+ high-performance file storage with RWX StorageClass and 10TB+ S3-compliant object storage. It also requests a monitoring dashboard and 5 days Slurm + 5 days K8s testing ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **SemiAnalysis requests no public/internet bandwidth commitment, transit, or egress allowance.** [inference] North-south capacity is whatever the default frontend network of the provider delivers during the test window.

### 1.3 The three-phase test structure, and where WAN appears **[observed]**
Phases: Audit (binary config checks, ~15 min, public via `cmax`) → Performance (microbenchmarks + real-world) → Reliability/fault-tolerance. SemiAnalysis adds 200+ user interviews ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Internet/WAN touches only two spots:
- **Lifecycle convenience tests** (Performance phase): "We start by checking internet speed using multiple approaches for download/upload speed, mostly from Cloudflare. We then test the time it takes to install common packages like PyTorch and vLLM via pip and uv, as well as download containers from Docker Hub, ghcr.io, and nvcr.io, and pull a model from Hugging Face and ModelScope" ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[observed]** These are minutes-scale, single-node spot checks. They are not sustained transfers. [inference]
- **Frontend/management-network check** (Reliability phase): "On the frontend network, we also test management-network packet loss, RTT, and TCP bandwidth between every directed pair across four nodes. It's not often that this extra test catches errors that the burn-in did not, but we like the data, and it has revealed big performance differences on certain Ethernet networks under load" ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[observed]** This check is node-to-node (internal), not internet-facing. All other network-related tests are east-west fabric tests ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). They include MPI collectives and NCCL/RCCL tests across 8 B–16 GB messages. They also include `ib_write_bw`/`ib_read_bw` per rail, scale-out fabric endurance loops, and EFA latency comparisons.

---

## 2. The Networking dimension on paper: 10 criteria, 0 north-south

The list below is the complete Key Requirements list from [clustermax.ai/criteria/networking](https://www.clustermax.ai/criteria/networking). That page is the current 3.0 page, "Networking — Network performance, latency, and connectivity options including RDMA and high-speed interconnects". vCluster's reproduction of all 142 criteria matches the list line-for-line ([vcluster.com/clustermax](https://www.vcluster.com/clustermax)):

**East-west fabric criteria (10 of 10):** **[observed]**
1. Out-of-the-box Slurm topology configuration (Slurm)
2. InfiniBand or RoCEv2 support
3. MPI distribution using higher performance HPC-X mpirun
4. NCCL configured in /etc/nccl.conf with NCCL_IB_GID_INDEX=3 set for RoCEv2
5. NCCL_MIN_NCHANNELS, NCCL_PROTO, NCCL_ALGO NOT set (auto-configuration)
6. SHARP support for enhanced performance
7. 4-node NCCL test within specification
8. PyTorch layer network performance within spec
9. NCCL monitoring plugin availability
10. Network bandwidth and latency testing

**North-south internet criteria: 0 of 10.** **[observed]** No criterion mentions public bandwidth, egress throughput, peering, transit, CDN/object-store transfer speed, or internet latency. The page subtitle itself scopes the dimension to "RDMA and high-speed interconnects." The 142-item list has only two internet-adjacent criteria. Both live in *other* dimensions.

One is Lifecycle's "No punitive data egress / offboarding fees" ([clustermax.ai/criteria/lifecycle](https://www.clustermax.ai/criteria/lifecycle)). The other is Reliability's "Network stability assessment" ([clustermax.ai/criteria/reliability](https://www.clustermax.ai/criteria/reliability)).

That Reliability criterion is the survivor of an explicit 2.0 Reliability bullet: "WAN connection is stable over time, upload/download speed is reasonable" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). **[inference]** In practice, "Network bandwidth and latency testing" (Networking #10) takes the form of NCCL/`ib_write_bw` fabric tests (§1.3). It does not take the form of internet tests. The examples on the criteria page make no reference to any public-internet measurement. The methodology article also makes no such reference.

For comparison, the 2.0 criteria list has two internet-adjacent items in prose. One is Lifecycle — "Is it easy to use the cluster? (i.e. download speed, upload speed)". The other is Reliability — "WAN connection is stable over time, upload/download speed is reasonable" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). [inference] The 3.0 criteria pages abstract these items away. The hands-on download/upload tests move wholly into the Lifecycle "ease of use" methodology (§3).

---

## 3. Hands-on internet tests per release, with exact numbers

### 3.1 ClusterMAX 1.0 (Mar 2025): no explicit internet-speed suite **[observed]**
The free portion of the 1.0 article covers security, Slurm/K8s, and storage (incl. the `import torch` LOSF probe). It also covers NCCL/RDMA fabric benchmarks from 128–1024 GPUs, health checks, and SLAs. But it contains **no timed download/upload or speedtest methodology**. It has only two WAN-adjacent items.

The first item is the "Preparatory Phase" observation that leading clouds "enable users to migrate datasets into clusters in advance". This observation treats bulk ingress as a *sales/ops* question, not a measured test. The second item is the egress-fee commentary in §6 below ([1.0 article](https://newsletter.semianalysis.com/p/the-gpu-cloud-clustermax-rating-system-how-to-rent-gpus)). [inference] The internet-speed test suite debuts with 2.0.

### 3.2 ClusterMAX 2.0 (Nov 2025): the timed WAN-ingress proxies, with medians **[observed]**
All quotes in this section come from the [2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard). The article says these "simple tests generally complete in under one minute". It also calls them "a proxy to reveal underlying issues with network configuration, storage performance, peering, and virtualization overhead":
- **uv install PyTorch:** "Best-in-class providers (e.g., CoreWeave, GCP) completed the install in ~3.2 seconds. The median time was ~8.5 seconds, while one Bronze-tier provider took a staggering 41.2 seconds. Using pip was universally slower, with a median of ~28 seconds."
- **NGC PyTorch container pull:** "A 22.1GB pull of the standard nvcr.io/nvidia/pytorch:24.05-py3 container is a critical test of a provider's peering and local caching strategy. Platinum-tier providers like CoreWeave, which maintain local NGC mirrors, completed the pull in under 10 seconds. Gold-tier providers (e.g., Nebius, Oracle) were respectable at 45-60 seconds. Silver-tier providers often took 90-120 seconds, and many Bronze-tier providers exceeded 4 minutes." **[calculated]** CoreWeave's <10 s for 22.1 GB implies ≥17.7 Gbps effective (mirror/cache). In contrast, >4 min implies ≤0.74 Gbps WAN-side.
- **import torch:** "The median was a tolerable ~1.8 seconds… multiple providers, particularly those with complex VM configurations… have a frustrating 8-10 second delays."
- **15B phi-4 Hugging Face download:** "A real-world test of sustained WAN throughput from Hugging Face's CDN. The median time was ~35 seconds (roughly 3.4 Gbps). Top-tier providers consistently achieved speeds over 6 Gbps, finishing in ~20 seconds."
- **15B phi-4 load into GPU memory:** "A pure test of the local data path… The median time here was ~12 seconds."
- **Whois IP-ownership check:** "A simple whois on the machine's public IP. This test is critical for exposing aggregators and resellers. In numerous tests of smaller providers, the IP ownership resolved back to Oracle, CoreWeave, or AWS."
- **speedtest-cli:** "We saw a median download of ~4.5 Gbps and upload of ~2.8 Gbps. More interestingly, some providers (like STN) would post excellent, symmetrical 10 Gbps speedtest results, but then perform poorly on real-world file (e.g., NGC, Hugging Face) downloads, suggesting traffic management is in place to game these exact synthetic tests." [inference] This is the only documented instance of ClusterMAX noticing synthetic-test gaming. A serious certification suite must defend against this phenomenon.
- Per-provider color from 2.0: **Sesterce** (Helsinki) — "Download speeds were solid… posting some of the fastest times to install pytorch, download an ngc pytorch container, and download a model from huggingface". **STN** — "we also ran into what looked like network traffic shaping over the WAN that slowed down our downloads, but made speedtest-cli look great". **Voltage Park** — "good download speeds". For **Together**, VSCode SSH sessions "responded very slowly… leading us to believe it was a problem with their datacenter provider" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)).

### 3.3 ClusterMAX 3.0 (Sep 2026): Cloudflare speedtest + multi-registry pulls **[observed]**
- Lifecycle phase, verbatim: "We start by checking internet speed using multiple approaches for download/upload speed, mostly from Cloudflare". The phase then times pip/uv installs of PyTorch and vLLM. It also times container pulls from Docker Hub, ghcr.io, and nvcr.io. It also times model pulls from Hugging Face and ModelScope ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[observed]**

  The new suite now measures upload speed explicitly (via Cloudflare). The 2.0 speedtest-cli also measures upload speed. But the article describes no bulk-transfer or object-store target. [inference]
- The 3.0 appendix gives per-provider WAN verdicts. **Nebius** (Platinum) — "WAN is good". **TensorWave** — "North-south bandwidth was strong". **Gcore** — "The N/S network was fine". **Hyperstack** — "The N/S network was fine". **Firmus** — "WAN was inconsistent but often quite poor, maintaining 0.25 Gb/s to NGC".

  **Crusoe** — "this cluster's WAN was among the slowest we tested, clocking in between 0.47 Gbps and 0.78 Gbps depending on the context. Iceland has some skinny cables getting off the island". **Bitdeer** — "the cluster's WAN performance was exceptionally bad, averaging around 0.1 GB/s across several tests. The cause of this poor performance is unknown to us; needless to say, it would be an impediment to real-world usage" ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

  **[calculated]** Bitdeer's 0.1 GB/s ≈ 0.8 Gbps. Firmus's 0.25 Gb/s to NGC is ~50–100× below CoreWeave's mirrored pull rate. It is also ~14× below the 2.0 phi-4 median.
- **Together @ IREN Prince George** (3.0): "weekend-long outages that eventually get blamed on a single ISP (yes, a single ISP at this site—no redundancy in Northern Canada)". The article notes transit diversity only as an anecdote/observation. It never tests transit diversity ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[observed]**

### 3.4 What these tests are not **[inference]**
Every documented internet test is a single-node, minutes-scale convenience probe. These probes are package installs, one 22.1 GB container pull, one ~15 GB model pull, and a Cloudflare speedtest. None runs for the 8-hour burn-in duration. None saturates a link for hours. None targets S3/R2/GCS as an egress/ingress endpoint. None repeats across days or from multiple nodes at the same time.

---

## 4. The public `cmax` CLI: full networking-check enumeration (code-grepped)

Source: a clone of [github.com/SemiAnalysisAI/ClusterMAX](https://github.com/SemiAnalysisAI/ClusterMAX) at commit `1492ac5` (Sep 30, 2026). We grep `cmax/criteria_links.py`, `cmax/audit_report.py`, and `cmax/scripts/1-audit/criteria-checks.json`. We also grep `cmax/scripts/1-audit/checks/fabric/` and the shell collectors. All findings are **[observed]** unless we note otherwise.

### 4.1 Every networking-related check ID
These check keys in `criteria_links.py` + `audit_report.py` link to the Networking criteria page or fabric checks:
- `software.nccl.installed` → Networking (anchor: bare "networking" category)
- `nccl_topo_file.status` → "networking-out-of-the-box-slurm-topology-configuration"
- `nccl_ib_qps.status` → Networking ("NCCL InfiniBand queue-pair setting is suitable for the detected fabric")
- `networking.topologyConfigured` → orchestration topology anchor ("The scheduler has a topology configuration")
- `networking.hcaNamingValid` → Networking ("The HCA and NIC device names use the expected naming convention")
- `networking.ncclAutoConfig` → "networking-nccl-min-nchannels-nccl-proto-nccl-algo-not-set-auto-configuration"
- Plus standalone profile checks: `bmc-ipmi`, `ufm-profile`, `pcie-passthrough`, `nvlink-boundary`, `securityVersions.connectxFirmware.status`, `securityVersions.virtioNetBluefield.*` (fabric-hardware security).
The file `criteria-checks.json` holds 73 machine-checkable criteria of the 142. Its "Networking & Fabric" category contains exactly 10 IDs: `fabric-class`, `hca-naming`, `topology-conf`, `gang-scheduling`, `bin-packing`, `nccl-autoconfig`, `ib-tenant-isolation`, `nccl-ib-qps-entropy`, `ingress-controller`, `load-balancer`. Adjacent IDs are `nccl-installed` (Software Stack), `nccl-topo-file-container` (Containers), and `network-operator` (Scheduler & Resources).

### 4.2 Which, if any, touch internet/WAN? **[observed + inference]**
- **None perform any internet measurement.** `fabric/nic-topology-check.py` *classifies* each `/sys/class/infiniband` HCA as **fabric / storage / frontend**. It uses `nvidia-smi topo -m` plus per-port rate and link layer ("frontend : non-RDMA NIC, or RDMA NIC running Ethernet at < 100 Gb/s"). In other words, the CLI *inventories* the north-south-facing NICs and their link speeds. But it never sends a packet through them.
- `ingress-controller` and `load-balancer` (K8s only) are in-cluster service plumbing. They cover MetalLB namespace/pod/IPAddressPool detection, `kubectl get svc` LoadBalancer-IP counts, and IngressClass discovery (`cluster-audit-k8s.sh` lines ~2018–2116). These checks verify that a tenant *can* expose services. They measure nothing about the internet path.
- A repo-wide grep for `speedtest|cloudflare|iperf|ping|traceroute|mtr|dig|nslookup|8.8.8.8|whois|egress|peering|transit` matches **zero** test code. The only "ping" hit is `scontrol ping` for Slurm target detection in `target_selection.py`. **[observed]**
- `virtio-net-check.py` reads BlueField DPU virtio-net controller versions via `virtnet version` (CVE-2026-65094, CVSS 9.0). This check covers frontend DPU *security*, not performance.

### 4.3 Network inventory the collector gathers **[observed]**
The audit values JSON has a `networking` block (`audit-common.sh` ~line 1223). The block holds `rdmaType`, `infinibandInstalled`, `mofedVersion`, `rdmaDevices`, and `hcaNamingValid`. It holds `hcaDevices` (per-HCA rate/state/link_layer/PCI IDs/hca_type/fw_ver from sysfs). It holds `ibPkeysConfigured`, `ibPkeyCount`, and `ibTenantIsolation` (incl. `ibhosts` sampling).

The block also holds `sharpAvailable`, `roceMode`, `topologyConfigured`/`topologyPlugin`, `ncclAutoConfig`, and `ncclIbGidIndex`. It holds `nicFabric` (per-device classification, `computeFabricClass/Count/Gbps`, `hasInfiniband/hasRoce/hasEfa`, `efaDevices`, `efaLibfabric`). It also holds `utilities`. This field has presence/exit-status probes for `ibdev2netdev`, `ibv_devices`, `rdma link show`, `rdma dev show`, `ibstat`, `ibstatus`, `lspci -D` (`host-check.sh` ~line 2128).

[inference] This is a config/inventory snapshot. The fastest NIC rate that the collector records is sysfs line rate, not measured throughput.

### 4.4 What the CLI explicitly omits **[observed]**
- README: "The audit omits criteria that require commercial, contractual, performance, reliability, provider-side, or scale-out network evidence". It also says "The core audit collects cluster, host, GPU, storage, network, health, and security data. **It does not run the planned performance or reliability tests**" ([README](https://github.com/SemiAnalysisAI/ClusterMAX)).
- README: the standalone audit "omits scale-out network checks. It does not inspect InfiniBand, RoCE, RDMA, HCA naming, PKeys, UFM, SHARP, fabric topology, or GPUDirect RDMA". Slurm/K8s audits keep their scale-out checks ([README](https://github.com/SemiAnalysisAI/ClusterMAX)).
- The UFM check in the security profile requires "provider-side verification" (`security.py`). In other words, even the fabric-security evidence is partly out-of-band. **[observed]**

---

## 5. The honest-miss list for internet quality (our differentiation base)

Each item gives evidence that ClusterMAX does not test it. The evidence comes from the three methodology articles, the current criteria pages, and the CLI code.

1. **Sustained egress at scale.** No test in any release moves 10TB+ of data *off* the cluster to an arbitrary destination (S3/R2/GCS or otherwise). The 2.0 suite times only ingress (NGC pull, HF model pull, speedtest). The 3.0 suite adds "download/upload speed, mostly from Cloudflare". This addition is a single-node speedtest-style probe, not a sustained bulk egress measurement.

   No source describes any egress cap/throttle/billing validation ([2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard), [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard), [criteria/networking](https://www.clustermax.ai/criteria/networking), [CLI grep](https://github.com/SemiAnalysisAI/ClusterMAX)). The sibling storage brief reaches the same conclusion from the storage side ([storage brief, §2.9](../storage-research/clustermax.md)). **[observed]**
2. **Loaded latency / bufferbloat.** No test measures latency under saturated load on the public path. The closest artifact is a burn-in observation about the frontend node-pair test. That test "has revealed big performance differences on certain Ethernet networks under load" ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

   But that test is an internal management-network test. Its loaded behavior is incidental to the GPU+network burn-in. It is not a dedicated bufferbloat (latency-vs-queue-depth) sweep. No article, criterion, or CLI file mentions bufferbloat. **[observed absence]**
3. **Jitter.** The word "jitter" has zero occurrences across the 1.0/2.0/3.0 articles, all ten fetched criteria pages, and the CLI repo. **[observed absence]**
4. **Loss rates on the public path.** The only packet-loss measurement is "management-network packet loss, RTT, and TCP bandwidth between every directed pair across four nodes". This measurement covers an internal frontend/management mesh, not the internet. No test covers UDP loss, a public-path loss-rate %, or loss-burst characterization ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). CLI grep confirms no loss-rate check. **[observed]**
5. **Path/routing audit (mtr / AS paths / BGP).** The articles, criteria, and code contain no traceroute, mtr, AS-path, or looking-glass analysis. The only IP-level check is the 2.0 whois IP-ownership test. That test verifies *provider identity* (exposing resellers), not path quality or routing hygiene ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). **[observed]**
6. **DNS.** No test checks DNS resolution performance, correctness, or failover. The CLI has no dig/nslookup/resolv.conf logic. No criterion covers DNS. No release article discusses DNS. **[observed absence]**
7. **Failover/convergence.** The fault-tolerance phase injects GPU XIDs and reboots nodes ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). No test covers ISP/uplink/link failover, BGP convergence timing, or dual-homing validation. Transit redundancy appears only in a user-reported anecdote about IREN Prince George's "single ISP… no redundancy in Northern Canada" ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[observed]**
8. **Transit diversity / peering posture.** ClusterMAX does not list it as a criterion and does not test it. ClusterMAX infers peering quality only indirectly through NGC/HF pull times ("a critical test of a provider's peering and local caching strategy", [2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). ClusterMAX collects no peeringDB, IX presence, or upstream-provider-diversity evidence. **[observed absence]**
9. **DDoS protection/scrubbing capacity.** The ClusterMAX corpus (articles, criteria pages, CLI) has zero mentions of DDoS. **[observed absence]**
10. **Multi-node / long-horizon internet measurement.** Every internet observation comes from a single machine over minutes. The 8-hour burn-in stresses only GPUs + east-west fabric ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). No test measures north-south behavior under concurrent cluster load, across the full test window, or day-over-day. **[inference from observed test descriptions]**
11. **Synthetic-test gaming defenses.** ClusterMAX itself catches STN posting "excellent, symmetrical 10 Gbps speedtest results" while real downloads crawl ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). But its published methodology offers no systematic defense against traffic shaping that favors speedtest endpoints. For example, it has no multi-endpoint, multi-protocol, or fixed-payload verification. **[observed + inference]**

**Net:** two items represent north-south internet quality on the 142-criterion scorecard. Item (a) is one Lifecycle criterion about *fees* ("No punitive data egress / offboarding fees", [criteria/lifecycle](https://www.clustermax.ai/criteria/lifecycle)). Item (b) is minutes of Cloudflare/pip/NGC/HF timing in the Lifecycle test phase ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

A 2-hour measured certification covers sustained egress/ingress to S3/R2/GCS, loaded latency, jitter, and loss. It also covers path audit, DNS, and TCP health. It always measures these values and never uses vendor claims. That certification covers ground that no ClusterMAX release touches. **[inference]**

---

## 6. ClusterMAX/SemiAnalysis commentary on internet/egress as a buying criterion

1. **Egress fees as vendor lock-in (1.0, verbatim):** "Lastly, for the **Offboarding Phase**, we evaluate if there is vendor lock-in. Hyperscalers famously have high egress fees to prevent their customers from switching to another cloud. Most Neocloud Giants and Emerging Neoclouds do not charge egress fees for moving data to another GPU cloud" ([1.0 article](https://newsletter.semianalysis.com/p/the-gpu-cloud-clustermax-rating-system-how-to-rent-gpus)). This concern is now a scored Lifecycle criterion: "No punitive data egress / offboarding fees" ([criteria/lifecycle](https://www.clustermax.ai/criteria/lifecycle)). **[observed]**
2. **Neocloud pricing includes free ingress/egress (1.0):** "For most Neoclouds, this price is all-inclusive and bundles in the on-board CPU, networking, power usage, local NVMe storage… **Internet connectivity and data ingress and egress are typically not chargeable**" ([1.0 article](https://newsletter.semianalysis.com/p/the-gpu-cloud-clustermax-rating-system-how-to-rent-gpus)). **[observed]**
3. **Market trend / R2 pressure (2.0, on storage+egress economics):** "we expect hyperscalers like AWS, Azure, GCP, and Oracle to follow the current trend of reducing their price per GB per month on their Object Storage offerings (driven by competition from CloudFlare R2 in many cases), **reduce or remove punitive egress fees**, and reduce or remove costs associated with storage operations like data access" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). **[observed]**
4. **Bandwidth as a line item (2.0, Bitdeer):** "Bitdeer offers different prices for bandwidth on a per-VM basis, ranging from 1Mb/s to 1024 Mb/s on a fixed or pay-per-use traffic basis. In heavy usage scenarios, this can double the cost of a 1x B200 VM on their platform from $4.69/hr to $8.27/hr" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). **[observed]** [inference] Metered/limited WAN is a live commercial variable in this market. Yet no ClusterMAX criterion scores *measured* WAN capacity.
5. **The zero-egress marketing wave:** CoreWeave announces "Zero Egress Migration" in the same period. The announcement markets free data movement for GPU-cloud migrations ([CoreWeave announcement](https://finance.yahoo.com/news/coreweave-announces-zero-egress-migration-140500798.html), as our sibling storage brief verifies). [inference] Egress economics is now a competitive buying criterion. Providers market it on claims. A measured certification closes this exact gap.
6. **Download convenience framed as buyer friction (2.0):** the article says slow phi-4 downloads "increas[e] friction for researchers switching between models". It calls the NGC pull "a critical test of a provider's peering and local caching strategy" ([2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)). **[observed]** SemiAnalysis treats internet speed as an ease-of-use signal, not a capacity/SLA dimension. **[inference]**

---

## 7. Implications for rack-bench `bench internet`

Each opening maps to the evidence above:

1. **Sustained object-store egress/ingress is the headline gap.** No ClusterMAX release measures a sustained 10TB+ transfer to S3/R2/GCS in either direction. Its WAN evidence is one 22.1 GB pull, one ~15 GB model pull, and a Cloudflare speedtest (§3, §5.1). Our bench's sustained-throughput-to-public-object-stores test is unique in the ecosystem.
2. **Loaded latency, jitter, and loss are untouched.** No source covers jitter. Loss/RTT appear only on an internal four-node management mesh (§5.2–5.4). A bufferbloat-style loaded-latency test and per-path loss-rate reporting are greenfield.
3. **Path/routing and DNS audits are greenfield.** The articles, criteria, and CLI code contain no mtr/AS-path/BGP/DNS evidence (§5.5–5.6). A Chennai node can certify its AS-path diversity, transit, and DNS behavior. That node then publishes data that no rival systematizes.
4. **TCP health under load** (congestion behavior, retransmits, window scaling on the WAN path) has no ClusterMAX analog. Its only TCP-bandwidth measurement is node-to-node internal (§1.3).
5. **Failover/convergence and transit diversity** are certifiable with the dual-uplink test that ClusterMAX never runs (§5.7–5.8). The IREN "single ISP" anecdote (§3.3) shows exactly the failure mode that buyers fear. Nobody measures that failure mode.
6. **Defend against synthetic-test gaming** by design. Use multi-endpoint (S3+R2+GCS+CF), fixed payloads, and concurrent-node testing. This design responds directly to the STN traffic-shaping finding (§5.11).
7. **Match the acceptance-testing contract moment.** ClusterMAX's SLA appendix recommends "acceptance testing… across GPU compute, networking, storage and software". It recommends this testing via a SemiAnalysis technical assessment (consulting engagement). Its public CLI "does not run the planned performance or reliability tests" (§4.4, [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). An open, reproducible 2-hour `bench internet` certification fills the measurement hole in that contractual moment. Our storage brief identifies the same positioning ([storage brief, §4](../storage-research/clustermax.md)).
8. **Egress economics + measurement together.** ClusterMAX scores egress only as a fee criterion (§6.1). One certificate can pair measured sustained-egress Gbps with the egress-fee schedule of the provider. That pairing is strictly more informative than either alone.

---

## 10-line summary: the internet-coverage gap we can exploit

1. ClusterMAX 3.0 (Sep 2026) is current: 77 providers, 10 dimensions, 142 criteria. The CLI ships as `cmax` 0.2.1 with nightly builds. No newer release exists.
2. The Networking dimension has 10 criteria, all east-west fabric. They cover topology, IB/RoCE, HPC-X, NCCL config, SHARP, 4-node NCCL, and NCCL monitoring. The dimension has zero north-south criteria.
3. Internet quality appears in only two forms. One is a Lifecycle fee criterion ("No punitive data egress / offboarding fees"). The other is minutes-scale convenience probes (pip/uv, NGC/HF pulls, Cloudflare speedtest).
4. The 2.0 article gives quantified WAN anchors. NGC 22.1 GB pull: CoreWeave <10 s mirrored; Nebius/Oracle 45–60 s; Silver 90–120 s; Bronze >4 min. phi-4 15B: median ~35 s ≈ 3.4 Gbps, top tier >6 Gbps. Speedtest median: ~4.5/~2.8 Gbps down/up.
5. The 3.0 article gives provider verdicts: Nebius "WAN is good"; TensorWave/Gcore/Hyperstack "N/S fine"; Firmus 0.25 Gb/s to NGC. Crusoe gets 0.47–0.78 Gbps (Iceland), and Bitdeer gets ~0.1 GB/s. These verdicts are anecdotes, not a suite.
6. The public `cmax` CLI greps clean of any internet test. It has no speedtest, ping, traceroute, mtr, DNS, iperf, or whois code. Its 10 Networking & Fabric checks are config/inventory only. It does classify frontend NICs and their sysfs link rates. But it never sends traffic.
7. The CLI's own README admits this gap. The README says the CLI "omits criteria that require commercial, contractual, performance, reliability, provider-side, or scale-out network evidence". The CLI runs none of the performance tests.
8. The honest-miss list is long and evidenced. It covers sustained egress at scale, loaded latency/bufferbloat, jitter (zero mentions corpus-wide), and public-path loss. It also covers mtr/AS-path audits, DNS, WAN failover/convergence, transit diversity, and DDoS. No source tests any of these items anywhere.
9. SemiAnalysis itself catches a provider (STN) gaming speedtest with traffic shaping. This case proves that the market needs a multi-endpoint, fixed-payload, tamper-resistant internet certification.
10. Egress is already a scored buying criterion (fees/lock-in). It is also a marketing battleground (CoreWeave "Zero Egress Migration"). But no one measures it. A 2-hour measured S3/R2/GCS egress/ingress, latency, jitter, loss, path, DNS, and TCP-health certification owns that ground outright.

---

## Gaps

- **ClusterMAX-internal repo is dark.** Our storage brief cites the `SemiAnalysisAI/ClusterMAX-internal` repo (e.g. its fio run artifacts). That repo now returns HTTP 404 for both the repo root and the linked blob (checked 2026-10-11). We cannot enumerate its run artifacts for any internet/speedtest evidence (e.g. a `tests/network` or `speedtest` directory). So the claim "the full suite is proprietary" rests on two items. They are the 3.0 article's "The rest we keep internally for now" plus our CLI grep.
- **Full 142-item criteria text.** The clustermax.ai dimension pages render only "Key Requirements" server-side. We reconstruct the complete itemized list from vCluster's scorecard. That scorecard reproduces all 142 line items, but it is a third-party copy (last synced date unknown). Networking's 10 items match clustermax.ai exactly, so confidence is high. But we do not individually re-verify the remaining 132 items against the primary source.
- **Paywalled 1.0 content.** The 1.0 article has a paywalled tail (GB200 pricing/IRR deep dive). We cannot check that tail for any additional internet-test methodology. Our "no internet suite in 1.0" finding covers the free portion only.
- **3.0 per-provider download/upload numbers beyond the seven WAN verdicts** (Nebius, TensorWave, Gcore, Hyperstack, Firmus, Crusoe, Bitdeer) are unpublished. The article gives no numbers for them. The dashboard charts in the article are images. Exact Gbps tables per provider for the 3.0 Cloudflare test do not exist in public form.
- **Exact test durations.** Neither article states how long the Lifecycle internet checks run. Neither article states the payload size of the Cloudflare test. So we cannot compute a "certification-window overlap" number vs our 2-hour window. We have only the qualitative "minutes-scale" characterization.
- **Verification of the exemplar's storage-side URLs** (e.g. CoreWeave triple-Platinum blog) does not repeat here. These URLs come from the sibling brief. We link them and do not re-derive them.
