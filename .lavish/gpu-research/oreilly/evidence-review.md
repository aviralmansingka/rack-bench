# O'Reilly evidence review

Research date: 2026-10-11.

## Evidence rules

The captain gives ten catalog records.
The children first check each supplied O'Reilly URL.
An access failure does not show that a record or chapter does not exist.
Public tables of contents show topics, not complete test procedures.

Keep proposed GPU techniques as inferences unless public text directly states the technique.
An ISBN-10 and its ISBN-13 equivalent name the same product.
A different ISBN does not, by itself, show a different edition.
Keep publication date, copyright year, and page count separate.

## Decisive passages checked

- [Gregg 2e publisher](https://www.informit.com/store/systems-performance-9780136821649): second edition; 928 pages; copyright 2021; eBook ISBN 9780136821649.
- That publisher lists methodology, statistics, observability, and benchmarking sections.

- [Cook publisher](https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4): twelve chapters; error handling, profiling, memory, power, and cooling topics.
- [PMPP 4e publisher](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0): 23 chapters and numerical considerations.
- Chapters 4–6 cover execution, memory architecture, and performance considerations as separate topics.
- [CUDA by Example publisher](https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683): first edition; 320 pages; copyright 2011; print ISBN 9780131387683.
- Its contents include events, synchronization, atomics, streams, and twelve chapters.

- [Fregly companion README](https://raw.githubusercontent.com/cfregly/ai-performance-engineering/main/README.md): November 2025 publication statement and twenty chapter headings.
- [Fregly companion checklist](https://raw.githubusercontent.com/cfregly/ai-performance-engineering/main/docs/appendix.md): matched workloads, warmup, CUDA events, output references, and raw artifacts.
- [Wiley description](https://www.wiley.com/en-us/Professional+CUDA+C+Programming-p-9781118739327): Cheng, Grossman, McKercher; execution, memory, concurrency, profiling, and tuning topics.
- [Bondi publisher TOC](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf): fifteen chapters; measurement validation and pilot testing.

- The Fregly companion checklist also gives configuration changes that the bench must not copy.
- Its clock, power, MIG, and persistence advice does not change the bench safety contract.

The orchestrator checks these passages with `web_fetch`.
These checks do not show access to complete book text.
Living companion documents can change after book publication.
The accepted source notes keep their other source URLs and access limits.

## Corrections

- Remove unsupported catalog-format labels.
- Do not treat ISBN-10 and ISBN-13 forms as separate formats.
- Do not call Prentice Hall an Addison-Wesley imprint.
- Separate 2020 publication from Gregg's 2021 copyright field.

- Separate approved active workloads from passive collection.
- Keep configurations unchanged during active workloads.

- Correct PMPP's second-edition product identifier to 9780124159921.
- Withdraw old-edition metadata claims from unfetched WorldCat records.
- Keep older/later edition and format gaps explicit.
- Correct local links from the source-note directory.

## Gaps

No source check measures a GPU on the target rack.
The supplement supplies no universal GB300 acceptance rule.
O'Reilly access failures and search limits restrict full-text and metadata checks.
The final supplement lists each unresolved source gap.
