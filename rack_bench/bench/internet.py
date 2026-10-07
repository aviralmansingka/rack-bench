"""Internet category contract; no network operations are implemented yet."""
from dataclasses import dataclass, field
from functools import partial

from rack_bench.common.models import Check

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


def summary(provider, options):
    return Check(f"internet.{provider}.summary", "skip", detail="not implemented")


CHECKS = {f"internet.{provider}.summary": partial(summary, provider) for provider in PROVIDERS}


def cost_estimate(options):
    """Spec §5 reference costs at 10 Gbit/s, not a quote for custom options."""
    costs = {"s3": 200, "r2": 0, "gcs": 260}
    return {provider: costs[provider] for provider in options.providers}
