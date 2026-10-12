# N14 — Modern Network Troubleshooting

Research date: 2026-10-11. Researcher: oreilly-white-N14.

## Observed product identity and agenda

Russ White teaches Modern Network Troubleshooting.
Pearson publishes the event on O'Reilly Live Events.
Event ID: 0790145043580. ISBN does not apply.
The researcher reports an ended-course notice. The orchestrator's extraction does not show that notice.
Do not use that notice as decisive availability evidence.
The public page does not show a date. The supplied 2025 date remains unverified.
The page does not prove recording availability.

Published agenda:

1. Resilience: 55 minutes. Resilience elements, MTBF/MTTR, abstractions, and troubleshooting.
2. Troubleshooting Process: 50 minutes. Half-split method and small-network reachability and routing examples.
3. Troubleshooting Example: 50 minutes. LLMs, flapping BGP, correlation and causation, and Internet slow performance.

The description names ping, traceroute, and MTR.
The agenda does not show the exact steps or measurements for the internet example.

## Proposed bench techniques — inferences

1. Compare controlled cases. Change one destination or load condition at a time.
   This applies the half-split method to a slow S3/R2/GCS transfer.
2. Compare repeated MTR observations with end-to-end transfer results.
   Intermediate non-response alone does not prove path loss.
   The event names MTR but does not document this interpretation rule.
3. Record DNS, connection setup, transfer timing, and retransmission evidence separately.
   This applies network models to fault isolation. The agenda does not name these exact measurements.
4. Compare idle and loaded latency. Added latency suggests queueing, but does not locate its cause.
5. Keep initial evidence. Test one causal hypothesis before a controlled repeat.
   PMTUD and CC comparisons are bench applications, not verified event exercises.

## Canon verdict

Optional troubleshooting-method candidate. Do not replace the four-book spine.
The Internet slow performance example gives this event direct scope relevance.
Public catalog evidence does not establish quantitative certification methods or thresholds.

## Gaps

- The specific 2025 session date remains unverified.
- No recording, transcript, slides, or session-specific listing supports deeper technical claims.
- The agenda does not specify object-store tests, jitter, DNS, PMTUD, or CC measurement procedures.

## Sources

- [Exact O'Reilly event](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580).
- [Separate White event](https://www.oreilly.com/live-events/network-troubleshooting-basic-theory-and-process/0636920158769).
  This different title and ID do not prove the date or identity of the requested event.
- Local comparison: `.lavish/internet-research/books.md`; `docs/internet-quality-research.md`.
