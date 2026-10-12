# O'Reilly INTERNET research handoff

Research date: 2026-10-11.
Worktree: `/home/avirus/.herdr/worktrees/rack-bench/research-internet`.
Branch: `research/internet`.
Status: complete, with declared evidence gaps.

## Result

The supplement covers all 15 sources. Each source has a note and an evidence-review record.
The research report contains the full map and one short lesson per node.
The updated canon keeps the ranked eight and the four-book spine.
The staged reading list waits for parent publication.
This run makes no project document changes.

Keep Gregg, Fall and Stevens, HPBN, and Jain as the spine.
Keep Sanders third edition as the main practical capture supplement.
Change Sloan from blanket SKIP to optional method SKIM.
Treat Schroder as a separate new candidate.
Hold VandenBrink's second edition until release and contents agree.

## Per-source verdicts

These labels compare each source with the existing canon.
**Confirm** keeps an existing recommendation. **New** adds an optional candidate, not a spine replacement.
**Supersede** replaces an earlier verdict or record. **Still-skip** keeps an earlier rejection.
No assessed source needs a still-skip verdict. Sloan's prior rejection changes; Schroder has no prior rejection.

| Node | Source | Change | One-line verdict | Declared limit |
| --- | --- | --- | --- | --- |
| N01 | TCP/IP Illustrated | Confirm; supersede wrong link | MUST: keep Fall and Stevens Volume 1 second edition. | Supplied 020163354X names the implementation volume; platform access remains unverified. |
| N02 | High Performance Browser Networking | Confirm; correct ISBN and BDP claim | MUST: keep free fundamentals; remove the impossible-window claim. | Corrected ISBN lacks an explicit format label; current CC needs separate sources. |
| N03 | Practical Packet Analysis | Confirm; correct classifier claims | MUST-lite: keep third edition as the main practical capture supplement. | Full third-edition text access remains unverified; Wireshark labels are heuristic evidence. |
| N04 | DNS and BIND | New | SKIM: fifth-edition resolver and troubleshooting chapters. | Child and orchestrator fetch access differs; old BIND versions need current documents. |
| N05 | Pro DNS and BIND | New | Optional DNS background; no spine promotion. | The separately titled 2011 book is not a verified second edition; complete 2011 TOC is missing. |
| N06 | DNS and BIND on IPv6 | New | SKIM: DNS data and transport distinctions; DNS64 only when applicable. | Direct metadata and full-text access remain limited. |
| N07 | Content Delivery Networks | New | SKIM Chapters 2–4 for request routing and goodput context. | TOC evidence does not establish current object-store procedures or physical cache location. |
| N08 | Packet Analysis with Wireshark | New; bounded | Optional SKIM; not a Sanders replacement. | Complete chapter hierarchy and exact examples remain unverified. |
| N09 | Wireshark 101 video | New; bounded | Optional guided packet-analysis labs. | Identifiers, supplied date, and exact runtime differ; playback remains unverified. |
| N10 | Packet Analysis Using Wireshark event | New; bounded | Optional security-focused introduction, not certification authority. | Supplied 2025 date and recording availability remain unverified. |
| N11 | Network Troubleshooting Tools | Supersede SKIP | Optional method SKIM of Chapters 4 and 12; keep off spine. | Historical details partly use secondary evidence; commands need current documents. |
| N12 | Linux Networking Cookbook | New | Optional Chapter 19 SKIM; separate from Sloan's book. | Detailed sections use secondary evidence; complete primary TOC remains unavailable. |
| N13 | Linux for Networking Professionals 2e | New; HOLD | Hold purchase and chapter recommendations until release and contents agree. | O'Reilly reports 2026; Amazon and OverDrive report 2027; complete 2e TOC is missing. |
| N14 | Modern Network Troubleshooting event | New; bounded | Optional method training, not measurement thresholds. | Supplied 2025 date, recording, and detailed exercises remain unverified. |
| N15 | Systems Performance | Confirm; reject wrong-edition detail | MUST: retain rank 1 and correct second-edition TOC evidence. | Detailed Chapter 10 inventory and direct platform access remain unverified. |

## Canon changes

1. Correct the O'Reilly TCP/IP volume link. Keep the recommended Volume 1 second edition.
2. Keep print and platform identifiers separate. Keep record-specific page counts visible.
3. Correct HPBN ISBN to 9781449344764 without an unsupported format claim.
4. Replace the impossible-window claim with RFC 7323's actual encoded receive-window maximum.
5. Use 781.25 MB decimal for 25 Gbps at 250 ms. Use example RTT, not implied rack measurements.
6. Remove the assumption that a configured `tcp_wmem` maximum alone proves a rate ceiling.
7. Confirm Sanders's CLI, transport, and slow-network chapters. Correct Wireshark classifier claims.
8. Identify zero-window senders separately by direction. Do not equate first-byte timing with pure server processing time.
9. Limit RTO and DSACK causal conclusions. The books do not establish automatic FAIL thresholds.
10. Replace Sloan's blanket SKIP with optional method SKIM. Add Schroder as a separate optional candidate.
11. Add bounded DNS, IPv6-DNS, CDN, and training candidates. Keep VandenBrink on hold.
12. Keep Gregg's publisher-confirmed section headings. Reject the first-edition detailed inventory as second-edition evidence.

