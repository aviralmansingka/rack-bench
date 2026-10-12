# O’Reilly lifecycle source research

Question: Which catalog sources change lifecycle guidance and proposed bench checks?
Research date: 2026-10-11.
Audience: GB300-class rack operators and GPU tenants in Chennai, India.
Scope: edition evidence, chapter evidence, portable techniques, and changes to the lifecycle canon.
Exclusions: project changes, live tests, destructive operations, and repeated internet or storage performance research.

Each source has one independent researcher. No source needs another source's result.
The catalog supplies leads, not verified chapter procedures.
N03's numeric MosaicML spot-use gap remains outside the accepted supplement results.

```mermaid
flowchart TD
N08["SRE second edition"]
N09["SRE first edition"]
N10["Secure recovery and integrity"]
N11["Practice edition coverage"]
N12["Facility lifecycle context"]
N13["Kubernetes Operators"]
N14["Operator Framework chapters - GAP"]
N15["SRE on AWS modules - GAP"]
N16["Practical SRE chapters - GAP"]
N17["SRE video identity - GAP"]
N18["Kubernetes Go controller checks"]
```

| Node | Question | Dependencies | Acceptance condition | Child | State |
| --- | --- | --- | --- | --- | --- |
| N08 | What does SRE second edition add? | None | Verified edition and contents; bounded excerpts and proposed checks | oreilly-sre-2e | done |
| N09 | Which first-edition citations remain valid? | None | Verified public chapter guidance; edition-specific citations | oreilly-sre-1e | done |
| N10 | What does BSRS sanitization mean? | None | Exact recovery sections; integrity versus media erasure | oreilly-bsrs | done |
| N11 | Does the second-edition result replace Practice third edition? | None | Both editions and distinct chapter numbers | oreilly-practice | done |
| N12 | What facility guidance does Data Centre Essentials add? | None | Primary contents; facility versus tenant boundaries | oreilly-data-centre | done |
| N13 | What operator lifecycle controls does the book cover? | None | Verified contents and readable mechanism; conditional checks | oreilly-kubernetes-operators | done |
| N14 | Which book chapters describe OLM lifecycle? | None | Book-linked evidence accepted; complete OLM chapter attribution unresolved | oreilly-operator-framework | gap |
| N15 | Which AWS video modules support lifecycle checks? | None | Limited modules accepted; full syllabus and release date unresolved | oreilly-sre-aws | gap |
| N16 | What does Practical SRE add to the core? | None | Identity accepted; exact lifecycle chapters and full metadata unresolved | oreilly-practical-sre | gap |
| N17 | Which course does identifier 0636920668534 identify? | None | Access limits recorded; identity and modules unresolved | oreilly-sre-videos | gap |
| N18 | What controller checks does the Go book support? | None | Publisher edition, chapter locations, and implementation boundaries | oreilly-kubernetes-go | done |

All eleven researchers return a source note. Corrections use the same sessions.
[Aggregate brief](../oreilly.md) gives per-source decisions and proposed checks.
[Evidence checks](evidence-checks.md) records independent passage checks and access differences.
`nodes/` indexes the complete source notes and their accepted states.

[Canon](../books.md) and [bench design](../docs/lifecycle-bench-research.md) contain the accepted changes.
The parent must publish project documents. No rack measurement occurs in this review.

## N08: Add the second edition without moving old citations

