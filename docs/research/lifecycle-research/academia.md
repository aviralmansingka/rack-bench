# Lifecycle measurement methods: traces, schedulers, and reliability limits

Research date: 2026-10-11. Each claim below has a source URL.

This file marks claims as **[observed]**, **[calculated]**, or **[inference]**. Observed means a cited source reports it. Calculated means arithmetic derived from stated values. Inference means proposed interpretation or rack-bench design. This is an academia-methods brief for node N06; it does not repeat internet or storage performance research.

## 1. Scope and answer

### 1.1 What this evidence can establish

- **[observed]** Lifecycle measurement is an event-history problem. Capture state transitions, timestamps, entity identity, causes, and observation-window bounds. State transitions include request, accepted, allocated, booted, ready, useful work, change, interruption, recovery, release, and deletion. Borg records job submissions and task events. It uses them for debugging, charging, and capacity planning. Its public workload traces demonstrate the value and limits of this event-based approach ([Borg EuroSys 2015, §§2.6, 3.1](https://research.google.com/pubs/archive/43438.pdf); [Borg: The Next Generation / Borg at 10, EuroSys 2020](https://research.google/pubs/borg-the-next-generation)).
- **[inference]** In a two-hour rack certification, rack-bench can PASS measured *bounded service properties*. Examples include observed provisioning-path durations for a controlled test request. They include boot/readiness and first-useful-work milestones. They include whether the system applied a configured change safely. They include whether a canary task survives or recovers from a bounded interruption. They include whether offboarding completes its tested cleanup path.

  It cannot certify the provider's fleet failure rate, contractual end-to-end p99, or long-term reclaim/interruption frequency.
- **[observed]** The local project describes lifecycle bench as BMC cold-boot → GPU-ready → CUDA-usable, NIC link-up, and time-to-job-ready. Audit is read-only. Bench is quick category pass/fail. Smoke is long-duration burn-in ([README.md lines 7–15](../../../README.md#L7-L15); [349–350](../../../README.md#L349-L350); [478–482](../../../README.md#L478-L482)). **[inference]** Extend—not replace—these measured milestones with a clearly scoped orchestration/tenant-lifecycle transaction, if supported by a non-destructive test endpoint.

### 1.2 Important boundary

Historical fleet papers describe their own systems, eras, populations, logging practices, and workloads. **[inference]** They guide measurement design and warn against simple reliability claims. None predicts GB300-class NVL72 rack reliability in Chennai. Rack-bench can report its measurements and uncertainty. It cannot transfer historical rates to this rack.

## 2. Definitions: what is an event and what is the denominator?

### 2.1 Event record and lifecycle clock

A useful event record includes several fields. It carries an immutable run/request ID plus rack, tray, GPU, node, tenant/job, and scheduler identities where applicable. It carries event type and event/ingestion timestamps with clock source/uncertainty. It carries outcome, reason/source (user, scheduler, hardware, operator, provider), prior/next state, and linked incident/change IDs. Record wall-clock and monotonic durations when possible.

**[inference]** This schema follows the trace papers' use of event timestamps, affected system/node, and cause. It guards against ambiguous start/end definitions ([Schroeder & Gibson, DSN 2006, §§2.3, 3](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf); [Vishwanath & Nagappan, SoCC 2010, §2.1](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf)).

- **Contract-to-first-useful-GPU-hour:** define the start as a recorded contractual acceptance/signature timestamp only when that timestamp is available and auditable. Define the end as first completed, validated useful GPU work, not merely VM allocation, driver presence, or GPU enumeration. For example, use a small known-good kernel/training step with correct output. Keep provider-controlled wait, customer setup, and external dependency delays separate.

  **[inference]** A certification bench normally cannot observe a real signature or a production tenant's first-hour semantics. It can measure a test-request-to-useful-work proxy. It can label its start/end precisely.
- **Provisioning latency:** request accepted → resource assigned → host powered/booted → GPU/CUDA usable → workload ready. Report each segment and total. One total hides queueing, image/package setup, device initialization, and client delay. **[inference]** Report median and range for a few controlled trials as descriptive observations, not fleet p99.
- **Change/recovery latency:** change initiated → desired state acknowledged → new state active → test workload healthy. For interruption: last known-good work → interruption detected → restart/resume → useful work restored. Count lost work and duplicate/partial work separately. Borg shows explicit task state transitions, rolling updates, disruption limits, termination notice, rescheduling, and restart behavior. These mechanisms show a lesson. Rack-bench must record lifecycle state and policy, not collapse them into uptime ([Borg 2015, §§2.3, 2.5, 4](https://research.google.com/pubs/archive/43438.pdf)).
- **Offboarding latency:** tenant release initiated → allocations/tasks stopped → access revoked → test resources returned → test data/credentials removed or deletion status evidenced. Keep control-plane completion separate from verified data sanitization. **[inference]** A two-hour test can observe the former on a synthetic tenant. It cannot infer secure erasure from an API response alone.

### 2.2 Denominators

- **Request success fraction** = completed eligible requests / all eligible requests submitted in a prespecified interval. Exclude or separately classify customer-invalid requests, but never silently drop timeouts or pending requests.
- **Allocation/availability rate** = eligible resource-time available / eligible resource-time requested or committed, depending on the service promise. State whether denominator is GPU-hours, node-hours, rack-hours, jobs, or requests; these are not interchangeable. **[inference]** A report must show numerator, denominator, and exclusions next to every percentage.
- **Failure rate** = defined count of failures / exposure, e.g. failure events per device-hour or per GPU-hour. Count incidents and affected components separately. One correlated rack outage can affect many GPUs, but it does not create many independent causes.
- **MTBF / MTTF:** MTBF applies to a specified repairable unit and operational state. MTBF is total qualifying uptime exposure divided by number of qualifying failure events. For a non-repairable item, MTTF is time to failure. Do not call elapsed calendar period divided by count “MTBF”.

  This applies when exposure includes planned downtime, idle/not-in-service periods, or right-censored units. The report must say when it does. **[inference]** Fix event definition, repair boundary, and exposure rules before computing these values.
- **MTTR:** choose and name the interval. “Mean time to repair” may start at fault onset or detection and end at restoration. “time to acknowledge/mitigate/restore” are different operational clocks. Report distribution and median/tails as well as mean.

  **[observed]** Schroeder and Gibson report that repair-time mean and median differ substantially. They report high variability. Lognormal fits better than exponential in their LANL trace ([DSN 2006, §6](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)).

### 2.3 Censoring, missing events, and selection

- **Right-censoring:** a unit/request still operating or pending at the observation cutoff has an unknown eventual failure/completion time. Record it as censored at cutoff, not as a successful completion at that time.

  **Left-truncation:** a unit already in service when logging begins has unknown earlier history. Do not treat it as new at window start. Repeated measures on one device are not independent samples. **[inference]** Survival analysis or explicit censored observations are appropriate for long-running lifecycle data. A two-hour test should report “no event observed during 2 h,” not “failure-free.”
- **Missingness and event semantics:** logs may be incomplete, delayed, manually classified, or capture repairs rather than fault onset. **[observed]** Vishwanath & Nagappan explain that operators did not design repair tickets for reliability research. The tickets had missing component detail and uncertain diagnosis, and may undercount. Schroeder & Gibson describe manually entered failure records, automated detection plus human repair workflow, and root-cause uncertainty ([Vishwanath & Nagappan, §2.1](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf); [Schroeder & Gibson, §§2.3, 4](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)). **[inference]** Rack-bench should separate observed failure onset, alert/detection, ticket open, repair start, and restored service. It should preserve “unknown” causes.
- **Selection bias:** certification tests see a selected rack, one configuration, one time, and usually a cooperating test workload. **[inference]** Do not generalize to other firmware, schedulers, tenants, power conditions, network paths, workloads, or seasons without additional evidence.

## 3. Borg, Borg at 10, and scheduler lineage

### 3.1 Borg (EuroSys 2015): lifecycle mechanisms and observables

- **[observed]** Borg admits, schedules, starts, restarts, and monitors jobs. A job contains tasks. Tasks transition through Pending/Running/Dead. Users can submit, update, or kill them. A Borg alloc can reserve resources across task stops/restarts ([Borg 2015, §§1–2.4](https://research.google.com/pubs/archive/43438.pdf)).

  This establishes a useful lifecycle vocabulary. Terms: requested, admitted, pending, running, updated, evicted, restarted, finished/dead.
- **[observed]** Borg places tasks asynchronously after durable submission. Borg's feasibility and scoring phases select a machine. Its workload policy includes priority, quota, preemption, and failure-domain spreading. The paper reports typical median task startup latency about **25 s**, with package installation accounting for about **80%**. These are Borg's historical workload measurements, not a contemporary GPU-rack threshold ([Borg 2015, §3.2](https://research.google.com/pubs/archive/43438.pdf)).
- **[observed]** Borg task preemption may provide SIGTERM notice before SIGKILL. The paper says Borg delivers notice about **80%** of the time in practice. Borg updates can be rolling, with a bound on disruptions. Borg reschedules tasks after eviction or machine failure. Placement spreads job tasks across machine/rack/power failure domains ([Borg 2015, §§2.3, 4](https://research.google.com/pubs/archive/43438.pdf)).

  This describes a mechanism. It does not guarantee the same behavior on this rack.
- **[observed]** Borg replicates the Borgmaster five times. Master failover typically takes about **10 s**. It can take up to **one minute** in a large cell. The paper reports Borgmaster **99.99% availability in practice**. This figure describes the control plane in Google's operational setting. It is not GPU allocation availability and not a two-hour confidence estimate ([Borg 2015, §§3.1, 4](https://research.google.com/pubs/archive/43438.pdf)).
- **[observed]** Borg's evaluation deliberately uses real production checkpoints and workload, high-fidelity simulation, repeated compaction trials, and 15 representative cells. It does not claim a short synthetic bench predicts fleet behavior. Its trace-based policy tests preserve actual constraints and heterogeneity, and the authors note simulation simplifications ([Borg 2015, §§5.1–5.2](https://research.google.com/pubs/archive/43438.pdf)). **[inference]** Lifecycle testing benefits from both event replay and direct measurement; do not substitute one for the other.

### 3.2 Borg at 10 (EuroSys 2020): versioned trace, not prophecy

- **[observed]** “Borg: The Next Generation” studies a newly published trace. The trace spans **eight Borg clusters during May 2019**. The paper compares it longitudinally to the widely used **May 2011** trace.

  Its abstract reports several findings. Alloc sets serve resource-heavy workloads, and automatic vertical scaling works effectively. Job dependencies explain much of earlier reported high failure rates. Arrival rate and overcommitment increased, and workload mix changed. The **top 1% of jobs consume over 99% of resources**. Between-cluster variation is substantial ([Tirmazi et al., EuroSys 2020](https://research.google/pubs/borg-the-next-generation)).
- **[inference]** The methodological lesson is to preserve workload version, cluster, policy, and job dependencies in every trace analysis. A raw “job failure” count can conflate failed dependencies, retries, user cancellations, and infrastructure failures. Report causal classifications and denominator rules. A change in workload mix can alter measured startup and failure distributions even if infrastructure is unchanged.
- **[inference]** The 2011/2019 Borg findings are historical evidence about Borg. They are not GB300 forecasts, nor proof that rack-bench's scheduler exhibits Borg policies or performance.

### 3.3 Omega, Mesos, and the scheduler lineage

- **[observed]** Omega proposed shared cluster state, parallel specialized schedulers, and optimistic concurrency control. Schedulers work from local state snapshots, commit resource claims, and retry conflicting work. The paper compares monolithic, two-level/offer-based, and shared-state approaches. It uses both synthetic simulation and high-fidelity replay of Google production traces ([Schwarzkopf et al., EuroSys 2013](https://research.google.com/pubs/archive/41684.pdf)).
- **[observed]** Omega's trace-driven results show why measurement needs scheduler-event detail. Concurrent allocation attempts can conflict and require retries. All-or-nothing/gang scheduling and coarse conflict detection increase conflict costs. Its evaluation measures wait time, scheduler busyness, and conflict fraction. It does not treat “job started” as the sole metric ([Omega, §§4–5](https://research.google.com/pubs/archive/41684.pdf)).
- **[observed]** Borg 2015 reports a scheduler separate from the Borgmaster. It operates on cached state and accepts assignments only when still appropriate. The paper says the mechanism is similar in spirit to Omega's optimistic concurrency control ([Borg 2015, §3.4](https://research.google.com/pubs/archive/43438.pdf)).
- **[inference]** For GB300 lifecycle checks, expose queue/pending time, rejected/unschedulable reason, conflict/retry count if available, actual placement, and ready time. This distinguishes scheduling delay from boot and image delay. If the interface does not expose scheduler internals, mark the cause unobservable rather than infer it from elapsed time.
- **[inference]** Scheduler lineage is useful as a measurement framework, not a performance benchmark. Rack-bench must not copy any Borg/Omega result as an expected latency or service-level target.

## 4. Failure-trace methodology and what fleet studies actually found

### 4.1 Vishwanath & Nagappan: repair records and data limitations

- **[observed]** The SoCC 2010 study combines inventory, configuration, and repair-ticket sources. It covers a Microsoft datacenter population of over **100,000 servers** and a **14-month** period. Operators had collected the sources for operational purposes, not unified reliability analysis. Identifiers and fields were imperfect. Some component detail was unavailable. The authors warn that repair events can undercount or misidentify actual faults ([Vishwanath & Nagappan, §§2.1–2.2](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf)).
- **[observed]** They report approximately **8% annual server repair-event incidence** in that dataset. They explicitly note that the window is only a slice and component-level rates are approximate. Estimated annual disk replacements are an upper bound. Replacement records cannot always identify which physical disk failed ([same paper, §§3.1–3.3](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf)). **[inference]** Treat this as a study-specific operational result, not an industry constant or a GB300 forecast.
- **[observed]** The paper reports that a previous failure changes the observed subsequent-failure behavior. It cautions that its fitted inverse relationship is descriptive of this dataset and not a validated future predictor. Datacenter and manufacturer were significant predictors in its classification exploration. Several obvious variables were not ([same paper, §§3.4, 4.1](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf)). **[inference]** Track history, location, hardware cohort, and shared causes. Do not assume each device has a common independent failure rate.

### 4.2 Schroeder & Gibson: long traces, distributions, heterogeneity

- **[observed]** The DSN 2006 analysis used **23,000 failures** over **nine years**. It covered **22 LANL HPC systems**, **4,750 machines**, and **24,101 processors**. Failure records include start/end time, affected system/node, workload, and categorized cause. The operational database captured failures requiring administrator attention ([Schroeder & Gibson, §§1–2](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)).
- **[observed]** System-wide counts ranged from roughly **20 to 1,000 failures/year**, and rates varied substantially by system. Weibull/gamma often fit time-between-failures better than exponential. The described case includes a Weibull shape parameter around **0.7–0.8**. Repair times ranged from under an hour to over a day between systems. Lognormal fit repair times better than exponential ([same paper, abstract, §§5–6, 8](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)). **[inference]** A constant-rate Poisson model and a single fleet-average MTBF can hide age, system, workload, and cause heterogeneity.
- **[observed]** In an early system-life period, the paper reports more than **30% zero inter-arrival times** in a system-wide view. This indicates simultaneous multi-node failures. The paper does not perform a rigorous correlation analysis in that passage ([same paper, §5.3](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)). **[inference]** Correlated power, fabric, firmware, scheduler, or operator events invalidate one simplistic assumption. The assumption says 18 trays are 18 independent trials. Count the common incident and affected units; use rack/site time blocks or cluster-robust methods for longer datasets.
- **[observed]** Their repair-time table shows a large difference between mean and median. It shows very high squared coefficient of variation for several causes. Unknown root cause can be a substantial category ([same paper, §6](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)). **[inference]** Lifecycle reporting should publish event counts, median, quantiles, range, cause category, and uncertainty. Mean alone is fragile under a long tail.

### 4.3 Correlation is operationally central

- **[observed]** Borg explicitly places tasks across machine, rack, and power failure domains to reduce correlated failures. It also rate-limits recovery when a network partition could resemble many simultaneous machine failures ([Borg 2015, §4](https://research.google.com/pubs/archive/43438.pdf)).
- **[inference]** For a single NVL72-class 18-tray rack, several factors are shared causes. They include rack power, cooling, management controller, fabric, firmware rollout, image/configuration, and operator actions. A tray-level denominator can overstate independent evidence. Record incident IDs and common-mode groups; report both affected-GPU count and independent incident count. With just one rack, between-rack variance is unmeasurable.

## 5. Spot/preemptible scheduling as an event model

### 5.1 What interruption research and provider telemetry mean

- **[observed]** Spot/preemptible capacity is a supply/demand and policy phenomenon as well as a hardware phenomenon. AWS's current Spot Instance Advisor reports interruption frequency in broad ranges over a trailing **30-day** window, by instance pool. It states the overall historical average interruption frequency has been below **5%**. A particular workload's rate depends on point-in-time capacity ([AWS Spot Instance Advisor](https://aws.amazon.com/ec2/spot/instance-advisor)). These are provider-level, rolling summaries, not fixed reliability guarantees for a single SKU or GB300 system.
- **[observed]** AWS documents a rebalance recommendation for elevated interruption risk. AWS documents a typical two-minute interruption notice for Spot instances. AWS emphasizes that the provider may interrupt an instance when it needs capacity ([AWS EC2 Spot documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)). **[inference]** A lifecycle test should distinguish notice, interruption, workload checkpoint, restart, and useful-work recovery. Instance survival alone omits application loss.
- **[observed]** A cross-cloud experimental paper (“Making Cloud Spot Instance Interruption Events Visible”) reports a median AWS spot run duration of **1.2 hours** in its experiments. More than half of its GCP and Azure instances ran without interruption during **24-hour** experiments. Reported shortest P90 run times differed across providers. Its experiment is time-, SKU-, region-, and sample-specific ([paper PDF](https://leeky.me/publications/spot-interrupt-visible.pdf)). **[inference]** This illustrates why capacity-pool selection and observation duration must accompany interruption statistics. It is not a transferable GB300 interruption prediction.

### 5.2 Safe two-hour checks; do not manufacture destructive faults

- **[inference]** Use a provider-supported, explicitly interruptible test allocation or a scheduler simulator/event replay. Do not forcibly terminate production workloads. Do not power-cycle a shared rack or induce shared-fabric failure just to create a sample. If no reversible test API exists, verify lifecycle behavior from a controlled dry-run/configuration. Record the destructive interruption check as NOT RUN.
- **[inference]** Safe checks within two hours: (1) timestamp a small, bounded resource request and first valid CUDA work. (2) Perform one pre-approved rolling change on a canary/test job. Verify old/new state and workload health. (3) Exercise pause/resume or restart using a test workload with checkpoint marker and checksum.

  (4) Request release of the test allocation. Verify the scheduler returns capacity. Remove test credentials and temporary objects. (5) Inspect lifecycle event completeness and clock consistency. These checks measure behavior, not rates.
- **[inference]** For each check record attempts, successes, timeouts, status transitions, elapsed intervals, host/tray identity, and excluded causes. A PASS can assert “this test request reached useful work in X seconds” or “this canary recovered in Y seconds”. It cannot assert “fleet provisioning p99 is X.”

## 6. MTBF/MTTR statistics and sample-size limits

### 6.1 Descriptive metrics and uncertainty

- **[inference]** Report exact observed quantities first: events `k`, exposed device/GPU/rack-hours `T`, rate `k/T`, censored units, and event definitions. If assuming a homogeneous Poisson process, a one-sided 95% upper bound after zero events is approximately `-ln(0.05)/T ≈ 3/T`. Clearly label the strong stationarity/independence assumptions. This bound concerns the chosen event process, not correlated fleet-wide faults.
- **[calculated]** Two hours across 18 trays creates at most **36 tray-hours** of exposure. This assumes all trays operate and stay observable for the full window. At zero failures, the approximate one-sided 95% Poisson upper bound is `3/36 = 0.0833` events per tray-hour. This equals a lower bound on MTBF of only about **12 tray-hours** under that simplistic model. This is nowhere near evidence for long-run fleet reliability. The model is especially weak for one rack with shared causes.
- **[calculated]** Even if 18 trays were independent, each tray would have a hypothetical 1% event probability during the window. The probability of at least one event is `1 - 0.99^18 ≈ 16.5%`. A zero-event observation would therefore be common. It would be weak evidence against that rate. **[inference]** In practice, per-tray events are not necessarily independent and fault rates are unknown. This makes the illustration optimistic about evidence strength.
- **[calculated]** Consider a p99 provisioning-latency estimate from a sample without distributional assumptions. The chance that `n` independent observations contain even one sample in the slowest 1% is `1 - 0.99^n`. It is about **9.6% at n=10**, **63.4% at n=100**, and **95.1% at n=300**. A handful of two-hour requests cannot characterize p99. This holds especially when requests share a rack, image cache, queue, operator, or time window.
- **[inference]** Percentiles from repeated measurements on one rack/time are conditional to that setup. Use empirical quantiles only with `n`, confidence intervals/order-statistic method, and a note about dependence. Avoid extrapolating tails from a fitted distribution unless a much larger, relevant trace validates the fit.

### 6.2 Why two hours cannot estimate fleet reliability or provisioning p99

1. **Exposure too short:** failures that occur monthly/yearly are unlikely to appear in a two-hour window. No-event is not proof of reliability.
2. **Sample unit ambiguity:** 18 GPUs/trays share rack-level power, cooling, network, and operational changes. Nominal component count is not independent replication.
3. **Rare tail:** p99 requires many independent requests. It also requires representation of queueing regimes, cold starts, maintenance, image pull state, and time-of-day/load variation. A two-hour window samples one slice.
4. **Censoring:** requests still pending at end of run are not successes or failures with known completion times. Preserve them as pending/right-censored.
5. **Rate nonstationarity:** historical HPC and datacenter studies report system, age, workload, and temporal variability. A constant failure-rate estimate can be misleading ([Schroeder & Gibson, §§5–6](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf); [Vishwanath & Nagappan, §§3–4](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf)).
6. **Common-mode causes:** one shared fault can affect many nodes at once. Treating each affected GPU as an independent event artificially narrows uncertainty.
7. **Selection and scope:** a certification configuration and test account may not match real tenants, workloads, or provider capacity policy. They may also not match the contractual start time.

## 7. Two-hour rack-bench measurement design

### 7.1 Proposed bounded checks

**[inference]** The following is a safe measurement design, not a promise that every provider exposes the necessary API. Keep audit read-only; run only on explicit test allocations/canaries and obtain approval for any state-changing request.

1. **Lifecycle clock sanity (5–10 min):** verify monotonic timing and timestamps across client, scheduler events, BMC/host logs, and GPU readiness. Record offset/uncertainty. If the run cannot correlate clocks, report component-local durations and mark end-to-end timing uncertain.
2. **Request → useful GPU work (about 30–45 min):** make sequential/parallel test requests (for example 3–10, subject to API limits). Retain every attempt. Include failure, pending-at-cutoff, and timeout attempts. Measure request accepted, allocation assigned, host ready, CUDA initialized, known-good GPU operation completed. Report per-attempt intervals, median/range, `n`, and start conditions (warm/cold image, queue status). Do not label as p99.
3. **Canary change (about 20–30 min):** use a test job to change a benign setting/image/version or resource shape. Change one canary at a time. Verify desired state, observed state, impact on workload, rollback, and time to healthy. Never update the entire rack for certification.
4. **Recovery semantics (about 20–30 min):** where supported, pause/restart a disposable canary or use a documented scheduler preemption simulator. Checkpoint a known marker. Trigger the approved transition. Validate resumed useful work and data integrity. If destructive interruption is unavailable, record recovery as NOT RUN, not PASS.
5. **Release/offboarding (about 15–20 min):** terminate the test tenant/job. Confirm resources no longer allocated, test access revoked, temporary credentials removed, and deletion workflow status returned. Record that secure media sanitization is not proven unless independently evidenced.
6. **Evidence review (remaining time):** confirm the complete event sequence. Identify missing transitions and retries. Separate operator/customer/provider waits. Record failures and censoring. Export an immutable run artifact.

### 7.2 Verdict language

- **PASS (measured):** the check reports its measurements, with event/result, value, denominator, `n`, test conditions, and raw event-log reference. PASS means measured, not vendor-claimed. It does not itself assert that the run met a default numeric threshold or establish fleet reliability.
- **Quality gate (expectation/invariant):** keep the expected behavior or invariant separate from the measurement result. Examples: correct GPU output, no leaked test allocation, or recovery by the test deadline. Apply a quality gate only when the profile/contract defines it; do not impose a default numeric threshold.
- **FAIL:** a measured operation violates an explicitly configured quality gate, produces incorrect GPU work/data, or misses an operational deadline. The check must meet that deadline. A request still pending at observation cutoff is censored for latency/failure-time analysis. If it has also breached its declared operational deadline, record that deadline breach as a measured failed operation.
- **SKIP / NOT RUN:** the run did not attempt an operation. Reasons: required API/credentials were unavailable, destructive action lacked approval, or the run could not observe the behavior. Observation cutoff alone does not turn an attempted operation into SKIP. Preserve it as pending/right-censored. Separately report any deadline breach.
- **DIAGNOSTIC:** observed duration/event without a configured gate or conclusive attribution. Preserve it for later operational comparisons.

### 7.3 Historical traces vs GB300 predictions

**[observed]** Borg 2015 reports approximately 25-second median startup, 80% package-install contribution, 80% SIGTERM notice observation, and Borgmaster availability. These are Google/Borg figures. Borg at 10 compares 2011 and 2019 Google workload traces. The two failure papers analyze Microsoft server repair tickets and LANL HPC systems from older generations ([Borg 2015](https://research.google.com/pubs/archive/43438.pdf); [Borg 2020](https://research.google/pubs/borg-the-next-generation); [Vishwanath & Nagappan 2010](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf); [Schroeder & Gibson 2006](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)).

**[inference]** They support event schema, metrics, trace methodology, and caution. They do not establish GB300 NVLink/NVL72 startup behavior or firmware failure rates. They also do not establish tray MTBF, Chennai site effects, or a rack-bench performance threshold.

## 8. Material takeaways for N06

1. Lifecycle is a series of separately timed transitions, not one “time to provision” number. Capture states, event causes, retries, and clock quality.
2. Use exposure denominators and keep request-level, device-level, and incident-level counts distinct. Preserve pending observations as censored.
3. Historical traces show heterogeneity, non-exponential durations, dependencies, and correlated events. Report context, not a universal MTBF/MTTR.
4. Borg and Omega provide useful lifecycle mechanisms and trace-driven evaluation patterns. Their numeric performance/availability results are not rack targets.
5. Two-hour certification can verify a bounded request/change/recovery/release path with measured evidence. It cannot estimate fleet reliability, long-term interruption frequency, or provisioning p99.
6. A safe PASS is a scoped empirical statement for the tested rack/run. No observed faults do not certify reliability.

## Sources

- Kept: [Verma et al., “Large-scale cluster management at Google with Borg,” EuroSys 2015](https://research.google.com/pubs/archive/43438.pdf) — primary paper for lifecycle states, scheduler mechanisms, failure handling, and exact numeric context.
- Kept: [Tirmazi et al., “Borg: The Next Generation,” EuroSys 2020](https://research.google/pubs/borg-the-next-generation) — primary longitudinal analysis of 2011 and May 2019 traces, eight clusters, workload dependencies and heterogeneity.
- Kept: [Schwarzkopf et al., “Omega: flexible, scalable schedulers for large compute clusters,” EuroSys 2013](https://research.google.com/pubs/archive/41684.pdf) — primary source for scheduler lineage, optimistic concurrency, replay methodology, conflicts and wait-time metrics.
- Kept: [Vishwanath & Nagappan, “Characterizing Cloud Computing Hardware Reliability,” SoCC 2010](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf) — primary repair-log methodology and explicit data-quality/selection limitations.
- Kept: [Schroeder & Gibson, “A large-scale study of failures in high-performance computing systems,” DSN 2006](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf) — primary long-duration HPC trace methods, failure rates, correlation warning, and repair/inter-arrival distributions.
- Kept: [AWS EC2 Spot Instance Advisor](https://aws.amazon.com/ec2/spot/instance-advisor) and [AWS Spot documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html) — current primary provider definitions for trailing interruption-frequency bands, rebalance signal, and interruption behavior.
- Kept: [“Making Cloud Spot Instance Interruption Events Visible”](https://leeky.me/publications/spot-interrupt-visible.pdf) — primary experimental comparison of spot interruption observation, retained only as a bounded experimental example.
- Kept (local evidence): [README.md lines 7–15](../../../README.md#L7-L15), [lines 349–350](../../../README.md#L349-L350), and [lines 478–482](../../../README.md#L478-L482) — confirmed directly with `nl -ba README.md`; these establish audit/bench/smoke roles, lifecycle milestones, and smoke duration/fault examples.
- Kept (local context): [`.lavish/lifecycle-research/research.md:1-13,26-30`](research.md) — N06 question, scope, intended acceptance condition, and explicit exclusion of internet/storage repeats.
- Dropped: secondary summaries/blog posts of Borg/Omega and generic MTBF how-to pages. Primary papers define the mechanisms and data context more precisely.

## Gaps

- The public Borg 2020 abstract provides key findings. Consult the full paper/trace before reproducing those analyses. It holds the exact operational definitions behind “failure,” job dependencies, and the reported top-1% resource concentration.
- No rack-bench-local lifecycle implementation or test runner is present in the cited local lines. The local README describes intended lifecycle behavior. Exact supported APIs, event output schema, and thresholds remain unverified.
- No GB300/NVL72 fleet failure trace or Chennai rack deployment exposure was available in this node. No provider-specific scheduler event feed, contract signature timestamp, or independently verifiable deletion evidence was available either. Historical study rates must not fill these gaps.
- Spot interruption examples are cloud-SKU/region/time dependent. They do not specify an applicable GB300 rack pool. They also do not provide enough detail here to recompute confidence intervals for those experiments.
- The Poisson zero-event bound and sample-size illustrations are intentionally simplified. They assume independent, stationary observations; shared rack failures, request retries, and repeated same-rack samples violate those assumptions. Use them as warnings, not as rack-level reliability estimates.
- Two-hour test design durations and sample counts are proposed allocations of a fixed window. They are not experimentally validated optimums. Tune only after confirming API rate limits, safe rollback, operator approval, and event visibility.
