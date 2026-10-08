"""Pure measurement math. Percentiles use linear interpolation at (n - 1) * p.

Empty populations have no measured value (None), never an invented zero.
Windows are half-open [start, end); timestamps and origin share a caller clock.
"""
import math
from statistics import fmean


def percentile(samples, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be in 0..100")
    values = sorted(samples)
    if not values:
        return None
    position = (len(values) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def describe(samples):
    values = list(samples)
    return {"count": len(values), "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": fmean(values) if values else None,
            **{f"p{p}": percentile(values, p) for p in (50, 95, 99)}}


def windows(samples, duration=1.0, *, origin=0.0):
    """Return populated fixed-duration windows, ordered by start time.

    Input is (timestamp, value) pairs; output is (start, list-of-values).
    Sparse/missing windows are omitted, not filled with fabricated samples.
    Boundary timestamps belong to the following window, including negatives.
    """
    if not math.isfinite(duration) or duration <= 0 or not math.isfinite(origin):
        raise ValueError("duration must be positive and finite; origin must be finite")
    buckets = {}
    for timestamp, value in samples:
        if not math.isfinite(timestamp):
            raise ValueError("timestamp must be finite")
        index = math.floor((timestamp - origin) / duration)
        buckets.setdefault(index, []).append(value)
    return [(origin + index * duration, buckets[index]) for index in sorted(buckets)]
