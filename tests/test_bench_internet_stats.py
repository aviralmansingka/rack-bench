"""Pure synthetic samples; no clock or I/O."""
import unittest

from rack_bench.bench.internet.stats import describe, percentile, windows


class StatsTests(unittest.TestCase):
    def test_empty_samples_are_unmeasured(self):
        self.assertEqual(describe([]), dict(count=0, min=None, max=None, mean=None,
                                            p50=None, p95=None, p99=None))
        self.assertEqual(windows([]), [])

    def test_single_and_repeated_values(self):
        for samples in ([7], [7] * 10):
            self.assertEqual(describe(samples), dict(count=len(samples), min=7, max=7,
                                                   mean=7, p50=7, p95=7, p99=7))

    def test_interpolated_percentiles_and_input_not_mutated(self):
        values = [100, 0]
        self.assertEqual(describe(values), dict(count=2, min=0, max=100, mean=50,
                                               p50=50, p95=95, p99=99))
        self.assertEqual(values, [100, 0])
        self.assertEqual(percentile(values, 0), 0)
        self.assertEqual(percentile(values, 100), 100)
        with self.assertRaises(ValueError):
            percentile(values, 101)

    def test_windows_boundaries_sparse_and_unsorted(self):
        samples = [(2, "c"), (0, "a"), (0.999, "b"), (1, "d"), (4, "e"), (-0.1, "f")]
        self.assertEqual(windows(samples), [(-1, ["f"]), (0, ["a", "b"]),
                                            (1, ["d"]), (2, ["c"]), (4, ["e"])])
        self.assertEqual(windows([(10, 1), (12, 2)], 2, origin=10), [(10, [1]), (12, [2])])
        for duration in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                windows([], duration)
        with self.assertRaises(ValueError):
            windows([(float("nan"), 1)])
