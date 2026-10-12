# Neocloud lifecycle controls and gaps — operational research for rack-bench

Research date: 2026-10-11. All claims below carry a source URL.

This file marks claims as **[observed]**, **[calculated]**, or **[inference]**. Observed means a published source or local artifact says/shows this. Calculated means arithmetic from stated values. Inference means interpretation or a test proposal.

Provider documentation is mutable. This brief uses page checks from the research date. It retains page-level date/version where available. This is published-policy research, not provider performance observation. Rack-bench measures actual behavior; a claim in docs is not a PASS.

## 1. Scope and relationship to existing research

This brief isolates lifecycle controls for neoclouds: contract-to-first-useful-GPU-hour, resource changes, interruption, data reclamation, and offboarding. It does not repeat internet egress-fee research. For that, see [prior internet-economics brief, §3: Egress economics](/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/neoclouds.md#3-egress-economics--who-charges-who-markets-zero-what-the-marketing-guarantees), especially lines 142–162 of that local file. [observed].

The published ClusterMAX Lifecycle criteria are broad. They cover transparent onboarding costs, met delivery timelines, and no punitive egress/offboarding fees. They cover usable, documented UI/API/Terraform/CLI, delivery-date accuracy, head-node provisioning, and standard ML expectations. They also require audit logs. The logs capture actor/action/resource/time/outcome fields, API filtering, 90-day retention, and export ([Lifecycle criteria](https://clustermax.ai/criteria/lifecycle)).

**[observed]** The criteria are requirements. They do not show evidence of each provider's compliance. They also do not show experimental lifecycle timings. This brief establishes no market-wide public distribution of provisioning time or wipe attestations here.

## 2. Provider comparison matrix

| Provider | Published provisioning / control-plane ergonomics | Interruptible policy | Images / environment | Resize, migrate, reclamation and offboarding |
|---|---|---|---|---|
| CoreWeave | **[observed]** Docs expose CKS, APIs, Terraform and self-serve platform products; no universal instance-ready distribution in the cited material ([docs entry](https://docs.coreweave.com/get-started)). | **[observed]** CKS Spot Node Pools use reclaimable capacity. They explicitly exclude Superchip instances, including GH200, GB200 and GB300. This policy therefore does not establish GB300 spot availability. The up-to-seven-minute window is a maximum measured from warning, not a guaranteed checkpoint budget. Drain starts after two minutes. Pod termination grace is commonly 30 seconds ([Spot Node Pools](https://docs.coreweave.com/platform/capacity-plans/spot-node-pools)). | Cluster/container deployment rather than assumption of arbitrary VM image; see product-specific docs. | **[observed]** Providers can drain/remove spot nodes after notice. Docs do not establish tenant NVMe sanitization evidence or a market-comparable export SLA. |
| Nebius | **[observed]** VM lifecycle available through Console, CLI, Terraform and SDKs; supported GPU platforms discoverable by CLI ([VM manage](https://docs.nebius.com/compute/virtual-machines/manage)). The cited docs show no promised provisioning percentile. | **[observed]** SIGTERM 60 seconds before stop; SIGKILL thereafter; attached volume data preserved, dynamic public IP not; local SSD ephemeral. Spot has no guaranteed availability ([policy](https://docs.nebius.com/compute/virtual-machines/preemptible)). | **[observed]** The changelog documents custom boot images via Packer ([Nebius changelog](https://docs.nebius.com/changelog)); image compatibility constrained by platform. | **[observed]** Users cannot convert an existing VM regular↔preemptible. Policy supports stop on preemption, not restart recovery. Public documentation cited does not specify secure erase certificate or export completion SLA. |
| Lambda | **[observed]** REST API launch/list/restart/terminate, alternate base images and cloud-init; launch may take several minutes, new-account quotas apply ([instance management](https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances)). | No spot/preemptible policy identified for On-Demand Cloud in checked docs; not evidence none exists across all Lambda products. | Alternative base images and cloud-init supported; docs recommend Docker for preserving environment, not suspending an instance. | **[observed]** ODC supports launch/restart/terminate but not suspend; local state needs backup. Users cannot extend/renew a 1-Click Cluster reservation. The provider deletes ephemeral local data at reservation end ([1CC intro](https://docs.lambda.ai/public-cloud/1-click-clusters)). Termination terms reserve broad data deletion rights but allow retention under policy ([Terms](https://lambda.ai/legal/terms-of-service)). |
| Runpod | **[observed]** Users can deploy/manage Pods via Web, CLI, REST; lifecycle logs include startup/shutdown/errors ([manage Pods](https://docs.runpod.io/pods/manage-pods)). The cited docs show no published ready-time distribution. | **[observed]** Distinguish On-Demand from interruptible/Spot offerings. The Pod page explicitly warns restart may yield zero GPUs if capacity has changed ([manage Pods](https://docs.runpod.io/pods/manage-pods); [zero GPU troubleshooting](https://docs.runpod.io/pods/troubleshooting/zero-gpus)). This file establishes no universal reclaim-notice duration here. | Templates and container configurations are first-class; Pod update allows image, storage, ports, environment changes ([manage Pods](https://docs.runpod.io/pods/manage-pods)). | **[observed]** Stop preserves `/workspace` volume disk but clears container disk. Termination deletes data not on network volume. Network volumes survive Pod termination and can attach to another Pod. They are location-bound and do not automatically sync ([manage Pods](https://docs.runpod.io/pods/manage-pods); [network volumes](https://docs.runpod.io/storage/network-volumes)). |
| Crusoe | **[observed]** Crusoe promotes Console, CLI, APIs, Terraform and SDKs; VM states include Creating (up to one minute), Starting, Running. Restricted GPU types/regions may require sales access ([VM overview](https://docs.crusoecloud.com/compute/virtual-machines/overview); [product](https://www.crusoe.ai/cloud)). | Published Cloud marketing advertises spot. The primary docs cited here do not establish a generally applicable notice guarantee. Do not infer one. | **[observed]** Curated/custom images supported. Custom images are customer-managed, project/region-specific; Crusoe does not maintain them or guarantee/troubleshoot their performance ([images](https://docs.crusoecloud.com/compute/images/overview)). | **[observed]** GPU local storage is ephemeral. Stop does not incur on-demand compute, but OS disk persists billed until deletion. Lifecycle scripts execute during startup/shutdown ([VM overview](https://docs.crusoecloud.com/compute/virtual-machines/overview)). The cited docs show no wipe attestation/export deadline. |

## 3. Mechanisms and operational examples

### 3.1 Provisioning is an event chain, not just API acceptance

**[observed]** Lambda explicitly says instances may take several minutes to launch and quotas can block launches. Crusoe documents a Creating state up to one minute, then Starting before Running. Some GPU types are region-restricted and require sales discussion ([Lambda](https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances); [Crusoe](https://docs.crusoecloud.com/compute/virtual-machines/overview)). Neither statement is an observed fleet distribution. Nebius offers multiple automation surfaces, but quota/capacity and image readiness remain separate operational risks.

**[inference]** A bench timestamp should start at accepted contract/order or accepted API request (report both). It should then record credentials/identity, capacity allocation, VM/cluster ready, and drivers healthy. It should also record image/customization completion and the first successful useful GPU-hour. Do not label “API returned resource ID” as delivered compute.

**Example:** Submit one same-spec request through documented API and one through console. Poll provider state, SSH/API reachability, `nvidia-smi`, CUDA workload, and measured useful GPU execution. Record median and tail for repeated independent requests where capacity permits. Preserve rejected/quota/timeout outcomes. **[inference]** A single successful request cannot establish lead-time reliability.

### 3.2 Reclaim semantics affect checkpoint budget

**[observed]** CoreWeave CKS Spot Node Pools explicitly exclude Superchip instances, including GH200/GB200/GB300; do not apply their reclaim policy to GB300. For eligible instances, the seven-minute maximum starts at warning. Drain begins after two minutes, and pod grace is commonly 30 seconds. Thus seven minutes is not a guaranteed checkpoint budget.

Nebius sends SIGTERM 60 seconds before stop, then SIGKILL if the guest does not exit. It preserves attached volume data but not dynamic public IP/local SSD data ([CoreWeave](https://docs.coreweave.com/platform/capacity-plans/spot-node-pools); [Nebius](https://docs.nebius.com/compute/virtual-machines/preemptible)). Runpod documents restart capacity may change and return zero GPUs ([Runpod](https://docs.runpod.io/pods/troubleshooting/zero-gpus)). These are materially different interruption contracts; do not treat “spot” as a uniform policy.

**Safe check:** Where test capacity and provider-approved test mode exist, run a disposable checkpointing job. Exercise the documented stop/reclaim path, or ask the provider to schedule a controlled reclaim. Log signal-to-process-exit and final checkpoint integrity. Then verify attached volume and local scratch behavior separately. Never induce a real reclaim on production data. **[inference]** Two hours can validate the configured signal handler and recovery path, not estimate spontaneous interruption frequency.

### 3.3 Images, BYO containers and change operations

**[observed]** Nebius exposes custom boot images. Lambda exposes alternative base images and launch-time cloud-init. Runpod supports templates and Pod image changes. Crusoe supports custom images but makes maintenance the tenant’s responsibility ([Nebius changelog](https://docs.nebius.com/changelog); [Lambda](https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances); [Runpod](https://docs.runpod.io/pods/manage-pods); [Crusoe](https://docs.crusoecloud.com/compute/images/overview)).

These options differ. A container template is not equivalent to control of a boot image. Custom images also introduce drift and driver/kernel compatibility risk.

**Safe check:** Launch with a pinned, digest-identified container and a known configuration marker. Reboot/recreate using the same template/image. Compare digest, driver/CUDA versions, mounts, and environment. For VM images, test a versioned custom image across two instances only where the provider supports it.

Record documented configuration pathway versus observed result. Do not claim migration or live resize from image/template support alone. **[inference]** Two-hour bench can expose reproducibility drift on sampled nodes, not fleet-wide drift rates.

### 3.4 Stop, terminate, and offboarding are separate operations

**[observed]** Runpod explicitly differentiates Stop from Terminate. Stop preserves `/workspace` volume disk but clears container disk. Termination removes all data not in a network volume. A network volume persists separately, and the tenant can reattach it. Cross-volume data does not sync automatically ([manage Pods](https://docs.runpod.io/pods/manage-pods); [network volumes](https://docs.runpod.io/storage/network-volumes)).

Lambda requires explicit API/console termination. Its legal terms allow deletion on termination but also permit retention under privacy/data-retention practices ([Lambda docs](https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances); [terms](https://lambda.ai/legal/terms-of-service)).

Crusoe treats GPU local storage as ephemeral. Stopped OS disks remain and incur storage charges until VM deletion ([Crusoe](https://docs.crusoecloud.com/compute/virtual-machines/overview)).

**[observed]** NIST SP 800-88 Rev. 2 defines sanitization as rendering access to target data infeasible for a given effort. The standard is not proof that any particular neocloud performs or attests to a wipe ([NIST SP 800-88 Rev. 2 final](https://csrc.nist.gov/pubs/sp/800/88/r2/final)). In the cited primary sources, this brief finds no market-wide NIST-aligned wipe certificate. It finds no per-volume sanitization record or standardized offboarding export SLA. This is a limited-search finding, not a claim that providers never provide contractual evidence.

**Safe check:** On disposable scratch, write unique random canary data. Terminate through the official control plane. Check that tenants cannot access the resource. Check final billing/resource state.

Check credential/API-token revocation where applicable. Verify persistent-volume behavior matches docs. Verify export succeeds to a customer-controlled destination.

Request deletion evidence through the support/contract channel. Report exactly what the test receives. Do not attempt cross-tenant forensic recovery or physical-media inspection. **[inference]** Guest-visible deletion cannot verify provider-side media sanitization. The test can verify control-plane lifecycle and tenant access only.

## 4. What a two-hour lifecycle bench can safely catch

1. **Request-to-useful-GPU timing:** timestamp accepted request, allocation, guest/cluster ready, driver health, workload start, and first completed GPU work. Record failure/quota/retry and exact SKU/region/image. [inference]
2. **API/CLI ergonomics:** create/list/describe/stop/start/delete using documented interfaces; verify idempotency, state transitions, actionable errors, audit/event visibility and cleanup. Compare API acceptance with usable GPU, not just call latency. [inference]
3. **Image/environment repeatability:** rebuild from pinned image/template. Compare image digest, driver/runtime, kernel, environment, and GPU visibility. Identify drift in tested instances. [inference]
4. **Change-path check:** exercise documented mutable changes (e.g., Runpod Pod update). Measure whether they require restart/redeploy. Test one stop/start and confirm expected persistence. Do not assume resize or migration exists absent provider-specific published operation. [inference]
5. **Interruption readiness:** validate checkpoint signal handling with controlled stop or provider-approved reclaim. Compare measured time to checkpoint against Nebius’s published 60-second notice.

   CoreWeave’s seven-minute maximum is only for eligible non-Superchip instances. It starts at warning. Drain begins after two minutes. The commonly 30-second pod grace further limits practical checkpoint time. The policy excludes GH200/GB200/GB300, so it does not apply to GB300. This verifies response capability, not reclaim probability. [observed policy + inference test]
6. **Offboarding evidence:** export a small canary dataset and terminate the test resource. Check that tenants cannot access the resource after deletion. Check bill cessation where applicable. Capture provider evidence and its scope. This does not certify NIST sanitization. [inference]
7. **Fleet drift sample:** repeat checks across a small rack sample or separate instances and compare firmware/driver/image/state, recording sample size. Two hours does not support fleet-wide reliability claims. [inference]

## 5. Honest misses and limits

- This brief finds no public, comparable provisioning-time distributions (p50/p95, queue time, contract signature to capacity) for the providers above. Lambda says “several minutes”. Crusoe documents a Creating transition up to one minute, not end-to-end delivery. Both are product-specific wording, not a market distribution. [observed]
- No universal spot/preemptible model exists. CoreWeave publishes notice mechanics only for eligible non-Superchip Spot Node Pool instances (explicitly excluding GH200/GB200/GB300). Nebius publishes concrete notice mechanics. Runpod’s restart/capacity warning is not a termination-notice promise. The cited Crusoe sources do not settle notice semantics. Do not infer omitted details. [observed]
- “Custom image,” “container template,” “BYO container,” “resize,” and “migration” are not interchangeable. The provider-specific docs cited support selected image/template operations. This research does not establish live GPU resize or transparent cross-host migration for every provider.
- Rack-bench cannot generalize a NIST 800-88 wipe-attestation conclusion from this limited source review. NIST gives a sanitization framework; operators must obtain provider evidence and contractual scope individually. Do not infer absence across market.
- This brief verifies no comparable export/offboarding completion SLA across all named providers. It also verifies no support response SLA, fleet drift rate, or support escalation performance. Crusoe’s homepage advertises 24/7 team, sub-six-minute average first response, and 100% CSAT over 12 months ([Crusoe Cloud](https://www.crusoe.ai/cloud)). This is provider marketing, not an independently observed SLA. Label similar vendor statements as claims, not guarantees.
- Two hours is enough to detect broken launch/change/delete paths and test a controlled recovery. It is not enough to measure long-tail capacity delivery, spontaneous reclaim frequency, or data-remanence on physical media. It is also not enough to measure multi-month configuration drift.
- Provider product/version scope matters. Lambda ODC differs from 1-Click Cluster. Runpod Pod types and storage differ. CoreWeave’s cited spot policy is specifically CKS Node Pools and explicitly excludes Superchip instances, including GH200/GB200/GB300. Confirm product, region, SKU, contract, and current docs at test time.

## 6. Rack-bench interpretation

**[inference]** Treat lifecycle certification as a chain of measured transitions. Stages: contract/accepted request → allocated rack → healthy GPU → first completed useful GPU work → controlled change/recovery → customer export → termination and evidence. Report policy separately from observation. Retain timestamps and exact product/version. Mark every untested transition explicitly. “No published evidence found” is the correct finding for unresolved provisioning distributions, wipe attestations, and export SLAs. It is not proof the control does not exist.

## Gaps

- CoreWeave source review here is strongest for CKS spot reclaim. It does not establish VM-style image, resize, or deletion semantics across all CoreWeave products.
- Check Nebius VM management/image and support/SLA material against the exact GPU SKU and current contract. The cited spot page is detailed but does not give preemption frequency.
- Lambda ODC launch docs give a qualitative “several minutes”. The reviewed sources give no account/region/SKU sample data or a current contractual support SLA. Lambda’s 1CC terms are a distinct product.
- Runpod notice period and exact spot termination policies need product-specific primary documentation or controlled provider test. Restart-to-zero-GPU is a capacity warning, not proof of a preemption signal contract.
- Crusoe spot notice, migration/resize, data deletion evidence, and contractual support SLA remain unresolved in the sources reviewed. This brief does not treat the homepage response-time statement as an SLA.
- No public source set establishes a provider-wide distribution of time from contract signature to first useful GPU-hour. This brief performs no cross-market wipe-evidence survey. Obtain contract/order-form evidence and provider-side sanitization records directly; do not generalize from this brief.
