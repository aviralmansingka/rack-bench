# Linux Networking - Basics and Beyond (video)

Research date: 2026-10-11. All claims below use a source URL.

## 1. Identity, release, and access

The task supplies O’Reilly identifier 9780138358051. Search shows its listing. A fetch of the listing shows HTTP 403. A public lesson URL also shows a permission denial. This page shows no access to the video and no viewing of it. [observed] [O’Reilly listing](https://www.oreilly.com/videos/linux-networking/9780138358051) [O’Reilly lesson URL](https://www.oreilly.com/videos/linux-networking/9780138358051/9780138358051-LNB1_05_00_00) [supplied O’Reilly URL](https://learning.oreilly.com/videos/-/9780138358051/?orm_source=mcp)

Pearson/InformIT’s public listing shows a separate product identifier, ISBN 9780138357979. It shows “Online Video,” first edition, copyright 2024. It shows no exact release date. The description shows “Over 10 Hours” as an advertisement. It separately shows “over 8 hours” of deep-dive discussions and demos. Task-supplied metadata shows 623 minutes.

The accessible publisher page shows no confirmation of this exact duration. Do not use these identifiers, formats, and duration statements as interchangeable. [observed] [InformIT product listing](https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979) [Prowse catalog](https://prowse.tech/recorded_training) [course lab repository](https://github.com/daveprowse/linux-net)

## 2. Public module / lesson outline

InformIT’s Sample Content shows a complete TOC for product ISBN 9780138357979. The TOC starts with Introduction.

Module 1 “Setup and Networking 101” starts with Lesson 1 “System Setup,” Lesson 2 “Computer Networking Basics,” in order. It then uses Lesson 3 “TCP/IP,” Lesson 4 “The OSI Model”. Module 2 “Networking Services” starts with Lesson 5 “Introduction to Networking Services,” Lesson 6 “The networking Service,” in order. It then uses Lesson 7 “The networkd Service,” Lesson 8 “The NetworkManager Service,” Lesson 9 “More Networking Services”.

Module 3 “Commands and Configurations” starts with Lesson 10 “The ip Command,” Lesson 11 “Network Testing Commands,” in order. It then uses Lesson 12 “Hostnames and DNS,” Lesson 13 “nmcli”. Module 4 “Connecting between Hosts with the Command Line” starts with Lesson 14 “SSH,” Lesson 15 “SCP and rsync,”. It then uses Lesson 16 “SFTP & More Connectivity Tools,” Lesson 17 “Additional Networking Tools”. The TOC ends with Summary. This outline shows a check against the InformIT package identifier only. [observed] [InformIT sample TOC](https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979)

The author-linked course page shows an advertisement for over 10 hours. It shows links to O’Reilly and InformIT. Its samples show Netplan static IP configuration, NetworkManager tools, `nmcli`, and `rsync`. The samples do not show a full syllabus. The Coursera sequence shows four related courses. First pair: Setup and Networking 101; Networking Services. Second pair: Commands and Configurations; Connecting Between Hosts with the Command Line. The sources show no evidence for that sequence as the exact O’Reilly manifest. [observed] [Prowse catalog](https://prowse.tech/recorded_training) [Coursera course 1](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-1-ly37x) [course 2](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-2-netjv) [course 3](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-3-t2fn4) [course 4](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-4-nnrb4)

## 3. Relevance to the rack-bench canon

This course shows Linux host/network fundamentals training, not an RDMA/NCCL fabric qualification reference. Its accessible descriptions show setup, basic networking, TCP/IP, DHCP/DNS, and Linux network services. They also show configuration commands and host-to-host connectivity. The retrieved course descriptions and samples show no coverage evidence for the topics below. The topics below start with NCCL collectives, per-rail RDMA read/write/latency, line-rate goodput normalization, and IB/RoCE topology. They also show ECN/PFC, fabric counter interpretation, flaps, and SHARP.

Absence from the accessible outline does not show absence from the inaccessible video. Do not use this course as a citation for those topics. [observed] [O'Reilly listing](https://www.oreilly.com/videos/linux-networking/9780138358051) [Coursera course 1](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-1-ly37x) [Prowse course catalog](https://prowse.tech/recorded_training)

**Canon verdict: SKIM for host/bootstrap diagnosis. Do not put it in the east-west fabric canon.**

The `ip`/interface and network-service material may show a host-level failure before the two-hour test. That failure may show a missing address, route, resolver, or misconfigured host interface. This material may keep that failure separate from a fabric-level failure.

That mapping shows an inference from the described course topics. It makes no claim that the video shows any exact command. Do not use it for a measured PASS.

Use the rack’s measured NCCL/RDMA/goodput and relevant rail/topology/congestion evidence for PASS. The existing canon shows this rule. [inference] [course 1](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-1-ly37x) [current books canon](../books.md) [NCCL networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 4. Portable host-check techniques (inferred mappings)

The accessible topic descriptions show these practical host-side checks. This page makes no claim of watched lessons for them. Do not use them in place of fabric validation.

1. **Check interface/address state:** use `ip -br link` and `ip -br address` for this check. Check each expected interface for presence and an administratively up state. Check that they use the intended addresses. Check the result against the host/rail inventory. This check can show bootstrap misconfiguration. It does not show link quality or RDMA performance. [inference] [course 2 description](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-2-netjv) [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)
2. **Check host routing:** `ip route` (and `ip route get <peer-address>`) shows the kernel’s selected route/interface for a peer address. Keep a record of both directions where relevant. This check shows host routing choice. It does not show switch topology, adaptive routing, rail striping, or path symmetry. [inference] [course 2 description](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-2-netjv)
3. **Check name/service configuration only when bootstrap uses it:** check resolver/host naming and DHCP/static configuration. Use the site’s approved read-only tools/configuration. These checks can show the cause of failed discovery or connection setup. They do not check collective data-plane goodput. [inference] [course 1](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-1-ly37x) [course 3](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-3-t2fn4)
4. **Use a basic peer reachability probe as triage:** `ping` a known peer on the intended network. Keep a record of interface/source selection where possible. A successful ICMP probe does not show RDMA availability. It also does not show absence of congestion or line-rate performance. A failed probe may show policy/filtering rather than a failed fabric. [inference] [course 1](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-1-ly37x) [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)
5. **Check configuration against actual host state:** use the documented distro manager (`NetworkManager`/`nmcli` or Netplan as applicable). Check intended configuration against live addresses/routes. Do not make configuration changes during certification without authorization. The course page shows these as sample topics. [observed] [Prowse course catalog](https://prowse.tech/recorded_training) [inference] [course 3](https://www.coursera.org/learn/pearson-linux-networking-basics-and-beyond-video-course-3-t2fn4)

## 5. Canon disposition

**SKIM** the relevant host setup/address/route/service portions if operators use Linux bootstrap triage. **SKIP** as required or core reading for the two-hour rack certification. The evidence shows no coverage of the measured NCCL collectives or rail-by-rail IB write/read/latency. It shows no coverage of goodput versus line rate or topology/routing validation. It also shows no coverage of ECN/PFC, flaps, or SHARP. Keep the existing NCCL, perftest, fabric-vendor, and counter references in `books.md` as the authoritative diagnostic canon. [inference] [current books canon](../books.md) [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html) [perftest](https://github.com/linux-rdma/perftest)

## Gaps

[observed] Missing fields: exact release date, 623-minute runtime and its ISBN/format attribution, and exact TOC correspondence. The TOC comparison uses InformIT 9780138357979 and the O’Reilly 9780138358051 course. Retrieval status: not publicly retrievable as of 2026-10-11. The O’Reilly listing and lesson URLs show access denial: https://www.oreilly.com/videos/linux-networking/9780138358051 https://www.oreilly.com/videos/linux-networking/9780138358051/9780138358051-LNB1_05_00_00 https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979
- The host-check commands above show inferred portable mappings. They do not show checked lesson quotations or guaranteed demonstrations. [inference] [Prowse course/labs](https://prowse.tech/recorded_training) [lab repository](https://github.com/daveprowse/linux-net)
