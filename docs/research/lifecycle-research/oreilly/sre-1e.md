# N09 — Site Reliability Engineering, 1e (2016)

Research date: 2026-10-11.

## 1. Metadata and access

1. **Catalog metadata [observed]:** *Site Reliability Engineering: How Google Runs Production Systems*, O’Reilly Media, published April 2016, 552 pages. ISBN 978-1-491-92911-7.

   Listed editors/authors: Niall Richard Murphy, Betsy Beyer, Chris Jones, Jennifer Petoff.

   The O’Reilly catalog is the source for this metadata. It does not itself provide primary evidence of chapter guidance. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781491929117/?orm_source=mcp)
2. **Access boundary [observed]:** This research fetches the exact requested O’Reilly URL. The fetch shows the title/catalog metadata and contents. It also shows the sign-in/“Read now Unlock full access” and trial/buy prompts. The fetched page shows no chapter-body text.

   The public Google-hosted SRE Book below provides accessible full text for cited passages. It is the publisher/author-hosted text, not evidence that the O’Reilly session grants access. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781491929117/?orm_source=mcp); [Google-hosted book TOC](https://sre.google/sre-book/table-of-contents/)
3. **Edition/authors corroboration [observed]:** Google Research identifies the title, four editors, and O’Reilly (2016). Google’s hosted book contents match the O’Reilly chapter sequence. The catalog gives April 2016 and 552 pages. [Google Research publication record](https://research.google/pubs/site-reliability-engineering-how-google-runs-production-systems/); [Google-hosted TOC](https://sre.google/sre-book/table-of-contents/); [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781491929117/?orm_source=mcp)

## 2. Relevant lifecycle chapters

- **Chapter 4, “Service Level Objectives” [observed]:** Google’s TOC verifies the chapter title. Its primary text defines service-level indicators, objectives, and agreements. It asks what users care about. It describes collecting indicators, defining objectives, and choosing targets. [Chapter 4 text](https://sre.google/sre-book/service-level-objectives/); [TOC](https://sre.google/sre-book/table-of-contents/)
- **Chapter 17, “Testing for Reliability” [observed]:** The TOC and chapter text verify this chapter. The text explicitly says passing tests does not prove reliability. It discusses smoke/system tests and configuration tests that compare actual configuration with intended files. It also discusses staged canaries with observation and reversion. [Chapter 17 text](https://sre.google/sre-book/testing-reliability/)
- **Chapter 18, “Software Engineering in SRE” [observed]:** The TOC and chapter text verify this chapter. Its contents explicitly include “Traditional Capacity Planning” and “Intent-Based Capacity Planning,” among other sections. This is a relevant capacity discussion inside Chapter 18, not a standalone “Capacity Planning” chapter. [Chapter 18 text](https://sre.google/sre-book/software-engineering-in-sre/); [TOC](https://sre.google/sre-book/table-of-contents/)
- **Chapter 27, “Reliable Product Launches at Scale,” and Appendix E, “Launch Coordination Checklist” [observed]:** Both titles and locations appear in the TOC. Chapter 27’s text discusses readiness checklists, resource/capacity assumptions, dependencies, rollout planning, validation steps, and contingency measures. [Chapter 27 text](https://sre.google/sre-book/reliable-product-launches/); [Appendix E](https://sre.google/sre-book/launch-checklist/); [TOC](https://sre.google/sre-book/table-of-contents/)
- **Chapter 32, “The Evolving SRE Engagement Model” [observed]:** The TOC verifies this chapter. Its text covers production readiness reviews and engagement. It supports explicit ownership/readiness conversations, not a rack-specific tenant-exit procedure. [Chapter 32 text](https://sre.google/sre-book/evolving-sre-engagement-model/); [TOC](https://sre.google/sre-book/table-of-contents/)

## 3. Transferable techniques and measured bench checks

These are adaptations for a rack-bench lifecycle on GB300/NVL72-class 18-tray racks in Chennai. They are not claims that the book prescribes GPU-rack procedures or acceptance thresholds.

Use an isolated, authorized target and disposable tenant. Do not run destructive/live tests, production eviction, firmware/OS changes, or repeat internet/storage performance tests. Reserve the final 20 minutes of the two-hour budget for cleanup. A verdict is PASS only on measured bench evidence. Absence of evidence is inconclusive.

[inference] Context: [rack-bench background](../books.md); source guidance: [SRE Chapter 17](https://sre.google/sre-book/testing-reliability/), [Chapter 27](https://sre.google/sre-book/reliable-product-launches/)

1. **Define observable SLO events across handoff to useful work [observed guidance; inference check]:** Chapter 4 says to define indicators/objectives and connect them to user concerns. For a disposable bench run, timestamp authorized provision/availability, scheduler-ready capacity, representative GPU job start, and verified useful-work completion. Report each interval and the locally agreed threshold separately. Do not call a source passage or inventory assertion a measured result.

   [Chapter 4](https://sre.google/sre-book/service-level-objectives/); [inference] check design.
2. **Use a bounded end-to-end smoke test [observed guidance; inference check]:** Chapter 17 calls smoke tests simple critical-behavior checks and emphasizes tests for reliability.

   Run a small, authorized representative GPU workload on the isolated target. Verify job completion and expected output. Retain timestamps/logs. A pass demonstrates this bounded path only. It does not establish sustained capacity or long-run reliability.

   [Chapter 17](https://sre.google/sre-book/testing-reliability/); [inference] check design.
3. **Reconcile declared configuration with observed configuration [observed guidance; inference check]:** Chapter 17 describes configuration tests that compare production’s actual configuration to a checked-in intended configuration and report discrepancies. For an approved, read-only bench check, compare recorded rack/tray identity and relevant scheduler/service configuration to the authorized manifest. Record mismatches rather than correcting them during the check. [Chapter 17](https://sre.google/sre-book/testing-reliability/); [inference] check design.
4. **Stage reversible change or resize/migration and verify before continuing [observed guidance; inference check]:** Chapters 17 and 27 discuss staged rollout, observation, validation, and reversal. Chapter 22’s TOC identifies planned changes, drains, or turndowns as a cascading-failure context.

   In this bench, exercise a reversible service/configuration-level resize or migration only on a dedicated isolated target. Require explicit operator authorization. Record before/after schedulable resources and representative job outcome. Stop on regression and restore the captured known-good state. Do not evict production workloads or change firmware/OS.

   [Chapter 17](https://sre.google/sre-book/testing-reliability/); [Chapter 27](https://sre.google/sre-book/reliable-product-launches/); [Chapter 22](https://sre.google/sre-book/addressing-cascading-failures/); [inference] check design.
5. **Make handoff, exit, and cleanup explicit, then verify the observed state [observed guidance; inference check]:** Chapter 27’s launch checklist text stresses concrete assigned actions and documented manual processes. Chapter 32 provides production-readiness engagement context.

   Rehearse only with a disposable tenant. Record named owner/handoff. Stop or disposition synthetic work per policy. Revoke test access using the authorized procedure. Verify allocation is removed. Reconcile the target’s post-check state.

   Tenant deletion or a status flag does not prove reclaim/wipe. This bench includes no destructive wipe or production tenant exit. Use final 20 minutes to restore and verify safe state and preserve evidence.

   [Chapter 27](https://sre.google/sre-book/reliable-product-launches/); [Chapter 32](https://sre.google/sre-book/evolving-sre-engagement-model/); [inference] check design.

## 4. Canon relation

This is the 2016 first-edition baseline. The O’Reilly 1e catalog and the public Google-hosted text ground it in the matching 1e chapter sequence. Retain these 1e edition-specific links and chapter numbers when citing this node. Do not automatically transfer them to a later edition. [observed] [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781491929117/?orm_source=mcp); [Google-hosted TOC](https://sre.google/sre-book/table-of-contents/)

Chapter 18 includes explicit traditional and intent-based capacity-planning discussion. There is **no standalone chapter titled “Capacity Planning.”** Chapter 27 and Appendix E are launch/readiness material. Chapter 32 is the engagement model. None is a GB300 qualification, safe eviction, migration, sanitization, or tenant-offboarding specification. [observed] [TOC](https://sre.google/sre-book/table-of-contents/); [Chapter 18](https://sre.google/sre-book/software-engineering-in-sre/); [Chapter 27](https://sre.google/sre-book/reliable-product-launches/); [inference] scope limit.

## Gaps

- **Rack-specific validation [inference]:** The book does not supply GB300/NVL72 18-tray procedures, Chennai site limits, firmware/OS change order, or hardware acceptance thresholds. Use OEM/site procedures before any such work. [NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)
- **Operational lifecycle limits [inference]:** These cited passages do not establish a safe production preemption/eviction protocol or migration guarantees. They do not establish tenant-exit authorization or secure media sanitization. A short disposable-tenant drill cannot certify them. [Chapter 17](https://sre.google/sre-book/testing-reliability/); [Chapter 27](https://sre.google/sre-book/reliable-product-launches/)
- **Measurement limits [inference]:** A two-hour bench check can reveal a failed transition or missing evidence. It cannot prove fleet capacity, long-horizon availability, durable wipe, or production reliability. Define local acceptance thresholds and preserve sample counts, raw outputs, times, and target identity. [Chapter 4](https://sre.google/sre-book/service-level-objectives/); [Chapter 17](https://sre.google/sre-book/testing-reliability/)
