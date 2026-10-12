# Books and canonical references for east-west fabric diagnosis

Research date: 2026-10-11. All claims below use a source URL.

Scope: N07 only. Which references show the best fit for east-west fabric-quality diagnosis in a two-hour GB300 NVL72-class (18-tray) rack certification?

Use books and primary technical references as the focus, not implementation of the suite. The needed evidence: 8 B–16 GB NCCL/RCCL collectives, per-rail RDMA bandwidth/latency, and line-rate normalization. Also: dead or asymmetric rails, topology/routing, congestion (ECN/PFC), errors/retries, and SHARP. North-south internet/storage: out of scope. The sibling canon exemplar: `.../research-internet/.lavish/internet-research/books.md`; project `README.md`: read-only.

## 1. Ranked canon: books, honestly scoped

Few books check modern GPU RDMA fabrics directly. The highest-value “canon” uses a short systems-performance book plus current vendor/tool documentation. Books make a reasoning source. They do not make a replacement for firmware-specific counter definitions, switch telemetry, or contemporary NCCL guidance. [inference] [NCCL networking troubleshooting, version 2.31.2](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

| Rank | Reference | Verdict | What it supports / does not |
|---|---|---|---|
| 1 | Brendan Gregg, *Systems Performance: Enterprise and the Cloud*, 2e (2020), especially chs. 2, 10, 12 | Must-read book | USE (utilization, saturation, errors), network stack and interfaces, experiment discipline, saturation/outlier interpretation. Not a RoCE/IB or NCCL manual. [observed] [Book/TOC](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) |
| 2 | Kurose & Ross, *Computer Networking: A Top-Down Approach*, 8e (2021), ch. 1 and transport/network foundations | Skim / fundamentals | Delay, loss, throughput, routing and queueing vocabulary. Useful for reasoning about bottlenecks, not GPU RDMA diagnosis or current switch behavior. Do not mistake its TCP framing for RDMA transport expertise. [observed] [Pearson](https://www.pearson.com/en-us/subject-catalog/p/computer-networking/P200000003334/9780135928615) |
| 3 | Raj Jain, *The Art of Computer Systems Performance Analysis* (1991), measurement/statistics chapters | Reference, not fabric guide | Experimental design, variance, comparison and reporting discipline for deciding whether rail asymmetry or collective regression is real. Old examples; the statistics still make useful tools. [observed] [Author book page](https://www.cse.wustl.edu/~jain/books/perfbook.htm) |

**Do not rank TCP/IP Illustrated as a core fabric book.** Supplied ISBN 020163354X shows *Volume 2: The Implementation*. Authors: Gary R. Wright and W. Richard Stevens. Its publisher TOC and preface show 4.4BSD-Lite code. [observed] [Publisher TOC and preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542) [Source note](oreilly/tcpip-illustrated.md)

 Its TCP retransmission, congestion, and packet-capture concepts can make management-plane/TCP bootstrap-failure work easier. But NCCL payload uses verbs/RDMA paths. TCP congestion-control explanations do not check IB/RoCE data-plane quality. Likewise, Kurose & Ross makes introductory conceptual background, not a fabric-docs substitute. [inference] [NCCL networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 2. Higher-ranked than books: current primary operational canon

1. **NCCL Networking Troubleshooting (NCCL 2.31.2 documentation)** — best concise diagnostic sequence. Check `ibstat`/`ibstatus` for active state, physical link, correct link layer, and expected rate. Then check `ib_write_bw`, `ib_write_lat`, RDMA stats, and port counters. Use `ibdiagnet` for fabric-wide topology/routing when available; for RoCE, check NIC and switch PFC/ECN/CNP/drop telemetry. It shows an explicit note: `NCCL_IB_GID_INDEX` behavior changed in NCCL 2.21, with dynamic GID selection in 2.21+. Do not blindly apply older instructions [observed] [NVIDIA NCCL networking guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
2. **NCCL diagnostics, tuning, logging, and environment-variable docs** — use actual NCCL logs and version-matched configuration. Do not assume the intended HCA/rail or transport selection. Force/debug variables can make transport changes. Do not let them silently contaminate the certified default result. The docs show a warning: `NCCL_IB_DISABLE=1` disables verbs and can make NCCL fall back to sockets. Such a run does not make an RDMA pass [observed] [NCCL troubleshooting index](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html), [environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html).
3. **Vendor fabric manuals (NVIDIA/Mellanox plus the actual switch vendor and firmware release)** — authoritative references. Coverage: counter semantics, QoS/priority mapping, PFC watchdogs, ECN thresholds, adaptive routing, and SHARP configuration. No portable universal command or counter set. Firmware, ASIC, OS, and management plane make the visibility rules. The NVIDIA ibdiagnet manual shows topology/fabric checks and SHARP counter options. Use the versioned manual that matches the deployed tool [observed] [ibdiagnet 2.11 manual PDF](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf).
4. **Open tool docs/source: `perftest`, `infiniband-diags`, `rdma-core`** — essential for flags and limitations. Keep the exact installed version pinned. `perfquery` runs queries for PMA basic/extended counters and optional detail groups. PMA/device support puts limits on its option availability and counter exposure [observed] [perfquery(8)](https://manpages.ubuntu.com/manpages/jammy/man8/perfquery.8.html).

## 3. Tools: practical checks and interpretation traps

### Per-rail bandwidth and latency

NCCL documentation shows a recommendation: the server/client pattern `ib_write_bw -d <device> -a` with matching client invocation. For a rack certification, use an explicit HCA/port/rail binding for each test. Keep both endpoints, direction, QP count, message geometry, tool version, CPU/NUMA placement, and GPU-vs-host memory mode on record.

Put `ib_read_bw` in the plan as well; WRITE alone does not make a complete check. Run paired reverse-direction checks to make asymmetric paths visible. A microbenchmark checks the transfer capability of a configured endpoint pair and RDMA verb. It does not make an equivalent to collective performance or concurrent rack-scale saturation [observed] [NCCL low-level tests](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html), [perftest README](https://github.com/linux-rdma/perftest).

The current upstream `perftest` README shows `-D/--duration=<sec>`, `-f/--margin=<sec>`, `-b/--bidirectional`, `-O/--dualport`, `-q/--qp`, `-d/--ib-dev`, `-i/--ib-port`, `-x/--gid-index`, and `--use_cuda=<gpu_index>` (for supported builds). Send the same options to server and client. Use the same perftest version on both peers. CUDA/DMA-BUF options keep build, CUDA, kernel, driver, and adapter dependence. Check the local `ib_write_bw --help`. Do not infer GB300 support from an older distro man page [observed] [perftest README](https://github.com/linux-rdma/perftest).

The README shows fixed-duration use for bandwidth tests and min/median/max latency reporting. It also shows a caution: latency values use RTT divided by two, so they can misrepresent asymmetric paths. The README puts `-a` sizes from 2 through 2^23. Version-specific implementations can show differences. In a two-hour window, use short fixed-duration, explicitly selected sizes/QPs for each rail. Do not use a broad blind sweep as the only evidence [observed] [perftest methodology](https://github.com/linux-rdma/perftest) [inference].

### Counters, units, deltas, rollover

- InfiniBand `perfquery` runs PMA counter queries; `PortXmitData` and `PortRcvData` show data octets divided by four. The spec text shows “Total number of data octets, divided by 4” (Volume 1, §16.1.3.5, Table 228, printed page 966, `PortXmitData`; `PortRcvData` follows). The same section shows a separate 32-bit field-width listing and counters “instead of overflowing, ... shall stop at all ones” (page 963). Optional Table 241, `PortCountersExtended`, printed pages 983–984, shows `PortXmitData`/`PortRcvData` 64-bit fields with semantics identical to the base fields. Four octets make the data unit, not the counter width; base saturation and extended width make distinct cases. Make delta conversion as `count × 4` octets; check the attribute the local tool/device exposes [observed] [IBTA InfiniBand Architecture Specification v1.2.1, §16.1.3.5, Table 228 p. 966 and §16.1.4.11, Table 241 pp. 983–984; quoted text verified from full PDF](https://www.afs.enea.it/asantoro/V1r1_2_1.Release_12062007.pdf) [perfquery(8), extended attribute optional](https://manpages.ubuntu.com/manpages/jammy/man8/perfquery.8.html).
- Put before/after counter samples in place and run delta computations, preferably at several short intervals. A nonzero historical error count does not show a current fault. Growth during a controlled load makes evidence. Counter reset makes a disruptive/destructive operation on shared observability. Do not use it without approval. Do not clear fabric-wide state during certification [inference] [NCCL counter guidance](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
- Counter saturation/rollover makes a real effect. Red Hat documentation shows older mlx4/mlx5 systems where `port_xmit_data`, `port_rcv_data`, and packet counters stop at roughly 4.3 billion. The symptom and remedy keep stack/version specificity. Use extended counters where supported, with frequent-enough sampling to bound wrap. Check for implausible negative/reset deltas. Do not present this historical issue as universal behavior on GB300 [observed] [Red Hat KB](https://access.redhat.com/solutions/1438663).
- RoCE shows multiple layers: Ethernet NIC counters (`ethtool -S`), RDMA counters (`rdma statistic`/sysfs), and switch per-priority queue/PFC/ECN counters. NVIDIA shows a recommendation: check port errors/drops/pause/PFC and congestion indicators. Growing `rnr_nak_retry_err`, `packet_seq_err`, `implied_nak_seq_err`, or `local_ack_timeout_err` can show transport trouble. But counter names/meaning keep variation across kernel/driver. Keep exact names plus driver/firmware version [observed] [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
- Oracle’s 2022 counter explainer shows `np_ecn_marked_roce_packets`, `np_cnp_sent`, `rp_cnp_handled`, and `rp_cnp_ignored`. ECN-marking and CNP/reaction activity make valuable congestion evidence. These counters keep implementation and kernel/OFED dependence. Increasing counts alone do not make a failure (they can show functioning congestion response). Check their deltas against PFC pause time, queue drops, latency tails, and throughput [observed] [Oracle Linux](https://blogs.oracle.com/linux/rocev2-congestion-counters-explained).

### Capture, privilege and topology limits

`ibdump` runs as an optional troubleshooting capture, not a required pass/fail instrument. Its upstream README shows a first warning: it can drop bursts beyond 4096 packets without reporting packet loss. It also shows possible mishandling of outbound retransmitted/multicast packets. And it shows possible capture stops on the same port as the Subnet Manager. It keeps adapter/firmware-build compatibility limits. Notably, builds without FW tools show no ConnectX-4+ support.

The README shows end-2026 removal for the standalone repository. It sends users to the `mstflint` project for `ibdump`. A clean capture therefore does not show a lossless fabric. Use counters and workload results as primary evidence. Check the replacement binary/build locally [observed] [Mellanox ibdump README and migration notice](https://github.com/Mellanox/ibdump) [mstflint](https://github.com/Mellanox/mstflint).

Host-side unprivileged RDMA verbs may run when device nodes and ulimits permit. But permissions put inventory and counter access in different places. `perfquery`, `ibdiagnet`, switch telemetry, and firmware interfaces often make elevated privileges or Subnet Manager/management access a requirement.

NCCL documentation shows a specific note: `ibdiagnet` fabric-wide diagnostics usually use SM access as a requirement. Pinned-memory registration failures may make unlimited memlock a requirement (check `ulimit -l`). With absent access, show the diagnostic as unavailable/limited—not PASS [observed] [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).

## 4. Applying the canon to the two-hour rack window

Use this practical evidence sequence. (1) Keep stack versions and selected HCA/port mapping on record. (2) Put read-only link state/rates and baseline error counters per rail in a capture. (3) Run a short, explicit QP sanity test and `ib_write_bw`/`ib_read_bw` in each direction. Check per-rail rates against physical line rate after protocol overhead.

(4) Run the prescribed NCCL all-reduce/all-gather/all-to-all sweep over 8 B–16 GB. Keep algorithm bandwidth and bus bandwidth plus actual NCCL transport/plugin logs. (5) Run counter sampling during and after the collective. Include per-rail errors/retries, ECN/CNP/PFC, and switch queue drops where available. (6) Put dead/slow rails, asymmetric directions, and unexpected transport fallback on the investigation list. Put a jagged message-size curve there too [inference] [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html) [local project README](../../../README.md#L327-L337).

For line-rate normalization, show the denominator type: per port, per rail, per direction, or aggregate full-duplex capacity. A 4×200 Gb/s setup does not automatically make one 800 Gb/s unidirectional stream. Topology, rail striping, and workload put all four links in use—or not. Do not label vendor theoretical rates or configured rail count as measured performance.

NCCL's algbw and busbw make distinct quantities. Keep both. Use the project's explicitly defined normalization. Do not compare unlike figures [inference] [NCCL tests performance guide](https://github.com/NVIDIA/nccl-tests).

Two hours make sufficient time for targeted diagnostics, not for a full combinatorial matrix. That matrix puts every 18-tray pair, all payloads, QP counts, verbs, directions, and congestion states in scope. Use all-rail coverage for link health and per-rail microbenchmarks, representative intra-rack pairs, then full-rack NCCL collective sweeps. A sample does not make a certificate for every pair. Show coverage and skipped pairs in the report. Keep a later smoke/burn-in phase for intermittent/thermal faults [inference] [local project README, bench network](../../../README.md#L327-L337) [local project README, smoke network and gpu-network](../../../README.md#L486-L493).

## 5. Current vendor docs and papers beat books

- **NCCL behavior, GID selection, HCA selection, plugins, logging and algorithm tuning:** use version-matched NCCL docs and source. They show superiority to any book. NCCL 2.21 made a change to dynamic RoCE GID selection. Older recipes can send readers in actively wrong directions [observed] [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
- **SHARP:** check the installed HPC-X/NVIDIA SHARP documentation and versioned `ibdiagnet` manual for enablement, aggregation topology, and counters. A successful NCCL result alone does not show SHARP selection. Logs/plugin evidence must show the actual path. Keep SHARP offload as an optional optimization. Do not infer its capacity/resource allocation from generic textbook collective theory [inference] [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf) [NCCL environment variables](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html).
- **RoCE ECN/PFC/DCQCN:** keep switch-vendor deployment guides and current NVIDIA NIC/firmware docs above textbooks. Reason: priority mapping, thresholds, counters, and congestion algorithms keep configuration and ASIC specificity. PFC can keep loss away. But pause propagation/head-of-line effects can put throughput down. Check ECN/CNP evidence against performance, not a score of “any PFC means fail.” [inference] [Oracle counter explainer](https://blogs.oracle.com/linux/rocev2-congestion-counters-explained) [Arista deployment guide](https://www.arista.com/assets/data/pdf/Arista-Broadcom-AI-Networking-Deployment-Guide.pdf)
- **Adaptive routing and routing validation:** use the exact switch/firmware management manual and fabric manager telemetry. A host endpoint test does not show the selected path or active adaptive routing. `ibdiagnet` makes topology/route consistency checks possible, subject to management-plane access [inference] [NVIDIA UFM adaptive routing](https://networking-docs.nvidia.com/ufmsdnappswum/41815/adaptive-routing) [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf).

## 6. Recommended reading order

1. Check Gregg *Systems Performance* 2e ch. 2, ch. 10, and ch. 12 for method, saturation, and benchmark hygiene [observed] [Gregg book page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html).
2. Check the current NCCL networking troubleshooting and logging/tuning pages end-to-end. Check each recommendation against the installed NCCL and plugin version [observed] [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
3. Check local `ib_write_bw --help`, `ib_read_bw --help`, `perfquery --help`, and perftest README for the exact installed binaries. Run non-destructive link checks first; keep client/server command lines matched [observed] [perftest](https://github.com/linux-rdma/perftest) [perfquery](https://manpages.ubuntu.com/manpages/jammy/man8/perfquery.8.html).
4. Check the exact switch/NIC vendor manuals for topology, counters, PFC/ECN, adaptive routing, and SHARP. Check read access before certification day [inference] [local project README, audit network telemetry](../../../README.md#L220-L239).
5. Use Kurose & Ross ch. 1 for conceptual queueing/throughput gaps. Use Jain for threshold/repeat-policy design. Do not use certification prep time to treat TCP texts as RDMA handbooks [inference] [Kurose & Ross](https://www.pearson.com/en-us/subject-catalog/p/computer-networking/P200000003334/9780135928615) [Jain](https://www.cse.wustl.edu/~jain/books/perfbook.htm).

## 7. O'Reilly supplement: optional references

[observed] The [eleven-source supplement](oreilly.md) checks edition identity, chapter evidence, access, and portable methods.
Its [source map](oreilly/research.md) keeps explicit gaps.
Catalog matches do not show subscriber access.

[inference] Keep the operational reading spine unchanged.
Current NCCL, perftest, counter specifications, and deployed vendor manuals keep first place.
The supplement puts background references on top, not certification thresholds.

| Reference | Supplement verdict | Evidence boundary |
| --- | --- | --- |
| [Shanley, InfiniBand Network Architecture, 2002](oreilly/infiniband-architecture.md) | KEEP as targeted native-InfiniBand architecture context | Indexed transport/management previews; exact link-counter chapter locations: unverified |
| [Dutt, Cloud Native Data Center Networking, 2019](oreilly/cloud-native-fabrics.md) | KEEP selectively for Ethernet architecture | Indexed Chapters 2, 11, 18; incomplete primary TOC; no established RoCE/ECN/PFC coverage |
| [Benvenuti, Understanding Linux Network Internals, 2005](oreilly/linux-network-internals.md) | Conditional host-path SKIM | Linux 2.6-era concepts, not current ABI or RDMA commands |
| [Schroder, Linux Networking Cookbook, 1e November 2007, copyright 2008](oreilly/linux-networking-cookbook.md) | Optional dated host SKIM | TOC shows Chapters 13–14 and 19; no current command validation |
| [VandenBrink 1e, ISBN 9781800202399](oreilly/linux-networking-1e.md) | SKIM indexed Chapter 3 | No verified improvement over inaccessible 2e chapters; complete chapter count unresolved |
| [VandenBrink 2e, ISBN 9781835881101](oreilly/linux-networking-2e.md) | HOLD chapter assignments | No verified 2e TOC; 2025/2026 and August/September date differences unresolved |
| [Prowse, Linux Networking - Basics and Beyond](oreilly/linux-networking-video.md) | Optional host/bootstrap SKIM | InformIT TOC verified for a separate ISBN; exact O'Reilly release/runtime/TOC match unverified |
| [Sloan, Network Troubleshooting Tools, 1e August 2001](oreilly/troubleshooting-tools.md) | SKIM diagnostic sequence; SKIP core addition | Existing internet-canon overlap; dated Ethernet/TCP/IP tools |
| [Wright/Stevens, TCP/IP Illustrated, Volume 2](oreilly/tcpip-illustrated.md) | Conditional host/bootstrap SKIM; SKIP certification reading | Publisher shows 4.4BSD-Lite implementation scope |
| [LaCroix, Mastering Linux Network Administration, 2015](oreilly/linux-administration.md) | Optional host-administration SKIM | Indexed TOC only; generic QoS does not show ECN/PFC procedures |
| [White, Modern Network Troubleshooting](oreilly/modern-troubleshooting.md) | SKIM methods, not fabric rules | Author puts January 26, 2023 forward for this ID; supplied 2025 attribution and delivered content unverified |

[inference] Use host books only when host-path evidence supports the question.
Use architecture books to define hypotheses and expected paths.
Do not turn an inferred technique into an attributed textbook prescription.
No source shows measured target-rack PASS.
[Supplement](oreilly.md) [NCCL](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## Sources

- Kept: [NCCL networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html) — NCCL 2.31.2 practical IB/RoCE checklist, version caveats, privilege/access notes.
- Kept: [NCCL troubleshooting index](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) and [NCCL env docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html) — version-sensitive behavior and transport selection.
- Kept: [perftest upstream](https://github.com/linux-rdma/perftest) — flags, benchmark methodology, version and GPU-build caveats.
- Kept: [IBTA InfiniBand Architecture Specification v1.2.1](https://www.afs.enea.it/asantoro/V1r1_2_1.Release_12062007.pdf) — primary source. Base unit/width: §16.1.3.5, Table 228 p. 966. Extended width: §16.1.4.11, Table 241 pp. 983–984. The review uses the full PDF text. Source quote: “Total number of data octets, divided by 4.” [perfquery(8)](https://manpages.ubuntu.com/manpages/jammy/man8/perfquery.8.html) — query operations and optional extended-counter attribute.
- Kept: [ibdiagnet 2.11 manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf) — fabric-wide and SHARP diagnostics.
- Kept: [Oracle RoCE counters](https://blogs.oracle.com/linux/rocev2-congestion-counters-explained) — concrete CNP/ECN counter semantics, with old-version caveat.
- Kept: [Mellanox ibdump README](https://github.com/Mellanox/ibdump) — capture failure modes and end-2026 migration notice to [mstflint](https://github.com/Mellanox/mstflint).
- Kept: [Gregg Systems Performance](https://www.brendangregg.com/systems-performance-2nd-edition-book.html), [Jain](https://www.cse.wustl.edu/~jain/books/perfbook.htm), [Kurose & Ross](https://www.pearson.com/en-us/subject-catalog/p/computer-networking/P200000003334/9780135928615) — ranked book canon.
- Kept: [NVIDIA NCCL tests](https://github.com/NVIDIA/nccl-tests) — collective benchmark definitions and measured outputs.
- Dropped: TCP-focused texts as core references. Reason: useful fundamentals, but not evidence for RDMA verbs, NIC/switch counters, or NCCL rail selection.
- Dropped: forums and generic RoCE tutorials — useful incident anecdotes, not authoritative definitions for certification thresholds.

## Gaps

- The research checked IBTA specification wording and page references against the full PDF text. Table 228, page 966, shows data octets divided by four and a 32-bit base field. Table 241, pages 983–984, shows 64-bit extended data fields. Actual extended-counter exposure and device behavior keep a dependence on PMA/device/driver support. Check the selected attribute locally.
- The precise GB300-specific SHARP/NVLS capabilities and required plugin versions keep a dependence on the deployed software/fabric release. Use the exact NVIDIA/HPC-X release manuals. Check runtime selection in the NCCL logs.
- The certification host's privilege model and switch/UFM credentials: not established here. Missing access puts limits on claims. Host-only counters cannot fully show fabric-wide routing, PFC, or ECN health.
- The upstream README runs live. `perftest` flags can show changes over time. Keep the binary version pinned and on record. Check local help. Use compatible peers. CUDA/DMA-BUF support keeps a dependence on build and installed driver/kernel/toolchain.
- Two-hour timing feasibility keeps a dependence on actual rail count, pair sampling, setup overhead, and 16 GB collective duration. Use a pre-run timed dry run to set final coverage. Keep this reading canon separate from measured rack performance.