Question: What does SRE second edition add?
An edition identifies a particular text and chapter sequence.
The [publisher](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
confirms second edition, September 2026, 796 pages, and ISBN 9798341607675.
Its contents add chapter 15 Capacity Planning and chapter 20 How SRE Supports AI.

Chapter 7 includes service lifecycle engagement beyond readiness reviews.
Chapter 20 lists continuous hardware qualification and accelerator SLO eligibility.
These headings show subject coverage, not tested GB300 acceptance procedures.

Example: record queue delay, scheduler capacity, and correct useful work separately.
This is a proposed check, not a second-edition test prescription.
Keep the 2016 Google-hosted passages under first-edition citations.
Do not transfer their chapter numbers to this edition.

The child reports a limited chapter 15 excerpt; the orchestrator's fetch denies access.
The exact publication day and full procedures remain gaps.
Use this result in the canon's edition-specific addition.
Full evidence: [source note](sre-2e.md).

## N09: Keep the inspected first-edition baseline

Question: Which first-edition citations remain valid?
An inspected passage gives stronger technique evidence than a catalog title.
The [first-edition text](https://sre.google/sre-book/testing-reliability/)
describes smoke tests, configuration comparisons, canaries, and reversion.
Its [chapter 18](https://sre.google/sre-book/software-engineering-in-sre/)
discusses traditional and intent-based capacity planning.
That discussion is not a standalone Capacity Planning chapter.

Example: compare observed configuration with the approved manifest before a disposable change.
Keep differences and failed checks in the evidence bundle.
A short successful workload shows that bounded path, not lease reliability.
The second edition does not invalidate an accurately cited first-edition passage.
Use this result beside N08's edition addition.
Full evidence: [source note](sre-1e.md).

## N10: Separate recovery integrity from media erasure

Question: What does BSRS sanitization mean?
Recovery integrity checks whether attacker changes remain after an incident.
[Chapter 18](https://google.github.io/building-secure-and-reliable-systems/raw/ch18.html)
checks code, binaries, images, configuration, and application data.
It uses known-good sources, provenance, and checksum comparisons.
Its quarantine guidance concerns potentially compromised assets.
Neither topic supplies a routine tenant-exit or physical-media erase procedure.

Example: compare an approved synthetic artifact manifest with observed hashes.
A matching hash does not prove media sanitization.
Use [chapter 9](https://google.github.io/building-secure-and-reliable-systems/raw/ch09.html)
for explicit revocation, then test denial with a disposable credential.

The earlier canon's Google Books link names an unrelated notebook; remove that citation.
Exact format and pagination mapping remain unresolved.
The canon keeps primary chapter citations and corrects its sanitization wording.
Full evidence: [source note](bsrs.md).

## N11: Keep Practice third edition

Question: Does the second-edition result replace Practice third edition?
Chapter numbers belong to editions, not titles alone.
O’Reilly lists [second edition](https://learning.oreilly.com/library/view/-/9780321545275/?orm_source=mcp)
and [third edition](https://learning.oreilly.com/library/view/the-practice-of/9780133415087).
Second-edition chapters 17–20 cover change, upgrades, conversions, and maintenance.
Third-edition change and maintenance chapters are 32–34.
The [publisher preview](https://api.pageplace.de/preview/DT0400.9780133415070_A28528899/preview-9780133415070_A28528899.pdf)
verifies third-edition lifecycle and retirement headings.

Example: define verification and backout before an approved reversible service change.
This proposal uses verified headings and preface principles, not unread chapter instructions.
O’Reilly gives November 2016; the preview gives copyright 2017.

Keep both date meanings. A second-edition search result does not justify a downgrade.
Use this result to retain the canon's third-edition numbering.
Full evidence: [source note](practice.md).

## N12: Keep facility and tenant lifecycle separate

Question: What facility guidance does Data Centre Essentials add?
Facility commissioning concerns infrastructure handover, not a tenant API alone.
The [primary contents](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8)
verify chapter 6 commissioning and handover.
Chapter 7 includes maintenance, change, capacity, training, and uptime/failures.

These contents close the earlier mirror-only chapter-evidence gap.
They do not expose full chapter instructions.

Example: compare expected handover inventory with observed rack and tray inventory.
Do not infer cooling or power headroom from software capacity.
Use this book as a facility supplement, not the tenant lifecycle spine.
Wiley and Wiley-VCH report different publication months; keep that difference visible.

No physical commissioning test follows from this reading.
Site and OEM approval remain necessary.
Full evidence: [source note](data-centre.md).

## N13: Check useful work beyond operator status

Question: What operator lifecycle controls does the book cover?
A controller compares desired and actual state, then acts on differences.
The readable [Red Hat excerpt](https://developers.redhat.com/e-books/kubernetes-operators)
explains that mechanism.
The researcher reads contents for recovery, upgrade, cleanup, reconciliation, and operator versioning.
The orchestrator's repeat catalog fetch denies access. Access differs across fetches.

Example: compare declared state, child resources, events, and correct GPU output.
Ready status alone does not prove useful work.
Resource deletion does not prove credential revocation or media erasure.

Use this supplement only for an actual operator-based tenant interface.
Named operator semantics and current versions still need separate documentation.
Use this result beside the existing Kubernetes operations reading.
Full evidence: [source note](kubernetes-operators.md).

## N14: Keep unsupported OLM chapter claims open

Question: Which book chapters describe OLM lifecycle?
OLM manages operator installation, dependencies, and updates.
The [publisher repository](https://github.com/PacktPublishing/The-Kubernetes-Operator-Framework-Book)
confirms the book identity and Michael Dame.
Indexed publisher pages give limited maintenance and case-study chapter headings.

The repository gives code folders, not complete OLM chapter evidence.
Its README contains unrelated DevOps marketing text; do not use that text as verified book coverage.

Example: inspect actual OLM dependency constraints and condition evidence on a disposable target.
That proposal uses [OLM documentation](https://github.com/operator-framework/operator-lifecycle-manager), not inspected book procedures.
Book-specific installation, dependency, upgrade, and rollback chapter attribution remains a gap.
Keep the book conditional. Do not promote it into the core spine.
Full evidence: [source note](operator-framework.md).

## N15: Treat unwatched video modules as topic evidence

Question: Which AWS video modules support lifecycle checks?
A module title identifies a topic, not an inspected procedure.
The child finds indexed [Packt metadata](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
for Malcolm Orr and 4 hours 41 minutes.

That duration equals 281 minutes. Another listing differs by one minute.
Only P1, P2, P3, and P7 have supporting module titles.
The supplied 2020 release year remains independently unverified.

Example: record readiness and recovery events for an approved isolated service.
This is a topic-based proposal, not an unwatched video prescription.
AWS region patterns do not establish NVL72 failure domains.

This review inspects no video or transcript. The full syllabus remains a gap.
Keep this source optional, not part of the core spine.
Full evidence: [source note](sre-aws.md).

## N16: Do not infer chapter coverage from code folders

Question: What does Practical SRE add to the core?
The [publisher README](https://github.com/PacktPublishing/Practical-Site-Reliability-Engineering/blob/master/README.md)
confirms the title, publisher, and three full author names.
It describes software delivery, containerization, service meshes, performance, and resilience.
Its code folders do not supply exact lifecycle chapter titles.
Edition, year, page count, and chapter evidence remain incomplete.

Example: compare intended and actual configuration under the existing canon's guidance.
Do not attribute that check to an uninspected Practical SRE chapter.
Unique lifecycle value remains unverified.
Do not promote this source without exact, non-duplicative chapter guidance.
Full evidence: [source note](practical-sre.md).

## N17: Keep the video identity unresolved

Question: Which course does identifier 0636920668534 identify?
The [requested record](https://learning.oreilly.com/videos/-/0636920668534/?orm_source=mcp)
denies access. Search requests return rate-limit errors.
No primary record resolves title, instructor, provider, dates, or modules.
SRE Fundamentals and SRE Essentials are not verified alternate names.
The supplied 2021/2025 dates do not resolve one course or two courses.

Example: use existing SLO guidance for readiness timestamps, not an unidentified course claim.
This review attributes no techniques to the video item.
Keep the identity and syllabus as explicit gaps.
Exclude this item from ranked reading until primary evidence identifies it.
Full evidence: [source note](sre-videos.md).

## N18: Separate controller tests from rack certification

Question: What controller checks does the Go book support?
The [publisher](https://link.springer.com/book/10.1007/978-1-4842-9026-2)
verifies Philippe Martin, first edition, and December 2022 publication.
Copyright 2023 is a different date field. The extent is XX + 316 pages.
Chapters 7 and 12 cover client and reconcile-loop testing.
The [chapter 12 page](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12)
confirms its title, pages, and limited abstract.

Example: distinguish fake-client assertions from a disposable actual-API check.
A fake-client pass does not prove target-cluster behavior.
Record observed transitions, retries, errors, cleanup, and exact version context.
Use this as an adapter/controller appendix only for an actual Kubernetes interface.
Full finalizer, status, ownership, and current GB300 details remain outside the accepted chapter evidence.
Full evidence: [source note](kubernetes-go.md).
