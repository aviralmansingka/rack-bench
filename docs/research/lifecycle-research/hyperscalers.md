# Hyperscaler Lifecycle Controls and Deletion Rules — N02

Research date: 2026-10-11. Each claim below has a source URL.

Use **[observed]** for statements in cited material. Use **[calculated]** for arithmetic from source data. Use **[inference]** for interpretation or proposed rack-bench tests. This file covers provider-published controls for GPU compute lifecycle, data deletion, and tenant-verifiable checks. Feature availability depends on SKU, region, orchestration, and accelerator generation. This file does not claim that GB300/NVL72-class products support any lifecycle feature.

## 1. Executive finding: two distinct lifecycles

### 1.1 Workload lifecycle is observable; physical sanitization is not

[observed] AWS, Azure, and Google publish APIs or events for provisioning and interruption. They also publish APIs or events for stopping, deallocation, deletion, and some recovery behavior. A tenant acceptance test can check these features. Submit an operation, capture API state and event times, and run a short GPU job. Check for the advertised transition or notification. Sources: [EC2 instance states](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html), [Azure Scheduled Events](https://learn.microsoft.com/en-us/azure/virtual-machines/scheduled-events-overview), [Google Spot VMs](https://docs.cloud.google.com/compute/docs/instances/spot).

[observed] Providers sanitize media in a separate process when they retire or reuse storage hardware. AWS describes end-of-life media decommissioning. Microsoft describes Clear/Purge/Destroy workflows and asset records. Google describes logical deletion and media retirement controls. A tenant does not trigger these processes by deleting a VM or object. Sources: [AWS data layer](https://aws.amazon.com/trust-center/data-center/data-layer), [Microsoft DBD destruction](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction), [Google Cloud deletion](https://docs.cloud.google.com/docs/security/deletion).

[inference] A rack-bench tenant test can measure API behavior and notice delivery. It can measure stop/start behavior, interruption response, and application recovery. It can also check readback after logical deletion. It cannot observe provider media sanitization or prove key destruction. It cannot prove replica or backup expiry, or certify hardware destruction. Do not describe a pass as “data irrecoverably erased.”

## 2. Lifecycle control matrix

### 2.1 AWS

| Control | Published semantics / window | Product-specific limits and rack-bench relevance |
|---|---|---|
| Capacity Blocks for ML | [observed] Reservation targets future GPU capacity (up to eight weeks); instances must target reservation ID. The block ends 11:30 UTC; termination process begins 11:00 UTC on final day. Users cannot cancel a Capacity Block. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html) | [observed] Select instance types/regions only. The current page lists `p6-b300.48xlarge` in selected regions. This does not prove NVL72 or the Chennai rack's availability. P6e-GB200 UltraServer requires instances terminated at least 60 minutes before block end. Users cannot move or split blocks. Each block supports at most 64 instances. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html). [inference] A two-hour test cannot certify reservation procurement. It cannot test end-of-block behavior unless it runs at the boundary. If possible, test API and event schedule metadata without using a full reserved block.
| EC2 stop/start | [observed] EBS-backed only; stopped state ceases instance-use billing, but EBS persists and remains charged. Start generally moves the instance to a new host. The instance loses instance-store data. The public IPv4 address may change; the private IPv4 address remains. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html) | [inference] This is not a GPU checkpoint guarantee. Check that the exact GPU SKU supports stop/start. Observe re-provisioning, GPU visibility, driver health, identity and IP expectations, and scratch loss. Test before useful work. Do not treat stop/start as a harmless pause.
| Hibernate | [observed] Hibernation saves RAM to EBS; instance store is lost. AWS supports hibernation only if the instance is EBS-backed, hibernation-enabled, and meets prerequisites. A failed hibernation falls back to ordinary shutdown. [overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-hibernate-overview.html), [prerequisites](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hibernating-prerequisites.html) | [observed] Hibernation has restrictions, including no Auto Scaling group/ECS use, and AWS warns capacity reservation does not guarantee resume. [overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-hibernate-overview.html). [inference] Do not assume GPU instances can hibernate; first query SKU support and test only on expendable data. This file makes no GB300-class support claim.
| Spot interrupt / rebalance | [observed] Typical interruption notice is up to two minutes. Rebalance recommendation is an earlier risk signal, not a fixed advance window. Capacity Rebalancing can launch replacement capacity before interruption. [AWS rebalance docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-fleet-capacity-rebalance.html) | [inference] A notification may not arrive, or may arrive too late for a safe checkpoint. Check event-channel delivery and the graceful handler during a controlled, non-production interruption. Do not force provider reclamation on certification workloads.
| EC2 Fleet health replacement | [observed] Fleet health checks run every two minutes. An instance becomes unhealthy when its EC2 instance or system status check is impaired for three consecutive checks. EC2 replaces instances only in `maintain` fleets and only for Spot. Users configure replacement at fleet creation. Target capacity can stay below target for a few minutes. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-ec2-fleet.html) | [inference] Three failed checks at two-minute intervals suggest a health qualification time measured in minutes. No source sets a time limit for capacity wait or replacement completion within a two-hour test. Measure timestamps. Do not predict a minimum or maximum replacement delay. Distinguish EC2 infrastructure health from GPU ECC/XID/application health; fleet check does not claim the latter.
| EC2 Auto Recovery | [observed] EC2 automatic instance recovery is a separate feature. It responds to eligible system-status-check failure. AWS documents supported instance and configuration constraints. [AWS docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recovery.html) | [inference] Do not collapse Auto Recovery with Fleet replacement or GPU health. Check eligible SKU and alarm/action configuration. An induced hardware fault is unsafe. It is not equivalent to a documented system-check fault.

