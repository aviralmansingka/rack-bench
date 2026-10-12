# Lifecycle research run

Research date: 2026-10-11.

Question: Which lifecycle faults can rack-bench measure during a two-hour tenant certification window?

Audience: GB300-class rack operators and GPU tenants in Chennai, India.
Scope: provisioning, environment bring-up, preemption, resize, migration, reclaim, offboarding, support, and fleet drift.
Exclusions: repeat internet throughput research, repeat storage performance research, code changes, and live destructive tests.

Seven independent category briefs support this run:

| Node | Brief | Child |
| --- | --- | --- |
| N01 | neoclouds.md | neoclouds |
| N02 | hyperscalers.md | hyperscalers |
| N03 | ai-labs.md | ai-labs-g2 (replacement) |
| N04 | large-companies.md | large-companies |
| N05 | clustermax.md | clustermax |
| N06 | academia.md | academia |
| N07 | books.md | books-g2 (replacement) |

`research.md` holds the node map, state, and short lessons.
`nodes/` indexes the complete accepted category briefs.
`docs/lifecycle-bench-research.md` holds the distilled bench design.
`ORCHESTRATOR-REPORT.md` holds the handoff and limits.

This agent writes only inside this research run directory.
The parent can copy the distilled design to the project path `docs/lifecycle-bench-research.md`.
The agent does not change project files.

Use primary sources for technical claims.
Keep observed facts, calculations, and inferences separate.
A complete brief can contain explicit evidence gaps.

The second pass replaces N03 and N07. N07 closes its chapter-evidence gap.
N03 closes its EleutherAI setup gap but retains the numeric MosaicML spot-use gap.

The O’Reilly supplement adds eleven independent source notes in `oreilly/`.
`oreilly/research.md` gives their map, states, and short lessons.
`oreilly.md` gives the aggregate review. The supplement completes seven source nodes; four retain material gaps.

The canon adds SRE second edition without changing first-edition chapter citations.
Primary Wiley-VCH contents verify facility chapter headings.
BSRS sanitization means recovery integrity here, not physical-media erasure.
No document or vendor claim counts as a measured bench PASS.