## Evidence checks

The orchestrator checks decisive primary passages before accepting important claims:

- Pearson: Volume 1 second-edition chapters and relevant sections.
- RFC 7323 §§2.2–2.3: shift count 14 and maximum encoded window calculation.
- O'Reilly errata: HPBN corrected ISBN, without explicit format confirmation.
- No Starch first-edition release: May 2007, 192 pages, ISBN 9781593271497.
- Current Wireshark guide: capture-order processing, several classifier conditions, and interpretation ambiguity.
- Springer: 2005 edition identity and separately titled 2011 BIND 10 record.
- RFCs 10001 and 9715: current mixed-family DNS and fragmentation guidance.
- Wiley TOC: request routing, goodput, object size, and latency sections.
- InformIT: Greer's video metadata and lessons; Gregg's correct second-edition metadata and TOC.
- O'Reilly event agendas: Chow and White topics, without inferred session dates or playback entitlement.
- Google Books and Linux Journal: Sloan's baseline and combined-tool method.

Several publisher fetches fail. The source notes identify indexed, central-catalog, and secondary evidence.
The researcher reports a complete DNS and BIND catalog list. The orchestrator cannot reproduce direct access.
The orchestrator does not treat that difference as proof of full-text entitlement.

## Recovery and corrections

All 15 nodes use the original researchers. No completed node restarts.
N08 first fails with a provider idle timeout. One same-child resume returns a bounded brief.
Follow-ups correct the TCP window claim, historical page count, wrong-edition Gregg TOC, and Schroder/Sloan confusion.
A follow-up limits the IPv6-DNS metadata access claim.
The captain resumes the orchestrator after a provider error. The saved artifacts remain available.
The orchestrator completes integration from the notes. It starts no new searches or researchers.

## Checks

The structural checker passes:
`Passed: 15 nodes, 15 lessons, each below 50 lines.`

Command:
`node /home/avirus/.agents/skills/research/scripts/check-report.mjs /home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/research.md`

The supplement contains a research date, 15 numbered source sections, coverage limits, and a final Gaps section.
All 15 notes and all 15 node records exist.
Local artifact checks pass: source coverage, 15 notes, 15 node records, local links, and BDP arithmetic.
Git confirms branch `research/internet`. Its status retains the initial untracked paths.
The structural checker does not validate vocabulary, source accuracy, or real rack performance.

## Parent publication steps

1. Review the [supplement](../oreilly.md) and [updated canon](../books.md).
2. Publish the replacement Reading list from [reading-list-update.md](reading-list-update.md).
3. Publish the staged Window/BDP bullet correction in the project's failure-mode catalog.
4. Review the additional RTO, DSACK, and physical-cache-location flags before publication.
5. Keep all catalog-access and measurement gaps visible.

The orchestrator leaves `docs/internet-quality-research.md` and other project files unchanged.
The worktree already contains untracked `.lavish/` and `docs/internet-quality-research.md` content.
Do not remove that content. Do not treat it as unrelated damage from this run.

## Absolute artifact paths

- Supplement: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly.md`.
- Canon: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/books.md`.
- Map and lessons: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/research.md`.
- Staged reading list: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/reading-list-update.md`.
- Handoff: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/ORCHESTRATOR-REPORT.md`.
- Source notes: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/{tcpip,hpbn,ppa,dns-bind,pro-dns,dns-ipv6,cdn,nath,greer,chow,sloan,cookbook,linux-pro,white,gregg}.md`.
- Evidence records: `/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/oreilly/nodes/N01.md` through `N15.md`.

## Declared gaps

- Catalog visibility does not prove full-text, acquisition, or recording entitlement.
- Authentication and bot checks prevent several direct publisher checks.
- Nath's complete TOC and exact examples remain unavailable.
- Greer's product identifiers, supplied date, and exact runtime remain unresolved.
- Chow's and White's dates and recording availability remain unverified.
- VandenBrink's 2e release dates conflict; complete contents remain unavailable.
- HPBN's corrected ISBN lacks an explicit format label in the checked record.
- Historical Sloan and Schroder detail partly depends on secondary evidence.
- Aitchison's 2011 complete TOC and Gregg's detailed 2e network inventory remain unverified.
- Current cloud-object behavior, BBR/QUIC diagnosis, and quantitative PASS gates require separate primary evidence.
- No catalog review or two-hour window establishes long-term availability, diurnal behavior, or measured Chennai routes.
