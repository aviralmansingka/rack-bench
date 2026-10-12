# Final targeted public-retrieval retry

Research date: 2026-10-11.

## 1. Scope

The parent sends one final retry request for four source gaps.
The original eleven-node map keeps its unchanged state.
Four fresh researchers use `openai-codex/gpt-6-luna`.
Each researcher makes changes only to its existing source note.
No researcher makes project file changes or starts agents.

## 2. Retrieval plan

| Node | Source | Retry child | Different retrieval routes |
| --- | --- | --- | --- |
| N02 | VandenBrink second edition | oreilly2-linux-networking-2e | Alternate Packt catalog/sample paths, public previews, author pages |
| N05 | Dutt | oreilly2-cloud-native-fabrics | O'Reilly shop/legacy catalog TOC, public previews, author pages |
| N06 | Prowse | oreilly2-linux-networking-video | Matching Pearson/InformIT catalog and sample outline, public previews, author announcement |
| N11 | White | oreilly2-modern-troubleshooting | Event schedule, publisher calendar, dated author announcements and archives |

## 3. Acceptance rule

Check matching edition, identifier, and format before accepting new evidence.
Do not bypass authentication or security verification.
Do not claim video viewing, recording access, or unseen full text.
Keep inferred rack techniques separate from attributed source instructions.
The orchestrator checks decisive passages after the researchers return.

Each unclosed retrieval gap shows this final declaration:
“not publicly retrievable as of 2026-10-11”.
Use the declaration only for the specified missing field or source material.
No catalog or book result shows rack PASS.

## 4. Result

The final retry is complete.
The orchestrator checks all four updated source notes from disk.
Each brief is complete.
Each source still keeps specific missing material.

One recovery resume sends the video child's updated source note.
The orchestrator checks that final note and publisher TOC directly.
No third researcher is necessary.
No child keeps assigned unfinished work.

| Source note | Brief | Source evidence | Final verdict |
| --- | --- | --- | --- |
| [VandenBrink 2e](linux-networking-2e.md) | Complete | Partial: matched metadata; no TOC/sample | HOLD chapters; conditional host SKIM |
| [Dutt](cloud-native-fabrics.md) | Complete | Partial: selected indexed chapters; incomplete primary TOC | KEEP selective Ethernet architecture |
| [Prowse](linux-networking-video.md) | Complete | Partial: complete InformIT TOC for a separate ISBN | Host/bootstrap SKIM; SKIP required fabric reading |
| [White](modern-troubleshooting.md) | Complete | Partial: public agenda and explicit 2023 announcement | SKIM methods; no fabric qualification rules |

### 4.1 VandenBrink second edition

[observed] Google Books shows a title, author, and ISBN match, but shows 2025 and no explicit edition label.
O'Reilly shows August 2026; Amazon shows September 9, 2026.
Packt's US, GB, and Poland routes show security verification.
Google Books shows no preview; the Amazon ISBN endpoint shows no readable listing.
No first-edition chapter makes second-edition evidence.

[observed] Second-edition TOC/sample and publication-date reconciliation: not publicly retrievable as of 2026-10-11. [Packt](https://www.packtpub.com/en-us/product/linux-for-networking-professionals-second-edition-9781835881101) [Google Books](https://books.google.com/books?vid=ISBN9781835881101) [O'Reilly](https://www.oreilly.com/library/view/linux-for-networking/9781835881101) [Amazon](https://www.amazon.com/dp/1835881106)

### 4.2 Dutt

[observed] The retry shows publisher-indexed Chapters 2, 11, and 18 and Google Books chapter-list excerpts.
These chapters show Clos topology, observability, and configuration validation.
No direct fetch shows a complete primary TOC or chapter prose.
The Google Books record shows November 22, 2019 and 486 pages.
The supplied catalog shows 483 pages; the author interview shows a May 16, 2020 date.

The public preview's purchase links use ISBN 9781492045571.
Keep these format identifiers, dates, and page counts separate.
Gai's “my book” Chapter 2 makes reference to Gai's book, not Dutt's chapter number.
The interview shows Dutt's Clos material, not that exact chapter assignment.

[observed] Complete primary TOC/Look Inside and Chapter 5 title/number: not publicly retrievable as of 2026-10-11. [O'Reilly](https://www.oreilly.com/library/view/cloud-native-data/9781492045595) [Google Books](https://books.google.com/books/about/Cloud_Native_Data_Center_Networking.html?id=79i_DwAAQBAJ) [Amazon](https://www.amazon.com/Cloud-Native-Data-Center-Networking/dp/1492045608)

### 4.3 Prowse

[observed] InformIT shows first-edition Online Video metadata, copyright 2024, and a complete publisher TOC.
The TOC shows four modules and seventeen lessons.
Its ISBN is 9780138357979, not the supplied O'Reilly identifier 9780138358051.
The author shows both products under the matching course title.

That link does not show identical manifests or runtime.
The publisher shows “Over 10 Hours” and separately shows “over 8 hours” of discussion and demos.
No researcher runs the video.

[observed] Exact O'Reilly release date, 623-minute runtime attribution, and InformIT/O'Reilly TOC correspondence: not publicly retrievable as of 2026-10-11. [O'Reilly](https://www.oreilly.com/videos/linux-networking/9780138358051) [InformIT](https://www.informit.com/store/linux-networking-basics-and-beyond-video-course-9780138357979) [Author catalog](https://prowse.tech/recorded_training)

### 4.4 White

[observed] The author explicitly shows January 26, 2023 and puts a link to the exact event ID.
This shows the date of that advertised session, not every session under the ID.
A later announcement puts a link to the same ID without a session year.
The public O'Reilly listing shows no year.

The earlier 2024 inference does not show the explicitly dated 2023 announcement.
The supplied 2025 metadata still shows no uniquely dated matching session.
The public agenda does not show delivered content.

[observed] Supplied 2025 session attribution, recording, transcript, and delivered-content evidence: not publicly retrievable as of 2026-10-11. [Explicit 2023 announcement](https://rule11.tech/modern-network-troubleshooting) [Later announcement](https://rule11.tech/upcoming-pearson-class-modern-network-troubleshooting) [Public listing](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)

## 5. Handoff

Seven supplement nodes keep `done`; four keep field-specific `gap` states.
The states show research evidence, not rack certification.
The operational canon and measured-PASS boundary keep their unchanged state.

The [supplement](../oreilly.md), [lessons](research.md), and [evidence checks](EVIDENCE-CHECKS.md) keep the final findings.
The [distilled reading list](../docs/network-bench-research.md#reading-list) keeps the retry summary.
The parent must make that changed document public and make its relative links fit.
The orchestrator makes no changes to project files.

Both report checks show a pass: seven original lessons and eleven supplement lessons are below 50 lines.
The artifact check shows eleven briefs, eleven source records, and zero local-link errors.
No own-prose sentence uses 20 or more words.
Run `python3 .lavish/network-research/check-artifacts.py` from the worktree to check these artifacts.
