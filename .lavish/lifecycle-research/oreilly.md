# O’Reilly lifecycle source supplement

Research date: 2026-10-11.

## 1. Scope and evidence rules

[inference] This review checks eleven catalog items for the Chennai GB300/NVL72-class, 18-tray rack.
It adds source evidence to the [lifecycle canon](books.md), but no measured rack results.
Use audit → bench → smoke. Require the named bench measurement for PASS.
Keep the final 20 minutes of each two-hour category for cleanup and evidence.

This review does not run live or destructive tests. It does not evict production workloads or change firmware or OS.
This supplement does not cover internet or storage performance.
Design basis: [existing report](research.md), [SRE testing](https://sre.google/sre-book/testing-reliability/).

[observed] The eleven source notes separate catalog metadata, contents, readable excerpts, and proposed checks.
URL and fetch method affect access. This session has no authenticated O’Reilly MCP access.
Public catalogs sometimes show contents. Some chapter endpoints deny access.
See the [source report](oreilly/research.md) and [independent checks](oreilly/evidence-checks.md).

## 2. N08 — Site Reliability Engineering, second edition

[observed] O’Reilly lists September 2026, 796 pages, ISBN 9798341607675, and six editors.
The editors are Beyer, Jones, Leng, Huska, Petoff, and Murphy.
The record does not establish September 16.
[Publisher record](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp).

[observed] Chapter 7 lists service lifecycle engagement beyond readiness reviews.
Chapters 13–18 cover automation, testing, capacity planning, data management, resilience, and platform engineering.
Chapter 20 covers SRE support for AI. It lists headings for hardware qualification and accelerator SLO eligibility.
Chapter 16 lists restore testing. Chapter 17 lists correct delete/undelete behavior.

The publisher contents confirm these topics. No one has inspected the procedures.
[Publisher contents](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp).

[inference] Proposed checks: (1) record lifecycle ownership. (2) Measure queue and useful-work events.
(3) Inspect approved synthetic restore evidence. (4) Compare declared and actual state.
(5) Require independent useful GPU work beside qualification records.

The contents identify relevant subjects. They do not give rack acceptance thresholds.
[Design basis](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp).

[observed] The child reports limited opening excerpts. The orchestrator cannot access chapter 15.
[inference] Add a separate second-edition entry. Keep citations and chapter numbers from the inspected first edition.
[Chapter endpoint](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html);
[full note](oreilly/sre-2e.md).

## 3. N09 — Site Reliability Engineering, first edition

[observed] The catalog lists April 2016, 552 pages, and identifier 9781491929117.
Google provides readable first-edition text.
Chapter 17 explains configuration comparisons, smoke tests, staged canaries, and reversion.
Chapter 18 discusses capacity planning. The contents have no standalone Capacity Planning chapter.
[Catalog](https://learning.oreilly.com/library/view/-/9781491929117/?orm_source=mcp);
[chapter 17](https://sre.google/sre-book/testing-reliability/);
[chapter 18](https://sre.google/sre-book/software-engineering-in-sre/).

[inference] Proposed checks: (1) timestamp observable service events. (2) Run one correct bounded GPU workload.
(3) Compare intended and actual configuration. (4) Verify an approved reversible change.
(5) Record explicit ownership and cleanup.

These checks apply readable guidance. They do not prove lease reliability or media erasure.
[SLO guidance](https://sre.google/sre-book/service-level-objectives/).
[testing guidance](https://sre.google/sre-book/testing-reliability/).
[launch guidance](https://sre.google/sre-book/reliable-product-launches/).

[inference] Keep this edition as the baseline for inspected public text.
Do not assign its chapter numbers to the second edition.
[First-edition contents](https://sre.google/sre-book/table-of-contents/); [full note](oreilly/sre-1e.md).

## 4. N10 — Building Secure and Reliable Systems

[observed] Google's maintained text verifies chapters 9, 16, and 18.
Chapter 9 covers explicit revocation and intended state. Chapter 16 covers safe response-plan tests.
Chapter 18 covers recovery plans, cleanup, rollback, quarantine, and Data Sanitization.
Data Sanitization checks for attacker changes in code, binaries, images, configuration, and application data.
It does not define a method to erase physical media.
[Chapter 9](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html);
[chapter 16](https://google.github.io/building-secure-and-reliable-systems/raw/ch16.html);
[chapter 18](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html).

[inference] Proposed checks: (1) record recovery roles and stop conditions. (2) Inspect visible test quarantine.
(3) Compare synthetic artifacts with known-good hashes. (4) Test revoked disposable credentials.
(5) Retain failed drill evidence and cleanup results.

Apply routine tenant exit as a separate design step.
[Recovery basis](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html).
[revocation basis](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html).

[observed] The supplied catalog lists 555 pages. The child finds a bibliographic record with 558 pages.
The format mapping remains unresolved. The earlier canon links to an unrelated notebook on Google Books.
[inference] Remove that incorrect link and its unsupported ISBN attribution. Keep the verified primary chapter citations.
[Removed link check](https://books.google.com/books?id=0KR7zQEACAAJ);
[alternate record](https://books.google.com/books/about/Building_Secure_and_Reliable_Systems.html?id=93HnDwAAQBAJ);
[full note](oreilly/bsrs.md).

## 5. N11 — The Practice of System and Network Administration

[observed] The supplied record lists the second edition, July 2007, and 1,056 pages.
The relevant chapters are 6 and 17–20. O’Reilly also lists the third edition, November 2016, with 1,232 pages.
The third-edition publisher preview lists copyright 2017.
Third-edition chapters 19, 26, 32–34, and 56 use different numbers.
[Second-edition record](https://learning.oreilly.com/library/view/-/9780321545275/?orm_source=mcp);
[third-edition record](https://learning.oreilly.com/library/view/the-practice-of/9780133415087);
[publisher preview](https://api.pageplace.de/preview/DT0400.9780133415070_A28528899/preview-9780133415070_A28528899.pdf).

[inference] Proposed checks: (1) limit change scope. (2) Reconcile launch evidence.
(3) Define verification and backout before change. (4) Separate access, data, and physical disposition.
(5) Record missing process evidence.

The preview verifies headings and preface principles. It does not verify all chapter procedures.
[Design basis](https://api.pageplace.de/preview/DT0400.9780133415070_A28528899/preview-9780133415070_A28528899.pdf).

[inference] Keep the third edition in the canon. A second-edition search result does not support a downgrade.
[Edition evidence](https://learning.oreilly.com/library/view/the-practice-of/9780133415087);
[full note](oreilly/practice.md).

## 6. N12 — Data Centre Essentials

[observed] Wiley identifies Vincent Fogarty and Sophia Flucker, 240 pages, and hardcover ISBN 9781119898818.
Wiley displays July 2023. The child reports first edition and September 2023 on Wiley-VCH.
Keep the difference between these dates visible.

The primary Wiley-VCH contents list commissioning and handover in chapter 6.
Chapter 7 lists maintenance, change, capacity, training, and uptime/failures.
Chapter 9 lists sustainability and life-cycle impacts.
[Wiley metadata](https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591);
[primary contents](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).

[inference] Proposed checks: (1) reconcile handover evidence. (2) Record approved reversible change.
(3) Compare configured and observed capacity. (4) Inspect existing failure and recovery logs.
(5) Record tenant-exit controls separately from media sanitization.

These checks use topic coverage, not unread chapter instructions.
[Design basis](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).

[inference] Use this book for facility context, not the tenant lifecycle spine.
This review does not define a physical commissioning test. The site and OEM must still approve.
The primary contents resolve the earlier chapter gap that relied only on a mirror.
[Primary contents](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8);
[full note](oreilly/data-centre.md).

## 7. N13 — Kubernetes Operators

[observed] The child reads O’Reilly metadata: Dobies and Wood, February 2020, 154 pages, ISBN 9781492048039.
Its contents include application recovery, scaling, upgrade, cleanup, reconciliation, idempotency, and operator versioning.
The orchestrator cannot access the repeated catalog fetch.

Red Hat's readable excerpt explains the controller loop.
Controllers compare desired and actual state. Then they act on differences.
[Catalog](https://learning.oreilly.com/library/view/-/9781492048039/?orm_source=mcp);
[readable excerpt](https://developers.redhat.com/e-books/kubernetes-operators).

[inference] Proposed checks: (1) compare desired state, actual resources, and useful work.
(2) Observe approved disposable application recovery. (3) Inspect a versioned reversible transition.
(4) Record residual child resources after approved cleanup. (5) Verify synthetic restore independently of backup status.

Use these checks only with an actual operator-based tenant interface.
Operator Ready status does not prove that GPU output is correct. Deletion does not prove media sanitization.
[Design basis](https://developers.redhat.com/e-books/kubernetes-operators).
[contents basis](https://learning.oreilly.com/library/view/-/9781492048039/?orm_source=mcp).

[inference] Add an optional operator supplement beside Kubernetes in Action. Do not replace the core spine.
Confirm named operator semantics and current version behavior first.
[Publisher scope](https://developers.redhat.com/e-books/kubernetes-operators); [full note](oreilly/kubernetes-operators.md).

## 8. N14 — The Kubernetes Operator Framework Book

[observed] Packt's repository confirms the title, Michael Dame, and ISBN-linked publisher page.
The child finds indexed July 2022 metadata, 328 pages, and limited chapter headings.
Chapter 8 covers ongoing maintenance. Chapter 10 presents a Prometheus Operator case study.

Direct chapter pages deny access. The repository does not provide a complete chapter guide.
Its README also contains unrelated DevOps marketing text. Do not treat that text as verified book coverage.
[Repository](https://github.com/PacktPublishing/The-Kubernetes-Operator-Framework-Book);
[indexed publisher preface](https://www.packtpub.com/en-br/product/the-kubernetes-operator-framework-book-9781803232850/chapter/preface-pref/section/what-this-book-covers-preflvl1sec03).

[inference] Proposed checks: (1) compare desired and actual disposable resources.
(2) Record an approved reversible version transition. (3) Inspect actual OLM dependency and condition evidence.
(4) Record access revocation and residual resources separately.

These proposals use current Framework/OLM documentation. They do not use inspected book chapters.
[Framework](https://operatorframework.io).
[OLM](https://github.com/operator-framework/operator-lifecycle-manager).
[revocation](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html).

[inference] Keep this as a conditional chapter-evidence gap.
No one has verified book-specific chapter claims about OLM installation, dependency, upgrade, or rollback.
[Publisher preface](https://www.packtpub.com/en-br/product/the-kubernetes-operator-framework-book-9781803232850/chapter/preface-pref/section/what-this-book-covers-preflvl1sec03);
[full note](oreilly/operator-framework.md).

## 9. N15 — Site Reliability Engineering on AWS video

[observed] The child finds indexed Packt metadata for Malcolm Orr and 4 hours 41 minutes.
[calculated] That duration equals 281 minutes. Another course listing reports 4 hours 40 minutes.
No independent source verifies the supplied 2020 year.

Indexed modules cover reliability basics, AWS resilience, multi-tier failure, and global-scale failure.
Only titles support modules P1, P2, P3, and P7. No one inspected a video or transcript.
[Packt record](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium);
[course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws);
[full note](oreilly/sre-aws.md).

[inference] Proposed checks: (1) timestamp readiness and useful work. (2) Inspect isolated recovery evidence.
(3) Compare state before and after approved change. (4) Identify failure-domain dependencies.
(5) Record separate exit and cleanup evidence.

These design proposals use topic coverage. They are not prescriptions from an unwatched course.
AWS region patterns do not define NVL72 failure domains.
[Scope basis](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium).
[existing measurement basis](https://sre.google/workbook/implementing-slos/).

[inference] Keep this video optional. No source confirms the release date, complete modules, or instructional details.
[Requested record](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp).

## 10. N16 — Practical Site Reliability Engineering

[observed] Packt's repository confirms the authors Pethuru Raj Chelliah, Shreyash Naithani, and Shailender Singh.
The repository confirms the title and ISBN-linked publisher page.
No source verifies the edition, 2018 year, 390-page extent, or exact chapter titles.
The README describes software delivery, containerization, service meshes, performance, and resilience.
Code directories do not verify lifecycle chapter titles.
[Publisher repository](https://github.com/PacktPublishing/Practical-Site-Reliability-Engineering/blob/master/README.md);
[requested catalog](https://learning.oreilly.com/library/view/-/9781788839563/?orm_source=mcp).

[inference] Proposed checks: (1) reconcile inventory and useful-work evidence.
(2) Define change approval and restoration. (3) Record queue and capacity separately.
(4) Compare intended and actual configuration. (5) Verify disposable-credential denial after revocation.

These checks come from the existing canon. They do not come from uninspected Practical SRE chapters.
[SLO basis](https://sre.google/workbook/implementing-slos/).
[change basis](https://sre.google/workbook/canarying-releases/).
[state and revocation basis](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html).

[inference] Do not promote this book into the core spine without verified, non-duplicative chapter guidance.
[Publisher scope](https://github.com/PacktPublishing/Practical-Site-Reliability-Engineering/blob/master/README.md);
[full note](oreilly/practical-sre.md).

## 11. N17 — Ambiguous SRE training videos

[observed] The request for identifier 0636920668534 returns access denied. Search requests return rate-limit errors.
No primary record identifies the title, instructor, provider, dates, or modules.
[inference] Do not merge SRE Fundamentals and SRE Essentials.
The supplied 2021/2025 dates do not show whether they identify one course or two.
[Requested record](https://learning.oreilly.com/videos/-/0636920668534/?orm_source=mcp);
[full note](oreilly/sre-videos.md).

[inference] Proposed checks: (1) timestamp readiness. (2) Verify an approved reversible change.
(3) Record disposable-tenant access and resource disposition. (4) Preserve cleanup and evidence time.

These checks use the existing canon. This review does not attribute techniques to an unidentified video.
[SLO basis](https://sre.google/workbook/implementing-slos/).
[change basis](https://sre.google/workbook/canarying-releases/).
[revocation basis](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html).

[inference] Exclude this item from ranked reading until a primary record resolves its identity and syllabus.
[Requested record](https://learning.oreilly.com/videos/-/0636920668534/?orm_source=mcp).

## 12. N18 — Kubernetes Programming with Go

[observed] Springer/Apress confirms Philippe Martin, the first edition, and publication in December 2022.
The publisher gives copyright year 2023. It lists XX + 316 pages, not the supplied 326 pages.

Chapters 2 and 6 cover API operations and client-go. Chapters 7 and 12 cover testing.
Chapters 10–11 cover controller-runtime operators and the reconcile loop.
Readable abstracts verify subject coverage, not all implementation details.
[Publisher record](https://link.springer.com/book/10.1007/978-1-4842-9026-2);
[chapter 12](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12).

[inference] Proposed checks: (1) record observed API transitions. (2) Check repeated reconcile without duplicate resources.
(3) Separate fake-client tests from actual API tests. (4) Observe asynchronous cleanup without forced metadata removal.
(5) Record server, client, and API versions.

These are controller-engineering proposals. They are not rack certification procedures.
[Chapter 11](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_11).
[chapter 12](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12).
[current finalizer authority](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/).

[inference] Add an optional adapter/controller appendix only if Kubernetes is the actual tenant interface.
Gather separate evidence for finalizers, status details, resource ownership, and current GB300 behavior.
[Publisher scope](https://link.springer.com/book/10.1007/978-1-4842-9026-2);
[full note](oreilly/kubernetes-go.md).

## Gaps

[observed] N14 lacks complete book-specific OLM chapter evidence. N15 lacks complete modules and a verified release year.
N16 lacks exact lifecycle chapters and complete metadata. N17 lacks course identity and modules.
These gaps limit promotion of the items into the canon. They do not show that sources omit this information.
[Gap records](oreilly/research.md); [source notes](oreilly/).

[observed] The earlier Workbook bibliography URL returns 404. The earlier BSRS URL names an unrelated notebook.
The canon removes those bibliography citations and unsupported ISBN attributions.
The exact ISBN-to-format mapping remains unresolved. Keep the verified primary chapter citations unchanged.
[Workbook link check](https://books.google.com/books?id=YxF7DwAAQBAJ);
[BSRS link check](https://books.google.com/books?id=0KR7zQEACAAJ).

[observed] The source does not resolve the SRE 2e publication day. The source limits access to full chapter bodies.
Wiley records give different publication months. AWS duration records differ by one minute.
Interpret BSRS and Kubernetes Go pagination by format.
[Source checks](oreilly/evidence-checks.md); [SRE 2e note](oreilly/sre-2e.md);
[facility note](oreilly/data-centre.md); [AWS note](oreilly/sre-aws.md); [BSRS note](oreilly/bsrs.md).

[inference] No source sets GB300 rack acceptance thresholds or approved Chennai maintenance procedures.
No one has confirmed the actual tenant interface. Review full licensed chapter procedures separately.
N03's numeric MosaicML spot-use gap stays open. This supplement supplies no missing numerator or denominator.
No short test proves media sanitization, provisioning p99, fleet MTBF/MTTR, or lease availability.
[NVIDIA scope](https://www.nvidia.com/en-us/data-center/gb300-nvl72/);
[NIST Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final); [existing research](research.md).
