"""Argument parsing and thin stage dispatch."""
import argparse
import sys

from rack_bench.audit import runner
from rack_bench.bench import runner as bench_runner


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
    bench_runner.add_categories(bench, parents=[flags])
    # Parse globals once so repeated patterns work on either side of the stage.
    options, remaining = flags.parse_known_args(argv)
    args = parser.parse_args(remaining, namespace=options)
    try:
        common = dict(only=getattr(args, "only", ()), skip=getattr(args, "skip", ()),
                      json_target=getattr(args, "json", None), run_dir=getattr(args, "run_dir", None),
                      show_command=getattr(args, "show_command", False), quiet=getattr(args, "quiet", False))
        if args.stage == "audit":
            return runner.run(args.scope, **common)
        return bench_runner.run(args.category, options=bench_runner.options_from_args(args), **common)
    except (OSError, ValueError) as exc:
        print(f"rack-bench: {exc}", file=sys.stderr)
        return 2
