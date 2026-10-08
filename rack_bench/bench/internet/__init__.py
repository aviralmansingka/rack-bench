"""Internet category contract and ordered, stable public check registry."""
from functools import partial

from .cli import DIRECTIONS, PROVIDERS, Options, add_arguments, before_run, cost_estimate, options_from_args
from .latency import latency_probe
from .path import dns_probe, path_probe
from .summary import not_implemented, summary

CHECKS = {}
for provider in PROVIDERS:
    for metric in ("as_path", "hops", "rtt_sanity"):
        CHECKS[f"internet.{provider}.path.{metric}"] = partial(path_probe, provider, metric)
    CHECKS[f"internet.{provider}.dns.resolve"] = partial(dns_probe, provider)
    CHECKS[f"internet.{provider}.latency.ttfb"] = partial(latency_probe, provider)
    for suffix in ("upload.throughput", "upload.objs_per_sec", "latency.loaded",
                   "download.throughput", "download.objs_per_sec", "tcp.pmtud", "tcp.retransmit_ratio"):
        CHECKS[f"internet.{provider}.{suffix}"] = partial(not_implemented, provider, suffix)
    CHECKS[f"internet.{provider}.summary"] = partial(summary, provider)


def selected_checks(options):
    return ((name, probe) for name, probe in CHECKS.items() if name.split(".")[1] in options.providers)
