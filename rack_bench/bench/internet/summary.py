"""Placeholder summary probe; replaced by measurements in later sessions."""
from rack_bench.common.models import Check


def summary(provider, options):
    return Check(f"internet.{provider}.summary", "skip", detail="not implemented")
