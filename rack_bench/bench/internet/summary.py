"""Transfer/summary placeholders; Part 2 owns their implementation."""
from rack_bench.common.models import Check
from .targets import reason, targets


def not_implemented(provider, suffix, options):
    detail = "not implemented"
    try:
        targets(provider, options)
    except ValueError as exc:
        detail = reason(exc)
    return Check(f"internet.{provider}.{suffix}", "skip", detail=detail)


def summary(provider, options):
    return not_implemented(provider, "summary", options)
