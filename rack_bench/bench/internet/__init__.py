"""Internet category contract and check registry; no network operations yet."""
from functools import partial

from .cli import DIRECTIONS, PROVIDERS, Options, add_arguments, before_run, cost_estimate, options_from_args
from .summary import summary

CHECKS = {f"internet.{provider}.summary": partial(summary, provider) for provider in PROVIDERS}


def selected_checks(options):
    return ((name, probe) for name, probe in CHECKS.items() if name.split(".")[1] in options.providers)
