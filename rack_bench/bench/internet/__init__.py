"""Internet category contract and ordered, stable public check registry."""
from functools import partial

from .cli import DIRECTIONS, PROVIDERS, Options, add_arguments, before_run, cost_estimate, options_from_args
from .latency import latency_probe
from .path import dns_probe, path_probe
from .download import download_probe
from .summary import summary
from .tcp import pmtud_probe, retransmit_probe
from .transfer import cleanup, transfer_check
from .upload import loaded_probe, upload_probe

CHECKS = {}
for provider in PROVIDERS:
    for metric in ("as_path", "hops", "rtt_sanity"):
        CHECKS[f"internet.{provider}.path.{metric}"] = partial(path_probe, provider, metric)
    CHECKS[f"internet.{provider}.dns.resolve"] = partial(dns_probe, provider)
    CHECKS[f"internet.{provider}.latency.ttfb"] = partial(latency_probe, provider)
    for metric in ("throughput", "objs_per_sec"):
        CHECKS[f"internet.{provider}.upload.{metric}"] = partial(upload_probe, provider, metric)
    CHECKS[f"internet.{provider}.latency.loaded"] = partial(loaded_probe, provider)
    for metric in ("throughput", "objs_per_sec"):
        CHECKS[f"internet.{provider}.download.{metric}"] = partial(download_probe, provider, metric)
    CHECKS[f"internet.{provider}.tcp.pmtud"] = partial(pmtud_probe, provider)
    CHECKS[f"internet.{provider}.tcp.retransmit_ratio"] = partial(retransmit_probe, provider)
    CHECKS[f"internet.{provider}.summary"] = partial(summary, provider)


def selected_checks(options):
    def remember(probe, options):
        check = probe(options)
        options.__dict__.setdefault("_internet_checks", {})[check.name] = check
        return check
    return ((name, partial(remember, probe)) for name, probe in CHECKS.items()
            if name.split(".")[1] in options.providers)


def after_run(options, result):
    # Runs even with --only/--skip or a raised probe: cleanup cannot depend on summary.
    cleanup(options)
    for check in result.checks:
        _, provider, *suffix = check.name.split(".")
        state = getattr(options, "_transfer_reports", {}).get(provider, {})
        replacement = None
        if suffix[0] in ("upload", "download"):
            direction = "up" if suffix[0] == "upload" else "down"
            if state.get(direction):
                replacement = transfer_check(provider, direction, suffix[1], options, state[direction])
        elif suffix == ["summary"] and isinstance(check.value, dict) and "checks" in check.value:
            replacement = summary(provider, options)
        if replacement:
            check.status = replacement.status
            check.detail = replacement.detail
            check.value = replacement.value