### 2.2 Azure

| Control | Published semantics / window | Product-specific limits and rack-bench relevance |
|---|---|---|
| Spot VM eviction | [observed] Spot has no availability SLA; Azure reclaims capacity with 30-second notice. Scheduled Events notification is best effort, up to 30 seconds before eviction. Eviction policy `Deallocate` (default) retains VM/disks in stopped-deallocated state and charges disks; `Delete` removes VM and underlying disks. [Azure Spot docs](https://learn.microsoft.com/en-us/azure/virtual-machines/spot-vms) | [observed] Scale-set Spot page documents `Deallocate`/`Delete`; `Spot-Try-Restore` opportunistically retries, not a capacity guarantee. [VMSS Spot](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/use-spot). [inference] Capture the eviction policy and event inside the VM and in the control plane. Do not force eviction on production assets. Do not assume all GPU SKUs or regions support this feature.
| Scheduled Events | [observed] Event minimum notices include Freeze 15 min and Reboot 15 min. They also include Redeploy 10 min, Preempt 30 sec, and Terminate configurable 5–15 min. [Azure docs](https://learn.microsoft.com/en-us/azure/virtual-machines/scheduled-events-overview) | [inference] Events tell users to prepare. They do not guarantee uninterrupted job completion. Record event ID, type, NotBefore, and the actual transition. Azure Spot page explicitly qualifies eviction event delivery as best effort.
| VMSS lifecycle / recovery | [observed] Scale sets coordinate instances and support Spot restore and eviction policy; exact operations depend on orchestration mode and configuration. [VMSS Spot](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/use-spot) | [inference] Do not make a “health check repairs GPU/application” inference. Test configured probes, repair policy, and GPU health separately. Measure Spot restore opportunism as attempted recovery, not promised time-to-replacement.

### 2.3 Google Cloud

| Control | Published semantics / window | Product-specific limits and rack-bench relevance |
|---|---|---|
| Dynamic Workload Scheduler (DWS) | [observed] DWS offers Calendar mode and Flex-start. Calendar mode schedules capacity blocks. Flex-start queues a request for capacity, duration, and region; Google provisions it when available. Google's launch description says Flex-start requests can last up to seven days. Calendar mode supports 7- or 14-day blocks, purchasable up to eight weeks ahead (source/availability can change). [Google announcement](https://cloud.google.com/blog/products/compute/introducing-dynamic-workload-scheduler) | [observed] Current Batch documentation associates DWS GPU jobs with Flex-start and Calendar-mode reservations; Flex-start has specific provisioning-model and reservation fields. [Batch GPU jobs](https://docs.cloud.google.com/batch/docs/create-run-job-gpus). [inference] DWS is an acquisition/scheduling mechanism, not an interruption notice or VM recovery API. Check current region and SKU eligibility, and mode semantics, before designing acceptance tests. This file does not establish GB300/NVL72 availability.
| Spot VM preemption | [observed] Default preemption notice duration is zero; shutdown handling is best-effort up to 30 seconds. The June 11, 2026 Compute Engine release notes introduced the optional 120-second preemption notice as Preview. This file does not independently resolve current GA status. Preemption uses metadata notice / ACPI shutdown and shutdown script, followed by forced off if needed. [Spot docs](https://docs.cloud.google.com/compute/docs/instances/spot), [create/use](https://docs.cloud.google.com/compute/docs/instances/create-use-spot), [release notes, June 11 2026](https://docs.cloud.google.com/compute/docs/release-notes) | [observed] Spot VMs do not support the A4X machine series or bare-metal instances. The documentation does not exclude all other GPU machine series. Check support for the exact SKU and region. Configuration sets the termination action to stop or delete. Local SSD lifecycle has distinct persistence behavior. [Spot docs](https://docs.cloud.google.com/compute/docs/instances/spot), [MIG Spot](https://docs.cloud.google.com/compute/docs/instance-groups/create-mig-with-spot-vms). [inference] Current GA status remains unresolved. Do not treat the 120-second option as a stable, generally available guarantee. Check live project eligibility. Test default notification handling with disposable workload, not a production GPU job.

### 2.4 Cross-cloud interpretation

[observed] AWS Spot typically documents up to 2 minutes. Azure Spot provides best-effort 30 seconds. GCP Spot defaults to no pre-notice and up to 30 seconds of best-effort shutdown. The June 11, 2026 release notes introduce a 120-second option as Preview. This file does not independently resolve current GA status.

GCP expressly excludes A4X and bare-metal from Spot. This exclusion does not establish ineligibility of every GPU series. These docs do not establish GB300 applicability.

These signals and shutdown rules differ. They do not provide directly comparable, guaranteed checkpoint windows. [AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-fleet-capacity-rebalance.html), [Azure](https://learn.microsoft.com/en-us/azure/virtual-machines/spot-vms), [GCP](https://docs.cloud.google.com/compute/docs/instances/spot).

[inference] Report notice latency distribution and event delivery success as separate metrics. Also report time from notice to actual loss, shutdown-script completion, and replacement readiness. A vendor-claimed maximum does not count as a measured rack pass. A provider can reclaim an instance before the application checkpoint completes. This can happen even when the control-plane feature functions as documented.

## 3. Change, recovery and first useful GPU-hour

### 3.1 Documented pre-flight examples and tenant-observable checklist

[observed] AWS publishes LLM Training Operations guidance with a pre-flight workflow. CloudFormation creates EC2 instances. It checks GPU health, CUDA drivers, NCCL, EFA connectivity, and CPU, memory, and disk performance. It then sends failure details through SNS before training starts. This is a documented example, not a universal AWS-required checklist or evidence of GB300/NVL72 applicability. [AWS Guidance: LLM Training Operations on AWS](https://docs.aws.amazon.com/solutions/llm-training-operations-on-aws).

Google documents a GPU-image preflight. Create a test GPU VM to check image configuration and driver loading. [Google: Install GPU drivers](https://docs.cloud.google.com/compute/docs/gpus/install-drivers-gpu).

These examples support preflight before work. Neither example provides a universal, provider-neutral rack checklist.

[inference] 1. Freeze an exact resource identity manifest. Include cloud, region/zone, SKU, accelerator count and topology, instance/resource IDs, image, driver/runtime versions, reservation/fleet/scale-set/job identifiers, and requested start/end time. Compare returned SKU/topology against contract; do not accept a family name as proof of GB300/NVL72.
2. [inference] Before launch, capture quota and capacity/reservation status. Capture subnet/network, image readiness, boot disk/scratch persistence, termination action, and auto-delete flags. Also capture Spot/eviction price, health checks, and event-channel configuration. Record missing fields as unknowns. Do not assume defaults.
3. [inference] Set clocks to UTC. Capture events in an append-only log. Include API responses, provider events, guest journals, and scheduler logs. Hash the artifacts and record operator/test IDs. API polling alone may miss transient event delivery.
4. [inference] Start one minimal, known-good GPU workload. Timestamp the resource request, allocation, boot, driver-ready state, GPU visibility, kernel launch, and completion of a small workload. Define the first useful GPU-hour. “VM running” does not mean “GPU useful.”
5. [inference] Record a successful job heartbeat/checkpoint and verify a clean stop/restart on disposable resources only. Hash an application-owned sentinel in persistent storage; separately verify expected loss of ephemeral scratch.
6. [inference] After a change, reimage, or replacement, compare hardware identity, firmware/driver stack, and topology with the baseline. Rerun a short GPU correctness probe before resuming work. Cloud lifecycle APIs do not prove GPU fabric health or application health.
7. [inference] For offboarding, stop or terminate resources. Delete tenant-managed volumes, snapshots, images, keys, and logs. Revoke credentials and service identities. Remove reservations and fleet targets. Check resource inventory and billing cessation. Preserve deletion request IDs, completion status and provider policy/version.

### 3.2 Safe two-hour bench proposals

| Test (within ~2h category budget) | Procedure and pass evidence | Limits / safety |
|---|---|---|
| Provision-to-use timing | [inference] One eligible disposable resource or representative provider API flow. Capture request→allocation→guest ready→GPU available→known-good tiny kernel / inference completes. Report p50/p95 only if repeated enough; otherwise individual elapsed times. | This test does not establish capacity across dates/regions or customer-scale scheduling. A failed/unsupported API path is a scope result, not a rack hardware failure. Keep workload tiny; never claim full training throughput.
| Stop/start persistence semantics | [inference] On a disposable instance, write a hashed sentinel to durable disk and scratch. Stop and start the instance. Validate the durable sentinel. Verify scratch outcome, GPU enumeration, address changes, and billing/state events. | Run this test only if the exact SKU supports the operation and the vendor approves. Not a substitute for maintenance or interruption recovery. Avoid hibernate on GPU unless explicitly supported.
| Notice-handler tabletop / harmless event | [inference] Verify the guest event endpoint/subscription. Parse the payload. Invoke the handler in dry-run mode. Measure event-to-handler latency. Validate checkpoint code using an application-generated simulated signal. | A simulated notice does not prove that the provider delivers a real preemption signal. Do not deliberately induce production reclaim. Mark simulation separately from observed provider event.
| Replacement/health-control configuration | [inference] Read back fleet/VMSS/MIG policy via API. Validate thresholds, replacement flags, notifications, health probe, and action with a synthetic guest health endpoint. Observe controller response only if safe fault injection exists. | Do not claim automatic GPU XID recovery from generic VM health. EC2 Fleet checks are two-minute intervals and three consecutive failures; full replacement may exceed test window. [AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-ec2-fleet.html)
| Offboarding inventory/readback | [inference] Delete a disposable VM and its explicitly managed disks/snapshots. Poll APIs for not-found/deleted state. Query resource inventory. Attempt authorized readback from remaining tenant-visible locations. Verify credential revocation. | This test establishes only tenant-visible logical deletion. It does not establish provider media sanitization, backup expiration, replica removal, or cryptographic key destruction.

### 3.3 PASS design

[inference] Scope a lifecycle category PASS to the tested operation and exact SKU/region/API version. Require actual measured timestamps and state transitions, expected persistence/loss, and event-handler behavior. Useful sub-results: `provision-to-GPU`, `notice-delivery`, `reclaim-response`, `replacement-ready`, `stop-start-state`, `tenant-delete-visible`. Do not issue a single PASS for lifecycle end-to-end if one control was not exercised.

## 4. Deletion and sanitization standards

### 4.1 Current NIST status; Clear, Purge, Destroy

[observed] NIST SP 800-88 Rev. 2 is the current final revision. The publication date is September 2025. NIST marks it as superseding Rev. 1 (2014). Do not cite Rev. 1 as current. [NIST Rev. 2 final page](https://csrc.nist.gov/pubs/sp/800/88/r2/final). NIST defines sanitization as making access to target data infeasible for a given level of effort.

[observed] The three familiar outcome categories are **Clear**, **Purge**, and **Destroy**. Clear uses logical techniques against ordinary user-addressable recovery. Purge uses physical or logical means to make recovery infeasible with state-of-the-art laboratory techniques. Destroy meets the same recovery objective. The media also no longer remains usable.

Microsoft's public operational description defines these terms. It says its datacenters use Clear/Purge/Destroy processes, approved tools, records, and chain-of-custody tracking. [Microsoft DBD destruction](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction). That page links to Rev. 1, however. Its controls are provider claims, not evidence that Microsoft revised every process to Rev. 2.

[observed] The NIST Rev. 2 page establishes supersession and current publication. The provider-specific docs reviewed here are version-mixed. The Google deletion page says NIST Rev. 1. Google explicitly marks it as last updated May 2024. Microsoft equipment-disposal and DBD pages link Rev. 1. AWS says NIST 800-88 without naming revision. [Google](https://docs.cloud.google.com/docs/security/deletion), [Microsoft](https://learn.microsoft.com/en-us/azure/security/fundamentals/physical-security), [AWS](https://aws.amazon.com/trust-center/data-center/data-layer). [inference] Treat these as provider statements of practices, not proof of Rev. 2 implementation or a per-tenant certificate.

### 4.2 Verification versus validation; cryptographic erase limits

[observed] NIST SP 800-88 Rev. 2 FAQ Q7 defines **verification** as “the operational step of inspecting the immediate outcome of a sanitization technique to ensure that it has completed successfully without technical errors or anomalies.” The FAQ defines **validation** as “a higher-level decision-making process”. In validation, an organization reviews verification data against data sensitivity. It formally approves execution as effective and accepts residual confidentiality risk. [NIST Rev. 2 FAQ, published July 16 2026, p. 3, Q7](https://csrc.nist.gov/files/pubs/sp/800-88/r2/final/docs/sp800-88r2-faq.pdf). The FAQ Q4 also says a formal policy defines validation and verification protocols. It also defines evidence requirements (certificate of sanitization), pp. 1–2. A successful tool status alone does not count as a validation decision.

[observed] Cryptographic erase (CE) removes or changes encryption keys. This makes ciphertext no longer decryptable. Google describes CE for Cloud Storage. Google says logical deletion can occur before block overwrite and backup expiration. [Google deletion](https://docs.cloud.google.com/docs/security/deletion).

[inference] CE assurance depends on the entire key hierarchy and data path. The provider must destroy or make unavailable all keys that protect relevant copies. No plaintext copies, exports, cached derivatives, snapshots, or separately wrapped keys may remain accessible. Algorithm/key strength and key destruction evidence matter. CE does not prove media-block overwrite or physical destruction.

[observed] Google says deletion requests may have an internal recovery period of up to 30 days. Its published overall deletion commitment is about 180 days. Active-system deletion generally takes about two months. Backups expire within six months. The page cautions it reflects May 2024 status. [Google](https://docs.cloud.google.com/docs/security/deletion).

[inference] Provider retention windows limit what tenant deletion proves. Deletion and readback soon after deletion cannot prove that backups or replicas are absent.

### 4.3 Provider-published deletion standards and evidence

- **AWS:** [observed] AWS says it decommissions end-of-life media with techniques detailed in NIST 800-88. AWS says media stays under AWS control until securely decommissioned. [AWS data layer](https://aws.amazon.com/trust-center/data-center/data-layer). This is a hardware end-of-life policy. It does not guarantee physical sanitization of a tenant's terminated instance or EBS volume at API completion.
- **Azure/Microsoft:** [observed] Azure says it uses a NIST 800-88-compliant wiping solution and secure erase where supported. Azure uses physical destruction (e.g., disintegrate/shred/pulverize/incinerate) if wiping fails. Azure keeps records. [Azure physical security](https://learn.microsoft.com/en-us/azure/security/fundamentals/physical-security). Microsoft DBD page describes asset assessment, Clear/Purge/Destroy, chain of custody, and retained records. [DBD destruction](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction).
- **Google Cloud:** [observed] Google documents a staged deletion pipeline. The stages include request, soft-delete/recovery, logical deletion on active systems, and backup expiration. Google also documents encryption at rest, CE for Cloud Storage, overwriting/garbage collection, and drive overwrite/verification. If erase fails, Google uses secure storage pending physical destruction. [Google deletion](https://docs.cloud.google.com/docs/security/deletion). This source dates to May 2024 and cites Rev. 1. Its current status is uncertain.

[observed] No reviewed provider source promises a sanitization certificate for each tenant or VM after ordinary VM deletion. Microsoft says it keeps records of erasure/destruction. AWS describes provider procedure. Google describes process. [inference] Ask for the contract scope, retention period, audit or attestation access, failed-erase process, and certificate fields. Do not treat a general compliance badge as an individual deletion receipt.

A useful certificate should identify the asset/media or scoped logical dataset. It should identify method/category, tool/process, result, timestamps, exception path, and chain of custody. It should name an accountable approver. It must not expose other customers' data.

### 4.4 What tenant deletion and readback cannot prove

[observed] Google documents replication, active systems and backup systems, soft-deletion windows, and delayed physical media sanitization. [Google](https://docs.cloud.google.com/docs/security/deletion). [inference] Therefore, after tenant delete and failed readback, one cannot prove several outcomes. These include already-expired backups/replicas, overwritten physical blocks, and irrecoverably destroyed cryptographic keys. They also include absent provider-only copies, no stray control-plane metadata, correct NIST-category device sanitization, and completed chain-of-custody/destruction.

[observed] VM termination/deletion API state describes compute resource lifecycle; AWS explicitly notes users can configure attached EBS `DeleteOnTermination` to preserve volumes. Root volumes default to deletion. Non-root volumes default to preservation. [AWS instance states](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html). [inference] “instance terminated” does not mean users deleted all attached storage. It also does not cover snapshots, images, logs, keys, marketplace artifacts, or external copies. Inventory and delete each resource class explicitly.

## 5. Recommended rack-bench scope and reporting

### 5.1 What N02 can credibly certify

[inference] Certify measured API lifecycle behavior for the exact tested configuration. Measure resource request to useful GPU execution, planned stop/start/restart, event notification wiring, and controlled handler response. Check tenant-visible deletion of enumerated resources and observed readback denial. Attach timestamps, API versions, event payloads, the resource manifest, and test limits.

[inference] For operational changes, run a short, known-good GPU sentinel after each supported change. Examples include image/driver or host replacement. Compare identity, driver, GPU enumeration, and a deterministic kernel result. Report the measured recovery interval; do not imply resilience to arbitrary host faults, fabric faults or provider-wide outages.

### 5.2 Explicit exclusions / no false assurance

[inference] A two-hour pass does not prove long-term spot availability or notice guaranteed under all reclamation conditions. It does not prove successful checkpoint of a real model or fleet recovery under capacity scarcity. It does not prove billing correctness over a full cycle or end-of-reservation behavior unless timed at boundary. It also does not prove provider media sanitization, backup purge, or NIST category compliance. It does not prove CE key destruction or a destruction certificate. These items require longer observation, provider evidence, contract terms, or an independent audit.

[inference] Do not stage real Spot reclamation or deliberate destructive faults on the NVL72 certification rack. Use sandbox resources, provider-supported simulation, or synthetic event injection. Label the evidence accordingly. Do not infer that VM Spot, stop/start, hibernate, or Fleet replacement features apply to GB300/NVL72. The same limit covers VMSS restore, DWS, and GPU checkpoint features. Confirm support with exact provider SKU documents and a live API response.

### 5.3 Suggested result fields

[inference] `provider`, `region/zone`, `resource_sku`, `accelerator_topology_claimed`, `api_version`, `resource_ids`, `operation`, `configured_policy`, `request_utc`, `event_utc`, `state_transition_utc`, `gpu_ready_utc`, `useful_work_utc`, `handler_exit`, `checkpoint_hash`, `persistent_sentinel`, `scratch_expected/observed`, `delete_inventory`, `readback_scope`, `provider_deletion_policy_reference`, `evidence_kind` (live/simulated/provider-doc), `pass_scope`, `limitations`.

## 6. Sources and confidence

### 6.1 Primary sources retained

- [NIST SP 800-88 Rev. 2 final](https://csrc.nist.gov/pubs/sp/800/88/r2/final) — authoritative current revision and supersession status.
- [AWS Capacity Blocks for ML](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html), [EC2 instance states](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html), [EC2 Fleet](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-ec2-fleet.html), [Spot rebalance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-fleet-capacity-rebalance.html), [hibernation overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-hibernate-overview.html) — API/service behavior and constraints.
- [Azure Spot](https://learn.microsoft.com/en-us/azure/virtual-machines/spot-vms), [VMSS Spot](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/use-spot), [Scheduled Events](https://learn.microsoft.com/en-us/azure/virtual-machines/scheduled-events-overview) — eviction, notifications and scale-set policies.
- [Google DWS launch description](https://cloud.google.com/blog/products/compute/introducing-dynamic-workload-scheduler), [Batch GPU/DWS documentation](https://docs.cloud.google.com/batch/docs/create-run-job-gpus), [Spot VMs](https://docs.cloud.google.com/compute/docs/instances/spot) — scheduling and reclaim semantics.
- [AWS media lifecycle](https://aws.amazon.com/trust-center/data-center/data-layer), [Microsoft DBD destruction](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction), [Azure physical security](https://learn.microsoft.com/en-us/azure/security/fundamentals/physical-security), [Google deletion](https://docs.cloud.google.com/docs/security/deletion) — provider-published sanitization/deletion descriptions.

### 6.2 Confidence and gaps

**Sourcing confidence: high** for NIST current revision and basic AWS/Azure/GCP operational semantics because claims use primary NIST/provider docs. **Moderate** for exact current availability across GPU SKU/regions. Dynamic pages and announcements have changing support matrices. Validate live API and commercial offer. **Low** for any inference about physical sanitization at tenant-resource deletion. The cited public docs describe provider process, not per-tenant proof.

## Gaps

- This brief does not verify all current live region/SKU matrices for AWS GB300/P6-B300. It does not verify Azure GB300/NVL72-class offerings or Google GPU products. This file does not claim that an NVL72-compatible lifecycle feature exists.
- This file links AWS Auto Recovery behavior to its primary documentation. This brief does not audit exact eligible GPU SKU/region combinations here. [AWS recovery docs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recovery.html)
- Google DWS duration and availability details draw partly on its launch announcement. Use current product documents and API availability for live acceptance. Product status and Preview or GA labels can change.
- This file links the NIST Rev. 2 FAQ but does not quote it clause-by-clause. Provider docs still refer to Rev. 1 or omit revision. No public evidence shows that providers updated internal procedures to Rev. 2.
- Public sources do not establish per-tenant sanitization certificates. They do not establish exact backup deletion for every product. They do not establish customer access to device-level destruction records. Obtain contract and assurance-package evidence directly.
- This file quotes NIST verification/validation wording from FAQ Q7. Operational application still depends on the organization’s sanitization policy and selected method.
- A two-hour bench cannot observe long recovery periods or multi-day spot behavior. It cannot observe backup expiry, which takes up to six months in Google's cited page. It also cannot observe physical media end-of-life processing.
