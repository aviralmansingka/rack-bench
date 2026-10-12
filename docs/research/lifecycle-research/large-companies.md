# Large companies — fleet change and reclaim lifecycle research (N04)

Research date: 2026-10-11. Each claim below has a source URL.

This file marks claims as **[observed]**, **[calculated]**, or **[inference]**. Observed means the cited primary source or local code directly states it. Calculated means arithmetic from source evidence. Inference means interpretation or a proposed rack-bench application.

This brief answers only N04: how large fleets control change and reclaim. It does not repeat internet or storage-performance research. It excludes scheduler lineage and failure-study statistics.

## 1. Executive answer: controlled transitions, not one-shot fleet mutation

Large fleets control lifecycle changes through reconciliation and guardrails. The recurring mechanisms in Meta/Facebook, Google Borg, and Azure Fleet Manager are listed below. They include an authoritative desired configuration and an observed machine/task/resource state. They include bounded rollout or disruption, readiness/health gates, and a halt or rollback path. They end with explicit cleanup when work or hardware leaves service.

[observed] Meta’s Twine describes machine unavailability events, health state, TaskControl coordination, task movement, and gradual release. Facebook’s configuration stack adds reviewed, validated, staged canaries with health predicates and automatic rollback. Borg documents declarative desired-state updates, rolling updates, disruption limits, graceful termination, and rate limits. Azure Fleet Manager offers ordered, staged cluster updates with wait/approval gates and previous-snapshot rollback. [1](https://www.usenix.org/system/files/osdi20-tang.pdf) [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)

[Inference] A tenant cannot certify those control planes merely by reading their desired-state files or accepting a provider assurance. A two-hour tenant session can validate observable results on the assigned GB300-class rack. It can check identity and inventory consistency. It can check readiness truth. It can check safe interruption behavior where the tenant has an authorized control. It can check whether a tested change actually converges or rolls back.

The session cannot prove region-wide canary policy, fleet-wide drift coverage, or provider-wide reclaim rates. It cannot prove durable media sanitization or complete offboarding. These need operator-supplied auditable control-plane records and full asset/media disposition evidence.

## 2. Meta/Facebook: unify management; coordinate the app before disruptive lifecycle operations

### 2.1 Twine: shared pool and machine/task lifecycle

[observed] Twine is Facebook’s production cluster-management system. Its paper describes a regional control plane managing one million machines and moving jobs across data centers. It manages machines, containers, and applications in shared infrastructure.

Resource Broker stores machine information and unavailability events. Operators schedule planned maintenance through Ops Planner. Health Check Service updates machine status. Twine’s scheduler manages job/task lifecycle. TaskControl can negotiate task operations with the application. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)

[observed] For a machine failure, HCS creates an unavailability event. The scheduler disables affected tasks in service discovery so clients stop routing to them. If a job has a TaskController, the scheduler notifies it, and it can acknowledge or delay moves. The allocator deallocates and places replacement tasks. Agents start them. The scheduler re-enables them in service discovery.

This sequence drains and evicts tasks. Traffic removal precedes task replacement. The workload may participate in deciding when a stateful task can move. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)

[observed] TaskControl is not just “restart one at a time.” The application can approve a subset of pending task operations in an order that preserves its internal invariants. Examples: upgrade ZooKeeper followers before leader; avoid restarting tasks that jointly hold redundant shards. For planned maintenance, advance notice includes a deadline. The app may move tasks, stop/restart them later, or do nothing. Maintenance proceeds when the deadline expires. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)

[observed] Twine paces releases using an unavailable-task threshold. If too many tasks are already down, further software-release restarts stop. The paper’s example covers concurrent power capping and release. There, rate-limited task moves halt an upgrade instead of letting capacity loss accelerate. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)

[observed] Twine reuses machines across entitlements. It switches host profiles when a machine takes a new assignment. Profiles can include kernel, sysctls, cgroup, storage, NIC, turbo, and prefetch settings. Hardware refresh uses new machines from a regional free pool and rolls tasks onto them. The paper says task migration is stop/restart, not live container migration. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)

[Inference] “Drain” therefore has multiple meanings. First, stop sending new work/traffic. Next, wait for the application to reach a safe state. Then stop/restart or relocate tasks. Only then release hardware.

A rack-bench test must state which layer it checks. A successful tenant-side `SIGTERM`/job stop is not evidence that operator maintenance drain or cross-entitlement reclaim works.

