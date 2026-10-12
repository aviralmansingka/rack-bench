# Data Centre Essentials

Research date: 2026-10-11.

## 1. Access and source status

1. **Requested O’Reilly access.** [observed] This research fetches the supplied O’Reilly URL first. The O’Reilly platform gates its content by authentication in this research context. The page does not provide inspectable book text. https://learning.oreilly.com/library/view/-/9781119898818/?orm_source=mcp
2. **Best primary source.** [observed] Wiley’s publisher page identifies the title, authors, July 2023 publication, publisher, 240 pages, and format-specific ISBNs. This page makes an appropriate primary metadata/description source. It does not give a full-text chapter preview. https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591
3. **Primary publisher TOC.** [observed] Wiley-VCH product page for the requested hardcover ISBN exposes contents headings and page numbers. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8

## 2. Edition and metadata

[observed] Wiley lists Vincent Fogarty and Sophia Flucker as authors, Wiley-Blackwell as publisher/imprint, July 2023, and 240 pages. The supplied ISBN 9781119898818 is the hardcover ISBN. Wiley also lists PDF ISBN 9781119898825 and e-book ISBN 9781119898832. https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591

[observed] Wiley describes the work as a broad, accessible survey of data-centre design, construction, and operation. Wiley intends it to give non-specialists a high-level understanding. The book is not a technical deep dive. https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591

[observed] Wiley-VCH’s publisher product page exposes the detailed contents and page locations for hardcover ISBN 978-1-119-89881-8. The page labels it first edition, September 2023. Wiley Online Books search results independently identify DOI 10.1002/9781119898849, title, authors, first publication date, and chapter pages. Bot verification blocks direct fetching of that platform. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8 ; https://onlinelibrary.wiley.com/doi/book/10.1002/9781119898849

## 3. Verified chapter coverage and locations

[observed] Wiley-VCH’s publisher page lists the chapter topics and exact contents/page locations below. This verifies chapter coverage and headings only, not specific instructions in chapter bodies. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8

1. **Chapter 3, “Site Selection,” p. 23.** [observed] The chapter includes climate, access, air quality, natural-disaster risk, ground conditions, and communications infrastructure. It also includes power, natural resources, regulation, stakeholders, and due diligence. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8
2. **Chapter 5, “Overview of Infrastructure,” p. 89.** [observed] Includes power, cooling, BMS, fire, and security. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8
3. **Chapter 6, “Building a Data Centre: Stakeholders, Design, Construction, and Commissioning,” p. 109.** [observed] Sections include project stages, pre-project, pre-design, design, procurement, and construction. Sections also include commissioning (p. 122), handover (p. 124), and operation (p. 125). “Planning” appears as pre-project/pre-design rather than a chapter explicitly named Planning. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8
4. **Chapter 7, “Operational Issues,” p. 127.** [observed] Sections include handover, legacy facilities, operations team, uptime and failures, and maintenance processes and procedures (p. 133). Sections also include managing change, capacity management, training, and performance optimisation beyond reactive maintenance. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8
5. **Chapter 9, “Sustainability,” p. 163.** [observed] Includes energy, water, lifecycle impacts, and policy/regulation. The contents list no dedicated end-of-life/decommissioning chapter or heading. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8

## 4. Lifecycle techniques and safe measured bench checks

[observed] Chapter titles/TOC headings give the evidence for the book’s coverage below. The checks are design-basis inferences for rack-bench. They are not book-prescribed instructions, thresholds, or claims of having tested hardware. A PASS must come from rack-bench measurements and recorded evidence. Never attribute it to the source. Facility commissioning, power, and cooling tests require OEM/site approval. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8

1. **Readiness evidence and handover.** [observed] Chapters 6–7 cover commissioning, handover, and operations.

   [inference] For a rack-bench transition, record expected versus observed rack/tray inventory. Record provisioning/image-bringup milestones and scheduler-visible resources. Record a bounded authorized workload’s measured start/completion and useful result. Report missing evidence as inconclusive, not pass.

   Design basis: [Wiley scope](https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591); [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).
