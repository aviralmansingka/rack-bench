# N05 — Pro DNS and BIND

Research date: 2026-10-11. Researcher: oreilly-pro-dns-N05.

## Observed edition evidence

Springer/Apress lists Ron Aitchison's Pro DNS and BIND as edition 1, 608 pages.
The print ISBN is 9781590594940, with publication date 23 August 2005.
The ebook ISBN is 9781430200505, with publication date 22 November 2006.
The publisher describes BIND 9.3.0. The supplied 605-page count differs from the publisher's 608 pages.
The supplied O'Reilly URL returns access denial. Central catalog evidence supplies its platform record.

Springer separately lists Pro DNS and BIND 10 as edition 1.
Print ISBN: 9781430230489, 25 February 2011.
Ebook ISBN: 9781430230496, 20 July 2011.
The publisher lists XXX, 692 pages and a BIND 10 focus.
Do not call this separately titled book a verified second edition of the 2005 title.
Do not treat its old BIND description as current implementation guidance.

## Chapter evidence

The returned brief lists these chapters for the 2005 book:

1. An Introduction to DNS
2. Zone Files and Resource Records
3. DNS Operations
4. DNS Types
5. DNS and IPv6
6. Installing BIND
7. BIND Type Samples
8. Common DNS Tasks
9. DNS Diagnostics and Tools
10. DNS Secure Configurations
11. DNSSEC
12. BIND Configuration Reference
13. Zone File Reference
14. BIND APIs and Resolver Libraries
15. DNS Messages and Records

Chapters 3, 9, and 15 have the closest diagnostic fit.
The researcher reports publisher TOC evidence and a secondary scan for detailed topic checks.
The orchestrator's publisher fetch shows 15 chapters. Its extraction omits their titles.
The 2011 full chapter list remains incomplete. Do not transfer chapter numbers between these titles.

## Proposed bench techniques — inferences

1. Record resolver address, answer, response code, and timing. Compare configured and selected resolvers.
2. Repeat lookups for actual artifact hosts during the window. Report observed failures, not a DNS SLA.
3. Compare EDNS and ordinary queries. Record truncation, timeout, and TCP completion.
   The chapter topics support message analysis, not a verified modern padded-response test recipe.
4. Separate DNS timing from connect, TLS, and sustained transfer timing.
5. Keep resolved addresses with MTR and transfer evidence. DNS does not prove routes or peering quality.

## Canon verdict

New optional DNS background. Do not change the four-book spine.
The book supports DNS fault evidence, not sustained-rate or TCP certification thresholds.
Skip BIND installation and authoritative-server administration unless a DNS failure requires that work.

## Gaps and source limits

- Direct O'Reilly access remains unverified.
- Full-text procedures and current DNS transport policy require current primary documents.
- The researcher uses a third-party scan for detail. Publisher metadata takes priority.
- The 2011 title's full TOC remains incomplete.

## Sources

- [2005 Springer/Apress record](https://link.springer.com/book/10.1007/978-1-4302-0050-5).
- [2011 Springer/Apress record](https://link.springer.com/book/10.1007/978-1-4302-3049-6).
- [Supplied O'Reilly record](https://learning.oreilly.com/library/view/-/9781590594940/?orm_source=mcp).
- Secondary scan reported by researcher: https://theswissbay.ch/pdf/Gentoomen%20Library/Operating%20Systems/Linux/DNS/Pro%20DNS%20and%20BIND.pdf
- Local canon: `.lavish/internet-research/books.md`; `docs/internet-quality-research.md`.

The orchestrator checks both Springer records for edition, dates, ISBNs, and page counts.