### 2.2 Facebook configuration drift and safe runtime configuration

[observed] Facebook’s 2015 configuration-management paper distinguishes runtime config from OS settings and software deployment. The paper says Chef handles the latter at that time. Configerator treats config as code. It compiles generated configs, versions source and output, and runs validators.

Changes get code review, sandbox CI when a change touches frontend products, manual testing, and staged production canaries. A canary spec identifies target groups, health metrics, and pass/fail predicates. Canary failure causes automatic rollback. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf)

[observed] Canary phases can start with 20 production servers and then expand to a full cluster of thousands. Health predicates compare new-config behavior to the old-config baseline. Facebook explicitly reports a limitation: a small canary can miss cluster-scale load faults. The paper describes adding a larger cluster phase for this reason. This is a valuable limitation: a passing small sample cannot establish safety at fleet load. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf)

[observed] Configerator’s committed repository is the configuration ground truth. Distribution is asynchronous. Servers can receive updates at different times, with eventual ordered delivery rather than simultaneous activation. A proxy cache allows applications to continue with cached configuration if the config-management components fail. Therefore “desired config committed” and “every host is actually ready on it” are distinct states. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf)

[observed] Gatekeeper provides reversible progressive exposure for features. Code can ship disabled. A live config can then enable it for internal users and increasing cohorts. A live config can also quickly disable it. This is a runtime traffic/feature control, not a physical rack acceptance control. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf)

[Inference] This is direct evidence for drift-control principles. The principles cover reviewable source, generated effective config, validation, staged exposure, health comparison, and rollback.

But the paper does not describe a generic host-by-host “drift detector”. The paper does not show continuous proof that every machine matches a desired state. Do not describe it that way. A tenant can compare its own requested image/driver/config with observed node versions and behavior. Operator-wide configuration authority, drift inventory, and all-host compliance remain operator-only.

## 3. Google Borg: declarative jobs, bounded rolling updates, controlled eviction

### 3.1 Job lifecycle, drain and rollout safeguards

[observed] Borg jobs comprise tasks and have explicit lifecycle states. Users can update a running job by submitting a new configuration and instructing Borg to update tasks. This transaction is lightweight and non-atomic. Users can undo it until committed.

