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
    buckets: dict[str, tuple[str, ...]] = field(default_factory=dict)
    concurrent: int | None = None
    duration: int | None = None  # seconds per test; defaults depend on profile
    object_size: int | None = None  # MiB per uploaded object; default depends on profile
    part_size: int | None = None  # MiB per multipart part / range GET; default 64
    upload_mode: str = "auto"  # auto: single-part-sized objects use one plain PutObject
    tool: str = "stdlib"
    keep_data: bool = False
    yes: bool = False

    def __post_init__(self):
        self._concurrent_override = self.concurrent is not None
        if self.concurrent is None:
            self.concurrent = 32
        if self.duration is None:
            self.duration = 300 if self.profile == "certify" else 60
        if self.part_size is None:
            self.part_size = 64  # MiB; see transfer.PART_SIZE for the timeout rationale
        if self.upload_mode not in ("auto", "multipart"):
            raise ValueError("upload_mode must be auto or multipart")
        # Library callers may pass a bare name; normalize to the ordered tuple
        # every consumer reads (targets.bucket_names).
        self.buckets = {provider: (names,) if isinstance(names, str) else tuple(names)
                        for provider, names in self.buckets.items()}


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


def _bucket_name(provider, bucket):
    if not bucket:
        raise argparse.ArgumentTypeError(f"empty bucket name for {provider}")
    if (not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket) or
            ".." in bucket or ".-" in bucket or "-." in bucket or
            re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}", bucket) or
            provider == "s3" and "." in bucket):
        raise argparse.ArgumentTypeError(
            "expected provider=bucket pairs with DNS-compatible bucket names "
            "(S3 virtual-hosted TLS names cannot contain dots)")
    return bucket


def buckets(value):
    """One --buckets occurrence: provider=bucket pairs; a provider may repeat.

    Repeated provider keys append buckets in flag order, so s3=one,s3=two is
    two S3 buckets. The exact same name twice is a typo, not a shard.
    """
    result = {}
    for item in value.split(","):
        provider, separator, bucket = item.strip().partition("=")
        if not separator or provider not in PROVIDERS:
            raise argparse.ArgumentTypeError("expected provider=bucket pairs, e.g. s3=bench-1,r2=bench-2")
        name = _bucket_name(provider, bucket)
        names = result.setdefault(provider, [])
        if name in names:
            raise argparse.ArgumentTypeError(f"duplicate bucket for {provider}: {name}")
        names.append(name)
    return {provider: tuple(names) for provider, names in result.items()}


class merge_buckets(argparse.Action):
    """--buckets may itself repeat; occurrences merge per provider in order."""

    def __call__(self, parser, namespace, values, option_string=None):
        merged = dict(getattr(namespace, self.dest) or {})
        for provider, names in values.items():
            combined = merged.get(provider, ()) + tuple(names)
            duplicates = sorted({name for name in combined if combined.count(name) > 1})
            if duplicates:
                raise argparse.ArgumentError(self, f"duplicate bucket for {provider}: {','.join(duplicates)}")
            merged[provider] = combined
        setattr(namespace, self.dest, merged)


def positive_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a positive integer") from None
    if number <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def part_size_mib(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a positive integer") from None
    if not 8 <= number <= 512:
        raise argparse.ArgumentTypeError(
            "expected 8..512 (MiB); every non-final part must stay above the 5 MiB minimum S3 and GCS enforce")
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
    parser.add_argument("--buckets", type=buckets, action=merge_buckets, default={}, metavar="PROVIDER=BUCKET,...",
                        help="existing buckets; a provider may repeat (in the list or the flag) "
                             "to shard streams across buckets, e.g. s3=bench-1,s3=bench-2; required for object probes")
    parser.add_argument("--concurrent", type=positive_int, metavar="N",
                        help="parallel streams (default: 32)")
    parser.add_argument("--duration", type=duration_seconds, metavar="DURATION",
                        help="per-test duration: seconds, Ns, Nm, Nh (default: quick 60s, certify 5m)")
    parser.add_argument("--object-size", type=positive_int, metavar="MIB",
                        help="uploaded object size in MiB (default: quick 32, certify 1024)")
    parser.add_argument("--part-size", type=part_size_mib, metavar="MIB",
                        help="multipart part / range GET size in MiB (default: 64; 8..512)")
    parser.add_argument("--upload-mode", choices=("auto", "multipart"), default="auto",
                        help="auto (default): an object that fits in one part uploads as one "
                             "plain PutObject; multipart forces multipart for every object "
                             "(request-pattern comparisons)")
    parser.add_argument("--tool", choices=("stdlib", "warp"), default="stdlib")
    parser.add_argument("--keep-data", action="store_true", help="retain objects under this run's rack-bench/ prefix")
    parser.add_argument("--yes", action="store_true", help="accept the certify reference cost estimate")


def options_from_args(args):
    return Options(**{item.name: getattr(args, item.name) for item in fields(Options)})


def before_run(options):
    # Options may be reused by library callers; measurements/prefixes are run-local.
    for cache in ("_path_reports", "_internet_prefix", "_internet_seed", "_transfer_reports", "_transfer_owners", "_internet_checks"):
        options.__dict__.pop(cache, None)
    if options.profile == "certify":
        show_cost_estimate(cost_estimate(options))
        if not options.yes:
            raise ValueError("The certify profile requires --yes to accept the cost estimate.")


def cost_estimate(options):
    """Spec §5 reference costs at 10 Gbit/s, not a quote for custom options."""
    costs = {"s3": 200, "r2": 0, "gcs": 260}
    return {provider: costs[provider] for provider in options.providers}
