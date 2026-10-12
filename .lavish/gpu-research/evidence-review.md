# Evidence review

Research date: 2026-10-11.

The orchestrator checks decisive primary-source passages before acceptance.
This file records checks, corrections, and limits.

## N03: Meta and OCP

- [Meta's article](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) defines static, transient, and silent faults.
- The article backs reductive triage and known-model tests.
- Fleetscanner, Ripple, and Hardware Sentinel cover AI and non-AI infrastructure.
- Their CPU-oriented evidence does not show NVIDIA GPU detector coverage.
- [OCP's whitepaper](https://www.opencompute.org/documents/sdc-in-ai-ocp-whitepaper-final-pdf) backs the six-month example on page 15.
- The whitepaper backs Gemini deterministic replay and idle scanners on page 19.
- Sections 5.2 and 6.2 help checksums, replication, and limits from nondeterminism.
- The researcher adds CP-Bench and corrected DCGM command evidence.
- [Pinned CP-Bench README](https://raw.githubusercontent.com/facebookincubator/CP-Bench/bc4343097f9dd77b6136d4608b76617b4cf78214/README.md) backs operator comparisons and model references.
- The README gives project-estimated presets. These estimates do not show GB300 runtime.
- Its 7,200-second example uses the complete two-hour window, before collection and output overhead.
- Peer agreement can miss common-mode errors. Model checksums can change across environments.

## N02: Google and DCGM

- [Google's GPU guide](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus) gives `dcgmi diag -r memory -j`.
- It distinguishes XID 94 containment from XID 95 uncontained errors.
- It requires co-occurring XIDs for root-cause interpretation.
- Its 87°C guidance concerns A3, not GB300.
- Its broad application-error paragraph conflicts with its detailed memory-error table for XID 94/95.
- Use the detailed table and NVIDIA's catalog. Do not classify all XIDs as hardware defects.
- The researcher corrects the rack count to 72 GPUs: 18 trays × 4 GPUs.
- Per-host expected counts must follow the deployed host map, not the full-rack count.
- [AWS recovery](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html) backs system-status recovery and eligibility restrictions.
- Simplified recovery excludes metal instances. CloudWatch recovery has different eligibility.
- Infrastructure recovery does not prove GPU correctness. AWS XID-specific help text remains unverified.
- [DCGM's guide](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) backs named plugins and JSON results.
- A duration override controls one plugin. It does not control every level-3 test.
- The guide excludes comprehensive hardware diagnosis, repairs, and RMA decisions.
- The guide describes 75% framebuffer allocation for the memory plugin.
- Its NVBandwidth help list names B300, not blanket GB300 rack help.

## N05: ClusterMAX

- [The 3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) states eight-hour concurrent GPU/network burn-in.
- It states DCGM injection, synthetic log injection, and upstream PCIe bridge reset.
- It attributes a real XID 79 to the bridge reset.
- The article keeps performance and reliability scripts internal.
- [Reliability criteria](https://www.clustermax.ai/criteria/reliability) include ECC, XIDs, PCIe, NVLink, thermal, power, and version consistency.
- The researcher adds criterion enumeration and commit-pinned CLI evidence.
- [Pinned criteria JSON](https://raw.githubusercontent.com/SemiAnalysisAI/ClusterMAX/1492ac5e4ac992ae436f062cc51a340d61672ca3/cmax/scripts/1-audit/criteria-checks.json) shows GPU driver and idle-thermal audit checks.
- It marks XID capture and the monitoring stack as partial coverage.
- ECC requirements do not show an active ECC collector in the public audit.
- The researcher identifies TinyMeg2 in 1.0 provider-practice text.
- No checked passage shows TinyMeg2 use in ClusterMAX 3.0.

## N06: Titan and Blackwell memory management

- [Titan's paper](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf) backs 18,688 GPUs and over 100,000 collective GPU-years.
- Its introduction attributes the late failure surge to silver-sulfide corrosion of a board resistor.
- The paper separates that batch defect from a general GPU-chip defect.
- Its conclusions limit the failure pattern to the affected batch.
- [NVIDIA's RMA policy](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html) adds Blackwell HBM channel repair.
- A third uncorrectable-remap attempt can invoke channel repair when a spare channel exists.
- Field diagnostics validate RMA eligibility. Online counter checks do not issue an RMA verdict.
- [NIST's Poisson formula](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm) backs the zero-event calculation.
- The 95% upper rate bound is `-ln(0.05)/exposure` under the stated model.
- The assumptions require constant rates, independent events, and complete detection.
- The calculation does not estimate actual GB300 reliability.
- [Delta's full text](https://arxiv.org/html/2503.11901v3) shows 1,056 GPUs and 11.7 million GPU-hours.
- It separates 448 A100 GPUs from 608 H100 GPUs and uses selected coalesced XID events.
- Its memory-rate and recovery figures match the brief's quoted values.
- Cohort durations and logging differ. These rates do not show GB300 rates.

## N01: Provider screening and visibility

- [CoreWeave verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification) backs 20–30-minute hourly idle-node checks.
- It names SDC, FP8/FP16/BF16 performance regression, and thermal tests.
- It gives approximately 35 minutes for on-demand verification.
- These durations describe the provider's procedure, not the target rack's measurements.
- [Runpod's Markdown page](https://docs.runpod.io/instant-clusters/cluster-observability.md) shows the metric table missing from extracted HTML.
- It names aggregate/volatile ECC, row-remap state, temperatures, clocks, power, and PCIe counters.
- Its five-second telemetry applies to Instant Clusters.

## N04: Company fleet methods

- Meta's checked article backs known-model tests, reductive triage, and layered fleet methods.
- CPU Fleetscanner/Ripple rates do not show GPU detector sensitivity.
- The brief keeps Microsoft-specific screening and “Florence” identity as gaps.
- NVLink5 counter-reset limits do not prevent valid before/after snapshot differences.
- The researcher corrects this interpretation and adds local-source links.
- The researcher removes the unsupported Azure guest/DCGM telemetry assertion.

## N07: Methods and operational guides

- [Gregg's book page](https://brendangregg.com/systems-performance-2nd-edition-book.html) backs methodology, observability, and benchmarking coverage.
- [nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html) backs stable UUID/BDF targeting and unsupported-field handling.
- It separates volatile/aggregate ECC, remap state, power scopes, and NVLink generation counters.
- It warns that CLI output can change between releases.
- [DCGM release notes](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html) name GB300 Bianca, Galaxy, and MaxQ help additions.
- Later releases change telemetry and diagnosis rules. Use matched deployed versions.
- [The diagnostic CLI](https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html) shows unlimited default timeout.
- It shows heartbeat cancellation, conditional plugin help, and the limits of expected-entity checks.
- Named diagnostics also run software checks. `software` is not a standalone test selector.

## Acceptance policy

- Preserve the complete category briefs and their source qualifications.
- Use recommendations as inferences, not vendor mandates.
- Keep collection completeness separate from quality assessment.
- Keep every expected physical GPU in the report, including missing devices.
- No live rack evidence backs a runtime guarantee or universal acceptance thresholds.
- The report omits disputed or unverified provider details from executable recommendations.
