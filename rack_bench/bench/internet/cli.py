"""Internet-specific arguments, defaults, validation, and cost acceptance."""
import argparse
from dataclasses import dataclass, field, fields
from functools import partial
import re

from rack_bench.common.output import show_cost_estimate

PROVIDERS = ("s3", "r2", "gcs")
DIRECTIONS = ("up", "down")


@dataclass
class Options:
    providers: tuple[str, ...] = ("s3", "r2")
    directions: tuple[str, ...] = DIRECTIONS
    profile: str = "quick"
    regions: dict[str, str] = field(default_factory=dict)
    concurrent: int = 32
    duration: int | None = None  # seconds per test; defaults depend on profile
    tool: str = "stdlib"
    keep_data: bool = False
    yes: bool = False

    def __post_init__(self):
        if self.duration is None:
            self.duration = 300 if self.profile == "certify" else 60


def csv_choices(value, *, choices):
    items = tuple(item.strip() for item in value.split(","))
    if any(item not in choices for item in items) or len(set(items)) != len(items):
        raise argparse.ArgumentTypeError(f"expected unique comma-separated choices: {','.join(choices)}")
    return items


def regions(value):
    result = {}
    for item in value.split(","):
        provider, separator, region = item.strip().partition("=")
        if not separator or provider not in PROVIDERS or not re.fullmatch(r"[A-Za-z0-9_-]+", region):
            raise argparse.ArgumentTypeError("expected provider=region pairs, e.g. s3=us-east-1,r2=auto")
        if provider in result:
            raise argparse.ArgumentTypeError(f"duplicate region for {provider}")
        result[provider] = region
    return result


def positive_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def duration_seconds(value):
    match = re.fullmatch(r"([0-9]+)([smh]?)", value)
    if not match or int(match[1]) <= 0:
        raise argparse.ArgumentTypeError("expected a positive duration, e.g. 60s, 5m, 1h (bare numbers are seconds)")
    return int(match[1]) * {"": 1, "s": 1, "m": 60, "h": 3600}[match[2]]


def add_arguments(parser):
    parser.add_argument("--providers", type=partial(csv_choices, choices=PROVIDERS), default=("s3", "r2"),
                        help="comma-separated providers: s3,r2,gcs (default: s3,r2)")
    parser.add_argument("--directions", type=partial(csv_choices, choices=DIRECTIONS), default=DIRECTIONS,
                        help="comma-separated directions: up,down (default: up,down)")
    parser.add_argument("--profile", choices=("quick", "certify"), default="quick")
    parser.add_argument("--regions", type=regions, default={}, metavar="PROVIDER=REGION,...",
                        help="region overrides; otherwise use provider defaults")
    parser.add_argument("--concurrent", type=positive_int, default=32, metavar="N",
                        help="parallel streams (default: 32)")
    parser.add_argument("--duration", type=duration_seconds, metavar="DURATION",
                        help="per-test duration: seconds, Ns, Nm, Nh (default: quick 60s, certify 5m)")
    parser.add_argument("--tool", choices=("stdlib", "warp"), default="stdlib")
    parser.add_argument("--keep-data", action="store_true", help="skip bucket cleanup (stub: no data created)")
    parser.add_argument("--yes", action="store_true", help="accept the certify reference cost estimate")


def options_from_args(args):
    return Options(**{item.name: getattr(args, item.name) for item in fields(Options)})


def before_run(options):
    if options.profile == "certify":
        show_cost_estimate(cost_estimate(options))
        if not options.yes:
            raise ValueError("The certify profile requires --yes to accept the cost estimate.")


def cost_estimate(options):
    """Spec §5 reference costs at 10 Gbit/s, not a quote for custom options."""
    costs = {"s3": 200, "r2": 0, "gcs": 260}
    return {provider: costs[provider] for provider in options.providers}
