# Hyperscaler GPU-fabric verification and diagnosis
Research date: 2026-10-11. All claims below use a source URL.

## 1. Executive answer: what “verified” means

A configured NIC does not show a healthy GPU fabric. An advertised link rate does not show a healthy GPU fabric. A successful job launch does not show a healthy GPU fabric. Use the intended placement, topology, and software versions. Run a low-level transport test on each physical rail. Run NCCL collectives with the production transport and rank layout.

Use NCCL logs to show the selected transport/plugin. Check performance and errors against host and switch counters. A NCCL benchmark can use sockets without notice. A completed socket test is not RDMA certification. **[inference]** [AWS EFA/NCCL test guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [NVIDIA NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html)

For rack-bench, a two-hour category can make evidence for a 1-rack NVL72 host-visible fabric. It can also make evidence for a representative full-rack collective. It does not show large-cluster-scale evidence. It does not show fabric behavior under long-duration congestion. It does not show switch-side ECN/PFC correctness when switch telemetry is inaccessible. It does not show fault recovery under sustained jobs.

Keep these evidence boundaries explicit. Do not make PASS claims from these limits. **[inference]** [rack-bench README](../../README.md#L327-L337); [NVIDIA NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html)

## 2. Provider stacks are not interchangeable

### 2.1 AWS EFA: Libfabric provider, not verbs InfiniBand

The AWS page shows an EFA path: NCCL runs through the `aws-ofi-nccl` plugin into Libfabric’s EFA provider (`FI_PROVIDER=efa`). This path is not the verbs-based `NET/IB` path that conventional InfiniBand/RoCE diagnostics use. AWS shows a provider-enumeration command: `fi_info -p efa -t FI_EP_RDM`. The AWS page also shows NCCL log evidence `NET/OFI Selected Provider is efa`. **[observed]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

The current AWS page (checked 2026-10-11) shows EFA installer `1.50.0` and NCCL source tag `v2.30.4-1`. The page shows supported base images: AL2023, Ubuntu 22.04/24.04/26.04, Debian 12/13, RHEL 10. The page shows EFA support from NCCL 2.4.2 onward and the installer command `sudo ./efa_installer.sh -y --mpi=openmpi5`. Since EFA 1.30.0, the installer puts Open MPI 4.1 and 5 in place by default. AWS shows a recommendation for Open MPI 5 alone, unless 4.1 is necessary. **[observed]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

The documented NCCL launch puts `FI_EFA_USE_DEVICE_RDMA=1`, `NCCL_DEBUG=INFO`, and an EFA-inclusive `LD_LIBRARY_PATH` into the environment. It removes MPI’s `cm` PML from selection and uses the TCP/self BTL. It also removes `lo,docker0` from the TCP BTL.

A positive run shows `NET/OFI Selected Provider is efa` in its logs. AWS also shows `NCCL_TOPO_FILE` auto-selection evidence for P4d. This shows plugin/provider selection. It does not show direct GPU memory transfers or per-rail balance by itself. **[observed]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

AWS’s complete published launch command is below. It makes transport/configuration reproducible. But the `LD_LIBRARY_PATH` paths are image-dependent. AWS docs show `/opt/amazon/efa/lib` here:

```bash
/opt/amazon/openmpi/bin/mpirun \
  -x FI_EFA_USE_DEVICE_RDMA=1 \
  -x LD_LIBRARY_PATH=/opt/nccl/build/lib:/usr/local/cuda/lib64:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/opt/amazon/ofi-nccl/lib:$LD_LIBRARY_PATH \
  -x NCCL_DEBUG=INFO \
  --hostfile my-hosts -n 8 -N 8 \
  --mca pml ^cm --mca btl tcp,self --mca btl_tcp_if_exclude lo,docker0 --bind-to none \
  $HOME/nccl-tests/build/all_reduce_perf -b 8 -e 1G -f 2 -g 1 -c 1 -n 100
```

**[observed]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

AWS shows a recommendation: cluster placement groups for low-latency placement in one AZ. But the AWS page shows no absolute requirement. EFA security-group self-referencing ingress/egress is mandatory in the documented setup. Placement is therefore a controlled variable for meaningful comparison. This evidence shows no requirement for a cloud placement-group analogue on all racks. **[observed/inference]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

AWS’s current guide shows an allreduce test at 8 bytes to 1 GiB, doubling (`-f 2`). The example uses 8 ranks on an 8-GPU instance and 100 iterations. This is an executable bootstrap example. It is not sufficient for rack-bench’s full 8 B–16 GB matrix. It is not sufficient for collective diversity, per-rail RDMA, or full 18-tray rank coverage. **[observed/inference]** [AWS EFA/NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

### 2.2 Azure ND H100/H200: verbs InfiniBand and GPUDirect RDMA

The Azure ND H200 v5 specification shows eight H200 GPUs per VM and 900 GB/s NVLink. It shows eight 400-Gbps Quantum-2 ConnectX-7 InfiniBand connections, one per GPU. It shows a 3.2 Tb/s aggregate VM interconnect. Azure shows automatic inter-VM IB configuration for VMs within the same VM scale set, and GPUDirect RDMA support. This is a verbs/IB fabric, not EFA/Libfabric. **[observed]** [Azure ND H200 v5 specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nd-h200-v5-series)

An Azure community troubleshooting article shows a useful symptom. NCCL output with `NET/Socket` instead of `NET/IB` shows a transport fallback. The article keeps this guidance: `NCCL_DEBUG=INFO`, OFED checks (`ofed_info`), interface state (`ibstat`), and the same placement group. Keep this as field guidance, not a Microsoft product guarantee.

Do not use the article’s stated 380+ Gb/s target as a universal acceptance threshold. It shows a particular H100/cloud configuration and message scale. Measured useful throughput is dependent on GPU/rank count, collective, rail use, message size, and protocol overhead. **[observed/inference]** [Microsoft Community troubleshooting article](https://techcommunity.microsoft.com/blog/startupsatmicrosoftblog/your-h100s-on-azure-wont-do-distributed-training-heres-probably-why-/4537502)

Keep ND HN (H100) and H200 claims separate. Do not put the same rank topology on every ND SKU. The H200 official specification is explicit for eight GPUs and eight 400-Gbps links. Check SKU-specific topology and fabric arrangement from the deployed offer and inventory before rate interpretation. **[inference]** [Azure ND H200 v5 specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nd-h200-v5-series)

### 2.3 Google A3: TCPX/TCPXO GPUDirect plugins; variant matters

Google’s current GPUDirect setup shows A3 Mega (`a3-megagpu-8g`, H100) with GPUDirect-TCPXO (RDMA-like/offloaded stack). It shows A3 High and A3 Edge (`a3-highgpu-8g`, `a3-edgegpu-8g`, H100) with GPUDirect-TCPX (optimized guest TCP). These stacks are neither AWS EFA nor conventional `NET/IB`. The NCCL plugin and its initialization log are the proof point. Google’s documented network maxima are up to 1,800 Gbps, an advertised ceiling, not a certification result. **[observed]** [Google GPUDirect setup](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)

The topology is different: A3 Mega uses eight data networks/interfaces plus management. High/Edge use four data networks plus management. Google’s setup uses MTU 8244. The page shows a large-MTU recommendation. The page shows NUMA alignment of High/Edge NICs to GPU pairs.

The documented test runs `all_gather_perf` through a wrapper across two VMs. One example is `/scripts/run-allgather.sh 8 eth1,eth2,eth3,eth4 1M 512M 2`. Its run time is about two minutes. The log line `NCCL INFO NET/GPUDirectTCPX ver. 3.1.1.` shows successful TCPX initialization. **[observed]** [Google GPUDirect setup](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)

The same page’s Mega instructions show sample RxDM image `v1.0.21` and plugin image `v1.0.15`. These are examples on a mutable “latest” documentation page, not a durable compatibility promise. Keep actual image digests, NCCL/plugin versions, driver, kernel, and NIC mapping in rack-bench artifacts. Do not put those GCP version pins onto GB300. **[observed/inference]** [Google GPUDirect setup](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)

A separate GKE guide shows GPUDirect-TCPX/TCPXO for specific machine types only. The guide shows no support for MIG, time-sharing, MPS, or NCCL FastSocket. It shows no support for partial GPU use or multiple pods sharing the node. Those are product-specific constraints, not general NCCL laws. Check the certification against its target deployment mode. **[observed]** [GKE GPUDirect bandwidth guide](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/gpu-bandwidth-gpudirect-tcpx)

## 3. Evidence ladder: isolate transport before NCCL tuning

1. **Check inventory and rail identity.** Keep records of NIC PCI BDF, firmware, driver/OFED or rdma-core, and link state/speed. Keep records of port errors, NUMA/GPU locality, interface-to-rail mapping, and expected topology. A line-rate readout is a denominator, never a measured PASS. **[inference]** [rack-bench README](../../README.md#L170-L241); [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)
2. **Check transport discovery and GDR prerequisites.** For EFA, run `fi_info -p efa -t FI_EP_RDM`. Check that NCCL logs show `NET/OFI` and `efa`. For IB/RoCE, check RDMA devices, link state, and NCCL’s selected `NET/IB` transport. Check the GPU peer-memory/DMABUF path and topology. NVIDIA shows `nvidia-peermem`, compatible drivers/devices, and GPU/NIC topology as relevant GDR conditions. **[observed]** [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [NVIDIA GPU troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/gpu_troubleshooting.html)
3. **Run point-to-point RDMA separately from collectives.** For verbs IB/RoCE, run `ib_write_bw`/`ib_read_bw` and latency tests per HCA/rail. These tests show link/PCIe/rail issues without NCCL algorithm confounders. EFA uses SRD with extended verbs support; perftest may run only with explicit EFA/SRD-mode support in the installed build. Do not use a conventional RC verbs recipe as valid for EFA. Check the device and transport mode in that build and use the AWS/EFA documented method **[observed/inference]** [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [AWS re:Invent EFA transport slides](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/events/approved/reinvent-2025/reinvent/2024/slides/cmp/CMP335_Drilling-down-into-performance-for-distributed-training.pdf). Run pair tests in both directions; keep raw command, HCA, message size, GID/MTU, and counter deltas **[inference]** [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html); [rack-bench README](../../README.md#L327-L337)
4. **Run workload collectives and check logs**. `nccl-tests` all-reduce/all-gather/reduce-scatter/all-to-all runs across tiny through large payloads show latency, collective efficiency, algorithm/protocol thresholds, and scale behavior. Check intended plugin/transport and selected network interfaces in the logs. A complete run over sockets is not a PASS for an RDMA fabric. **[inference]** [NVIDIA nccl-tests](https://github.com/NVIDIA/nccl-tests); [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Google GPUDirect setup](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)
5. **Use correct normalization.** Keep NCCL `algbw` and `busbw` separate; `algbw` is application algorithm throughput. `busbw` uses normalized collective data movement; it is the better comparison to effective fabric capacity. Check it against a declared, topology-aware denominator: the aggregate bandwidth actually available to ranks. The denominator is not the sum of every port when the topology cannot use them all. Show percentage and raw GB/s. Do not use vendor advertised aggregate or a single cloud blog’s percentage as a universal gate **[inference]** [NVIDIA nccl-tests performance notes](https://github.com/NVIDIA/nccl-tests); [rack-bench README](../../README.md#L327-L337)

## 4. NCCL controls: evidence, versioning, and restraint

`NCCL_DEBUG=INFO` is a high-value diagnostic for selected transport, plugin, interface, rank mapping, and fallback. Use it in a bounded diagnostic run and in archived logs. Verbose logging can make timing perturbations. Keep exact NCCL, CUDA, driver, MPI, plugin, and fabric driver versions alongside results.

The current AWS example makes an NCCL `v2.30.4-1` build. The troubleshooting index shows 2.32.3; its linked networking subpage shows 2.31.2. Keep each source page version separate; do not use them as one release. These are source snapshots. They are not a mix recommendation or a promise of the newest compatible GB300 stack. **[observed/inference]** [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [NVIDIA troubleshooting index (2.32.3)](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html); [networking subpage (2.31.2)](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

For ordinary verbs IB/RoCE, several variables can make path selection and GDR isolation easier. Examples: `NCCL_IB_HCA` (device selection), `NCCL_IB_GID_INDEX` (RoCE GID selection), `NCCL_SOCKET_IFNAME`, and `NCCL_NET_GDR_LEVEL`. Values and semantics are NCCL-version-sensitive; check the version-matched environment-variable reference before value pinning. Do not use global HCA/GID/GDR values just because a blog shows them. First check the default-selected path; then use one-variable A/B diagnostics. **[inference]** [NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html); [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html)

AWS EFA uses its own control namespace: `FI_EFA_USE_DEVICE_RDMA=1` in AWS’s example. Libfabric `FI_*` controls are not aliases for `NCCL_IB_*`. GCP TCPX/TCPXO uses Google plugin binaries and wrapper/runtime setup, not verbs tuning. **[observed]** [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Google GPUDirect setup](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)

Do not use tuning flags as certification defaults. Forced `NCCL_ALGO`, `NCCL_PROTO`, channel counts, PXN, or SHARP can make auto-selection/topology errors invisible. They or their semantics may be deprecated or different in later releases.

Keep an untuned baseline first; then run diagnostic A/B tests with the exact version. Remove overrides for the acceptance result; keep them only for an intentionally pinned production configuration. NVIDIA’s troubleshooting structure explicitly puts basic diagnostics before tuning. **[inference]** [NVIDIA NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html); [NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html)

No inspected primary hyperscaler source shows a validated GB300-specific `NCCL_IB_QPS_PER_CONNECTION`, ECN/PFC thresholds, adaptive-routing settings, or SHARP acceptance recipe. Keep those as fabric-vendor/controller configuration and telemetry tasks, not guessed NCCL knobs. Check current NCCL configuration and legacy/deprecated controls against the pinned NCCL release. This evidence set shows no complete deprecation table. **[inference]** [NVIDIA NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html); [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 5. Fault localization matrix

| Observation | First diagnosis | Evidence / interpretation |
|---|---|---|
| NCCL makes a complete run but uses `NET/Socket` instead of the intended RDMA/plugin | Wrong/missing interface, device, plugin/library path, or policy/placement; use the transport-fallback class, not fabric PASS | Azure troubleshooting makes this guidance: use `NCCL_DEBUG=INFO`, OFED checks, and `ibstat`. AWS makes explicit `NET/OFI ... efa` provider evidence mandatory. **[observed]** [Azure troubleshooting](https://techcommunity.microsoft.com/blog/startupsatmicrosoftblog/your-h100s-on-azure-wont-do-distributed-training-heres-probably-why-/4537502); [AWS guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html) |
| Per-rail RDMA rates show material differences | Port/link/optic, PCIe locality, wrong HCA binding, rail mapping, or asymmetric route/counter errors; run both directions and check per-port deltas | Per-rail pairing is a diagnostic design recommendation, not a cloud-published universal threshold. **[inference]** [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html) |
| RDMA point-to-point healthy; NCCL collective low | Rankfile/GPU-NIC locality, plugin selection, algorithm/protocol, shared rail contention, collective scaling or CPU/progress bottleneck | Keep transport and collective layers separate; keep per-message-size curves. **[inference]** [NVIDIA NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html) |
| One message-size band or one collective alone shows degradation | Algorithm/protocol transition, latency floor, rendezvous, rail imbalance, or congestion; check allreduce/allgather/alltoall and logs | The rack-bench README explicitly shows plans for 8 B–16 GB sweeps and monotonicity diagnostics. That monotonicity is a heuristic, not a physical law (algorithm transitions can make steps). **[observed/inference]** [rack-bench README](../../README.md#L327-L337) |
| Retries/timeouts/errors or throughput collapse under concurrency | Link/fabric errors, congestion, loss, ECN/PFC pause or buffer behavior; keep before/after host and switch counters | Host counters alone cannot show switch queue congestion, ECN marking, PFC storms, or route/adaptive-routing choices. Use switch/UFM/vendor telemetry for those. **[inference]** [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html) |
| Hang rather than clean failure | MPI/bootstrap/control-plane reachability, incompatible network selection, blocked ports, bad peer setup, runtime/shared-memory issue; bounded timeout and per-rank logs | AWS EFA self-referencing security-group rules are mandatory; NCCL docs put runtime/MPI and networking troubleshooting in separate sections. **[observed]** [AWS guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html) |

## 6. Fabric features and what a short test can actually establish

**ECN/PFC/congestion:** check configured intent and counter deltas under a controlled concurrent test. On RoCE, host-side counters can show symptoms. But switch telemetry/config makes the switch-side check possible: marking thresholds, pause propagation, headroom, queue drops, pause storms. A quiet counter during a brief unloaded run does not show congestion safety. **[inference]** [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

**Adaptive routing and SHARP:** check operational availability through the installed fabric manager/plugin and logs. Run the enabled/disabled comparison only as a diagnostic, when supported. The examined hyperscaler sources show no sufficient detail for these: portable SHARP activation command, adaptive-routing proof, acceptance threshold. Use the deployed fabric vendor as the source for switch/controller evidence. **[inference]** [NVIDIA NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html)

**Failures/asymmetry:** a paired bidirectional rail test plus error/retry counter deltas shows static asymmetry and some bad links. Link flap, failed-rail reroute, job recovery, and convergence use controlled fault injection. Put them in a separately authorized reliability test or smoke phase. Do not put them in a destructive default bench. **[inference]** [rack-bench README](../../README.md#L327-L337)

**Scale:** AWS’s example uses 8 GPUs on one instance. Google’s documented example uses two VMs, each with eight H100s, and a short all-gather. Azure H200 shows the topology and scale potential, but the cited product page is not a benchmark runbook. These examples show that hyperscalers use small representative tests for setup and larger-scale context. They do not show full 18-tray NVL72 certification from an 8-rank run. **[observed/inference]** [AWS guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Google guide](https://docs.cloud.google.com/compute/docs/gpus/gpudirect); [Azure specs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nd-h200-v5-series)

## 7. Transfer to rack-bench: realistic two-hour evidence plan

The project README already shows the right broad coverage. It shows per-port link checks, point-to-point RDMA perftest, and TCP/RDMA pair bandwidth. It shows an intra-rack matrix sample, small-message latency, and packet/error counter checks. It shows NCCL allreduce/allgather/alltoall from 8 B to 16 GB through MPI and `torch.distributed`. It shows normalized bus bandwidth, plus an N-node topology-aware run. **[observed]** [rack-bench README](../../README.md#L327-L337)

A practical sequencing proposal (time is an engineering budget, not a source-prescribed provider recipe):

1. **0–10 min, gate and snapshot:** check that all expected 18 trays/ranks are present. Keep manifest versions, HCA/port state, topology/rail mapping, counters, NCCL env and plugin availability. Use fail-closed logic for a missing rank or device. Do not put a PASS label on a partial rack. **[inference]** [rack-bench README](../../README.md#L327-L337)
2. **10–30 min, per-rail transport:** run bidirectional short RDMA bandwidth/latency tests for each expected rail. Or run a provider-appropriate Libfabric test. Keep per-port counter snapshots. Do not use aggregate multi-rail bandwidth as evidence for each rail. **[inference]** [NVIDIA network troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)
3. **30–45 min, sparse pair matrix:** use topology-informed pairs: same rail, adjacent trays, cross-rack/leaf if included. Use them to show miswires and outliers. Do not run all 153 tray pairs if that uses the whole window. Keep directed results to show asymmetry. **[inference]** [rack-bench README](../../README.md#L327-L337)
4. **45–100 min, collective sweep:** run full expected GPU ranks for a curated log-size set spanning 8 B–16 GB. Use allreduce/allgather/alltoall collectives. Put both MPI and `torch.distributed` paths in the sweep only if both are production-supported. Keep per-size latency/algbw/busbw, selected transports, algorithm/protocol, rank map, and failures. Use fixed bounded iterations and watchdogs. **[inference]** [rack-bench README](../../README.md#L327-L337); [NVIDIA nccl-tests](https://github.com/NVIDIA/nccl-tests)
5. **100–115 min, loaded concurrency and counter delta:** run overlapped representative collectives/rail traffic only in controlled mode. Check host counters and switch/UFM telemetry if credentials are present. This can show gross contention/ECN/PFC symptoms. But it is not burn-in. **[inference]** [rack-bench README](../../README.md#L327-L337)
6. **115–120 min, repeat anomalous checks and report:** make PASS/FAIL/SKIP classes with raw evidence, versions, and coverage. Do not make a missing switch data source into “no congestion.” **[inference]** [rack-bench README](../../README.md#L327-L337)

Use explicit gates from the exact rack profile and measured baseline, not generic “98% line rate.”

Put effective aggregate rail capacity, oversubscription, and expected collective scaling in the profile. Keep raw as well as normalized numbers. Use tolerance bands, and run outlier repeats.

Use the README’s “untuned RoCE near 60%, tuned near 98%” as a motivating heuristic only. It is not a defensible universal pass/fail threshold without topology, workload, NCCL version, and measurement-method evidence. **[inference]** [rack-bench README](../../README.md#L327-L337)

## 8. Telemetry boundary and artifacts

Keep this minimum host-side evidence: NCCL logs (`NCCL_DEBUG=INFO` for diagnosis) and per-rank command/env/version. Keep a rank-to-GPU/HCA map and NIC port link/error/retry counters before/after. Keep RDMA test outputs, per-collective-size data, timeouts, and exit codes. Keep GDR path/module evidence in the set. Keep module presence separate from actual data-path use. **[inference]** [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html); [AWS EFA guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html)

Where accessible, put switch-port utilization, discards, ECN marks, and PFC pause counters into the evidence. Also put queue occupancy, link flaps, adaptive-routing state, and SHARP job/controller evidence into the record. Show inaccessible provider-side telemetry as a scope limitation/SKIP, not as zero errors. Host counters show only host-observable effects. They cannot show every switch queue or fabric-wide congestion absence. **[inference]** [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 9. Conclusions for the exact question

Hyperscalers check GPU fabrics this way: they run NCCL tests across actual placed ranks. They check that the intended transport is active, not link-rate claims alone. AWS shows EFA through Libfabric provider selection. Azure’s ND H100/H200 path is conventional ConnectX InfiniBand/GPUDirect RDMA. Google’s A3 Mega vs High/Edge paths use distinct TCPXO vs TCPX plugin stacks and different interface counts. **[observed]** [AWS guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Azure H200 specs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nd-h200-v5-series); [Google GPUDirect guide](https://docs.cloud.google.com/compute/docs/gpus/gpudirect)

For GB300 certification, use the strongest two-hour diagnostic: a layered one. Start with per-rail transport and directional checks; use topology-aware pair sampling next. Then run full-rank, multi-collective NCCL sweeps with correct bus-bandwidth normalization and versioned logs.

Put a bounded loaded run last, checked against host and switch counters. Show coverage gaps explicitly: adaptive routing, SHARP, queue-level congestion, full-fabric scale, and failure recovery. Use management-plane access and/or smoke tests for these. **[inference]** [rack-bench README](../../README.md#L327-L337); [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html)

## Interim coverage caveats

- Public hyperscaler material is deployment-specific. It does not show their internal acceptance thresholds, full-scale diagnostic matrices, or all switch-side telemetry/runbooks.
- The cited Azure community item is not an authoritative Microsoft runbook. Official H200 specs show topology, not a reproducible NCCL acceptance command. Check public ND HNDR/H100/H200 SKU claims against the exact deployed SKU and region.
- Google’s GPUDirect page shows both TCPX and TCPXO setup. But sample images and plugin versions are mutable. Check digest/version compatibility at execution time. A3 naming does not show an identical networking stack across all variants.
- The inspected sources show no portable commands/thresholds for SHARP, adaptive routing, ECN/PFC tuning, or QP entropy. They show no complete deprecated NCCL-variable list. Use the exact switch-vendor/UFM and pinned-NCCL documentation before hard-gate implementation.
- No examined source shows a universal busbw-to-line-rate pass percentage for GB300 NVL72. Make the denominator and thresholds from the rack’s verified topology and supplier acceptance evidence. Then check them empirically.

## 10. Azure ND HNDR/H100 official evidence

Azure’s official ND H100 v5 SKU is `Standard_ND96isr_H100_v5`. The SKU shows 96 vCPUs, 1,900 GiB memory, eight H100 80-GB GPUs, and eight network interfaces. Microsoft shows one dedicated 400-Gbps Quantum-2 ConnectX-7 InfiniBand connection per GPU and 3.2 Tb/s interconnect per VM.

It shows GPUDirect RDMA and automatic inter-VM IB configuration between VMs in the same VM scale set. This official SKU evidence is complementary to the H200 entry above. Keep “HNDR”/H100 separate from H200 SKU specifics. **[observed]** [Microsoft ND H100 v5 SKU page](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series)

Microsoft’s official Azure ML NCCL test sample shows a diagnostic job. The job runs NCCL correctness/performance tests. The job keeps standard diagnostics (including `nvcc`, `lspci`). It shows result columns: latency, `algbw`, `busbw`, and error. It is an official sample/run artifact, not a SKU-specific guaranteed performance threshold or universal bare-metal runbook.

Use this sample with the ND H100 SKU page for practical verification. Start the exact SKU group in a common VM scale set. Check IB/OFED and topology. Run the full-rank NCCL test. Check transport logs and keep errors/results. **[observed/inference]** [Microsoft Learn NCCL test sample](https://learn.microsoft.com/en-us/samples/azure/azureml-examples/run-nccl-tests-on-gpu-to-check-performance-and-configuration); [ND H100 v5 SKU](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series)

## 11. Google A3 Ultra, GPUDirect RDMA, gIB and Tier_1

The A3 family is not one networking stack. Google shows A3 Ultra (`a3-ultragpu-8g`, H200) as GPUDirect RDMA over RoCE. It uses eight ConnectX-7 MRDMA virtual functions and 3.2 Tb/s GPU-to-GPU traffic. The listed aggregate maximum is 3.6 Tb/s, including general networking. This is different from A3 Mega (H100, TCPXO) and A3 High/Edge (H100, TCPX).

Use the earlier “A3 stacks are TCPX/TCPXO” statement only for those H100 variants. Do not use it for A3 Ultra. **[observed]** [Google GPU networking overview](https://docs.cloud.google.com/compute/docs/gpus/gpu-network-bandwidth); [Google A3 Ultra/A4 machine types](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines)

Google’s A3 Ultra/A4 create-instance instructions make two regular VPC networks mandatory for gVNIC general-purpose host communication. They also make one RoCE-profile VPC network with eight subnets mandatory, one per CX-7 NIC. Use MRDMA for GPU-communication interfaces. Check this topology and transport as an RDMA fabric, not as a TCPX plugin.

The official NCCL/gIB test guidance uses `NCCL_NET=gIB`. It uses `/usr/local/gib/scripts/set_nccl_env.sh` (the install guide also shows the environment script). Logs and prescribed gIB diagnostics are the validation path. **[observed]** [Google A3 Ultra/A4 create VM](https://docs.cloud.google.com/compute/docs/gpus/create-gpu-vm-a3u-a4); [Run NCCL on GKE A4/A3 Ultra](https://docs.cloud.google.com/ai-hypercomputer/docs/nccl/test-gke-custom); [Install gIB NCCL](https://docs.cloud.google.com/ai-hypercomputer/docs/nccl/install-nccl)

Google’s documentation shows NCCL/gIB as a Google-enhanced NCCL stack for A3 Ultra/A4, with version compatibility tables. For example, the release-notes search result shows A3 Ultra bundled NCCL 2.30.4. It shows minimum driver 550.90.07 for a specific diagnostic image version. That table is image-version-specific. Keep the actual gIB image digest and compatibility row for every certification run. Do not keep only “latest.” **[observed/inference]** [NCCL/gIB x86 release notes](https://docs.cloud.google.com/ai-hypercomputer/docs/nccl/release-notes-x86)

**Tier_1 is a different configuration dimension**. Google Compute Engine’s Tier_1 setting (`--network-performance-configs=total-egress-bandwidth-tier=TIER_1`) uses a network-bandwidth performance tier for supported VM types; it makes gVNIC mandatory. By itself it does not put RoCE, an MRDMA interface, or GPUDirect RDMA in place.

It makes no RDMA-path guarantee and does not show NCCL use of an RDMA path. The RoCE VPC network/profile and MRDMA NICs put A3 Ultra’s RDMA configuration in place separately. Show Tier_1 and RDMA provisioning as separate facts; only active NCCL/gIB transport and measured collective results make GPU-fabric evidence. **[observed/inference]** [Google Tier_1 configuration](https://docs.cloud.google.com/compute/docs/networking/configure-vm-with-high-bandwidth-configuration); [Google GPU networking](https://docs.cloud.google.com/compute/docs/gpus/gpu-network-bandwidth); [Google A3 Ultra setup](https://docs.cloud.google.com/compute/docs/gpus/create-gpu-vm-a3u-a4)

## 12. RoCE GID selection: version guidance vs provider exception

The NVIDIA networking troubleshooting page shows explicit guidance: NCCL 2.21 and later make the GID-index selection dynamic. For those versions, keep `NCCL_IB_GID_INDEX` unset. Older NCCL versions may make this procedure necessary: check the RoCEv2 GID with `show_gids` and use the corresponding index. The NVIDIA NCCL 2.21 environment-variable documentation also shows dynamic-selection filters: `NCCL_IB_ADDR_FAMILY`, `NCCL_IB_ADDR_RANGE`, and `NCCL_IB_ROCE_VERSION_NUM`. **[observed]** [NVIDIA networking troubleshooting, page labeled NCCL 2.31.2](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html); [NCCL 2.21.5 environment variables](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2215/user-guide/docs/env.html)

This guidance is in conflict with a documented, provider-specific GB300 observation. SemiAnalysis shows a Google GB300 incident: built-in NCCL auto-selection of an unroutable link-local GID, with a hang. The `NCCL_IB_GID_INDEX=3` setting makes that tested setup work. That finding shows no invalidation of NCCL’s general 2.21+ default guidance. It shows no justification for index-3 forcing on all RoCE fabrics.

Keep forced GID as a pinned provider/image/NCCL-specific workaround. First check version, `show_gids`, route/address state, and logs. Run a default-selection test. Only then use the documented provider exception. Put it in the certification profile. **[observed/inference]** [SemiAnalysis ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard); [NVIDIA networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 13. Precise local evidence references

Rack-bench’s local network benchmark contract is in [README.md](../../README.md#L327-L337), lines 327–337. It shows perftest, pair bandwidth, latency/counters, collective sweep, normalization, and N-node run. Its network inventory and NCCL/GDR/topology audit contract is in [README.md](../../README.md#L170-L241), lines 170–241. The README shows planned checks. It is a local design spec. It is not independent evidence of implemented tests **[observed]** [Local README](../../README.md#L327-L337)

- EFA is SRD-based with extended verbs support. But `perftest` use in the intended EFA mode is dependent on the installed build/provider and command support. Do not use conventional RC `ib_write_bw` options without a check. Check `--help`, provider support, and AWS-specific instructions on the target image.

## 14. A4X Max / GB300 directly relevant comparison

Google shows A4X Max with GB300 Ultra Superchips as an 18-instance, 72-GPU NVLink subblock. Scale-out RoCE networking runs between those subblocks. Its network design uses four 800-Gbps ConnectX-8 NICs, shown as eight physical functions (PFs). It uses two 400-Gbps rails per NIC.

These are published topology and bandwidth specifications. They are not measured throughput or line-rate-achievement proof for any deployed rack. The architecture is useful comparison evidence for GB300-class rack scale. But it does not show matching cabling, routing, balance, or NCCL performance in a rack-bench installation. **[observed/inference]** [Google GPU networking and monitoring](https://docs.cloud.google.com/compute/docs/gpus/gpu-network-bandwidth)

Google shows an observability warning. The `_phy` counters on A3 Ultra/A4 MRDMA virtual functions are visible but show no updates. Use vPort counters for those VFs. A4X Max uses PFs; the PFs show physical counters.

Counter names and interface presence alone are not telemetry validation. Check counter movement during traffic. Put a counter-layer tag (VF/vPort vs PF/physical) in the artifacts. Do not use static `_phy` values as zero-traffic or healthy-link evidence. **[observed/inference]** [Google GPU networking and monitoring](https://docs.cloud.google.com/compute/docs/gpus/gpu-network-bandwidth)

The §§10–14 addenda make the §§2 and 9 Azure and Google A3 coverage wider. They also make the narrower earlier coverage superseded. Specifically, use the ND H100/HNDR evidence as a supplement to the H200 entry. A3 Ultra is GPUDirect RDMA/RoCE/gIB rather than TCPX/TCPXO. A4X Max is the directly relevant GB300-scale comparator. **[observed]** [Azure ND H100 SKU](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series); [Google GPU networking and monitoring](https://docs.cloud.google.com/compute/docs/gpus/gpu-network-bandwidth)

## Gaps

- Azure official sources show ND H100/H200 topology and an official NCCL sample. But the reviewed sources show no authoritative, current ND HNDR end-to-end fabric-troubleshooting runbook with acceptance thresholds and counter interpretation.
- Google documentation shows A3 Ultra RoCE/MRDMA/gIB as distinct from H100 TCPX/TCPXO and Tier_1. But exact installed hardware/firmware diagnostics and provider-side switch telemetry are still deployment-dependent.
- EFA is SRD-based with extended verbs support. But `perftest` use in the intended EFA mode is dependent on the installed build/provider and command support. Do not use conventional RC `ib_write_bw` options without a check. Check `--help`, provider support, and AWS-specific instructions on the target image.