2. **Change control with before/after state.** [observed] Chapter 7 lists managing change.

   [inference] For an approved, reversible tenant/service-level change only, capture target, approval, baseline, and intended state. Capture measured outcome and restoration check. Use a disposable/isolated workload. Do not alter firmware or OS.

   Design basis: [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).
3. **Capacity and drift reconciliation.** [observed] Chapter 7 lists capacity management and performance optimisation.

   [inference] Snapshot configured versus observed inventory/capacity before and after a bench category. Identify unexplained deltas and configuration drift. Distinguish provisioned, schedulable, and measured-useful capacity. Do not infer facility power/cooling headroom from software inventory.

   Design basis: [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).
4. **Maintenance/failure learning.** [observed] Chapter 7 explicitly covers uptime/failures and maintenance processes.

   [inference] Use existing logs and non-destructive checks to record failure symptoms, timestamps, attribution, and recovery. Preserve failures as evidence. Verify safe return to the prior state. No induced facility fault or destructive test.

   Design basis: [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8).
5. **Tenant exit and hygiene boundary.** [observed] The TOC covers operation and sustainability/lifecycle impacts. It does not document a dedicated tenant offboarding, media sanitisation, or facility end-of-life procedure.

   [inference] A safe rack-bench rehearsal can measure admission denial, test-identity revocation, authorized synthetic-job disposition, inventory reconciliation, and capacity release. Record wipe/sanitisation as a separate controlled workflow with its own approved evidence. Do not claim deletion or forensic sanitisation based on namespace removal or a short command check.

   Design basis: [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8); [NIST SP 800-88 Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final).

[observed] The contents identify facility commissioning and operational-maintenance subject areas, not GB300/NVL72 procedures. [inference] For the Chennai GB300/NVL72-class 18-tray context, this plan proposes no physical power/cooling commissioning. It proposes no live/destructive test or whole-rack power cycle. It proposes no production eviction, repeated storage/internet performance test, or firmware/OS change. Any facility-level power/cooling test requires OEM and site approval.

A two-hour category uses the final 20 minutes for cleanup. If safe cleanup cannot be completed, mark the category inconclusive and continue restoration. Design basis: [TOC](https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8); [NVIDIA GB300 NVL72 overview](https://www.nvidia.com/en-us/data-center/gb300-nvl72/).

## 5. Canon relation

[observed] Existing canon names three works as the core lifecycle spine. These works are SRE Workbook, *The Practice of System and Network Administration*, and *Building Secure and Reliable Systems*. Its scope is service/tenant lifecycle evidence, change, recovery, and offboarding.

[inference] *Data Centre Essentials* should be a **facility supplement**, not a replacement or extension of the tenant lifecycle core. Use it for facility siting, infrastructure context, construction/commissioning/handover, operations, maintenance, capacity, and sustainability. Keep rack-bench provisioning, image bringup, spot/preempt, resize/migrate, and reclaim/wipe hygiene grounded in the existing tenant/SRE/security canon. Keep tenant offboarding grounded in that canon and local approved procedures. [observed] The book explicitly presents itself as high-level non-expert coverage, not a technical deep dive. Sources: [books.md canon](../books.md); [Wiley description](https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591).

## Gaps

- [observed] Wiley’s public page verifies authors, title, publisher, July 2023, page count, and ISBN variants. It does not expose a public chapter preview/TOC in the fetched page. https://www.wiley.com/en-us/Data+Centre+Essentials%3A+Design%2C+Construction%2C+and+Operation+of+Data+Centres+for+the+Non-expert-p-00400591
- [observed] Wiley-VCH provides an authoritative publisher TOC for the hardcover ISBN. Bot verification blocks direct Wiley Online Library book/chapter fetches. The bounded search finds no publisher-distributed Pageplace preview. The primary TOC establishes chapter headings only. This review claims no specific chapter-body instruction. https://www.wiley-vch.de/en/areas-interest/engineering/data-centre-essentials-978-1-119-89881-8
- [inference] This research finds no verified coverage of rack-level tenant offboarding, secure wipe, GB300/NVL72-specific commissioning, or end-of-life facility decommissioning. Check the licensed O’Reilly text and current OEM/site-approved procedures for those topics. Do not infer procedures from TOC headings. https://learning.oreilly.com/library/view/-/9781119898818/?orm_source=mcp
