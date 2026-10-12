# Network Troubleshooting Tools — Sloan supplement

Research date: 2026-10-11. All claims below use a source URL.

## 1. Identity and access

**[observed]** Joseph D. Sloan, *Network Troubleshooting Tools*, O’Reilly, first edition, August 2001. 364 pages per Amazon catalog listing. ISBN 0-596-00186-X / 978-0-596-00186-5. The book itself shows “First Edition” and copyright 2001.

The O’Reilly Learning Library URL supplied for this task showed HTTP 403. So this session shows no authenticated access. Keep this as an access restriction, not evidence of book absence. A publicly accessible scan shows the title/copyright page and contents. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/059600186X/?orm_source=mcp) · [public full-text scan, title/copyright and TOC](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [Amazon catalog details](https://www.amazon.com/Network-Troubleshooting-OReilly-System-Administration/dp/059600186X)

## 2. Verified chapters

**[observed]** The scan’s TOC shows these chapters and starting pages. [TOC](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)

- Chapter 1, “Network Management and Troubleshooting” (page 1).
- Chapter 3, “Connectivity Testing” (page 45).
- Chapter 4, “Path Characteristics” (page 71).
- Chapter 5, “Packet Capture” (page 100).
- Chapter 6, “Device Discovery and Mapping” (page 134); Chapter 7, “Device Monitoring with SNMP” (page 160).
- Chapter 8, “Performance Measurement Tools” (page 194); Chapter 9, “Testing Connectivity Protocols” (page 224); Chapter 12, “Troubleshooting Strategies” (page 273).

**[observed]** The preface shows the book as a tutorial on information-collection tools and techniques. Chiefly freely available Unix tools, mostly Ethernet/TCP/IP. **[inference]** The inspected scope shows no evidence of modern RDMA/NCCL diagnostic guidance. [Book scan, TOC and preface](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)

## 3. Relevance to the Chennai east-west bench

**[inference]** Keep its durable contribution as a diagnostic sequence, not as any current accelerator-fabric procedure. The sequence: make a baseline, check connectivity and path, put packet/device/performance evidence on record, then use tools together. The preface explicitly puts emphasis on proactive knowledge of normal behavior and information collection. Chapter 12 shows troubleshooting strategy.

Use this sequence on an 18-tray, two-hour GB300 NVL72-class bench as a discipline. The discipline: keep before/after evidence, put the failing layer in isolation, and keep the outcome measured. It does not show a PASS threshold. It makes no substitute for measurements.

**[inference]** For the actual target, use current, domain-specific evidence first. Use NCCL logs and `nccl-tests` for collective goodput. Use `perftest` for RDMA link/path tests. Use deployed vendor/fabric telemetry for rail topology, ECN/PFC and flaps. Check measured goodput against line rate explicitly. Keep counters as deltas and check them against link/port events.

Keep those as implementation recommendations from the target and modern sources, not Sloan-asserted techniques. [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest upstream](https://github.com/linux-rdma/perftest) · [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf)

## 4. Portable diagnosis techniques (adaptations, not RDMA instrumentation)

1. **[observed]** The preface puts its support behind knowing normal network behavior and proactive information collection. **[inference]** Baseline before fault-finding: make a record of normal configuration and behavior, then check the loaded run. **[inference]** Adaptation: keep per-rail link state/counters and NCCL/perftest results from before and after the two-hour run. Sloan’s proactive-baseline principle: explicit. This review, not Sloan, puts the rail-counter and run-window choice forward. [Book scan, ch. 1](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)
2. **[observed]** Chapters 3–4 show connectivity testing and path characteristics. **[inference]** Use a layered connectivity ladder: keep local link, peer, path, and application/collective checks separate. **[inference]** Adaptation: use ping/route checks only as preliminary reachability evidence, then use RDMA tests and NCCL. TCP/IP-era probes do not show verbs or GPU data-path health. [Book scan, chs. 3–4](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html)
3. **[observed]** Chapter 5 shows packet capture. **[inference]** Run selective captures on a suspected protocol/path issue and check the results together with other evidence. **[inference]** Adaptation: keep ordinary TCP/Ethernet captures out of first-line RDMA-payload visibility. Use them only where the deployed transport and capture point make them meaningful. Use NIC/switch counters and fabric tools for ECN/PFC and port events [Book scan, ch. 5](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [ibdiagnet manual](https://docs.nvidia.com/ibdiagnet-infiniband-fabric-diagnostic-tool-user-manual-v2-11.pdf)
4. **[observed]** Chapters 4 and 8 show path characteristics and performance measurement. **[inference]** Run measurements at multiple scopes and keep capacity separate from achieved throughput. **[inference]** Adaptation: put per-rail/link measurements and collective goodput in the report separately. Check both against line-rate expectations; keep test size/topology on record. Keep a successful small ping or single-link bandwidth result out of collective PASS evidence [Book scan, chs. 4 and 8](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest upstream](https://github.com/linux-rdma/perftest)
5. **[inference] Use independent clues together; put fault location before changes.** Use the path/device view with host and application evidence. Do not put every throughput symptom on the network. Adaptation: check NCCL rank/rail behavior against link flaps, error counters, ECN/PFC telemetry, and matched RDMA tests. Do this before any PASS/FAIL verdict. Keep this as a synthesis for this bench, not a ready-made Sloan recipe. [Book scan, ch. 12](http://www.nylxs.com/docs/networktroubleshootingtools.pdf) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html)

## 5. Canon and overlap verdict

**[observed] Sibling overlap evidence (read-only inspection).** The internet books brief explicitly shows Sloan at `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/books.md`, lines 510–517. It shows the book as a 2001, 364-page title. It shows ping/traceroute/netstat/sniffers/tcpdump. It puts the verdict at **SKIP**. ULSAH 5e Chapter 13 and man pages show newer coverage of those tools.

Its skip list shows the same rationale again at lines 593–594. Keep this exact overlap as the general TCP/IP troubleshooting toolkit, not the present east-west RDMA/NCCL diagnosis. [Sibling brief, lines 510–517 and 593–594](../../internet-research/books.md#L510)

**[observed]** The network canon shows Gregg/Jain/Kurose and modern NCCL/perftest/vendor sources. **[inference]** Sloan puts little into that tool canon. Its date puts it before modern RDMA fabrics, GPU collectives, current congestion telemetry, and rail-aware diagnosis.

Keep the sibling’s SKIP as correct for the internet track. Keep this narrowly scoped supplemental extraction as a **SKIM** for general diagnostic sequencing. Do not put it into the canon or required reading. Do not start new research on the sibling brief’s north-south suite. Do not use that suite again. [Network canon](../books.md) · [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [perftest](https://github.com/linux-rdma/perftest)

## Gaps

- **[observed]** The O’Reilly authenticated catalog access shows a block (HTTP 403); a public publisher TOC search shows rate limiting. So the public scan checks first edition, copyright, and chapter list. Keep the supplied O’Reilly URL as the primary catalog citation; this session makes no inspection of its page. The 364-page count shows corroboration from the Amazon catalog, not from an independent check of accessible publisher metadata. This review makes no claim about later editions; the inspected scan shows the first edition explicitly. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/059600186X/?orm_source=mcp) · [public scan](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)
- **[inference]** The inspected Sloan material shows no verification of GB300/NVL72 behavior, NCCL release requirements, or rail mapping. It shows no verification of PFC/ECN thresholds, telemetry access, or two-hour coverage feasibility. Check these against the deployed hardware/software manuals. Run measurements on the bench. Keep PASS measured, not vendor-claimed. [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting.html) · [NCCL tests](https://github.com/NVIDIA/nccl-tests) · [perftest](https://github.com/linux-rdma/perftest)
