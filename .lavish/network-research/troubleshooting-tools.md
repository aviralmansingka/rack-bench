# Network Troubleshooting Tools — Sloan supplement

Research date: 2026-10-11. All claims below use a source URL.

Superseded draft. Use [the corrected source note](oreilly/troubleshooting-tools.md).
Do not use this draft as accepted evidence.

## 1. Identity and access

**Verified facts.** Joseph D. Sloan, *Network Troubleshooting Tools*, O’Reilly, first edition, August 2001. The O’Reilly/Amazon catalog shows 364 pages. ISBN: 0-596-00186-X / 978-0-596-00186-5. The book itself shows “First Edition” and copyright 2001.

O’Reilly Learning Library URL supplied for this task shows HTTP 403, so authenticated access is not available. This is an access restriction, not evidence that the book is absent. A publicly accessible scan shows the title/copyright page and contents. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/059600186X/?orm_source=mcp) · [public full-text scan, title/copyright and TOC](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [Amazon catalog details](https://www.amazon.com/Network-Troubleshooting-OReilly-System-Administration/dp/059600186X)

## 2. Verified chapters

The scanned book’s TOC shows these especially relevant chapters (chapter numbers and titles are observed facts):

- Ch. 1, “Network Management and Troubleshooting” (p. 1).
- Ch. 3, “Connectivity Testing” (p. 45).
- Ch. 4, “Path Characteristics” (p. 71).
- Ch. 5, “Packet Capture” (p. 100).
- Ch. 6, “Device Discovery and Mapping” (p. 134); ch. 7, “Device Monitoring with SNMP” (p. 160).
- Ch. 8, “Performance Measurement Tools” (p. 194); ch. 9, “Testing Connectivity Protocols” (p. 224); ch. 12, “Troubleshooting Strategies” (p. 273).

The book shows itself as a tutorial on information-collection tools and techniques, chiefly freely available Unix tools, mostly Ethernet/TCP/IP. These are not RDMA/NCCL chapters. [Book scan, TOC and preface](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)

## 3. Relevance to the Chennai east-west bench

**Inference.** Its durable contribution is a diagnostic sequence, not any current accelerator-fabric procedure.
The sequence: make a baseline, check connectivity and path, put packet/device/performance evidence together, then use tools in combination.
The preface explicitly shows proactive knowledge of normal behavior and information collection.
Ch. 12 shows troubleshooting strategy.

The sequence makes a useful discipline for an 18-tray, two-hour GB300 NVL72-class bench.
Make before/after evidence.
Make the failing layer clear.
Keep the outcome measured.
It shows no PASS threshold and no substitute for measurements.

For the actual target, use current, domain-specific evidence first.
Use NCCL logs and `nccl-tests` for collective goodput.
Use `perftest` for RDMA link/path tests.
Use deployed vendor/fabric telemetry for rail topology, ECN/PFC and flaps.

Explicitly check measured goodput against line rate.
Keep counters as deltas.
Check the deltas against link/port events.
An inference from the target and modern sources makes these implementation recommendations.
Sloan makes no such technique claims. [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest upstream](https://github.com/linux-rdma/perftest) · [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf)

## 4. Portable diagnosis techniques (adaptations, not RDMA instrumentation)

1. **Baseline before fault-finding.** Keep a record of the normal configuration and observed behavior. Then check the loaded run against that record. Adaptation: keep per-rail link state/counters and NCCL/perftest results before and after the two-hour run. Sloan’s proactive-baseline principle is explicit. Choosing rail counters and the run window is our inference. [Book scan, ch. 1](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)
2. **Layered connectivity ladder.** Make local interface/link, peer connectivity, path, and application/collective checks separate. Do not use one successful ping as proof of service. Adaptation: use ping/route checks only as preliminary reachability evidence. Then use RDMA tests and NCCL. TCP/IP-era probes do not show verbs or GPU data-path health. [Book scan, chs. 3–4](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html)
3. **Capture and correlation, with restraint.** Use packet capture on a targeted suspected protocol/path issue. Check its time against performance symptoms. Adaptation: ordinary TCP/Ethernet captures are not the first-line visibility for RDMA payloads. Use them only where the deployed transport and capture point make them meaningful. Put NIC/switch counters and fabric tools first for ECN/PFC and port events. [Book scan, ch. 5](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf)
4. **Run measurements at multiple scopes; keep capacity separate from achieved throughput.** Sloan’s contents show path characteristics and performance measurement. Adaptation: show per-rail/link measurements and collective goodput separately. Check both against line-rate expectations. Make a note of test size/topology. A successful small ping or a single-link bandwidth result is not collective PASS evidence. [Book scan, chs. 4 and 8](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest upstream](https://github.com/linux-rdma/perftest)
5. **Put independent clues together; make the location clear before changes.** Use the path/device view alongside host and application evidence. Do not put every throughput symptom on the network. Adaptation: check NCCL rank/rail behavior against link flaps, error counters, ECN/PFC telemetry and matched RDMA tests. Make the PASS/FAIL declaration after these checks. This is a synthesis for this bench, not a ready-made Sloan recipe. [Book scan, ch. 12](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html)

## 5. Canon and overlap verdict

**Sibling overlap evidence (read-only inspection).** The internet books brief explicitly shows Sloan at `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/books.md`, lines 510–517.
It shows the book as a 2001, 364-page title.
It shows ping/traceroute/netstat/sniffers/tcpdump.

It makes a **SKIP** verdict because ULSAH 5e ch. 13 and man pages show those tools newer.
Its skip list shows the same rationale again at lines 593–594.
This exact overlap is the general TCP/IP troubleshooting toolkit, not the present east-west RDMA/NCCL diagnosis. [Sibling brief, lines 510–517 and 593–594](file:///home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/books.md#L510)

The network canon already shows Gregg/Jain/Kurose and modern NCCL/perftest/vendor sources.
Sloan makes little contribution to that tool canon.
Modern RDMA fabrics, GPU collectives, current congestion telemetry and rail-aware diagnosis all start after the book.

The sibling’s SKIP is therefore correct for the internet track.
This narrowly scoped supplemental extraction is still useful as a **SKIM** for general diagnostic sequencing.
It is not a canon addition or required reading.
Do not re-research or reuse the sibling brief’s north-south suite. [Network canon](books.md) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [perftest](https://github.com/linux-rdma/perftest)

## Gaps

- A block (HTTP 403) keeps out O’Reilly authenticated catalog access. The public scan shows the first edition, copyright, and chapter list. Catalog metadata shows the listed pagination. The researchers make no claim about later editions. The inspected scan is explicitly the first edition. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/059600186X/?orm_source=mcp) · [public scan](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)
- No Sloan material shows GB300/NVL72 behavior, NCCL release requirements, rail mapping, PFC/ECN thresholds, telemetry access, or two-hour coverage feasibility. Check these against the deployed hardware/software manuals. Make measurements of them on the bench. Keep PASS measured, not vendor-claimed. [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest](https://github.com/linux-rdma/perftest)
