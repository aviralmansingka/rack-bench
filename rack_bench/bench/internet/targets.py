"""Shared probe policy: credentials, effective bands, and scoped run ownership."""
from uuid import uuid4

from .s3client import Credentials, CredentialError, resolve_endpoint


def targets(provider, options):
    """Nearest band first; unsupported providers/bands remain explicit records."""
    Credentials.from_env()  # Spec §6: even context probes require provider credentials.
    if provider == "gcs":
        raise ValueError("GCS interoperability not implemented")
    nearest = options.regions.get(provider, "ap-south-1" if provider == "s3" else "apac")
    regions = [nearest]
    if options.profile == "certify" and provider not in options.regions:
        regions += ["ap-southeast-1", "us-east-1"]
    result = []
    for index, region in enumerate(regions):
        endpoint = resolve_endpoint(provider, region)
        reason = None
        if provider == "r2" and region not in {"apac", "auto"}:
            reason = "unsupported pinned R2 band: placement hint does not establish a regional path"
        result.append({"region": region, "endpoint": f"https://{endpoint.host}",
                       "host": endpoint.host, "band": "nearest" if index == 0 else "light",
                       "runs": 3 if options.profile == "certify" and index == 0 else 1,
                       "reason": reason})
    return result


def reason(exc):
    if isinstance(exc, CredentialError):
        return f"credentials not set: {exc}"
    return str(exc)


def run_prefix(options):
    if not hasattr(options, "_internet_prefix"):
        options._internet_prefix = f"rack-bench/{uuid4().hex}/"
    return options._internet_prefix
