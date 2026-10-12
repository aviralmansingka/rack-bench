# internet-research — diagnosing internet quality

Parallel researcher subagents produce seven sourced research briefs, one per category, on 2026-10-11:

- `neoclouds.md` — GPU clouds: what they publish, test, and guarantee
  about north-south internet quality
- `hyperscalers.md` — AWS / Azure / GCP: published network-performance
  methodology and diagnostic runbooks
- `ai-labs.md` — how AI labs and model trainers consume and diagnose
  WAN links (HF ingress, container pulls, checkpoint egress)
- `large-companies.md` — Netflix, Cloudflare, Akamai, Google, Meta,
  Spotify: internet-quality diagnosis at consumer/edge scale
- `clustermax.md` — the internet/WAN slice of the ClusterMAX rating
  system
- `academia.md` — measurement science: IPPM RFCs, bufferbloat, BBR,
  Netalyzr, Hubble, M-Lab, FCC MBA
- `books.md` — ranked canonical books for internet-quality diagnosis

The sibling directory `.lavish/storage-research/` holds the storage/disk twin of this research.
Its location is the main repo checkout (`git worktree` of the same project).
Format exemplar for every brief here:
`/home/avirus/rack-bench/.lavish/storage-research/clustermax.md`.

These briefs produce the distilled output in
`docs/internet-quality-research.md` (failure-mode catalog + suite
design), parallel to `docs/storage-bench-research.md`.
