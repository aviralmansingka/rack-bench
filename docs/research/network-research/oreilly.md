# O'Reilly network source supplement

Research date: 2026-10-11. All claims below use a source URL.

## 1. Result and scope

[inference] The source set shows architecture and host-diagnosis context, not a new certification authority.
Keep current NCCL, perftest, counter specifications, and deployed vendor manuals first.
Keep Gregg, Jain, and Kurose/Ross in their existing roles.
No book or catalog claim shows rack PASS.
[Existing canon](books.md) [NCCL](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

The target is an 18-tray GB300 NVL72-class rack in Chennai.
The test window is two hours.
The scope keeps out internet, storage, code changes, and live tests.
The original seven-category research is still complete.
This supplement checks eleven supplied catalog sources only.

[observed] The notes keep metadata, TOCs, excerpts, and full text separate.
They also keep event agendas separate from delivered sessions.
The [source map](oreilly/research.md) and [evidence checks](oreilly/EVIDENCE-CHECKS.md) show access limits.

## 2. Source verdicts

### 2.1 Shanley: InfiniBand Network Architecture

[observed] ISBN 0321117654 shows the 2002 InfiniBand architecture title.
Catalogs show different author credit and page count.
The note shows indexed transport, physical-layer, and subnet-management evidence.
Do not use indexed navigation as inspected chapter prose.
[Full note](oreilly/infiniband-architecture.md)
[Catalog](https://www.oreilly.com/library/view/infiniband-network-architecture/0321117654)

[inference] KEEP as a targeted native-InfiniBand architecture reference.
Use its concepts to keep physical, transport, and management faults separate.
Check endpoint work requests and completions separately from link state.
Check counter changes against workload failures.
Use current manuals for counter definitions and commands.
The book shows no RoCE, NCCL, SHARP, or GB300 thresholds.

[Full note](oreilly/infiniband-architecture.md) [Canon](books.md)

### 2.2 VandenBrink: Linux for Networking Professionals, second edition

[observed] O'Reilly shows second edition, ISBN 9781835881101, August 2026.
Amazon shows September 9, 2026. Matching Google Books metadata shows 2025.
The date differences are still unresolved.
The retry checks US, GB, and Poland Packt routes, Google Books, and Amazon.

Packt shows security verification. Google Books shows no preview. Amazon shows no readable listing.
Second-edition TOC/sample and publication-date reconciliation: not publicly retrievable as of 2026-10-11. [Packt](https://www.packtpub.com/en-us/product/linux-for-networking-professionals-second-edition-9781835881101) [Google Books](https://books.google.com/books?vid=ISBN9781835881101)
The public Packt repository explicitly shows the first-edition ISBN.

[Google Books](https://books.google.com/books?vid=ISBN9781835881101)
[Packt US](https://www.packtpub.com/en-us/product/linux-for-networking-professionals-second-edition-9781835881101)
[Amazon](https://www.amazon.com/dp/1835881106)
[Full note](oreilly/linux-networking-2e.md)
[Catalog](https://www.oreilly.com/library/view/linux-for-networking/9781835881101)
[First-edition repository](https://github.com/PacktPublishing/Linux-for-Networking-Professionals)

[inference] HOLD chapter recommendations until a matching TOC is available.
SKIM only as possible host background. SKIP as operational fabric guidance.
Check host interface state. Keep counter samples. Keep host checks separate from RDMA measurements.

These are proposed checks, not verified second-edition instructions.
[Full note](oreilly/linux-networking-2e.md) [Canon](books.md)

### 2.3 VandenBrink: Linux for Networking Professionals, first edition

[observed] ISBN 9781800202399 shows the first edition.
Indexed Packt evidence shows Chapter 3, “Using Linux and Linux Tools for Network Diagnostics.”
The chapter-count evidence is inconsistent.
The repository's Chapters 1–14 code scope does not remove the catalog navigation count inconsistency.
[Full note](oreilly/linux-networking-1e.md)
[Packt chapter](https://www.packtpub.com/en-us/product/linux-for-networking-professionals-9781800202399/chapter/chapter-3-using-linux-and-linux-tools-for-network-diagnostics-5/section/further-reading?chapterId=5)
[Repository](https://github.com/PacktPublishing/Linux-for-Networking-Professionals)

[inference] SKIM Chapter 3 for host-diagnosis orientation. Otherwise SKIP for certification preparation.
Keep host state, selected transport, and measured workload results separate.
Keep service configuration separate from fabric qualification.
Keep time-stamped counter samples around controlled tests.
Do not send these chapter assignments to the second edition.

[Full note](oreilly/linux-networking-1e.md) [Canon](books.md)

### 2.4 Benvenuti: Understanding Linux Network Internals

[observed] The first-edition book shows a 2005 date. It shows Linux 2.6-era networking.
The child shows direct public TOC access. Later fetches show no access.

Its note shows Chapters 8–11 for device state, interrupts, reception, and transmission.
It shows Chapters 30–32 for host routing.
This review uses no chapter prose.
[Full note](oreilly/linux-network-internals.md)
[Bibliography](https://kernelnewbies.org/KernelBooks/ULNI)

[inference] KEEP as conditional host-path context, not core fabric guidance.
Check host route and source selection for bootstrap failures.
Check interface events during stalls.
Check CPU and softirq pressure against workload timing.
Do not use historical kernel code for present Linux ABI or RDMA behavior.

[Full note](oreilly/linux-network-internals.md) [Canon](books.md)

### 2.5 Dutt: Cloud Native Data Center Networking

[observed] The title uses O'Reilly identifier 9781492045595 and print ISBN 9781492045601.
The retry checks publisher catalog routes, Google Books, Amazon, and the author interview.
Publisher-indexed entries show Chapter 2, Clos; Chapter 11, observability; and Chapter 18, configuration validation.
Google Books shows matching chapter-list excerpts, not a complete TOC.
Its record shows November 22, 2019, and 486 pages. The supplied catalog shows 483 pages.

The public preview's purchase links use ISBN 9781492045571.
Keep format identifiers and page counts separate.
The interview shows a May 16, 2020 date. Keep that date separate from book publication metadata.
Complete primary TOC/Look Inside and Chapter 5 title/number: not publicly retrievable as of 2026-10-11. [O'Reilly](https://www.oreilly.com/library/view/cloud-native-data/9781492045595) [Google Books](https://books.google.com/books/about/Cloud_Native_Data_Center_Networking.html?id=79i_DwAAQBAJ)

[Google Books](https://books.google.com/books/about/Cloud_Native_Data_Center_Networking.html?id=79i_DwAAQBAJ)
[Public preview](https://books.google.com/books?id=79i_DwAAQBAJ&printsec=frontcover)
[Full note](oreilly/cloud-native-fabrics.md)
[Public description](https://www.overdrive.com/media/5147220/cloud-native-data-center-networking)

[inference] KEEP selectively for Ethernet fabric architecture. SKIM relevant design material.
Keep a record of expected topology and paths before measurements.
Keep endpoint results separate from switch telemetry.

Keep a record of link rates, software versions, peers, directions, and commands.
Do not use the title as evidence for RoCE, ECN, PFC, GPU rails, or NCCL coverage.
The architecture supplement keeps the operational reading spine unchanged.
[Full note](oreilly/cloud-native-fabrics.md) [Canon](books.md)

### 2.6 Prowse: Linux Networking - Basics and Beyond

[observed] The author puts the O'Reilly course and Pearson/InformIT product under the same title.
InformIT shows Online Video, first edition, copyright 2024, ISBN 9780138357979.
It shows four modules and seventeen lessons in its public TOC.
The modules show setup, networking services, commands/configuration, and command-line host connections.
The publisher shows “Over 10 Hours” and separately shows “over 8 hours” of discussion and demos.

The supplied O'Reilly identifier is still 9780138358051.
Its exact release, 623-minute runtime, and exact publisher-TOC correspondence are still unverified.
Exact O'Reilly release/runtime/TOC match: not publicly retrievable as of 2026-10-11. [O'Reilly](https://www.oreilly.com/videos/linux-networking/9780138358051) [InformIT](https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979)
The researchers show no video-viewing evidence.
[Publisher product and TOC](https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979)
[Full note](oreilly/linux-networking-video.md)
[Instructor catalog](https://prowse.tech/recorded_training)

[inference] SKIM for operator host/bootstrap preparation. SKIP as required fabric reading.
Check live interface and address state.
Check host routes and required name resolution.
Check live state against the deployed configuration manager.
Related Coursera courses do not show an identical O'Reilly syllabus.

[Full note](oreilly/linux-networking-video.md) [Canon](books.md)

### 2.7 Schroder: Linux Networking Cookbook

[observed] The matching ISBN is 9780596102487.
The reproduced front matter shows first edition, November 2007, and copyright 2008.
The TOC shows Chapter 13, Nagios; Chapter 14, MRTG; and Chapter 19, network troubleshooting.
The mirror shows 634 PDF pages. The supplied catalog shows 642 pages.
PDF page count and catalog extent need not use the same counting method.

[Full note](oreilly/linux-networking-cookbook.md)
[Front matter and TOC](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf)

[inference] KEEP as optional dated host context, not required fabric reading.
Check address conflicts when the deployed network uses ARP.
Use short, approved captures for bootstrap problems.
Keep reachability, throughput, and latency evidence separate.
Do not put historical service or firewall changes into certification.
Do not use the TOC for current RDMA, NCCL, or PFC procedures.

[Full note](oreilly/linux-networking-cookbook.md) [Canon](books.md)

### 2.8 Sloan: Network Troubleshooting Tools

[observed] The reproduced front matter shows first edition, August 2001.
The TOC shows connectivity, paths, capture, discovery, SNMP, performance, and troubleshooting strategies.
The preface puts emphasis on information collection and normal network behavior.
Its main scope is Ethernet/TCP/IP.
[Full note](oreilly/troubleshooting-tools.md)
[Front matter, TOC, and preface](http://www.nylxs.com/docs/networktroubleshootingtools.pdf)

[observed] The sibling internet canon already shows a Sloan review at lines 510–517 and 593–594.
It shows SKIP because newer references show the tools.
This supplement does not run that internet research again.
[Exact local evidence](../internet-research/books.md#L510)

[inference] SKIM for diagnostic sequence. SKIP as a core-canon addition.
Keep a record of a measured baseline before fault diagnosis.
Check the implicated layer before changing configuration.
Put host, link, path, and workload evidence together.
Use current tool manuals for commands.

[Full note](oreilly/troubleshooting-tools.md) [Canon](books.md)

### 2.9 Wright and Stevens: TCP/IP Illustrated, Volume 2

[observed] ISBN 020163354X shows Volume 2, “The Implementation,” not Volume 1.

The authors are Gary R. Wright and W. Richard Stevens.

The publisher shows a public TOC and preface.
The preface shows Berkeley 4.4BSD-Lite implementation code.
Relevant TOC entries show interfaces, routing, ARP, TCP timers, and BSD Packet Filter.
[Full note](oreilly/tcpip-illustrated.md)
[Publisher TOC and preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)

[inference] SKIM only for conditional host/bootstrap context. SKIP as certification reading.
Check addresses, host routes, and neighbors.
Check required bootstrap services separately from payload transport.
Use an approved capture only for a defined host-path question.
BSD implementation detail does not show present Linux, RDMA, or NCCL behavior.

[Full note](oreilly/tcpip-illustrated.md) [Canon](books.md)

### 2.10 LaCroix: Mastering Linux Network Administration

[observed] Indexed catalog metadata shows November 2015, ISBN 9781784399597, and 260 pages.
Indexed contents show host setup, networking basics, SSH, resource monitoring, and advanced networking.
Direct publisher fetches show access denial or security verification.
The review shows no complete readable TOC or inspected chapter text.
[Full note](oreilly/linux-administration.md)
[Publisher contents](https://www.packtpub.com/en-TW/product/mastering-linux-network-administration-9781784399597/chapter/preface-pref/section/what-this-book-covers-preflvl1sec02)

[inference] SKIM for host administration. SKIP as core fabric reading.
Keep a record of host identity and interface mapping.
Check host resource pressure against measured workload timing.
Keep SSH/bootstrap availability separate from RDMA health.
Generic QoS coverage does not show ECN/PFC procedures.

[Full note](oreilly/linux-administration.md) [Canon](books.md)

### 2.11 White: Modern Network Troubleshooting

[observed] The public O'Reilly agenda shows Pearson, Russ White, and event ID 0790145043580.
It shows resilience, half-split diagnosis, network models, and correlation versus causation.
It shows “Flapping BGP in a DC fabric.”
The public listing shows no year.

The retry shows an author post with an explicit January 26, 2023 advertisement for this event ID.
Do not use the earlier 2024 inference for that explicitly dated announcement.
A later author announcement shows the same ID without a session year.

The supplied 2025 metadata still shows no matching uniquely dated session.
2025 session attribution and delivered-content evidence: not publicly retrievable as of 2026-10-11. [Author](https://rule11.tech/modern-network-troubleshooting) [Listing](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)
This review uses no recording or delivered-session evidence.
[Explicit author announcement](https://rule11.tech/modern-network-troubleshooting)
[Later announcement](https://rule11.tech/upcoming-pearson-class-modern-network-troubleshooting)
[Full note](oreilly/modern-troubleshooting.md)
[Public agenda](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)
[Author context](https://rule11.tech/upcoming-pearson-class-modern-network-troubleshooting)

[inference] SKIM for diagnosis methods, not protocol-specific certification rules.
Use a divided host/rail scope only with a topology-correct comparison.
Use a network model for the next check's selection.
Use controlled evidence before a cause attribution.
BGP flaps are not RDMA link-flap qualification.
[Full note](oreilly/modern-troubleshooting.md) [Canon](books.md)

## 3. Reading-spine changes

[inference] Keep the operational reading order unchanged.
Use current NCCL, NCCL-tests, perftest, counter specifications, and deployed vendor manuals for procedures.
Use Gregg for host performance and measurement method.
Use Jain for experiment design and uncertainty.
Use Kurose/Ross for general network concepts.
[Canon](books.md)

[inference] Make Shanley a targeted native-InfiniBand architecture reference.
Make Dutt optional Ethernet fabric architecture context.
Keep Benvenuti and Schroder as conditional, dated host references.
Keep Sloan, TCP/IP Volume 2, LaCroix, and White outside required certification reading.
Keep second-edition chapter assignments and the complete video syllabus on hold pending evidence.
[Source notes and map](oreilly/research.md)

## 4. Certification boundary

[inference] Book methods show check guidance, not measurements.
Same-rack NVL72 collectives can use NVLink/MNNVL rather than RDMA.
Use actual transport logs and moving counters before claiming RDMA results.
Keep per-rail tests separate from collective goodput.
Keep host IP routes separate from fabric path proof.
Keep observed congestion response separate from an unsupported universal failure threshold.

[Original distilled report](docs/network-bench-research.md)
[NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## Gaps

- [observed] Most supplied O'Reilly book/video fetches show no access. Catalog matches do not show full text. [Evidence checks](oreilly/EVIDENCE-CHECKS.md)
- [observed] Second-edition TOC/sample and the exact O'Reilly video manifest are still not publicly retrievable as of 2026-10-11. [2e note](oreilly/linux-networking-2e.md) [Video note](oreilly/linux-networking-video.md)
- [observed] Dutt's retry shows evidence for selected chapter assignments. The complete primary TOC is still not publicly retrievable as of 2026-10-11. [Dutt note](oreilly/cloud-native-fabrics.md)
- [observed] White shows a January 26, 2023 session advertisement for the same ID. The supplied 2025 session attribution is still not publicly retrievable as of 2026-10-11. [Agenda](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)
- [observed] Shanley author/page-count records and VandenBrink first-edition chapter counts are still inconsistent. [Shanley note](oreilly/infiniband-architecture.md) [1e note](oreilly/linux-networking-1e.md)
- [inference] Third-party scans show evidence only for the inspected passages. They show no evidence for subscriber access or publisher authorization. [Evidence checks](oreilly/EVIDENCE-CHECKS.md)
- [inference] Use deployed-version review and target-rack measurements for all proposed rack checks. No source shows a measured PASS. [Canon](books.md)
