"""Shared probe policy: credentials, effective bands, and scoped run ownership."""
from uuid import uuid4

from .s3client import Credentials, CredentialError, resolve_endpoint


DEFAULT_REGIONS = {"s3": "ap-south-1", "r2": "apac", "gcs": "asia-south1"}
# The gcs default matches the S3/R2 nearest band: asia-south1 (Mumbai) sits in
# the same metro as ap-south-1, and Google's Chennai edge POP terminates the
# anycast interop endpoint close to the node (docs/internet-performance.md §3).


def targets(provider, options):
    """Nearest band first; unsupported providers/bands remain explicit records."""
    Credentials.from_env(provider)  # Spec §6: even context probes require provider credentials.
    nearest = options.regions.get(provider, DEFAULT_REGIONS[provider])
    regions = [nearest]
    if options.profile == "certify" and provider not in options.regions:
        regions += ["ap-southeast-1", "us-east-1"]
    result = []
    for index, region in enumerate(regions):
        endpoint = resolve_endpoint(provider, region)
        reason = None
        if provider == "r2" and region not in {"apac", "auto"}:
            reason = "unsupported pinned R2 band: placement hint does not establish a regional path"
        elif provider == "gcs" and index > 0:
            # The interop endpoint is one global anycast host: far bands would
            # measure the same edge path, so only the pinned location runs.
            reason = "unsupported pinned GCS band: global anycast endpoint; pin --regions gcs=<location> to move the measured location"
        result.append({"region": region, "endpoint": f"https://{endpoint.host}",
                       "host": endpoint.host, "band": "nearest" if index == 0 else "light",
                       "runs": 3 if options.profile == "certify" and index == 0 else 1,
                       "reason": reason})
    return result


def reason(exc):
    if isinstance(exc, CredentialError):
        return f"credentials not set: {exc}"
    return str(exc)


def bucket_names(provider, options):
    """Ordered bucket names for a provider; the first name is the default.

    Options normalizes values to tuples at construction; this helper also
    accepts a bare string for library callers that assign Options.buckets
    directly. Order is flag order and is the round-robin assignment order.
    """
    names = options.buckets.get(provider) or ()
    return (names,) if isinstance(names, str) else tuple(names)


def run_prefix(options):
    if not hasattr(options, "_internet_prefix"):
        options._internet_prefix = f"rack-bench/{uuid4().hex}/"
    return options._internet_prefix


def run_seed(options):
    """One payload seed per run, shared by every transfer object.

    Keys stay unique per object; only the pseudorandom seed is shared, so the
    chunk at any given offset is identical across sibling objects and their
    part digests hit the data-path caches. Per-object records still persist
    {seed, size, chunk_size}, so verification of any stored object is unchanged.
    """
    if not hasattr(options, "_internet_seed"):
        options._internet_seed = uuid4().hex
    return options._internet_seed
