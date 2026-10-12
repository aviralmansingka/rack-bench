# Neocloud fabric evidence for a two-hour GB300 rack certification

Research date: 2026-10-11. All claims below use a source URL.

## 1. Scope and evidence standard

### 1.1 What counts as tenant-obtainable evidence

[observed] Use this brief for east-west GPU fabric evidence a tenant can access or reproduce. That evidence makes these classes: configuration and topology disclosures, executable benchmark recipes, measured collective results, and health telemetry. Do not use vendor link-rate claims as measured tenant results. The user-provided bench contract uses measured (never vendor-claimed) PASS outcomes only.

Separately, README shows these quick checks: port/link state, perftest, TCP/RDMA pairs, and a sampled intra-rack matrix. It also shows small-message latency, loss counters, and NCCL allreduce/allgather/alltoall from 8 B to 16 GB. It shows algbw/busbw as line-rate percentages and checks curve monotonicity. [README network checks](../../README.md#L327-L337); [network audit fields](../../README.md#L170-L184)

[observed] Use the intended separation: audit inventory/configuration first; active QP creation and a two-rank all-reduce canary during bench. Audit keeps rail names/planes, NCCL variables/plugins, and accessible switch information. Keep switch access optional. Put unavailable switches in SKIP, with host RDMA counters as fallback. [README NCCL configuration and active validation](../../README.md#L220-L241); [network audit fields](../../README.md#L170-L184)

## 2. Provider evidence: claims, recipes, and disclosure

### 2.1 Nebius: bandwidth and Quantum-X800 are published capabilities, not pass results

[observed] Nebius documentation shows 400 Gbps per GPU NIC. It shows 3.2 Tbps per 8-GPU VM, with GPUDirect RDMA. It shows clusters as occupying physical InfiniBand fabrics. It uses unique P-Keys to isolate tenant clusters on shared physical fabric. Keep these as architecture/capability statements. The documentation shows no per-rail measured bandwidth, latency, goodput, or GB300 tenant result ([Nebius GPU cluster networking](https://docs.nebius.com/compute/clusters/gpu)).

[observed] Nebius AI Cloud 3.1 marketing shows GB300 NVL72 and HGX B300 on 800 Gbps NVIDIA Quantum-X800 InfiniBand. It shows this as doubling throughput for distributed workloads. This shows a product/fabric deployment claim, not measured NCCL output or proof every rail achieves line rate. [Nebius announcement](https://nebius.com/newsroom/nebius-ai-cloud-3-1-delivers-next-generation-nvidia-blackwell-ultra-compute-with-transparent-capacity-management-for-ai-at-scale)

[observed] Nebius shows a tenant-usable NCCL test route. Its GPU-cluster guide shows an MPIrun tutorial using NCCL tests and an Soperator all-reduce example. The guide shows a separately linked physical-state test. Keep that as actionable test guidance. A recipe makes no published fleet baseline. [Nebius guide](https://docs.nebius.com/compute/clusters/gpu); [Soperator all-reduce example](https://docs.nebius.com/slurm-soperator/jobs/examples/nccl-all-reduce)

### 2.2 CoreWeave: strongest public NCCL troubleshooting and topology-health evidence

[observed] CoreWeave shows `nccl-tests` container images and MPI/Slurm sample jobs. It also shows a baseline-driven triage method. Use it: keep `busbw` records from a small known-good group. Then check suspect nodes against that baseline. Their guide shows single-node success (NVLink path) and multi-node failure (RDMA path) as separate cases. It shows TCP fallback as a possible cause of very low multi-node throughput ([CoreWeave nccl-tests](https://github.com/coreweave/nccl-tests); [NCCL error triage](https://docs.coreweave.com/support/sunk/articles/what-do-nccl-errors-mean); [InfiniBand GPUDirect RDMA guide](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma)).

[observed] CoreWeave's GB300 RoCE guidance explicitly shows NCCL's verbs path and UCX-based traffic as separate. NCCL passing does not show UCX/NIXL working. It shows RoCE-specific variables and a UCX perftest recommendation for UCX workloads. This makes a case for testing the actual transport stack in addition to NCCL. [CoreWeave RoCE GPUDirect guide](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma-roce)

[observed] CoreWeave shows a rail-optimized design with large rail pods and fewer hops for communicating GPUs. Internal tools check link flaps and bit errors in rail group/SuperPOD/fabric impact context. Keep this as a first-party architecture/operations disclosure. It shows no tenant-accessible raw per-rail results or flap-rate time series. [CoreWeave engineering statement](https://www.coreweave.com/blog/coreweave-ranks-as-1-ai-cloud-backed-by-semianalysiss-platinum-clustermax-tm-rating)

[observed] A CoreWeave sample intentionally makes a non-SHARP reference run with CollNet/SHARP disabled (`NCCL_COLLNET_ENABLE=0`). Use this experimentally. Run identical SHARP-disabled/enabled comparisons only where tenant permissions and fabric support allow. Do not make the raw link rate the source of a gain. [CoreWeave SGLang/NCCL test example](https://docs.coreweave.com/products/cks/clusters/frameworks/sglang)

### 2.3 Lambda: dedicated fabric disclosure, limited public performance evidence

[observed] Lambda Private Cloud shows a dedicated tenant network design. It uses in-band Ethernet plus InfiniBand, compute nodes on a spine-leaf IB fabric, and unrestricted compute-to-compute communication. It shows RoCE as a possible IB substitute, depending on cluster size. The document shows topology/isolation, not per-rail measurements or workload benchmark results. [Lambda security posture](https://docs.lambda.ai/private-cloud/security-posture)

[observed] Lambda's managed Slurm health-check material shows network checks for high-speed fabric links: present, up, and at full speed. It shows diagnostics/benchmark jobs in `/data/examples`. Keep this as evidence of a provider-side health-check practice. The public wording shows no numerical thresholds, per-rail output, or time-series fault rates. [Lambda Managed Slurm health checks](https://docs.lambda.ai/managed-slurm/health-checks)

[observed] Lambda's SHARP article shows tenant-facing use through NCCL-aware collectives with the Quantum InfiniBand network and plugin configured. Keep it as enablement guidance, not a comparative measured result. [Lambda SHARP guide](https://lambda.ai/blog/nvidia-sharp-on-lambda-1cc)

### 2.4 Crusoe: unusually concrete configuration disclosure, no public per-rail results

[observed] Crusoe shows 8 HCAs and aggregate 3.2 Tbps for documented H100/H200 SXM instances (1.6 Tbps A100). It also shows logical IB networks and partitions for tenant placement/isolation. Keep the figures as advertised instance capacity, not measured goodput. [Crusoe IB management](https://docs.crusoecloud.com/networking/infiniband/managing-infiniband-networks)

[observed] Crusoe shows NCCL topology XML files by instance type. It shows a topology/configuration handling requirement for virtualized PCI addresses. Its image service uses `NCCL_TOPO_FILE`. The guidance removes an Ethernet HCA from `NCCL_IB_HCA`. Keep this as strong configuration guidance and a concrete warning. Incorrect device/topology selection can make collective results invalid ([Crusoe IB management](https://docs.crusoecloud.com/networking/infiniband/managing-infiniband-networks)).

[observed] Crusoe's burn-in description shows multi-node NCCL collectives testing the IB fabric. It shows a contrast with single-node GPU P2P/NVLink tests for fault attribution. It shows the test class but no published rail-separated measured tables or flap rates. [Crusoe burn-in overview](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)

## 3. Routing, SHARP, and what aggregate NCCL can hide

### 3.1 Rail-optimized versus static routing

[observed] CoreWeave publicly shows rail-optimized topology and fewer hops. The cited disclosure shows no evidence that tenants can choose or inspect adaptive routing policy. [CoreWeave statement](https://www.coreweave.com/blog/coreweave-ranks-as-1-ai-cloud-backed-by-semianalysiss-platinum-clustermax-tm-rating)

[observed] NVIDIA's Quantum InfiniBand operations guidance shows recommendations for topology and fabric-health validation and link monitoring/telemetry review. Keep this as operational guidance, not evidence of tenant adaptive-routing controls at any named neocloud. [NVIDIA Quantum InfiniBand operations](https://developer.nvidia.com/blog/simplifying-network-operations-for-ai-with-nvidia-quantum-infiniband)

[inference] Do not make routing-policy inferences from aggregate NCCL alone in a two-hour tenant certification. Keep HCA-to-rail mapping and per-port link state records. Then check rail-isolated point-to-point and collective runs where controls permit.

If the provider does not show route mode or rail pinning, keep that as unobservable. Do not make adaptive/static behavior assertions. This approach uses README’s per-rail topology and validation requirements ([README](../../README.md#L170-L184), [NCCL configuration](../../README.md#L220-L237)). NVIDIA shows topology and fabric-health validation recommendations but no tenant routing controls ([operations guidance](https://developer.nvidia.com/blog/simplifying-network-operations-for-ai-with-nvidia-quantum-infiniband)).

### 3.2 SHARP: separate feature validation from baseline

[observed] NVIDIA shows SHARP as switch-offloaded collective reduction integrated with NCCL, intended to reduce host/network work and improve scalability. These make mechanism and benefit claims, not a guaranteed gain for every workload. [NVIDIA SHARP overview](https://developer.nvidia.com/blog/advancing-performance-with-nvidia-sharp-in-network-computing)

[observed] Nebius Quantum-X800 material shows SHARP-capable fabric context. Lambda shows SHARP enablement guidance. CoreWeave shows a non-SHARP NCCL reference configuration. Public sources reviewed here show no comparable tenant-measured SHARP-on versus SHARP-off numbers for GB300. [Nebius announcement](https://nebius.com/newsroom/nebius-ai-cloud-3-1-delivers-next-generation-nvidia-blackwell-ultra-compute-with-transparent-capacity-management-for-ai-at-scale); [Lambda SHARP guide](https://lambda.ai/blog/nvidia-sharp-on-lambda-1cc); [CoreWeave sample](https://docs.coreweave.com/products/cks/clusters/frameworks/sglang)

[inference] First, make a non-SHARP known-good collective baseline in the certification window. Then run a short identical SHARP-enabled comparison if plugin/fabric access is available. Keep actual plugin selection and log records. A configuration flag alone does not show that offload occurred. Keep SHARP as an optimization/feature check, not a substitute for ordinary per-rail correctness and bandwidth.

## 4. Recommended two-hour evidence plan

### 4.1 Fast checks that fit and diagnose

[inference] Use this practical order. (1) Make an inventory of each port/HCA, negotiated speed/state, rail mapping, and accessible counters. (2) Run one short `ib_write_bw` and `ib_read_bw` per rail in both directions, and keep achieved throughput and error records. (3) Run a small set of node pair checks, including same-rack and cross-rack/scale-out endpoints. (4) Run NCCL all-reduce/all-gather/all-to-all at representative sizes: tiny latency-sensitive messages, medium messages, and large transfers.

(5) Make goodput calculations against the correct aggregate or per-rail line-rate denominator. (6) Check monotonicity and asymmetry, then run suspect points again. Keep this order aligned with the local README contract. [README network bench checks](../../README.md#L327-L337)

[inference] Put the 8 B–16 GB sweep first, in a bounded set rather than exhaustive dense sampling. Use 8 B/latency, logarithmically spaced transitions, and large payloads. Run MPI and `torch.distributed` canaries only as time allows. Use collective `algbw` and `busbw` to separate algorithm-level operation throughput from fabric-equivalent bandwidth. Keep raw output and environment/configuration for reproducibility. [README network bench checks](../../README.md#L327-L337)

[inference] For RoCE, keep ECN/PFC and congestion-control configuration plus port counters before and after load. For IB, keep port symbol/link errors and available congestion/fabric counters. A clean zero-loss counter makes sense only with readable counters and a captured measurement interval. Dead rail = absent/down HCA or failed QP. Slow rail = per-rail goodput materially below matched peers. Asymmetry = directional read/write or endpoint differences.

Use profile thresholds, not vendor claims. README shows requirements for ECN configuration, packet-loss checks, and RDMA counter fallback ([network audit](../../README.md#L170-L184), [network bench](../../README.md#L327-L337)). NVIDIA also shows a telemetry review recommendation ([guidance](https://developer.nvidia.com/blog/simplifying-network-operations-for-ai-with-nvidia-quantum-infiniband)).

### 4.2 Scale-out and telemetry evidence

[observed] Keep one physical plane distinct from one logical HCA rail: these labels show different topology levels. They do not alone show independent path diversity. README explicitly shows planes and expected HCA names as distinct ([README](../../README.md#L222-L225)). Crusoe also shows topology/configuration artifacts ([guide](https://docs.crusoecloud.com/networking/infiniband/managing-infiniband-networks)).

[observed] CoreWeave shows internal monitoring for link flaps and bit errors. The public source does not show tenant access to raw telemetry or historical flap rates. Lambda shows provider management/observability nodes. It shows no tenant-facing IB telemetry fields. Nebius shows diagnostic logs including GPU/InfiniBand/node logs in its changelog. Cited docs show no continuous per-rail telemetry guarantees ([CoreWeave statement](https://www.coreweave.com/blog/coreweave-ranks-as-1-ai-cloud-backed-by-semianalysiss-platinum-clustermax-tm-rating); [Lambda posture](https://docs.lambda.ai/private-cloud/security-posture); [Nebius changelog](https://docs.nebius.com/changelog)).

[inference] Within two hours, keep counter snapshots before/after traffic. Keep node/port identifiers, link transitions if exposed, NCCL logs, and timestamps. README shows host RDMA counters as a permitted fallback ([README](../../README.md#L181-L184)). A snapshot cannot show long-term flap rates.

Importantly, multi-node traffic within an NVL72/MNNVL scale-up domain may still use NVLink rather than RDMA. Check RDMA via NCCL logs and counters, or use a cross-rack peer. README shows a warning: jobs must not silently cross the NVLink domain ([README](../../README.md#L232-L237)). CoreWeave shows NVLink and RDMA paths as distinct ([triage guide](https://docs.coreweave.com/support/sunk/articles/what-do-nccl-errors-mean)).

## 5. Measured results versus disclosed claims

### 5.1 Measured tenant-visible performance

[observed] The primary provider materials cited above chiefly make testing instructions, topology/configuration guidance, or operational descriptions. Do not use the cited Nebius 3.2 Tbps and Quantum-X800 figures as tenant-measured per-rail results. Do not use the Crusoe 3.2 Tbps figures or CoreWeave rail-optimized description as such results. CoreWeave's baseline method shows customers how to check their own `busbw`. It shows no published universal threshold. [Nebius](https://docs.nebius.com/compute/clusters/gpu); [Crusoe](https://docs.crusoecloud.com/networking/infiniband/managing-infiniband-networks); [CoreWeave triage](https://docs.coreweave.com/support/sunk/articles/what-do-nccl-errors-mean)

### 5.2 Missing disclosure, carefully scoped

[observed] The reviewed primary public pages for Nebius, CoreWeave, Lambda, and Crusoe show no comparable per-rail measured `ib_write_bw`/`ib_read_bw` tables. They show no directional asymmetry results, rail-level goodput percentages, or quantified flap rates. Keep this bounded finding on the cited public sources, not private portals or internal data. Sources: [Nebius fabric/NCCL guide](https://docs.nebius.com/compute/clusters/gpu), [CoreWeave NCCL triage](https://docs.coreweave.com/support/sunk/articles/what-do-nccl-errors-mean) and [rail disclosure](https://www.coreweave.com/blog/coreweave-ranks-as-1-ai-cloud-backed-by-semianalysiss-platinum-clustermax-tm-rating), [Lambda posture](https://docs.lambda.ai/private-cloud/security-posture) and [health checks](https://docs.lambda.ai/managed-slurm/health-checks), [Crusoe IB guide](https://docs.crusoecloud.com/networking/infiniband/managing-infiniband-networks).

[observed] Use different classes for provider evidence: Nebius shows capacity and an NCCL recipe. CoreWeave shows sample images, baselining/triage, and qualitative rail-aware operations. Lambda shows private-cluster topology and link health-check descriptions. Crusoe shows per-instance bandwidth claims, tenant partitioning, and NCCL topology/configuration artifacts. Keep all those evidence classes separate from a rack-bench PASS.

## 6. Gaps

1. [observed] Public material reviewed shows no answer on per-rail telemetry or adaptive-routing controls at Nebius. It shows no answer on tenant-visible ECN/PFC counters or measured GB300 collective baselines. Use a tenant cluster. Check available logs/counters. Send a rail-separated result-set request.
2. [observed] Keep CoreWeave's public rail/flap disclosure as qualitative. The public pages reviewed show no tenant access to flap histories, rail-level counters, or routing mode. Send an anonymized telemetry export request. Run the baseline recipe on the target allocation.
3. [observed] Lambda's public private-cloud description shows dedicated spine-leaf IB and health checks. It shows no per-rail measured output. Keep `/data/examples` and management telemetry availability as possibly deployment-dependent. Check with a real handoff.
4. [observed] Crusoe's published detailed topology files and bandwidth table show A100/H100/H200 examples, not GB300. Do not make GB300 or Quantum-X800 extrapolations from those advertised capabilities.
5. [inference] Public evidence makes no sufficient basis for universal pass thresholds on 8 B–16 GB NCCL curves or SHARP uplift. Use the rack certification profile, matched topology, and measured hardware line rate. Keep capability claims in a separate report.