Updates are generally rolling. A disruption limit can skip changes that would exceed the allowed number of disrupted tasks. Tasks can receive SIGTERM before SIGKILL to save state, finish requests, and decline new work. [3](https://research.google.com/pubs/archive/43438.pdf)

[observed] Borg limits the rate and simultaneous count of task disruptions during maintenance such as OS or machine upgrades. It also rate-limits rescheduling after machines become unreachable. The control plane cannot immediately distinguish a broad failure from a network partition. This protects against a mistaken mass-replacement surge. [3](https://research.google.com/pubs/archive/43438.pdf)

[observed] Borg’s Borglet starts/stops/restarts tasks and reports machine state. If a machine fails, Borg reschedules its tasks. If communication returns, the Borgmaster tells the old Borglet to kill tasks already rescheduled elsewhere. This prevents duplicate execution. Existing tasks continue running through Borgmaster failure, although new jobs, updates, and rescheduling wait. [3](https://research.google.com/pubs/archive/43438.pdf)

[observed] The paper explicitly describes declarative desired-state representations and idempotent mutations so failed clients can safely retry forgotten requests. Borg also avoids repeating task/machine pairings associated with crashes. These mechanisms are evidence for reliable reconciliation and retry. They are not proof that an external customer can inspect or control them. [3](https://research.google.com/pubs/archive/43438.pdf)

### 3.2 “Borg at 10”: what the decade-of-operation source does—and does not—add

[observed] The 2015 Borg paper is explicitly a report of a decade of production operation. Its lifecycle-relevant contribution is the qualitative control set already summarized above. The set includes bounded maintenance disruption and declarative/idempotent changes. It includes retry pacing when failure and partition are ambiguous. It also includes tasks continuing through control-plane loss. Those are operational safeguards for change/reconciliation, not a measured tenant API contract. [3](https://research.google/pubs/archive/43438.pdf)

[observed] The later Google paper *Borg: the Next Generation* (EuroSys 2020) describes how Borg evolved. Its public abstract centers on workload-trace analysis and scheduling/resource-use observations. I do not use its trace/statistical findings here because they are outside N04 and assigned to the statistics-focused child. It supplies no newer public description of drain, rollout rollback, or data wipe practice. [8](https://research.google/pubs/borg-the-next-generation)

[Inference] Do not read “Borg at 10” as a current 2026 Google operations manual. The ten-year operational account is valuable evidence of design mechanisms. Present fleet practice and tenant-observable behavior remain unverified.
### 3.2 Resource reclaim is distinct from hardware offboarding

[observed] Borg’s resource reclamation estimates reservations from observed task use and makes excess resources available to lower-priority/batch tasks. Production feasibility uses limits, so production tasks do not depend on reclaimed resources. Non-production tasks can schedule into reclaimed capacity. Borg may sacrifice them if reservations are wrong. This process reclaims compute resources. It does not wipe disks or dispose of machines. [3](https://research.google.com/pubs/archive/43438.pdf)

[Inference] The meaningful tenant test is not “prove Borg’s fleet reclamation algorithm.” Instead, where the rack-bench tenant contract authorizes it, test that the tenant can stop or reduce its job. Check that the job's own declared allocation disappears. Verify that remaining GPUs are usable and health passes. Verify that no tenant process remains.

The tenant lacks access to operator allocation/accounting. So the test cannot show actual reassignment or return of freed capacity to the shared pool.

## 4. Microsoft Azure: documented fleet rollouts and deployment health policy

### 4.1 Azure Kubernetes Fleet Manager

[observed] Azure Kubernetes Fleet Manager is a currently documented multi-cluster management service. It offers automated safe updates, update runs, and reusable strategies. It also offers ordering/timing control and optional manual or automated approvals. [5](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/overview)

[observed] Resource placement supports rolling updates with configurable `maxUnavailable`, `maxSurge`, and a readiness delay (`unavailablePeriodSeconds`). The page documents 25% unavailable and 25% surge defaults. But it conflicts with itself on `unavailablePeriodSeconds`. “Default behavior” says 10 seconds. “Configuration parameters” says 60 seconds.

Do not treat either value as a universal default. Read the live strategy and effective resource readiness policy during a tenant bench. An explicit staged strategy can separate staging, canary, and production, with wait periods, approval gates, ordering, and concurrency limits. Users can select a prior resource snapshot to roll back. [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)

[observed] Fleet update runs can stop and resume. The service may retry a failing member cluster and mark it stuck. It does not necessarily abort the whole run. Membership/label changes or validation failures can also stop a run. This shows why a tenant should read rollout status alongside per-cluster actual readiness and failure state. [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)

[observed] Azure Well-Architected safe-deployment guidance recommends progressive exposure. It recommends health gates at each phase and immediate halt on health changes. It also recommends rollback or roll-forward recovery. It says bake time should generally be hours/days to observe regional and usage variation. This is guidance for workload owners, not a claim that every Azure platform update uses a particular canary implementation. [6](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments)

[Inference] A two-hour rack-bench window can validate a deliberately short, bounded canary and immediate rollback path. It cannot satisfy the multi-hour/day bake recommendation for broad production promotion. Certification should report “two-hour local operational behavior measured,” not “large-fleet change policy proven.”

### 4.2 Actual readiness, not merely desired state

[observed] Azure Fleet Manager’s rollout API distinguishes two resource groups. It separates resources successfully applied from resources considered ready only after a configured unavailable period. Staged updates expose run/stage progression and stuck-cluster status. [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)

[Inference] For GPU hardware, translate readiness to observable workload-level facts. Expect 18 trays/72 GPUs present and consistent device enumeration. Require health checks to pass. Check that a representative allocation reaches usable GPU work. Check that the new state stays healthy through a short observation interval.

A successful control-plane “update accepted” or “node ready” condition alone is weaker than a first useful GPU-hour. Neither condition proves future workload SLOs.

## 5. Reclaim, decommissioning, and data wipe: do not conflate lifecycle layers

### 5.1 Three different end states

1. **Task/tenant reclaim:** stop or evict workload, disable traffic, release scheduler allocation. Twine TaskControl and Borg disruption/termination controls address this layer. [1](https://www.usenix.org/system/files/osdi20-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf)
2. **Machine reclaim/reuse:** return machine to an operator pool, clear tenant association, apply correct baseline/host profile, establish inventory and health. Twine describes dynamic reassignment and host-profile switching; this is not evidence of data sanitization. [1](https://www.usenix.org/system/files/osdi20-tang.pdf)
3. **Media sanitization/disposal:** sanitize or destroy storage media before reuse or release outside organizational control. Attach verification, validation, and traceable records.

   [observed] NIST SP 800-88 Rev. 2 (2025) defines Clear, Purge, Destroy. It recommends risk- and media-appropriate selection. It recommends inspection of successful completion and validation of residual risk. It also recommends a certificate. The certificate records asset identity, method, tool/version, verification, validation, and disposition. [7](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf)

[observed] NIST warns that normal overwrite may miss SSD spare/overprovisioned areas. NIST says to match Purge techniques to device type. Cryptographic erase depends on key generation, implementation, key copies/escrow, and error handling. It also states that full/representative sampling of contents after clear/purge is not required unless policy requires it. Tool status/errors and risk-based validation are central. [7](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf)

[Inference] NIST is a sanitization practice reference, not proof that Meta, Google, or Microsoft use a specific wiping process. Google Cloud and Microsoft publish company-specific media-disposal controls (below). Neither source provides tenant-verifiable per-device sanitization evidence for this Chennai rack. This brief finds no Meta-specific public wipe evidence in this research. A rack-bench tenant must not claim “data wiped” from a short read test or its own filesystem deletion.

[observed] Google Cloud says data deletion can include soft-deletion/recovery, logical deletion from active systems, and expiry from backups. It documents media retirement when hardware fails tests or receives an upgrade. It documents asset tracking through installation/retirement/destruction and authorized drive erase verification.

Its page states zero-overwrite plus multi-step verification for hard drives. If erase fails, Google holds the drive securely for physical destruction and secure recycling. This is Google’s published practice, not a measurement or per-asset certificate for a tenant. The page says it represents status as written in May 2024, so treat currency as bounded. [9](https://cloud.google.com/docs/security/deletion)

[observed] Microsoft Azure says end-of-life hardware follows data-handling/disposal procedures. Supported drives receive secure erase. Microsoft destroys drives that secure erase cannot handle by disintegration, shredding, pulverizing, or incineration, and keeps disposal records. This is Microsoft’s documented operator process, not a tenant-observed wipe. [10](https://learn.microsoft.com/en-us/azure/security/fundamentals/physical-security)

[observed] Microsoft Service Assurance separately describes failed data-bearing devices as audited and destroyed on campus. It categorizes Clear/Purge/Destroy. It says staff maintain chain of custody during on-site sanitization/disposal. [11](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction)

[Inference] Company statements are evidence that the process is documented. They are not evidence that a named drive in this rack completed the process. Request asset serials, method/result, exception handling, verification records, destruction record when applicable, and custody trail. Do not convert a policy statement into measured PASS.

### 5.2 Contract offboarding and safe removal

[observed] Azure Well-Architected guidance says deletion can be irreversible. It tells users to confirm inactivity over a relevant business cycle and preserve needed state. It tells users to disable before delete where possible, observe a watch window, and clean up residual references. [6](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments)

[Inference] A rack-bench run can safely verify only tenant-side offboarding. The API/console acknowledges job termination. No tenant-owned process remains. The allocation disappears from tenant-visible inventory. The tenant can revoke test credentials/tokens. A subsequent authorized tenant allocation can use the released device.

Operator-side asset retirement, secure erase, physical chain of custody, and final disposal require records and sampling beyond tenant scope.

## 6. Desired versus actual state: reconcile by identity and evidence

[observed] The cited sources show multiple versions of reconciliation. Facebook keeps version-controlled config as ground truth but acknowledges asynchronous propagation. Borg stores declarative desired state and retries idempotently. Azure Fleet Manager uses resource snapshots and reports rollout/cluster status. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)

[Inference] A useful operational reconciliation record should bind several fields per stable device/rack identity. Fields include desired SKU/firmware/driver/config version and observed identity and version. They include desired lifecycle state (available, drained, updating, reclaiming, retired). They also include actual health/readiness, last transition and result, and any unexplained mismatch. Compare both sides, not just a provider’s desired-state screenshot. Detect duplicates, missing trays/GPUs, stale entries, unexpected versions, and “ready” devices that cannot run a small real workload.

[Inference] A rack-bench tenant cannot read the operator’s complete fleet database. Its bounded reconciliation is a tenant-visible inventory snapshot. The tenant compares it with observed PCI/GPU enumeration and a small per-GPU usability check. Report sample size and exclusions. Operator should separately provide signed/dated fleet inventory and change/reclaim event records if certification scope includes operator controls.

## 7. What is operator-only versus tenant-testable

| Control / assertion | Operator-only evidence (unless tenant API exposes it) | Safe tenant-side evidence |
|---|---|---|
| Change authority, review, config validators, fleet canary cohort | Change record, review/approval, policy/version, cohort selection, canary health and rollback history. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf) | Validate tenant-visible config and versions. Do not claim to test provider change governance. |
| Fleet desired/actual drift | Fleet-wide inventory/reconciler output, exceptions and age. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) | Compare assigned rack manifest to observed 18-tray/72-GPU inventory and version/health snapshot. |
| Maintenance drain and app-aware eviction | Scheduler events, traffic-disable actions, TaskControl/maintenance deadlines, disruption budgets. [1](https://www.usenix.org/system/files/osdi20-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) | Authorized tenant stop/reschedule. Prove graceful signal handling, no duplicate tenant work, successful recovery. Never inject rack-wide failure without approval. |
| Fleet rollout/rollback | Fleet-manager run ID, cohort, approval, health gate, rollback target, all-member readiness. [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy) | In isolated tenant workload, exercise a reversible config or job change, observe it, revert and verify baseline. |
| Capacity reclaim/reallocation | Operator scheduler/accounting confirms resource returned/reassigned and no stale ownership. [1](https://www.usenix.org/system/files/osdi20-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) | Tenant stop/resize then reallocate only its authorized resources. Verify tenant allocation cleared and usable. |
| Media wipe and physical disposal | Asset serials, media list, sanitization technique/tool/version, verification/validation, certificate, chain of custody. [7](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf) | Do not run a destructive wipe test. Verify only evidence package and tenant-visible access revocation. |
| Contract/offboarding closure | Contract entitlements, final billing/egress/account closure, asset disposition, support ticket close. | Check tenant console/API access, credentials, data/export completion, final allocation/inventory state. |

## 8. Fleet sampling limits and safe two-hour checks

### 8.1 Sampling limitations

- [inference] A single GB300 rack is an individual-rack sample, not a statistically representative fleet sample. It cannot establish region-wide rollout safety, common-mode failure rates, or rollout tail latency. It also cannot establish all-tenant eviction behavior or correctness of a fleet-wide inventory.
- [observed] Facebook’s canary paper is explicit that small production samples may not expose scale-dependent load issues. It describes adding a full-cluster phase. [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf)
- [inference] A two-hour window is shorter than Azure guidance’s hours/days bake time. It can find deterministic local faults and immediate rollback failures, not diurnal/peak-load, delayed propagation, or long-horizon drift. [6](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments)
- [inference] Treat N=1 rack results as “observed on this rack at this timestamp.” Increase confidence with repeat racks, independent batches, and operator fleet-level evidence. Do not imply that a canary PASS is an all-fleet guarantee.

### 8.2 Safe proposed two-hour lifecycle checks

These are **proposed** checks, not claims that the repository already contains them. Do not force firmware, BMC, switch, OS, or destructive-storage changes during certification. Run only on the isolated rack with the tenant authorization provided.

1. **Identity and desired/actual snapshot (10–15 min).** Record rack/host IDs, expected 18 trays/72 GPUs, GPU UUIDs/count, firmware/driver/software version, health, and tenant-visible allocation. Compare contract/manifest to observed state. Fail/warn on missing, duplicate, unknown, stale, or unhealthy components. [Inference; method based on observed desired/actual distinctions in [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf), [3](https://research.google.com/pubs/archive/43438.pdf), [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)]
2. **Readiness truth (15–20 min).** Run lightweight GPU enumeration plus a short approved CUDA/NCCL or framework smoke. Require all allocated GPUs to execute useful work. Require them to report healthy afterward. Separate control-plane “ready” from measured usable GPU readiness. [Inference]
3. **Graceful tenant drain/reclaim (15–25 min).** Start a short tenant-owned workload with checkpoint/termination logging. Request normal stop through the supported tenant API. Verify termination signal/exit, no orphan processes, and allocation release. Then reallocate the same authorized GPU(s) and run a small smoke again. Do not fake operator maintenance or disrupt other tenants. [Inference, informed by [1](https://www.usenix.org/system/files/osdi20-tang.pdf) and [3](https://research.google.com/pubs/archive/43438.pdf)]
4. **Reversible config/job change (20–30 min).** Change only a tenant-owned reversible parameter or job image/config. Record desired version, observed version, readiness, and functional result. Revert to known-good and confirm actual state returns. If the operator offers a staged update API, use an isolated canary target and record its run status. Do not promote fleet-wide. [Inference; primary mechanisms [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf), [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)]
5. **Rollback and stuck-state handling (10–15 min).** On a harmless intentionally invalid tenant-level setting, verify rejection or rollback to known-good. Never deliberately fail firmware/hardware. Confirm the system does not report success while the workload remains unready. [Inference]
6. **Final reconciliation and offboarding evidence (15–20 min).** Compare start/end inventory and versions. Confirm allocation absent or returned as agreed. Confirm tenant credential revocation is effective and logs/results exported. List operator-only evidence still outstanding. No wipe command or physical removal. [Inference; offboarding practice [6](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments), sanitization record [7](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf)]

[Calculated] The broad timebox range is 85–125 minutes, so its longest combination exceeds the 120-minute window by five minutes. Use the shorter ranges in an actual schedule. Reserve 30 minutes for setup, recovery, and report capture. Do not attempt every optional operator API integration. A practical schedule is 10 + 15 + 20 + 20 + 10 + 15 = 90 minutes. Reserve 30 minutes for setup, unexpected delay, and cleanup.

### 8.3 Rack-bench implementation boundary and exact local evidence

[observed, local] Bench dispatch currently registers only `internet`. It supports pre-run hooks, selected-check filtering, and ordered execution, but contains no lifecycle category or scheduler/client integration. **Exact local evidence:** [`rack_bench/bench/runner.py:12-15,27-64`](../../../rack_bench/bench/runner.py#L12-L64).

[observed, local] Audit dispatch is a separate set of hardware/software scopes. It is not evidence of lifecycle control-plane state or fleet drift. **Exact local evidence:** [`rack_bench/audit/runner.py:10-22,25-49`](../../../rack_bench/audit/runner.py#L10-L49).

[observed, local] Internet bench options are specific to S3/R2/GCS uploads/downloads, duration, object size, and concurrency. This brief does not repeat their performance findings. **Exact local evidence:** [`rack_bench/bench/internet/cli.py:9-24`](../../../rack_bench/bench/internet/cli.py#L9-L24).

[Inference] An N04 bench category would require an explicitly authorized lifecycle adapter/API and immutable record schema. Without that access, run only local inventory/readiness/tenant-job stop checks. Report operator controls as “not measured.” Do not infer successful drain/reclaim from a process disappearing. First check scheduler allocation and a successful subsequent workload.

## 9. Practical conclusion for GB300-class rack certification

[observed] The primary sources converge on staged change, actual health/readiness gates, and bounded disruptions. They also converge on graceful or application-coordinated eviction, rollback, and reconciliation between desired and observed state. They also distinguish machine/resource reclaim from storage sanitization and offboarding. [1](https://www.usenix.org/system/files/osdi20-tang.pdf) [2](https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf) [3](https://research.google.com/pubs/archive/43438.pdf) [4](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy) [7](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf)

[Inference] For rack-bench, PASS must mean measured state, never vendor assertion. Tenant-visible GPU inventory reconciles. Usable GPU work succeeds. A safe tenant workload drains and releases allocation. Reversible change and rollback restore observed known-good state. The run verifies final tenant access/allocation closure.

Fleet canary policy, scheduler internals, cross-tenant reclaim, secure wiping, and physical decommissioning are separate operator evidence tracks. Mark each as **operator-only / not measured** unless the run inspected direct, auditable evidence.

## Sources

- Kept: Tang et al., **Twine: A Unified Cluster Management System for Shared Infrastructure** (USENIX OSDI 2020, primary Facebook/Meta systems paper). Coverage: direct mechanisms for maintenance, TaskControl, drain, release pacing, host profiles, and machine reassignment. https://www.usenix.org/system/files/osdi20-tang.pdf
- Kept: Tang et al., **Holistic Configuration Management at Facebook** (SOSP 2015, primary source). Coverage: config-as-code, validation, review, canary phases, health predicates, rollback, and propagation limits. https://sigops.org/s/conferences/sosp/2015/current/2015-Monterey/printable/008-tang.pdf
- Kept: Verma et al., **Large-scale cluster management at Google with Borg** (EuroSys 2015, primary Google research paper). Coverage: declarative jobs, rolling updates, termination, disruption bounds, idempotence, machine/task recovery, and reclaim distinctions. https://research.google.com/pubs/archive/43438.pdf
- Kept: Tirmazi et al., **Borg: the Next Generation** (EuroSys 2020, Google Research primary source). The brief checks it for lifecycle relevance. It uses the source only to date the evolution. The brief excludes its workload/failure statistics as out of N04 scope. https://research.google/pubs/borg-the-next-generation
- Kept: Microsoft Learn, **Azure Kubernetes Fleet Manager rollout strategy**. Coverage: current public API behavior, readiness delay, staged updates, approval, rollback snapshots, and stuck state. https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy
- Kept: Microsoft Learn, **Azure Kubernetes Fleet Manager overview** — current service scope and multi-cluster update mechanisms. https://learn.microsoft.com/en-us/azure/kubernetes-fleet/overview
- Kept: Microsoft Learn, **Safe deployment practices**. Coverage: health-gated progressive rollout, halt/rollback and decommission safety guidance. This is guidance, not universal implementation proof. https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/safe-deployments
- Kept: Google Cloud, **Data deletion on Google Cloud**. Coverage: company-specific deletion pipeline, hardware retirement, secure erase, verification, destruction fallback, and asset tracking. Its status is explicitly dated May 2024. https://cloud.google.com/docs/security/deletion
- Kept: Microsoft Azure, **Azure facilities, premises, and physical security** — company-specific secure erase/destruction options and destruction-record practice. https://learn.microsoft.com/en-us/azure/security/fundamentals/physical-security
- Kept: Microsoft Service Assurance, **Data-bearing device destruction** — on-campus failed-device destruction, sanitization categories and custody process. https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction
- Kept: NIST SP 800-88r2, **Guidelines for Media Sanitization** (2025). It gives current primary standard guidance for media disposition, sanitization assurance, and certificates. https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-88r2.pdf
- Dropped: Borg secondary summaries and commentary. This brief uses the primary Google paper instead.
- Dropped: non-primary Facebook server-wipe search results. They do not establish Meta’s actual lifecycle procedure. This brief repeats no vendor wipe claim.

## Gaps

- The Meta/Twine and Facebook config papers are 2020 and 2015 respectively. They establish published mechanisms at those dates. They do not show the exact 2026 internal implementation or whether Meta has since replaced components. This file makes no claim that the old config stack remains unchanged.
- Google Borg’s cited paper is 2015. It is a primary description of Borg but not current documentation of all present Google fleet workflows.
- Azure Fleet Manager docs are current public product documentation. They are not evidence that Azure uses the same APIs internally to update its physical GPU hosts.

  The cited rollout-strategy page contradicts itself. Its default-behavior paragraph says `unavailablePeriodSeconds` is 10 seconds. Its configuration-parameters paragraph says the default is 60 seconds. This file asserts no universal default. A bench must inspect the live policy and observed readiness. Do not conflate Azure workload rollout guidance with infrastructure-fleet mechanisms.
- The sources describe controls. They do not provide customer-accessible proof that a particular provider runs them on this Chennai rack. Require dated events, run IDs, observed status, immutable asset identity and exception records for operator claims.
- Google Cloud’s published deletion page is dated May 2024 and describes its process as-of-publication. Verify current terms and control evidence before relying on it. Microsoft’s pages are public descriptions rather than per-asset audit records.
- Google’s 2020 *Borg: the Next Generation* paper is not a lifecycle-control update. This brief deliberately does not repeat its trace-analysis/statistical content. The 2015 Borg paper remains the source for the mechanisms relevant here.
- This brief does not establish Meta-specific public wipe/decommissioning practice from primary public material. Twine/config papers describe compute lifecycle and configuration but not media sanitization. Do not infer Meta’s wipe controls from NIST or another company. A Meta primary security/engineering source or operator evidence is still needed.
- Rack-bench local code has no lifecycle bench category and no control-plane adapter. This brief performs no lifecycle check. The suggested checks are a safe measurement design, not a certification result.
- Two hours cannot establish fleet-scale drift coverage, long bake-time safety, or statistical failure rates. They also cannot establish behavior across regions or time zones, or complete offboarding. Report fleet sampling separately from the one-rack tenant measurement.
