"""Argument parsing and thin stage dispatch."""
import argparse
from functools import partial
import re
import sys

from rack_bench.audit import runner
from rack_bench.bench import internet, runner as bench_runner


def csv_choices(value, *, choices):
    items = tuple(item.strip() for item in value.split(","))
    if any(item not in choices for item in items) or len(set(items)) != len(items):
        raise argparse.ArgumentTypeError(f"expected unique comma-separated choices: {','.join(choices)}")
    return items


def regions(value):
    result = {}
    for item in value.split(","):
        provider, separator, region = item.strip().partition("=")
        if not separator or provider not in internet.PROVIDERS or not re.fullmatch(r"[A-Za-z0-9_-]+", region):
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


def main(argv=None):
    flags = argparse.ArgumentParser(add_help=False, argument_default=argparse.SUPPRESS)
    flags.add_argument("--json", nargs="?", const="-", metavar="FILE",
                       help="write the result envelope to FILE; without FILE, print JSON")
    flags.add_argument("--run-dir", metavar="DIR",
                       help="artifact directory (default: ./rack-bench-runs/<timestamp>/)")
    flags.add_argument("--only", action="append", metavar="GLOB", help="include matching check names; repeatable")
    flags.add_argument("--skip", action="append", metavar="GLOB", help="exclude matching check names; repeatable")
    flags.add_argument("--show-command", action="store_true", help="echo commands/file reads live on stdout with check names; use --json FILE for a clean JSON export")
    flags.add_argument("--quiet", action="store_true", help="suppress command trace and PASS rows in the human view")
    parser = argparse.ArgumentParser(prog="rack-bench", parents=[flags])
    stages = parser.add_subparsers(dest="stage", required=True)
    audit = stages.add_parser("audit", parents=[flags], help="read-only inventory and passive security checks")
    audit.add_argument("scope", nargs="?", choices=runner.SCOPES)
    bench = stages.add_parser("bench", parents=[flags], help="per-component benchmarks (dispatch stub only)")
    bench.add_argument("category", nargs="?", choices=bench_runner.CATEGORIES)
    bench.add_argument("--providers", type=partial(csv_choices, choices=internet.PROVIDERS), default=("s3", "r2"),
                       help="comma-separated providers: s3,r2,gcs (default: s3,r2)")
    bench.add_argument("--directions", type=partial(csv_choices, choices=internet.DIRECTIONS), default=internet.DIRECTIONS,
                       help="comma-separated directions: up,down (default: up,down)")
    bench.add_argument("--profile", choices=("quick", "certify"), default="quick")
    bench.add_argument("--regions", type=regions, default={}, metavar="PROVIDER=REGION,...",
                       help="region overrides; otherwise use provider defaults")
    bench.add_argument("--concurrent", type=positive_int, default=32, metavar="N",
                       help="parallel streams (default: 32)")
    bench.add_argument("--duration", type=duration_seconds, metavar="DURATION",
                       help="per-test duration: seconds, Ns, Nm, Nh (default: quick 60s, certify 5m)")
    bench.add_argument("--tool", choices=("stdlib", "warp"), default="stdlib")
    bench.add_argument("--keep-data", action="store_true", help="skip bucket cleanup (stub: no data created)")
    bench.add_argument("--yes", action="store_true", help="accept the certify reference cost estimate")
    # Parse globals once so repeated patterns work on either side of the stage.
    options, remaining = flags.parse_known_args(argv)
    args = parser.parse_args(remaining, namespace=options)
    try:
        common = dict(only=getattr(args, "only", ()), skip=getattr(args, "skip", ()),
                      json_target=getattr(args, "json", None), run_dir=getattr(args, "run_dir", None),
                      show_command=getattr(args, "show_command", False), quiet=getattr(args, "quiet", False))
        if args.stage == "audit":
            return runner.run(args.scope, **common)
        options = internet.Options(
            providers=args.providers, directions=args.directions, profile=args.profile, regions=args.regions,
            concurrent=args.concurrent, duration=args.duration,
            tool=args.tool, keep_data=args.keep_data, yes=args.yes)
        return bench_runner.run(args.category, options=options, **common)
    except (OSError, ValueError) as exc:
        print(f"rack-bench: {exc}", file=sys.stderr)
        return 2
