# N08 — *Site Reliability Engineering*, 2nd Edition

Research date: 2026-10-11.

## 1. Access and verified metadata

The specified O’Reilly Learning catalog URL comes first. It returns the title page, contents and overview. The catalog itself is accessible. Full chapter access varies and requires the “Read now Unlock full access” prompt.

In this research fetch, Ch. 15 returns an opening body excerpt. A separate user report says the same chapter fetch can return Akamai 403. Do not assume stable public access or full-text availability. [observed] [O’Reilly Learning catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [Ch. 15 fetch URL](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html)

The publisher catalog identifies *Site Reliability Engineering, 2nd Edition*, O’Reilly Media, ISBN 9798341607675, and 796 pages. It names six editors/authors: Betsy Beyer, Chris Jones, Christof Leng, David Huska, Jennifer Petoff, and Niall Richard Murphy. The catalog date is September 2026. The catalog does not show the precise day, September 16. [observed] [O’Reilly Learning catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)

### Decisive Ch. 15 body excerpt actually fetched (limited excerpt, not full text)

> “Capacity planning is the discipline of forecasting future demand and provisioning the supply to meet it. To scale infrastructure successfully, you must balance performance, cost, and reliability—all anchored by your core business goals.”
>
> “Capacity planning heavily parallels the concept of error budgets. Just as 100% uptime is the wrong target for reliability, provisioning for every statistical edge case is the wrong target for capacity; you must make deliberate choices based on your explicit risk tolerance.”
>
> “Your first capacity planning decision is determining whether you actually need the rigorous and expensive process detailed here. Is your service large enough, growing quickly enough, or critical enough to warrant it?”

These sentences come from the fetched page’s “Content preview” for “Chapter 15. Capacity Planning”. Only this limited excerpt is readable, not the chapter in full. [observed] [Ch. 15, opening paragraphs/content preview](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html)

## 2. Lifecycle-relevant 2e chapters

The following are verified publisher TOC headings only. This review makes no claim to have read their detailed chapter bodies:

- Ch. 7 “SRE Engagement Models,” with “Service Lifecycle Engagement Beyond Production Readiness Reviews.” [observed] [publisher Contents, Ch. 7](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- Ch. 13 “Automation and Tooling”. Ch. 14 “Testing”. Ch. 15 “Capacity Planning,” including “Capacity Isolation and Failure Domains,” “Resource Pooling and Flex,” and “Reclaiming Stranded Capacity.” [observed] [publisher Contents, Chs. 13–15](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- Ch. 16 “Data Management,” including “Restore Testing.” Ch. 17 “Designing for Resilience,” including “Progressive Rollout,” “Change Supervision,” and “Qualification Environments and Shifting Left,”. It also includes “Delete and Undelete Data Correctly.” [observed] [publisher Contents, Chs. 16–17](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- Ch. 18 “Platform Engineering in SRE,” including “Seeing Like a State Machine” and “Legibility and Introspection.” [observed] [publisher Contents, Ch. 18](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- Ch. 19 “SRE at the Tipping Point” (SDLC and staging/test environments). Ch. 20 “How SRE Supports AI” (product lifecycle integration, continuous hardware qualification, accelerator SLO-eligibility, utilization, capacity and scheduling). These are headings, not verified detailed procedures. [observed] [publisher Contents, Chs. 19–20](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)

Ch. 20’s opening body excerpt discusses operating AI services. It distinguishes applying SRE to AI from applying AI to SRE. It does not establish detailed procedures for the lifecycle-related headings. [observed] [Ch. 20, opening body excerpt](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch20.html)

This bounded TOC review does not establish global absence or presence of every topic. Such topics include offboarding, wipe, preemption, resize, and migration. Any such claim requires a defined scope and full-text search/review. Do not infer from omitted headings or import 1e content into 2e. [inference] [2e Contents](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)

## 3. Portable techniques and safe measured catches

The Ch. 15 introductory excerpt directly supports balancing demand/supply, cost, performance, reliability, business goals and explicit risk tolerance. The safe check below is a rack-bench proposal. For all other mechanisms, only the cited TOC heading is [observed]. Mechanism application to this bench is [inference]. None is a book-prescribed test or OEM acceptance threshold. PASS means rack-bench-measured evidence only.

Use an isolated test target and synthetic workload. Do not run live/destructive tests, firmware/OS changes, or repeated internet/storage performance. Reserve the final 20 minutes for cleanup. [inference] [lifecycle canon](../books.md)

1. **Demand/supply and explicit risk (Ch. 15).** Mechanism [observed]: capacity planning forecasts demand and provisions supply. It balances performance, cost and reliability around business goals and explicit risk tolerance.

   Safe measured catch [inference]: record expected synthetic workload, scheduler-visible GPU capacity, queue/start/completion timestamps, and uncertainty. A short run does not establish sustained capacity.

   [observed] [Ch. 15 opening excerpt](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html); [inference] check
2. **Lifecycle engagement beyond readiness (Ch. 7 TOC).** Mechanism [inference from heading]: consider SRE engagement after production-readiness review rather than treating readiness as the whole service lifecycle.

   Safe measured catch [inference]: tabletop one isolated test allocation’s named owner, handoff, support contact, and exit/closure evidence. Time completion and record missing ownership. Do not assert that this checklist is prescribed by the chapter.

   [observed] heading only [Ch. 7 TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [inference] proposal
3. **State legibility (Ch. 18 TOC).** Mechanism [inference from headings]: represent lifecycle state so an operator can inspect current state and reason about transitions.

   Safe measured catch [inference]: read-only compare declared state with scheduler/control-plane inventory for one isolated target. Record discrepancies and time to identify them. Do not modify state or claim the chapter prescribes this method.

   [observed] heading only [Ch. 18 TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [inference] proposal
4. **Correct delete/undelete (Ch. 17 TOC).** Mechanism [inference from heading]: treat deletion and recovery semantics as a resilience concern. The heading alone gives no operational recipe or sanitization assurance.

   Safe measured catch [inference]: inspect an already-authorized synthetic test-data workflow. Reconcile its test manifest before/after. Do not delete production data or infer secure wiping.

   [observed] heading only [Ch. 17 TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [inference] proposal
5. **Restore testing (Ch. 16 TOC).** Mechanism [inference from heading]: test restoration rather than relying only on backup status.

   Safe measured catch [inference]: use disposable synthetic data and an isolated target. Verify an existing approved restore rehearsal’s source identity, completion result, and content/hash reconciliation. Avoid production restore or storage-performance benchmarking.

   [observed] heading only [Ch. 16 TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [inference] proposal

## 4. Exact canon citation changes

- **Add/bump:** add 2e as its own edition-specific entry. Cite the publisher catalog for title/authors/imprint/September 2026/796 pages/ISBN and TOC. Cite Ch. 15 only for the limited opening excerpt quoted above. [observed] [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [Ch. 15 excerpt](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html)
- **Supersede narrowly:** if the canon says the *first edition* has no standalone capacity-planning chapter, retain that 1e statement. Add a 2e contrast: its TOC has Ch. 15 “Capacity Planning,” plus lifecycle-relevant Chs. 7, 16–18 and 20. Do not conflate editions. [observed] [2e TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp); [1e Google TOC](https://sre.google/sre-book/table-of-contents/)
- **Retain:** retain the 2016 1e citation and verified Google-hosted TOC as a distinct, accessible baseline. It cannot substantiate 2e chapters. [observed] [Google 1e TOC](https://sre.google/sre-book/table-of-contents/)
- **Date precision:** record September 2026; do not assert September 16 based on this catalog evidence. [observed] [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)

## Gaps

- The exact publication day remains unknown. The publisher catalog displays September 2026. [observed] [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- Full chapter bodies are not available for review in this research. The Ch. 15 quoted text is a limited opening excerpt, not full text. Access may vary, including Akamai 403. Ch. 20 likewise yields only an opening excerpt. All other chapter details in this note are TOC-only. [observed] [Ch. 15](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch15.html); [Ch. 20](https://learning.oreilly.com/library/view/site-reliability-engineering/9798341607675/ch20.html)
- This bounded contents review does not settle the full book’s treatment of spot/preemption, resizing/migration, or image/container lifecycle. It does not settle tenant offboarding, configuration drift, or secure data wiping. The Ch. 16/17 headings establish restore-testing and delete/undelete topics only. They do not establish secure erasure. Review licensed full text and applicable site/OEM procedures before making more specific claims. [inference] [2e Contents](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- The displayed ISBN is 9798341607675. This note establishes no second format/ISBN. [observed] [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
- The 1e TOC is independently accessible. Do not use it to fill 2e gaps. [observed] [Google 1e TOC](https://sre.google/sre-book/table-of-contents/); [O’Reilly 2e TOC](https://learning.oreilly.com/library/view/-/9798341607675/?orm_source=mcp)
