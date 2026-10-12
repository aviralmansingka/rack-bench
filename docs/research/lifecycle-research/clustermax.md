# ClusterMAX Lifecycle: Published Criteria and Hands-on Coverage

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Current release and scope

### 1.1 Release status **[observed]**

The site marks ClusterMAX 3.0 (September 2026) Current as of the research date. It also exposes 2.1 (April 2026), 2.0 (November 2025), and 1.0 (March 2025) as prior releases. [ClusterMAX home](https://www.clustermax.ai)

The 3.0 methodology describes three stages. Stage one is an approximately 15-minute yes/no audit. Stage two is performance testing with microbenchmarks and real-world benchmarks. Stage three is reliability/fault-tolerance testing.

The public `cmax` audit is available. SemiAnalysis says the rest of its detailed testing remains internal. The report cautions that tests evolve over time. [ClusterMAX 3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 1.2 Lifecycle's meaning **[observed]**

In 3.0, Lifecycle is a performance-phase category. It aims to understand “ease of use of the cluster throughout its lifecycle.” The published method is a set of “contrived tests,” not an exhaustive contractual lifecycle assessment. It combines setup/use convenience, software readiness, storage-tier behavior, application start, Kubernetes churn and PVC behavior, and destructive node-reboot recovery. These tests touch tenant experience from first access through workload use and a reboot. The published methodology does not present an end-to-end stopwatch from contract signature to first useful GPU-hour. [ClusterMAX 3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 2. Exact published Lifecycle criteria (current 3.0 page)

The current criteria page lists these 15 Lifecycle requirements. **[observed]** The wording below follows the live page; its last items explicitly carry a “Slurm” tag. [ClusterMAX Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle)

1. Transparent onboarding costs and delivery timelines that are met.
2. No punitive data egress / offboarding fees.
3. Easy onboarding with no preference between console/UI or API/Terraform/CLI, as long as whichever options are offered are well-documented and easy to use.
4. Delivery date accuracy and meeting expectations.
5. Knowledge of industry experts (e.g., Sylvain).
6. Provisioning of CPU head node for Slurm without explicit request (Slurm).
7. Understanding of standard ML user expectations.
8. Out-of-the-box GPUDirect RDMA (between NIC and GPU) setup.
9. Out-of-the-box IB/RoCEv2 & NVIDIA drivers configuration.
10. Performance optimization libraries (e.g., Together AI kernel collection).
11. Audit logs capturing resource actions (create/start/stop/delete), administrative actions (role changes, login success/failure), and billing events.
12. Audit log entries include actor identity (user ID, email, IP address), action details, target resource, timestamp, and success/failure status.
13. Audit logs queryable via API with filtering by resource type, project, user, and date range.
14. Minimum 90-day audit log retention with export capability.
15. Audit log access restricted to administrators with no additional usage charges.

**[inference]** This is a mixed category: customer journey and contract/commercial expectations, environment configuration, and audit-log controls sit together. The page labels these “Key Requirements”. It does not expose a separately numbered acceptance protocol. It also does not explain which requirements are hands-on versus document/contract evaluation.

## 3. Hands-on method by release

### 3.1 ClusterMAX 3.0: published direct tests **[observed]**

The article gives a concrete, release-specific mechanism:

- The method checks internet speed using multiple methods, mostly Cloudflare. It times PyTorch and vLLM package installation with `pip` and `uv`. It tries container downloads from Docker Hub, ghcr.io, and nvcr.io. It pulls models from Hugging Face and ModelScope. (Sibling briefs detail internet/storage-specific coverage; this brief links rather than re-derives.) [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- The method repeats `pip`/`uv` installs with fresh caches across each available tier. Tiers: home, shared filesystem, local NVMe scratch, and additional mounts. It then times `import torch` from each location. The published example says most providers take 1–2 seconds; some filesystems with LOSF issues take 10–20 seconds. **[observed]** [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- The method uses downloaded models with `vllm serve`. It measures the time to successfully reach `/v1/models`. The article reports some providers load a small model from shared storage to GPU memory in 10–40 seconds. Some providers take over two minutes. This is an application-readiness proxy, not a complete production inference quality test. **[observed/inference]** [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- Kubernetes churn repeatedly creates/deletes GPU pods and checks API GPU allocation. It reports scheduling and startup latency and failures such as stuck `kubectl delete po`. The method also increases CPU-only sandbox pod batches. It records how many reach Ready, elapsed time, and reasons for Pending. **[observed]** [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- PVC cycle: repeatedly start a pod mounting a volume. Write and `fsync` a file. Delete the pod. Wait for teardown between cycles. A warmup cycle removes the initial image pull from measured runs.

  The method therefore checks a real create/mount/write/durability-call/delete/release sequence. It does not publish an exact cycle count, target latency, or data-integrity readback assertion. **[observed]** [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- Node reboot: reboot all nodes. For Kubernetes, cordon and drain, reboot, and require a changed boot ID. Wait for node return. Stop timing when `nvidia-smi` succeeds in a fresh pod on that node.

  For Slurm, obtain allocation or SSH and run `sudo reboot`. Slurm-on-Kubernetes has a distinct approach. The article says scripts time the process. **[observed]** [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

**[inference]** For an NVL72-class 18-tray rack, the article's stated reboot method is operationally relevant. But its public description does not clarify the meaning of “all nodes”. The phrase may mean every tenant-visible compute node/tray, the whole rack at once, or a sequential reboot. The description also omits rack-scale NVLink-domain integrity checks after recovery. Avoid assuming a specified 18-tray test protocol.

### 3.2 ClusterMAX 2.0: legacy tests and continuity **[observed]**

The 2.0 article explicitly times PyTorch installation via `uv` and `pip`. It uses these as convenience proxies for WAN quality and local small-file I/O. Reported `uv` results: leading examples about 3.2 seconds, median about 8.5 seconds, and one Bronze provider 41.2 seconds. Reported `pip` median: about 28 seconds. [ClusterMAX 2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)

The 2.0 report also describes `import torch` as a practical startup convenience test. The latest detailed, complete method appears in the current 3.0 article. It expands this into per-tier fresh-cache installs and per-location imports. The 3.0 article includes provider experiences reflecting reboot recovery and PVC attach/detach. This does not establish that every 3.0 provider received every test. [2.0 article](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard) · [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 3.3 Evidence boundary **[observed]**

ClusterMAX's public `cmax` release is an audit, not its performance/reliability test harness. The 3.0 article says the audit takes about 15 minutes, checks pre-load configuration, and is public. It adds “the rest we keep internally for now.” Therefore, do not claim a public CLI audit executed the timed package, PVC, churn, `vllm serve`, or reboot tests. The article does say a comprehensive proprietary process uses `cmax` during technical assessments. But it does not publish the internal test code or full evidence outputs. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 4. Hands-on tests versus claim/document/contract checks

### 4.1 Hands-on, measured behavior **[observed]**

The strongest published Lifecycle measurements are durations and outcomes from direct interaction. They include install/import/model-serving time and container/model download time. They also include K8s pod scheduling/startup/deletion behavior and PVC mount/write/fsync/delete with teardown. They cover reboot-to-fresh-pod-GPU-usability. Criteria such as “easy onboarding” may draw on evaluator experience. But the article does not publish a formal scoring instrument or measured onboarding task script. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 4.2 Claims, documentation, and commercial evidence **[observed + inference]**

The criteria “transparent onboarding costs,” “delivery timelines,” and “no punitive data egress / offboarding fees” are fundamentally commercial/contractual propositions. Verifying them requires offers, delivery records, or contract terms, not a GPU benchmark. The expectation that UI/API/Terraform/CLI options are well-documented and easy to use invites a documentation review plus usability observation. “Knowledge of industry experts” and “understanding of standard ML user expectations” are evaluative judgments, not reproducible hardware measurements. Verify audit-log requirements by inspecting records, querying APIs, checking retention/export/access controls, and ideally performing controlled actions. Merely reading a vendor assertion would not verify them. [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle)

The 3.0 article says some topics cannot be hands-on tested. They require other research methods. It explicitly names support experience, pricing, delivery timelines, reliability over time, and performance at scale. It separately says its standardized SLA documents define downtime, thresholds/credits, and two-way measurement commitments. They also define review cadence, termination rights, acceptance testing, and related contract provisions.

This is a proposed contractual framework and research process. It is not evidence that a short bench verified a provider's actual support SLA performance or all terms. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

**Claim-check versus test boundary:** published Lifecycle combines direct tests with claims and research. The public materials do not provide a criterion-by-criterion evidence rubric. The rubric would state the scoring method for each of the 15 current criteria. Methods: inspection, hands-on test, interviews, or contract review. [inference] We should preserve that uncertainty rather than assert exact internal scoring mechanics.

## 5. What is not established by the published method

These are bounded statements about the *publicly described method*, not assertions about unpublished internal work.

1. **Contract signature to first useful GPU-hour / provisioning time.** The 3.0 report describes the allocation of tested clusters, the audit, and lifecycle tests. It mentions provisioning and delivery in other contexts. It does not publish a standardized start event at signed contract/order. It also does not publish a stop event at first useful GPU-hour. Nor does it publish a comparable provisioning-time benchmark protocol across providers.

   Provider anecdotes do report individual elapsed provisioning examples. Examples: Verda 30 minutes; Runpod under two minutes. But these are not a defined cross-provider Lifecycle test. [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
2. **Wipe / sanitization verification at offboarding.** The criteria page evaluates whether egress/offboarding fees are punitive. But the published Lifecycle method does not describe a destructive data-wipe test. It also does not describe tenant-data remanence inspection, cryptographic erase verification, or certificate-of-destruction validation. [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle) · [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
3. **Support-SLA verification.** The 3.0 report expressly identifies support experience as something not fully testable hands-on and based on other research. It proposes SLA definitions and recommends assessments/reviews. The published method does not specify repeated controlled ticket submissions or clocked response/resolution tests against contractual thresholds. It also does not specify independent verification of service-credit fulfillment. [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
4. **Change/reconfiguration and offboarding end-to-end.** Public Lifecycle criteria mention resource create/start/stop/delete audit events and egress/offboarding fees; 3.0 has pod churn and reboot. No detailed published scenario demonstrates a tenant-requested resize, migration/reprovision, or credential revocation. None demonstrates data export and deletion or complete account/project closure. **[observed scope of published method; not universal absence]** [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle) · [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The 3.0 article includes customer anecdotes and provider-specific experiences. Do not conflate these with a systematic Lifecycle benchmark. For example, it reports reboot tests completing for named providers and provisioning problems on AWS. Those are valuable observed cases. They are not proof of uniform test execution or exact score weighting across all providers. [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 6. Two-hour rack-bench implications (GB300 NVL72, Chennai)

### 6.1 What is realistically measurable **[inference]**

A two-hour bench can borrow ClusterMAX's robust operational shapes without copying its undisclosed thresholds. Steps: establish a timed, reproducible tenant task. Execute one minimal Python environment install and `import torch`. Launch a small known GPU workload. Record the first successful useful GPU work.

Test a bounded pod/PVC lifecycle with write, sync, readback, deletion, and teardown. Measure a controlled reboot/recovery only if rack operations authorize it. Record wall-clock timestamps, exit status, retries, resource state, and a machine-readable workload identity. A measured PASS must rest on rack telemetry and direct observations, not provider claims.

A safe quick pass should not claim a destructive reboot of the whole 18-tray rack. This applies when the bench reboots only one node. ClusterMAX's public reboot protocol is disruptive, and the NVL72 system has rack-scale coupling. Therefore the rack operator should decide whether a single tenant-safe node/tray reboot is representative, permitted, and safe. If not, mark it deferred. Do not simulate proof through documents. **[inference]**

### 6.2 Keep claim-checks separate **[inference]**

In a two-hour window, record several claim items. Do not treat them as measured PASS. Items: contract/order timestamp, promised delivery date, written egress/offboarding pricing, and deletion/wipe commitments. Also record SLA terms, support channels and escalation policy, and onboarding docs. If time and access permit, perform a live support-contact exercise and inspect/query audit logs. Label those clearly as protocol/controls checks rather than GPU performance.

Actual delivery-time SLA compliance needs an order-to-ready observation across a real transaction. Actual SLA performance requires repeated observations over the contractual period. Wipe assurance needs a dedicated isolated test protocol and suitable evidence.

### 6.3 Comparison boundary **[observed/inference]**

ClusterMAX 3.0 accepts 5 days each for Slurm and Kubernetes testing, in parallel or sequentially. Its broader evaluation also includes 8-hour GPU/network burn-in. Its method is therefore much larger than rack-bench's approximately two-hour category window. Lifecycle can borrow individual short probes, not claim equivalent lifecycle coverage. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 7. Related sibling research (not repeated)

- Internet/WAN measures and gaps: [ClusterMAX internet brief](../internet-research/clustermax.md).
- Storage measures and gaps: [ClusterMAX storage brief](../storage-research/clustermax.md).

These briefs cover adjacent storage/internet slices. This note focuses on Lifecycle category criteria and operational lifecycle behavior. It does not re-derive their measurements.

## 8. Findings in brief

1. **Current Lifecycle criteria are 15 mixed requirements.** They span onboarding/delivery, egress fees, documentation/usability, standard ML expectations, and Slurm head-node provisioning. They also span out-of-box GPU/network configuration, optimization libraries, and detailed audit-log controls. [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle)
2. **3.0's distinctive hands-on lifecycle mechanisms are explicit.** They include per-storage-tier fresh-cache `pip`/`uv` installs and `import torch`. They include `vllm serve` readiness and K8s churn with sandbox-pod readiness. They include PVC create/mount/write/fsync/delete cycles with teardown and warmup. They end with node reboot to fresh-pod `nvidia-smi` success. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
3. **Not every lifecycle item is a measured performance test.** Fees, delivery commitments, docs, expertise, and many audit-log properties require documentary, contractual, or control-plane evidence. The public source does not map each criterion to internal evidence/scoring method. [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle) · [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
4. **The public `cmax` audit is not the performance suite.** SemiAnalysis says the audit is public, roughly 15 minutes, and the rest of its detailed evaluation is internal. Do not claim the CLI runs Lifecycle timed tests. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
5. **Three meaningful published-method gaps for rack-bench are bounded.** Gap one: no standardized contract-signature-to-first-use provisioning clock. Gap two: no published wipe-verification protocol. Gap three: no published repeated support-SLA verification protocol. This is a statement about public disclosure, not proof such internal or separate work never occurs. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
6. **For a two-hour GB300 pass, reuse small operational probes, not the total ClusterMAX claim.** Measure directly. Gate destructive reboot. Report tenant-safe scope honestly. Put contracts, docs, fee schedules, and SLA assertions in a separate claim-check record.

## Gaps

- The current Lifecycle page supplies 15 “Key Requirements”. But it does not publish itemized criterion IDs, individual weights, pass thresholds, evidence types, or a formal scoring rubric. [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle)
- The 3.0 article says the wider internal test suite is not public. The public method does not provide the precise scripts, timeout limits, repetitions, or thresholds. It also does not provide the provider-by-provider coverage matrix or scoring treatment for Lifecycle. [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- The public article does not state the exact number of PVC cycles or the size/content of test files. It does not say whether the method performs file readback/hash verification. It also does not state numeric pass criteria for teardown, install, import, serving, churn, or reboot.
- ClusterMAX 2.0's article provides some concrete install timings. But public evidence located here does not fully enumerate its 2.0 Lifecycle implementation. It also does not establish which tests persisted unchanged into 3.0. Avoid treating 2.0 detail and 3.0 method as identical.
- The public materials omit exact internal criterion counts. This brief verifies the 15 current Lifecycle requirements by counting the live primary-source list. It does not assert a globally reported total criteria count. It also does not assert a public CLI machine-checkable Lifecycle count.
- Public disclosure does not settle where provisioning clocks, wipe checks, or support-SLA verification occur. Candidate venues: private assessments, provider-specific exercises, interviews, or other SemiAnalysis work. They are gaps in the published Lifecycle method, not universal absences.
- Rack-bench's safe reboot semantics for GB300 NVL72 require local operator approval and platform-specific safety procedure. Open questions: per-node/tray versus complete rack, and sequential versus coordinated. The ClusterMAX description does not resolve this.
