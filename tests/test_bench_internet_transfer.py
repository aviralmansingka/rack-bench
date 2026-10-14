"""Fake transport, clocks and commands only: no sockets, sleeps or cloud data.

Fixture provenance (captured on the development host, 2026-10-08):
- internet-ss.txt: two loopback socket records from `ss -4tinH` (verbatim).
- internet-ping-{pass,mtu}.txt: `ping -4 -n -M do -c 1 -W 1 -s SIZE
  127.0.0.1`, SIZE=1472/65508, stdout + stderr (verbatim).
Timeout, PID ownership and counter-delta mutations below are synthetic, not
represented as captures. No capture command executes during these tests.

The process-pool tests are the exception: they drive the real worker-process
path against a loopback HTTP server, with the real monotonic clock. No cloud
data and no capture commands there either.
"""
import argparse
import base64
from contextlib import redirect_stdout
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import zlib

from rack_bench.bench import internet, runner
from rack_bench.bench.internet import download, s3client as s3, stats, targets, tcp, transfer, upload
from rack_bench.bench.internet.latency import OBJECT_SIZE as LATENCY_SIZE
from rack_bench.bench.internet.cli import Options, before_run, part_size_mib
from rack_bench.bench.internet.s3client import S3Client, Timing, TransportError
from rack_bench.common.models import Check

FIXTURES = Path(__file__).parent / "fixtures"


def response(size=8, direction="up", **overrides):
    timing = Timing(connect_seconds=.001, response_first_byte_seconds=.002,
                    headers_seconds=.003, first_byte_seconds=.004,
                    elapsed_seconds=.005, bytes_sent=size if direction == "up" else 0,
                    bytes_received=size if direction == "down" else 0)
    for key, value in overrides.items():
        setattr(timing, key, value)
    return SimpleNamespace(timing=timing)


class Clock:
    def __init__(self):
        self.now = 0
        self.lock = threading.Lock()

    def __call__(self):
        with self.lock:
            self.now += .1
            return self.now


class FakeTCP:
    def __init__(self, host, pids=None):
        self.host = host
        self.pids = pids  # bulk windows pass a parent+worker-process provider
        self.detail = {"segments": 1000, "retransmits": 2, "ratio_pct": .2,
                       "observations": [{"window_bytes": 1024 * 1024, "rtt_ms": 10}],
                       "sources": ["ss -4tinpH ( dst 192.0.2.1 )"], "errors": [],
                       "limits": {"ticks": 5, "busy_pct_median": 100.0,
                                  "rwnd_limited_pct_median": 0.0, "cwnd_limited_pct_median": 0.0,
                                  "sndbuf_limited_pct_median": 0.0, "sockets_per_dominant_state": {"busy": 4},
                                  "dominant_state": "busy",
                                  "semantics": "shares of socket busy time in percent; busy_pct is 100 when ss reports any busy time"}}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class FakeClient:
    def close(self):
        pass

    def __init__(self, *args, invalid=None):
        self.endpoint = SimpleNamespace(host="example.invalid", path_style=False)
        self.bucket = "bench-test"
        self.objects, self.deleted, self.calls = {}, [], []
        self.invalid = invalid or {}

    def put_object(self, key, payload):
        self.objects[key] = payload
        return response(payload.size)

    def multipart_upload(self, key, payload, part_size, on_part, on_progress):
        self.calls.append(("up", key))
        for offset in range(0, payload.size, part_size):
            size = min(part_size, payload.size - offset)
            on_progress(size // 2, .001)
            on_progress(size, .002)
            on_part(response(size, **self.invalid))
        self.objects[key] = payload
        return response(0)  # Completion timing MUST NOT become a payload sample.

    def get_object(self, key, payload, byte_range=None, consume=None, fresh_connection=False):
        self.calls.append(("down", key))
        self.assert_owned(key)
        start, end = byte_range or (0, payload.size - 1)
        size = end - start + 1
        if consume:
            consume(b"x" * size, start)
        return response(size, "down", **self.invalid)

    def assert_owned(self, key):
        if key not in self.objects:
            raise AssertionError("GET did not read an uploaded object")

    def delete_object(self, key):
        self.deleted.append(key)
        self.objects.pop(key, None)


class TransferTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "fake", "AWS_SECRET_ACCESS_KEY": "fake", "R2_ACCOUNT_ID": "fake",
                                      "GCS_ACCESS_KEY_ID": "fake", "GCS_SECRET_ACCESS_KEY": "fake"}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.options = Options(providers=("s3",), buckets={"s3": "bench-test"}, duration=1)
        self.client = FakeClient()
        self.clock = Clock()

    def window(self, **kwargs):
        with patch.object(transfer, "PART_SIZE", 8):
            return transfer.transfer_window(self.client, direction="up", prefix="rack-bench/test/", concurrency=2,
                                          duration=.1, objects=[], owned=[], size=16, one_object=True,
                                          clock=self.clock, tcp_factory=FakeTCP,
                                          pool_factory=transfer._thread_pool_factory, **kwargs)

    def test_parallel_multipart_samples_buckets_and_completion_not_counted(self):
        run, objects = self.window()
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 32)
        self.assertEqual(run["progress_bytes_lower_bound"], 32)
        self.assertEqual(len(run["samples"]), 4)
        self.assertEqual(len(objects), 2)
        self.assertEqual(sum(b["bytes"] for b in run["buckets"]), 32)
        self.assertAlmostEqual(run["mib_per_sec"], 32 / transfer.MIB / run["elapsed_seconds"])
        self.assertTrue(all(s["cpu_ms"] >= 0 for s in run["samples"]))

    def test_range_gets_read_uploaded_objects_and_single_stream(self):
        _, objects = self.window()
        with patch.object(transfer, "PART_SIZE", 8):
            run, _ = transfer.transfer_window(self.client, direction="down", prefix="unused/", concurrency=1,
                                            duration=.1, objects=objects, owned=[], one_object=True,
                                            clock=self.clock, tcp_factory=FakeTCP)
        self.assertEqual(run["bytes"], 16)
        self.assertEqual(run["objects"], 1)
        self.assertEqual(len(run["samples"]), 2)
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["tcp"]["ratio_pct"], .2)

    def test_invalid_timing_attempts_and_bytes_skip_not_zero(self):
        for invalid in ({"attempts": 2}, {"bytes_sent": 7}, {"connect_seconds": .1},
                        {"elapsed_seconds": float("nan")}, {"first_byte_seconds": .1}):
            with self.subTest(invalid=invalid):
                self.client.invalid = invalid
                run, _ = self.window()
                self.assertEqual(run["status"], "skip")
                self.assertIsNone(run["mib_per_sec"])
                self.assertTrue(run["errors"])

    def test_progress_mismatch_and_transport_failure_are_explicit(self):
        def broken(key, payload, part_size, on_part, on_progress):
            on_progress(7, .001)
            on_part(response(8))
        self.client.multipart_upload = broken
        run, _ = self.window()
        self.assertIn("progress bytes", run["errors"][0]["reason"])
        self.client.multipart_upload = Mock(side_effect=TransportError("broken socket"))
        run, _ = self.window()
        self.assertEqual(run["status"], "skip")
        self.assertIn("broken socket", run["errors"][0]["reason"])

    def test_deadline_stops_at_part_boundary_without_forcing_gib_objects(self):
        with patch.object(transfer, "PART_SIZE", 8):
            run, objects = transfer.transfer_window(self.client, direction="up", prefix="rack-bench/test/",
                                                  concurrency=1, duration=.1, objects=[], owned=[], size=1024,
                                                  clock=self.clock, tcp_factory=FakeTCP)
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 8)
        self.assertEqual(run["incomplete_objects"], 1)
        self.assertEqual(objects, [])
        self.assertEqual(run["objs_per_sec"], 0)

    def test_deadline_abort_uses_existing_client_and_preserves_abort_failure(self):
        client = S3Client("bench-test", "us-east-1")
        client.initiate_multipart = Mock(return_value="owned-upload-id")
        client.complete_multipart = Mock()
        client.abort_multipart = Mock()
        def part(key, upload_id, number, payload, offset, size, on_progress):
            on_progress(size, .01)
            result = response(size)
            result.headers = {"etag": "part-tag"}
            result.upload_crc32 = "AAAAAA=="
            return result
        client.upload_part = part
        def run():
            # 8 MiB parts split the 16 MiB object so the deadline lands mid-object.
            return transfer.transfer_window(client, direction="up", prefix="rack-bench/test/", concurrency=1,
                                          duration=.1, objects=[], owned=[], size=16 * transfer.MIB,
                                          clock=Clock(), tcp_factory=FakeTCP, part_size=8 * transfer.MIB)[0]
        self.assertEqual(run()["status"], "pass")
        client.abort_multipart.assert_called_once_with("rack-bench/test/0-0.bin", "owned-upload-id")
        client.complete_multipart.assert_not_called()
        client.abort_multipart.side_effect = TransportError("abort denied")
        failed = run()
        self.assertEqual(failed["status"], "skip")
        self.assertIn("abort denied", failed["errors"][0]["reason"])

    def test_quick_object_smaller_than_part_is_valid_single_part_upload(self):
        # Default 64 MiB parts against a 32 MiB quick-profile object: one part,
        # still legal S3 (only non-final parts must reach 5 MiB).
        client = S3Client("bench-test", "us-east-1")
        client.initiate_multipart = Mock(return_value="single-upload-id")
        client.complete_multipart = Mock(return_value=response(0))
        client.abort_multipart = Mock()
        def part(key, upload_id, number, payload, offset, size, on_progress):
            on_progress(size, .01)
            result = response(size)
            result.headers = {"etag": "part-tag"}
            result.upload_crc32 = "AAAAAA=="
            return result
        client.upload_part = part
        run = transfer.transfer_window(client, direction="up", prefix="rack-bench/test/", concurrency=1,
                                       duration=.1, objects=[], owned=[], size=transfer.LIGHT_SIZE,
                                       clock=Clock(), tcp_factory=FakeTCP)[0]
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], transfer.LIGHT_SIZE)
        self.assertEqual([s["part"] for s in run["samples"]], [0])
        client.complete_multipart.assert_called_once()
        self.assertEqual(client.complete_multipart.call_args.args[2], [(1, "part-tag", "AAAAAA==")])
        client.abort_multipart.assert_not_called()

    def test_part_size_kwarg_sizes_multipart_and_range_gets(self):
        seen = {}
        def multipart(key, payload, part_size, on_part, on_progress):
            seen["upload"] = part_size
            for offset in range(0, payload.size, part_size):
                size = min(part_size, payload.size - offset)
                on_progress(size, .001)
                on_part(response(size))
            return response(0)
        def get(key, payload, byte_range=None, consume=None, fresh_connection=False):
            seen.setdefault("ranges", []).append(byte_range)
            if consume:
                consume(b"x" * (byte_range[1] - byte_range[0] + 1), byte_range[0])
            return response(byte_range[1] - byte_range[0] + 1, "down")
        self.client.multipart_upload, self.client.get_object = multipart, get
        run, objects = self.window(part_size=16)
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 32)
        self.assertEqual([s["part"] for s in run["samples"]], [0, 0])  # one part per 16-byte object
        self.assertEqual(seen["upload"], 16)
        with patch.object(transfer, "PART_SIZE", 8):
            run, _ = transfer.transfer_window(self.client, direction="down", prefix="unused/", concurrency=1,
                                              duration=.1, objects=objects, owned=[], one_object=True,
                                              clock=self.clock, tcp_factory=FakeTCP, part_size=16)
        self.assertEqual(run["bytes"], 16)
        self.assertEqual([s["part"] for s in run["samples"]], [0])
        self.assertEqual(seen["ranges"], [(0, 15)])  # explicit kwarg beats the patched module default

    def test_default_part_size_is_64_mib_and_module_constant_matches(self):
        self.assertEqual(transfer.PART_SIZE, 64 * transfer.MIB)
        self.assertEqual(Options().part_size, 64)
        self.assertEqual(Options(part_size=8).part_size, 8)

    def test_part_size_flag_reaches_transfer_windows_both_directions(self):
        records = self.reports()
        self.assertTrue(all(c["part_size"] == 64 * transfer.MIB for c in self.calls))
        self.client.deleted.clear()
        self.options = Options(providers=("s3",), buckets={"s3": "bench-test"}, duration=1, part_size=16)
        self.reports()
        download.download_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)
        self.assertTrue(all(c["part_size"] == 16 * transfer.MIB for c in self.calls))
        self.assertEqual([c["direction"] for c in self.calls], ["up", "up", "down", "down"])

    def test_part_size_cli_type_bounds(self):
        for value in (8, 64, 512):
            self.assertEqual(part_size_mib(str(value)), value)
        for value in ("7", "513", "0", "-8", "x", "8.5"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                part_size_mib(value)

    def test_gcs_windows_pin_the_location_and_use_the_global_host(self):
        # The gcs provider path through the policy layer: records pin the
        # bucket location, and every window's ss host is the bare global
        # endpoint (path-style), never a bucket-prefixed virtual host.
        self.options = Options(providers=("gcs",), buckets={"gcs": ("bench-gcs",)}, duration=1)
        self.calls = []
        records = upload.upload_reports("gcs", self.options, client_factory=lambda *a, **k: self.client,
                                        window=self.fake_window)
        download.download_reports("gcs", self.options, client_factory=lambda *a, **k: self.client,
                                  window=self.fake_window)
        self.assertTrue(self.calls)
        self.assertTrue(all(call["host"] == "storage.googleapis.com" for call in self.calls))
        self.assertEqual(records[0]["region"], "asia-south1")
        self.assertEqual(records[0]["endpoint"], "https://storage.googleapis.com")

    def test_multi_bucket_round_robin_assignment_and_records(self):
        names = ("bench-a", "bench-b")
        clients = {name: FakeClient() for name in names}
        for name, fake in clients.items():
            fake.bucket = name
        owned = []
        with patch.object(transfer, "PART_SIZE", 8):
            run, objects = transfer.transfer_window(clients[names[0]], direction="up", prefix="rack-bench/test/",
                                                    concurrency=4, duration=.1, objects=[], owned=owned,
                                                    size=16, one_object=True, clock=self.clock, tcp_factory=FakeTCP,
                                                    pool_factory=transfer._thread_pool_factory,
                                                    buckets=names, clients=clients)
        self.assertEqual(run["status"], "pass")
        # Streams 0..3 are assigned round-robin at window start, in order.
        self.assertEqual([obj["bucket"] for obj in objects], ["bench-a", "bench-b", "bench-a", "bench-b"])
        self.assertEqual(owned, [(obj["bucket"], obj["key"]) for obj in objects])
        self.assertEqual([sample["bucket"] for sample in run["samples"]],
                         ["bench-a", "bench-a", "bench-b", "bench-b", "bench-a", "bench-a", "bench-b", "bench-b"])
        self.assertEqual(len(clients["bench-a"].objects), 2)
        self.assertEqual(len(clients["bench-b"].objects), 2)
        # Single-stream windows always use the first bucket.
        with patch.object(transfer, "PART_SIZE", 8):
            run, objects = transfer.transfer_window(clients[names[0]], direction="up", prefix="rack-bench/test/",
                                                    concurrency=1, duration=.1, objects=[], owned=[],
                                                    size=16, one_object=True, clock=self.clock, tcp_factory=FakeTCP,
                                                    buckets=names, clients=clients)
        self.assertEqual(run["status"], "pass")
        self.assertEqual([obj["bucket"] for obj in objects], ["bench-a"])

    def test_download_reads_each_object_from_its_recorded_bucket(self):
        names = ("bench-a", "bench-b")
        clients = {name: FakeClient() for name in names}
        objects = []
        for index, name in enumerate(names):
            fake = clients[name]
            fake.bucket = name
            key = f"rack-bench/test/{index}-0.bin"
            fake.objects[key] = True  # assert_owned fails any GET against the wrong bucket's store
            objects.append({"key": key, "bucket": name,
                            "payload": {"seed": key, "size": 16, "chunk_size": 65536}})
        run, completed = transfer.transfer_window(clients[names[0]], direction="down", prefix="unused/",
                                                  concurrency=2, duration=.1, objects=objects, owned=[],
                                                  one_object=True, part_size=8, clock=self.clock, tcp_factory=FakeTCP,
                                                  pool_factory=transfer._thread_pool_factory,
                                                  buckets=names, clients=clients)
        self.assertEqual(run["status"], "pass")
        self.assertEqual([obj["bucket"] for obj in completed], ["bench-a", "bench-b"])
        self.assertEqual(clients["bench-a"].calls, [("down", "rack-bench/test/0-0.bin")] * 2)  # two verified ranges
        self.assertEqual(clients["bench-b"].calls, [("down", "rack-bench/test/1-0.bin")] * 2)
        self.assertEqual({sample["bucket"] for sample in run["samples"]}, set(names))

    def test_multi_bucket_reports_cleanup_and_check_detail(self):
        fakes = {}
        def factory(name, *args, **kwargs):
            if name not in fakes:  # one client per bucket survives across windows and cleanup
                fake = FakeClient()
                fake.bucket = name
                fakes[name] = fake
            return fakes[name]
        self.options = Options(providers=("s3",), buckets={"s3": ("bench-a", "bench-b")}, duration=1)
        self.baseline()
        self.calls = []
        records = upload.upload_reports("s3", self.options, client_factory=factory, window=self.fake_window)
        self.assertEqual(records[0]["buckets"], ["bench-a", "bench-b"])
        self.assertTrue(all(call["buckets"] == ("bench-a", "bench-b") for call in self.calls))
        download.download_reports("s3", self.options, client_factory=factory, window=self.fake_window)
        owned = {bucket: [key for holder, key in records[0]["owned"] if holder == bucket]
                 for bucket in ("bench-a", "bench-b")}
        self.assertIn(records[0]["loaded_key"], owned["bench-a"])  # the loaded probe uses the first bucket
        self.assertTrue(all(owned.values()))
        transfer.cleanup(self.options)
        for bucket, fake in fakes.items():
            self.assertEqual(fake.deleted, owned[bucket])  # every bucket loses exactly its own keys
        check = transfer.transfer_check("s3", "up", "throughput", self.options, records)
        self.assertEqual(json.loads(check.detail)["buckets"], ["bench-a", "bench-b"])
        self.assertIn("buckets=bench-a,bench-b", check.source[0])

    def test_single_bucket_regression_normalized_shape(self):
        # A bare name normalizes to a 1-tuple; single-bucket runs keep today's shape.
        self.assertEqual(self.options.buckets, {"s3": ("bench-test",)})
        records = self.reports()
        self.assertEqual(records[0]["buckets"], ["bench-test"])
        self.assertTrue(all(call["buckets"] == ("bench-test",) for call in self.calls))
        self.options.buckets = {"s3": "direct-assign"}  # library callers may assign a bare name
        self.assertEqual(targets.bucket_names("s3", self.options), ("direct-assign",))

    def test_buckets_idle_seconds_boundary_and_partial_tail(self):
        buckets = transfer.throughput_buckets([(0.1, transfer.MIB), (2., transfer.MIB)], 2.5)
        self.assertEqual([b["mib_per_sec"] for b in buckets], [1, 0, 2])
        self.assertEqual([b["start_seconds"] for b in buckets], [0, 1, 2])

    def test_window_profiles_ttfb_post_ttfb_steadiness_and_ceiling(self):
        # FakeClient timings are constant: PUT parts turn around in 2 ms (status
        # line), GET bodies start at 4 ms and stream the range in 1 ms.
        run, _ = self.window()  # up: 4 parts of 8 bytes
        self.assertEqual(run["ttfb_ms"], {"count": 4, "min": 2.0, "max": 2.0, "mean": 2.0,
                                         "p50": 2.0, "p95": 2.0, "p99": 2.0})
        self.assertEqual(run["post_ttfb_mib_per_sec"]["p50"], 8 / transfer.MIB / .001)  # request-phase rate
        self.assertEqual(run["steadiness_ratio"], stats.steadiness([b["mib_per_sec"] for b in run["buckets"]]))
        self.assertEqual(run["ceiling"], transfer.ceiling_verdict(run["bucket_stats"], run["tcp"].get("limits"),
                                                                   run["tcp"]["ratio_pct"]))
        _, objects = self.window()
        with patch.object(transfer, "PART_SIZE", 8):
            run, _ = transfer.transfer_window(self.client, direction="down", prefix="unused/", concurrency=1,
                                            duration=.1, objects=objects, owned=[], one_object=True,
                                            clock=self.clock, tcp_factory=FakeTCP)
        self.assertEqual(run["ttfb_ms"]["p50"], 4.0)  # GET TTFB is the first body byte
        self.assertEqual(run["post_ttfb_mib_per_sec"]["count"], 2)  # one per verified range
        self.assertEqual(run["post_ttfb_mib_per_sec"]["p50"], 8 / transfer.MIB / .001)

    def test_post_ttfb_zero_span_has_no_invented_rate(self):
        # A body that completes with its first byte has no streaming span.
        sample = {"bytes": 16, "connect_ms": 1.0, "response_first_byte_ms": 4.0,
                  "headers_ms": 4.0, "body_first_byte_ms": 5.0, "total_ms": 5.0}
        self.assertIsNone(transfer.post_ttfb_mib_per_sec(sample, "down"))
        self.assertEqual(transfer.ttfb_ms(sample, "down"), 5.0)
        self.assertEqual(transfer.ttfb_ms(sample, "up"), 4.0)

    def test_ceiling_verdict_labels_thresholds_and_retransmit_percent_units(self):
        flat = {"p50": 100, "p95": 110}
        limits = {"busy_pct_median": 100.0, "rwnd_limited_pct_median": 0.0,
                  "cwnd_limited_pct_median": 0.0, "sndbuf_limited_pct_median": 0.0}
        self.assertEqual(transfer.ceiling_verdict(flat, limits, .2)["finding"], "service-paced")
        self.assertEqual(transfer.ceiling_verdict(flat, dict(limits, busy_pct_median=0.0), None)["finding"],
                         "flat ceiling, clean sockets")
        self.assertEqual(transfer.ceiling_verdict(flat, None, None)["finding"], "flat ceiling, clean sockets")  # no owned socket observed
        self.assertEqual(transfer.ceiling_verdict(flat, dict(limits, rwnd_limited_pct_median=40.0), None)["finding"],
                         "receive-window limited")
        self.assertEqual(transfer.ceiling_verdict(flat, dict(limits, cwnd_limited_pct_median=25.0), None)["finding"],
                         "congestion or loss")
        self.assertEqual(transfer.ceiling_verdict(flat, limits, 1.5)["finding"], "congestion or loss")  # elevated retrans
        self.assertEqual(transfer.ceiling_verdict(flat, limits, .5)["finding"], "service-paced")  # 0.5 is 0.5%, not 50%
        self.assertEqual(transfer.ceiling_verdict(flat, dict(limits, sndbuf_limited_pct_median=30.0), None)["finding"],
                         "send-buffer limited")
        self.assertEqual(transfer.ceiling_verdict({"p50": 10, "p95": 30}, limits, None)["finding"], "bursty")
        self.assertEqual(transfer.ceiling_verdict({"p50": 10, "p95": 15}, limits, None)["finding"],
                         "no dominant ceiling signature")  # spread between flat and bursty bands
        self.assertEqual(transfer.ceiling_verdict({"p50": None, "p95": None}, limits, None)["finding"],
                         "no dominant ceiling signature")  # no buckets, no invented shape
        verdict = transfer.ceiling_verdict(flat, limits, .2)
        self.assertIn("not certification gates", verdict["reference"])
        self.assertIn("1.0 = 1%", verdict["reference"])

    def test_multi_bucket_window_reports_per_bucket_sample_evidence(self):
        names = ("bench-a", "bench-b")
        clients = {name: FakeClient() for name in names}
        for name, fake in clients.items():
            fake.bucket = name
        with patch.object(transfer, "PART_SIZE", 8):
            run, _ = transfer.transfer_window(clients[names[0]], direction="up", prefix="rack-bench/test/",
                                              concurrency=4, duration=.1, objects=[], owned=[],
                                              size=16, one_object=True, clock=self.clock, tcp_factory=FakeTCP,
                                              pool_factory=transfer._thread_pool_factory,
                                              buckets=names, clients=clients)
        per_bucket = run["per_bucket"]
        self.assertEqual(set(per_bucket), set(names))  # buckets without samples stay absent, never zeroed
        for name in names:
            self.assertEqual(per_bucket[name]["bytes"], 32)  # two 16-byte objects per bucket
            self.assertEqual(per_bucket[name]["ttfb_ms"]["count"], 4)
            self.assertEqual(per_bucket[name]["post_ttfb_mib_per_sec"]["count"], 4)
            self.assertGreater(per_bucket[name]["mib_per_sec"], 0)
        # Single-bucket windows keep today's shape: no per_bucket key at all.
        single, _ = self.window()
        self.assertNotIn("per_bucket", single)

    def test_transfer_check_surfaces_ceiling_detail_additively(self):
        self.reports()
        records = download.download_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)
        chosen = next(r for r in records[0]["runs_detail"] if r["kind"] == "bulk")
        chosen["per_bucket"] = {"bench-test": {"bytes": 1, "mib_per_sec": 1, "ttfb_ms": {}, "post_ttfb_mib_per_sec": {}}}
        check = transfer.transfer_check("s3", "down", "throughput", self.options, records)
        detail = json.loads(check.detail)
        for field in ("bucket_stats", "p95_p50_ratio", "retransmit_pct", "steadiness_ratio",
                      "ttfb_ms", "post_ttfb_mib_per_sec", "socket_limits", "ceiling", "per_bucket"):
            self.assertIn(field, detail)
        self.assertEqual(detail["ceiling"]["finding"], "flat ceiling, clean sockets")
        self.assertEqual(detail["socket_limits"]["dominant_state"], "busy")
        self.assertEqual(detail["ttfb_ms"]["p50"], 110)
        # Envelope shape is unchanged; only detail fields were added.
        self.assertEqual(detail["selection"], "nearest; median of 3 by MiB/s per concurrency, scalar is largest concurrency; all runs retained")
        self.assertTrue(all("runs_detail" in region for region in detail["regions"]))

    def test_concurrent_loaded_gets_are_inside_upload_window(self):
        started, twice = threading.Event(), threading.Event()
        original = self.client.multipart_upload
        calls = []
        key = "rack-bench/test/loaded.bin"
        payload = upload.SeededPayload(key, upload.LATENCY_SIZE)
        self.client.put_object(key, payload)
        def multipart(*args, **kwargs):
            started.set()
            kwargs["on_progress"](4, .001)
            self.assertTrue(twice.wait(1))
            return original(*args, **kwargs)
        def get(*args, **kwargs):
            self.assertTrue(started.wait(1))
            calls.append(1)
            if len(calls) >= 2:
                twice.set()
            return response(upload.LATENCY_SIZE, "down")
        self.client.multipart_upload, self.client.get_object = multipart, get
        run, _ = self.window(loaded={"key": key, "payload": payload}, loaded_interval=0)
        self.assertTrue(run["loaded_samples"])
        self.assertTrue(all(0 <= s["at_seconds"] <= run["elapsed_seconds"] for s in run["loaded_samples"]))
        self.assertGreaterEqual(run["loaded_bytes"], upload.LATENCY_SIZE)

    def fake_window(self, client, **kwargs):
        self.calls.append(kwargs)
        size = kwargs.get("size", transfer.OBJECT_SIZE) if kwargs["direction"] == "up" else kwargs["objects"][0]["payload"]["size"]
        # One completed object per bucket, mirroring the real round-robin spread.
        objects = [{"key": f'{kwargs["prefix"]}{name}-{index}.bin', "bucket": name,
                    "payload": {"seed": name, "size": size, "chunk_size": 65536}}
                   for index, name in enumerate(kwargs["buckets"])]
        if kwargs["direction"] == "up":
            kwargs["owned"].extend((obj["bucket"], obj["key"]) for obj in objects)
        run = {"status": "pass", "concurrency": kwargs["concurrency"], "bytes": size,
               "mib_per_sec": 100 if kwargs["direction"] == "up" else 50, "objs_per_sec": 2,
               "elapsed_seconds": 1, "progress_bytes_lower_bound": size, "samples": [],
               "bucket_stats": {"p50": 100, "p95": 100}, "p95_p50_ratio": 1,
               "steadiness_ratio": .98,
               "ttfb_ms": {"count": 2, "p50": 110, "p95": 130, "p99": 150},
               "post_ttfb_mib_per_sec": {"count": 2, "p50": 40, "p95": 45},
               "ceiling": {"finding": "flat ceiling, clean sockets",
                           "reference": "tcp_info socket time shares, 1 s bucket percentiles, retransmit percent (1.0 = 1%); diagnostic thresholds, not certification gates"},
               "tcp": FakeTCP("").detail, "loaded_samples": [{"response_first_byte_ms": 45}],
               "loaded_errors": [], "loaded_bytes": upload.LATENCY_SIZE}
        return run, objects

    def reports(self):
        self.calls = []
        return upload.upload_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)

    def baseline(self, p95=20):
        self.options._internet_checks = {"internet.s3.latency.ttfb": Check("internet.s3.latency.ttfb", "pass", 10,
                                                                       detail=json.dumps({"baseline_ms": {"p95": p95}}))}

    def test_quick_plan_and_cache_prevent_duplicate_transfers(self):
        records = self.reports()
        self.assertEqual([(c["concurrency"], c["duration"]) for c in self.calls], [(32, 1), (1, 1)])
        # quick completes 32 MiB objects so download windows can run
        self.assertTrue(all(c["size"] == transfer.LIGHT_SIZE for c in self.calls))
        self.assertEqual(records[0]["object_size"], transfer.LIGHT_SIZE)
        self.assertIs(upload.upload_reports("s3", self.options), records)
        self.assertEqual(len(self.calls), 2)

    def test_certify_sweep_three_runs_and_far_band_hard_budget(self):
        self.options = Options(profile="certify", providers=("s3",), buckets={"s3": "bench-test"})
        records = self.reports()
        self.assertEqual([len(r["runs_detail"]) for r in records], [15, 1, 1])
        self.assertEqual([c["concurrency"] for c in self.calls[:12]], [1]*3 + [8]*3 + [32]*3 + [64]*3)
        self.assertTrue(all(c["duration"] == 300 for c in self.calls))
        self.assertTrue(all(c["size"] == transfer.OBJECT_SIZE for c in self.calls[:12]))  # certify keeps sustained 1 GiB streams
        self.assertTrue(all(c["one_object"] and c["size"] == 32 * transfer.MIB and c["loaded"] is None for c in self.calls[-2:]))
        download.download_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)
        self.assertEqual(len(self.calls), 34)
        self.assertTrue(all(c["direction"] == "up" for c in self.calls[:17]))
        self.assertTrue(all(c["direction"] == "down" for c in self.calls[17:]))
        self.assertTrue(all(c["one_object"] for c in self.calls[-2:]))

    def test_object_size_override_wins_for_quick_and_certify(self):
        for profile in ("quick", "certify"):
            self.options = Options(profile=profile, object_size=64, buckets={"s3": "bench-test"})
            self.reports()
            self.assertTrue(all(c["size"] == 64 * transfer.MIB for c in self.calls))
            self.client.deleted.clear()

    def test_certify_explicit_concurrency_override_and_region_override(self):
        self.options = Options(profile="certify", concurrent=8, regions={"s3": "us-east-1"}, buckets={"s3": "bench-test"})
        records = self.reports()
        self.assertEqual(len(records), 1)
        self.assertEqual([c["concurrency"] for c in self.calls], [8, 8, 8, 1, 1, 1])

    def test_run_shared_seed_records_reproduce_bytes_and_share_digests(self):
        # A run-shared seed keeps keys unique while every object derives the
        # same bytes per offset: stored per-object records reproduce the exact
        # uploaded bytes and sibling parts hit the digest cache.
        uploads = {}
        original = self.client.multipart_upload
        def recording(key, payload, part_size, on_part, on_progress):
            uploads[key] = payload
            return original(key, payload, part_size, on_part, on_progress)
        self.client.multipart_upload = recording
        run, objects = self.window(seed="run-token")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(len(objects), 2)
        self.assertEqual(len(uploads), 2)  # keys stay unique; only the seed is shared
        for obj in objects:
            self.assertEqual(obj["payload"]["seed"], "run-token")
            self.assertEqual(obj["payload"]["chunk_size"], 1024 * 1024)
            record = transfer.SeededPayload(**obj["payload"])
            record.verify(b"".join(uploads[obj["key"]].iter_chunks()))
        one, two = list(uploads.values())
        self.assertEqual(s3.part_checksum_headers(one, 0, 8),
                         s3.part_checksum_headers(two, 0, 8))

    def test_three_run_reduction_drops_best_worst_and_rejects_failures(self):
        runs = [{"status": "pass", "mib_per_sec": n} for n in (10, 100, 20)]
        self.assertEqual(transfer.reduce_runs(runs)["mib_per_sec"], 20)
        runs[0]["status"] = "skip"
        self.assertIsNone(transfer.reduce_runs(runs))
        self.assertIsNone(transfer.reduce_runs(runs[:2]))

    def test_loaded_gate_is_detail_not_warn_or_expected(self):
        self.baseline()
        self.reports()
        check = upload.loaded_probe("s3", self.options)
        self.assertEqual((check.status, check.value, check.expected), ("pass", 45, None))
        detail = json.loads(check.detail)
        self.assertEqual(detail["inflation_ms"], 25)
        self.assertTrue(detail["gate_exceeded"])
        self.baseline(25)
        self.assertFalse(json.loads(upload.loaded_probe("s3", self.options).detail)["gate_exceeded"])

    def test_loaded_three_run_reduction_and_dedicated_single_has_no_load(self):
        self.options = Options(profile="certify", buckets={"s3": "bench-test"})
        self.baseline()
        records = self.reports()
        for run in records[0]["runs_detail"]:
            run["loaded_samples"] = [{"response_first_byte_ms": [10, 100, 30][run["run"]]}]
        check = upload.loaded_probe("s3", self.options)
        self.assertEqual(check.value, 30)
        self.assertEqual(json.loads(check.detail)["retained_run_by_concurrency"], {"1": 2, "8": 2, "32": 2, "64": 2})
        self.assertTrue(all(c["loaded"] is None for c in self.calls[12:]))
        self.assertTrue(all(c["host"] == "bench-test.s3.ap-south-1.amazonaws.com" for c in self.calls[:15]))

    def test_loaded_without_baseline_and_download_without_upload_skip(self):
        self.assertIn("baseline_ms.p95", upload.loaded_probe("s3", self.options).detail)
        check = download.download_probe("s3", "throughput", self.options)
        self.assertEqual(check.status, "skip")
        self.assertIn("upload objects", check.detail)
        self.baseline()
        self.assertIn("upload transfer window", upload.loaded_probe("s3", self.options).detail)

    def test_directions_disabled_and_failed_upload_dependency(self):
        self.options.directions = ("down",)
        self.assertIn("direction up disabled", upload.upload_probe("s3", "throughput", self.options).detail)
        self.options.directions = ("up",)
        self.assertIn("direction down disabled", download.download_probe("s3", "throughput", self.options).detail)
        records = self.reports()
        records[0]["runs_detail"][0]["status"] = "skip"
        self.options.directions = ("up", "down")
        check = download.download_probe("s3", "throughput", self.options)
        self.assertEqual(check.status, "skip")
        self.assertIn("successful upload", check.detail)

    def test_asymmetry_bdp_and_no_invented_download_window(self):
        self.reports()
        records = download.download_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)
        check = transfer.transfer_check("s3", "down", "throughput", self.options, records)
        self.assertEqual(json.loads(check.detail)["download_to_upload_ratio"], .5)
        self.assertIsNone(json.loads(check.detail)["single_stream"]["expected_mib_per_sec"])
        signal = transfer.bdp(1, 100, transfer.MIB, 10)
        self.assertEqual(signal["expected_mib_per_sec"], 100)
        self.assertIn("node-side", signal["finding"])
        self.assertAlmostEqual(transfer.bdp(1, 1000, 1024 * transfer.MIB, 1)["expected_mib_per_sec"], 5e9/8/transfer.MIB)
        self.assertIsNone(transfer.bdp(1, 100, None, 10)["expected_mib_per_sec"])

    def test_cleanup_exact_owned_keys_keep_data_and_failure(self):
        records = self.reports()
        owned = list(records[0]["owned"])
        records[0]["owned"].append(("bench-test", "someone-elses/key"))
        transfer.cleanup(self.options)
        self.assertEqual(self.client.deleted, [key for _, key in owned])
        self.assertIn("outside owned prefix", records[0]["cleanup_errors"][0]["reason"])
        self.assertEqual(transfer.transfer_check("s3", "up", "throughput", self.options, records).status, "skip")
        self.options.keep_data = True
        self.client.deleted.clear()
        transfer.cleanup(self.options)
        self.assertEqual(self.client.deleted, [])
        self.assertIn("retained", records[0]["cleanup"])

    def test_finalizer_runs_with_filtered_summary_and_on_exception(self):
        def probe(options):
            self.reports()
            return transfer.transfer_check("s3", "up", "throughput", options, options._transfer_reports["s3"]["up"])
        with patch.dict(internet.CHECKS, {"internet.s3.upload.throughput": probe}, clear=True):
            result = runner.collect("internet", options=self.options)[0]
        self.assertTrue(self.client.deleted)
        self.assertIn("deleted exact owned keys", result.checks[0].detail)
        def broken(options):
            self.reports()
            raise RuntimeError("probe interrupted")
        self.client.deleted.clear()
        with patch.dict(internet.CHECKS, {"internet.s3.upload.throughput": broken}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                runner.collect("internet", options=self.options)
        self.assertTrue(self.client.deleted)

    def test_failed_check_cleanup_details_are_refreshed_without_summary(self):
        def failed(options):
            records = self.reports()
            records[0]["runs_detail"][0]["status"] = "skip"
            return transfer.transfer_check("s3", "up", "throughput", options, records)
        self.client.delete_object = Mock(side_effect=TransportError("delete failed"))
        with patch.dict(internet.CHECKS, {"internet.s3.upload.throughput": failed}, clear=True):
            check = runner.collect("internet", options=self.options)[0].checks[0]
        self.assertEqual(check.status, "skip")
        self.assertIn("delete failed", check.detail)
        self.assertNotIn("pending collection finalizer", check.detail)

    def test_tcp_scalar_excludes_light_bands(self):
        self.options = Options(profile="certify", buckets={"s3": "bench-test"})
        records = self.reports()
        for region in records[1:]:
            region["runs_detail"][0]["tcp"]["retransmits"] = 999
        check = tcp.retransmit_probe("s3", self.options)
        self.assertEqual(check.value, .2)
        self.assertEqual(len(json.loads(check.detail)["regions"]), 3)
        self.assertIsNone(check.expected)

    def test_new_collection_resets_all_state(self):
        self.reports()
        self.baseline()
        self.assertEqual(targets.run_seed(self.options), targets.run_seed(self.options))
        before_run(self.options)
        for key in ("_internet_prefix", "_internet_seed", "_transfer_reports", "_transfer_owners", "_internet_checks"):
            self.assertNotIn(key, vars(self.options))

    def test_summary_artifacts_json_and_human_rendering(self):
        def probe(options):
            records = self.reports()
            return transfer.transfer_check("s3", "up", "throughput", options, records)
        checks = {"internet.s3.upload.throughput": probe, "internet.s3.summary": internet.CHECKS["internet.s3.summary"]}
        with patch.dict(internet.CHECKS, checks, clear=True), tempfile.TemporaryDirectory() as tmp, redirect_stdout(StringIO()) as out:
            runner.run("internet", options=self.options, json_target="-", run_dir=tmp)
            document = json.loads(out.getvalue())
            summary = document["results"][0]["checks"][-1]
            self.assertEqual(summary["status"], "pass")
            self.assertEqual(summary["value"]["bytes"]["uploaded"], 2 * transfer.LIGHT_SIZE)  # quick uploads 32 MiB objects
            self.assertEqual(json.loads(summary["detail"])["cleanup"][0]["status"], "deleted exact owned keys")
            # The ceiling verdict lands in the summary value, detail and human line.
            self.assertEqual(summary["value"]["ceiling"], {"upload": "flat ceiling, clean sockets"})
            self.assertEqual(json.loads(summary["detail"])["ceiling_findings"], {"upload": "flat ceiling, clean sockets"})
            self.assertEqual(Path(tmp, "bench.values.json").read_text(), out.getvalue())
            self.assertIn("upload=100.00 MiB/s", Path(tmp, "bench.out").read_text())
            self.assertIn("ceiling upload=flat ceiling, clean sockets", Path(tmp, "bench.out").read_text())


class WorkerProcessS3(BaseHTTPRequestHandler):
    """Loopback S3 for the real worker-process path: multipart PUT, range GET,
    abort DELETE, and a loadable failure hook. Serves seeded bytes only."""

    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _drain(self):
        remaining = int(self.headers.get("Content-Length", "0"))
        data = bytearray()
        while remaining:
            block = self.rfile.read(min(1 << 16, remaining))
            if not block:
                break
            data.extend(block)
            remaining -= len(block)
        return bytes(data)

    def _reply(self, status=200, body=b"", headers=None):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _record(self):
        self.server.state.setdefault("requests", []).append((self.command, self.path))

    def do_POST(self):
        self._record()
        self._drain()
        if "uploads" in self.path:
            self._reply(body=b"<InitiateMultipartUploadResult><UploadId>proc-1</UploadId></InitiateMultipartUploadResult>")
        else:
            self._reply(body=b"<CompleteMultipartUploadResult><ETag>done</ETag></CompleteMultipartUploadResult>")

    def do_PUT(self):
        self._record()
        body = self._drain()
        if self.server.state.get("fail_prefix") and self.server.state["fail_prefix"] in self.path:
            self._reply(503, b"<Error><Code>SlowDown</Code></Error>")
            return
        crc = base64.b64encode(zlib.crc32(body).to_bytes(4, "big")).decode()
        self._reply(headers={"ETag": '"part"', "x-amz-checksum-crc32": crc})

    def do_GET(self):
        self._record()
        spec = self.headers.get("Range")
        if spec:  # verified range GETs from worker processes
            payload = self.server.state["payload"]
            start, end = map(int, spec.removeprefix("bytes=").split("-"))
            self._reply(206, b"".join(payload.iter_chunks(start, end - start + 1)),
                        {"Content-Range": f"bytes {start}-{end}/{payload.size}"})
        else:  # parent-side loaded-latency probe: one cold full-object GET
            payload = self.server.state["loaded_payload"]
            self._reply(200, b"".join(payload.iter_chunks()))

    def do_DELETE(self):
        self._record()
        self._drain()
        self._reply(204)


class ProcessPoolTransferTests(unittest.TestCase):
    """The real process-pool path: worker processes build their own S3Client
    from plain config, validate parts in-process, and return picklable results
    the parent merges. The loaded-latency probe stays parent-side. FakeTCP
    stands in for ss diagnostics; the clock is the real monotonic clock."""

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), WorkerProcessS3)
        cls.server_beta = ThreadingHTTPServer(("127.0.0.1", 0), WorkerProcessS3)  # second bucket root
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread_beta = threading.Thread(target=cls.server_beta.serve_forever, daemon=True)
        cls.thread.start()
        cls.thread_beta.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server_beta.shutdown()
        cls.server.server_close()
        cls.server_beta.server_close()
        cls.thread.join()
        cls.thread_beta.join()

    def setUp(self):
        env = patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "fake", "AWS_SECRET_ACCESS_KEY": "fake", "R2_ACCOUNT_ID": "fake"}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(s3.clear_payload_caches)
        self.addCleanup(lambda: s3.set_chunk_cache_limit(s3.CHUNK_CACHE_LIMIT))
        self.addCleanup(transfer._POOL_STATE.clear)
        self.endpoint = s3.Endpoint("127.0.0.1", "auto", True, self.server.server_port, False)
        self.endpoint_beta = s3.Endpoint("127.0.0.1", "auto", True, self.server_beta.server_port, False)
        self.client = S3Client("bucket", "auto", timeout=10, backoff=0, endpoint=self.endpoint)
        self.addCleanup(self.client.close)
        self.size, self.part = 16 * transfer.MIB, 8 * transfer.MIB

    def test_upload_worker_processes_build_clients_validate_and_merge(self):
        loaded = {"key": "proc/loaded.bin", "payload": s3.SeededPayload("proc-seed", LATENCY_SIZE)}
        self.server.state = {"payload": s3.SeededPayload("proc-seed", self.size),
                             "loaded_payload": s3.SeededPayload("proc-seed", LATENCY_SIZE),
                             "requests": []}
        owned = []
        run, objects = transfer.transfer_window(self.client, direction="up", prefix="proc/", concurrency=2,
                                                 duration=.05, objects=[], owned=owned, size=self.size,
                                                 one_object=True, part_size=self.part, seed="proc-seed",
                                                 loaded=loaded, loaded_interval=.05,
                                                 tcp_factory=FakeTCP, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 2 * self.size)
        self.assertEqual(run["objects"], 2)
        self.assertEqual([sample["part"] for sample in run["samples"]], [0, 1, 0, 1])  # two parts per process
        self.assertEqual([obj["key"] for obj in objects], ["proc/0-0.bin", "proc/1-0.bin"])
        self.assertEqual(owned, [("bucket", "proc/0-0.bin"), ("bucket", "proc/1-0.bin")])  # ambiguous PUTs stay cleanable
        self.assertEqual(run["progress_bytes_lower_bound"], 2 * self.size)
        self.assertEqual(run["errors"], [])
        self.assertTrue(all(obj["payload"]["seed"] == "proc-seed" for obj in objects))
        self.assertTrue(all(obj["bucket"] == "bucket" for obj in objects))  # records name their bucket
        self.assertEqual({sample["bucket"] for sample in run["samples"]}, {"bucket"})
        # Loaded-latency stays a parent-side probe with fresh-connection semantics.
        self.assertTrue(run["loaded_samples"])
        self.assertTrue(all(0 <= sample["at_seconds"] <= run["elapsed_seconds"] for sample in run["loaded_samples"]))
        self.assertGreaterEqual(run["loaded_bytes"], LATENCY_SIZE)

    def test_download_worker_processes_stream_verified_ranges(self):
        self.server.state = {"payload": s3.SeededPayload("proc-seed", self.size), "requests": []}
        objects = [{"key": f"proc/{index}-0.bin",
                    "payload": {"seed": "proc-seed", "size": self.size, "chunk_size": 1024 * 1024}}
                   for index in range(2)]
        run, completed = transfer.transfer_window(self.client, direction="down", prefix="unused/", concurrency=2,
                                                   duration=.05, objects=objects, owned=[], one_object=True,
                                                   part_size=self.part, tcp_factory=FakeTCP, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 2 * self.size)
        self.assertEqual([obj["key"] for obj in completed], ["proc/0-0.bin", "proc/1-0.bin"])
        self.assertEqual(len(run["samples"]), 4)
        self.assertEqual(run["errors"], [])

    def test_gcs_worker_processes_upload_and_stream_verified_ranges(self):
        # End-to-end gcs provider path through the real worker processes:
        # children build gcs clients (GCS env names, location-scoped signing,
        # no flexible checksums), upload parts, then read verified ranges back.
        env = patch.dict(os.environ, {"GCS_ACCESS_KEY_ID": "fake", "GCS_SECRET_ACCESS_KEY": "fake"})
        env.start()
        self.addCleanup(env.stop)
        endpoint = s3.Endpoint("127.0.0.1", "asia-south1", True, self.server.server_port, False)
        client = S3Client("bucket", "asia-south1", provider="gcs", timeout=10, backoff=0,
                          endpoint=endpoint)
        self.addCleanup(client.close)
        self.server.state = {"payload": s3.SeededPayload("gcs-seed", self.size), "requests": []}
        owned = []
        run, objects = transfer.transfer_window(client, direction="up", prefix="gcs/", concurrency=2,
                                                 duration=.05, objects=[], owned=owned, size=self.size,
                                                 one_object=True, part_size=self.part, seed="gcs-seed",
                                                 tcp_factory=FakeTCP, host="127.0.0.1", provider="gcs")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 2 * self.size)
        self.assertEqual(run["errors"], [])
        run, completed = transfer.transfer_window(client, direction="down", prefix="unused/",
                                                   concurrency=2, duration=.05, objects=objects,
                                                   owned=[], one_object=True, part_size=self.part,
                                                   tcp_factory=FakeTCP, host="127.0.0.1", provider="gcs")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 2 * self.size)
        self.assertEqual(run["errors"], [])

    def test_multi_bucket_worker_processes_route_by_recorded_bucket(self):
        # Two loopback roots, one per bucket: worker processes build a client
        # per bucket from the pool initargs, streams shard round-robin, and
        # downloads follow each record's bucket, not the stream assignment.
        clients = {"alpha": S3Client("alpha", "auto", timeout=10, backoff=0, endpoint=self.endpoint),
                   "beta": S3Client("beta", "auto", timeout=10, backoff=0, endpoint=self.endpoint_beta)}
        for server in (self.server, self.server_beta):
            server.state = {"payload": s3.SeededPayload("proc-seed", self.size), "requests": []}
        owned = []
        run, objects = transfer.transfer_window(clients["alpha"], direction="up", prefix="proc/",
                                                 concurrency=4, duration=.05, objects=[], owned=owned,
                                                 size=self.size, one_object=True, part_size=self.part,
                                                 seed="proc-seed", buckets=("alpha", "beta"), clients=clients,
                                                 tcp_factory=FakeTCP, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["bytes"], 4 * self.size)
        self.assertEqual([obj["bucket"] for obj in objects], ["alpha", "beta", "alpha", "beta"])
        self.assertEqual([obj["key"] for obj in objects], [f"proc/{index}-0.bin" for index in range(4)])
        self.assertEqual(owned, [(obj["bucket"], obj["key"]) for obj in objects])
        for server, name in ((self.server, "alpha"), (self.server_beta, "beta")):
            paths = [path for _, path in server.state["requests"]]
            self.assertTrue(paths)
            self.assertTrue(all(f"/{name}/" in path for path in paths))  # this root saw only its bucket
        self.server.state["requests"] = []
        self.server_beta.state["requests"] = []
        run, completed = transfer.transfer_window(clients["alpha"], direction="down", prefix="unused/",
                                                   concurrency=2, duration=.05, objects=objects, owned=[],
                                                   one_object=True, part_size=self.part,
                                                   buckets=("alpha", "beta"), clients=clients,
                                                   tcp_factory=FakeTCP, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        self.assertEqual([obj["bucket"] for obj in completed], ["alpha", "beta"])
        gets = {name: {path for method, path in server.state["requests"] if method == "GET"}
                for server, name in ((self.server, "alpha"), (self.server_beta, "beta"))}
        self.assertEqual({path for paths in gets.values() for path in paths},
                         {f'/{obj["bucket"]}/{obj["key"]}' for obj in completed})
        for name, paths in gets.items():
            self.assertTrue(all(f"/{name}/" in path for path in paths))
        # Cleanup deletes every owned key from the bucket that holds it.
        options = Options(providers=("s3",), buckets={"s3": ("alpha", "beta")}, duration=1)
        prefix = targets.run_prefix(options) + "s3/ap-south-1/transfer/"
        options.__dict__["_transfer_owners"] = [(clients, {"owned": [("alpha", prefix + "a.bin"),
                                                                      ("beta", prefix + "b.bin")]}, prefix)]
        self.server.state["requests"] = []
        self.server_beta.state["requests"] = []
        transfer.cleanup(options)
        deletes = {name: [path for method, path in server.state["requests"]
                          if method == "DELETE" and "uploadId" not in path]
                   for server, name in ((self.server, "alpha"), (self.server_beta, "beta"))}
        self.assertEqual(deletes["alpha"], [f"/alpha/{prefix}a.bin"])
        self.assertEqual(deletes["beta"], [f"/beta/{prefix}b.bin"])

    def test_loopback_window_captures_socket_limits_and_passes_without_sockets(self):
        # Real worker processes on loopback with the real TCPWindow: the ss
        # command is faked (macOS dev hosts have no ss); the flags capture and
        # the socket-less fallback are what is under test.
        self.server.state = {"payload": s3.SeededPayload("proc-seed", self.size), "requests": []}
        info = (" cubic rtt:1/1 mss:1448 cwnd:10 data_segs_out:5 segs_out:6 "
                "delivery_rate 65208000000bps busy:3529ms rwnd_limited:1411ms(40.0%)")
        text = f'ESTAB 0 0 127.0.0.1:1 192.0.2.1:443 users:(("python",pid={os.getpid()},fd=4))\n\t{info}\n'
        objects = [{"key": "proc/0-0.bin", "bucket": "bucket",
                    "payload": {"seed": "proc-seed", "size": self.size, "chunk_size": 1024 * 1024}}]
        def flagged(host, pids=None):
            return tcp.TCPWindow(host, command=lambda args, timeout: text, interval=.05, pids=pids)
        run, _ = transfer.transfer_window(self.client, direction="down", prefix="unused/",
                                           concurrency=2, duration=.05, objects=objects, owned=[],
                                           one_object=True, part_size=self.part,
                                           tcp_factory=flagged, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        limits = run["tcp"]["limits"]
        self.assertGreater(limits["ticks"], 0)  # flag capture present in detail
        self.assertEqual(limits["busy_pct_median"], 100.0)
        self.assertEqual(limits["rwnd_limited_pct_median"], 40.0)
        self.assertEqual(limits["dominant_state"], "rwnd_limited")
        self.assertEqual(run["ceiling"]["finding"], "receive-window limited")
        # ss with no matching sockets: the window still passes, limits explain themselves.
        def socketless(host, pids=None):
            return tcp.TCPWindow(host, command=lambda args, timeout: "", interval=.05, pids=pids)
        run, _ = transfer.transfer_window(self.client, direction="down", prefix="unused/",
                                           concurrency=2, duration=.05, objects=objects, owned=[],
                                           one_object=True, part_size=self.part,
                                           tcp_factory=socketless, host="127.0.0.1")
        self.assertEqual(run["status"], "pass")
        self.assertEqual(run["tcp"]["limits"]["ticks"], 0)
        self.assertIn("no sample tick", run["tcp"]["limits"]["reason"])
        self.assertIn(run["ceiling"]["finding"],  # a verdict still lands from the bucket shape
                      {"service-paced", "receive-window limited", "congestion or loss", "send-buffer limited",
                       "flat ceiling, clean sockets", "bursty", "no dominant ceiling signature"})

    def test_worker_error_sets_cross_process_stop_and_siblings_drain_out(self):
        self.server.state = {"payload": s3.SeededPayload("proc-seed", self.size),
                             "fail_prefix": "0-0", "requests": []}
        owned = []
        run, _ = transfer.transfer_window(self.client, direction="up", prefix="proc/", concurrency=2,
                                           duration=10, objects=[], owned=owned, size=self.size,
                                           part_size=self.part, seed="proc-seed",
                                           tcp_factory=FakeTCP, host="127.0.0.1")
        self.assertEqual(run["status"], "skip")
        self.assertEqual(run["errors"][0]["type"], "ServiceError")
        self.assertIn(("bucket", "proc/0-0.bin"), owned)
        # The multiprocessing stop event reaches sibling processes: no worker
        # streams for the full scheduled window after the first failure.
        self.assertLess(run["elapsed_seconds"], 10)
        self.assertTrue(any(method == "DELETE" and "uploadId" in path
                            for method, path in self.server.state["requests"]))  # aborted upload IDs

    def test_pool_initialiser_state_and_picklable_worker_task(self):
        import pickle
        slots = multiprocessing.Array("i", 2)
        stop = multiprocessing.Event()
        transfer._pool_initialiser((("bucket", self.endpoint, 10, 2, 0, "s3"),), stop, slots,
                                   2 * 1024 * 1024, None)
        self.assertIsInstance(transfer._POOL_STATE["clients"]["bucket"], S3Client)
        self.assertIs(transfer._POOL_STATE["stop"], stop)
        self.assertIn(os.getpid(), list(slots))
        s3.clear_payload_caches()
        payload = s3.SeededPayload("cap-seed", 6 * 1024 * 1024)
        for chunk_index in range(3):
            payload.chunk(chunk_index)
        self.assertEqual(s3._CHUNK_CACHE.total, 2 * 1024 * 1024)  # re-capped per process
        self.assertIs(pickle.loads(pickle.dumps(transfer._transfer_worker)), transfer._transfer_worker)
        task = {"direction": "up", "prefix": "p/", "index": 3, "objects": [], "size": 8,
                "one_object": True, "deadline": 1.5, "start": .5, "part_size": 8, "seed": None,
                "clock": time.monotonic, "bucket": "bucket", "clients": None, "stop": None, "active": None}
        self.assertEqual(pickle.loads(pickle.dumps(task)), task)  # the process-mode task payload


class TCPTests(unittest.TestCase):
    def test_ss_captured_positive_negative_and_process_filter(self):
        text = (FIXTURES / "internet-ss.txt").read_text()
        parsed = tcp.parse_ss(text)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(list(parsed.values())[0]["retransmits"], 0)
        self.assertEqual(list(parsed.values())[1]["retransmits"], 2383)
        self.assertEqual(list(parsed.values())[0]["window_bytes"], 115300)
        self.assertEqual(tcp.parse_ss(text, 123), {})
        self.assertEqual(tcp.parse_ss("ESTAB 0 0 a b\n cubic rcv_space:100"), {})
        owned = text.replace("127.0.0.1:35823", '127.0.0.1:35823 users:(("python",pid=123,fd=4))')
        self.assertEqual(len(tcp.parse_ss(owned, 123)), 1)

    def test_ss_deltas_not_lifetime_counters_and_counter_resets(self):
        first = tcp.parse_ss((FIXTURES / "internet-ss.txt").read_text())
        second = deepcopy(first)
        for entry in second.values():
            entry["segments"] += 1000
            entry["retransmits"] += 2
        delta = tcp.tcp_deltas([first, second])
        self.assertEqual((delta["segments"], delta["retransmits"], delta["ratio_pct"]), (2000, 4, .2))
        self.assertIsNone(tcp.tcp_deltas([second, first])["ratio_pct"])
        self.assertIsNone(tcp.tcp_deltas([{}, first])["ratio_pct"])

    def test_ping_captured_pass_mtu_and_synthetic_timeout(self):
        self.assertEqual(tcp.parse_ping((FIXTURES / "internet-ping-pass.txt").read_text()), "pass")
        self.assertEqual(tcp.parse_ping((FIXTURES / "internet-ping-mtu.txt").read_text()), "too_large")
        self.assertEqual(tcp.parse_ping("2 packets transmitted, 0 received, 100% packet loss, time 1001ms"), "timeout")
        self.assertEqual(tcp.parse_ping("ping: socket: Operation not permitted"), "unavailable")

    def test_ss_pid_iterable_scopes_parent_and_worker_processes(self):
        text = (FIXTURES / "internet-ss.txt").read_text()
        tagged = text.replace("127.0.0.1:35823", '127.0.0.1:35823 users:(("python",pid=123,fd=4))') \
                     .replace("127.0.0.1:59364", '127.0.0.1:59364 users:(("python",pid=456,fd=5))')
        self.assertEqual(len(tcp.parse_ss(tagged, {123, 456})), 2)  # parent + worker pids
        self.assertEqual(len(tcp.parse_ss(tagged, (456,))), 1)  # any int iterable
        self.assertEqual(tcp.parse_ss(tagged, {9999}), {})

    def test_tcp_window_pid_provider_covers_worker_processes(self):
        text = (FIXTURES / "internet-ss.txt").read_text()
        both = text.replace("127.0.0.1:35823", '127.0.0.1:35823 users:(("python",pid=123,fd=4))') \
                   .replace("127.0.0.1:59364", '127.0.0.1:59364 users:(("python",pid=456,fd=5))')
        grown = both.replace("data_segs_out:126952", "data_segs_out:127952")
        command = Mock(side_effect=[both, grown])
        with patch.object(tcp.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("192.0.2.1", 443))]):
            with tcp.TCPWindow("example.invalid", command=command, interval=1000, pids=lambda: {123, 456}) as window:
                self.assertEqual(command.call_count, 1)
        self.assertEqual(command.call_count, 2)
        self.assertEqual(window.detail["segments"], 1000)
        self.assertEqual(window.detail["ratio_pct"], 0)
        self.assertEqual(window.detail["owned_pids"], [123, 456])

    def test_pmtud_clean_blackhole_and_all_filtered_are_not_warn(self):
        options = Options(providers=("s3",))
        good = (FIXTURES / "internet-ping-pass.txt").read_text()
        timeout = "2 packets transmitted, 0 received, 100% packet loss, time 1001ms"
        with patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "fake", "AWS_SECRET_ACCESS_KEY": "fake"}, clear=True):
            for replies, status, value in (([good]*3, "pass", 1472), ([good, timeout, timeout], "pass", 1200), ([timeout]*3, "skip", None)):
                check = tcp.pmtud_probe("s3", options, command=Mock(side_effect=replies))
                self.assertEqual((check.status, check.value, check.expected), (status, value, None))
                if value == 1200:
                    self.assertIn("possible PMTUD blackhole", check.detail)

    def test_tcp_window_brackets_with_owned_snapshots_and_no_remote_io(self):
        text = (FIXTURES / "internet-ss.txt").read_text().replace("127.0.0.1:35823", f'127.0.0.1:35823 users:(("python",pid={os.getpid()},fd=4))')
        command = Mock(side_effect=[text, text.replace("data_segs_out:262", "data_segs_out:1262")])
        with patch.object(tcp.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("192.0.2.1", 443))]):
            with tcp.TCPWindow("example.invalid", command=command, interval=1000) as window:
                self.assertEqual(command.call_count, 1)
        self.assertEqual(command.call_count, 2)
        self.assertEqual(window.detail["segments"], 1000)
        self.assertEqual(window.detail["ratio_pct"], 0)
        self.assertIn("192.0.2.1", window.sources[0])

    def test_ss_limit_flags_captured_and_absent_flags_zero(self):
        text = (FIXTURES / "internet-ss.txt").read_text()
        parsed = tcp.parse_ss(text)
        first, second = list(parsed.values())
        # The capture has busy/delivery_rate/cwnd but no limit flags (the kernel
        # reported none): absent shares are zero, never invented.
        self.assertEqual(first["busy_pct"], 100.0)
        self.assertEqual((first["rwnd_limited_pct"], first["cwnd_limited_pct"], first["sndbuf_limited_pct"]),
                         (0.0, 0.0, 0.0))
        self.assertEqual(first["delivery_rate_bps"], 65208000000.0)
        self.assertEqual(first["cwnd"], 10)
        self.assertEqual(second["busy_pct"], 100.0)
        self.assertEqual(second["retransmits"], 2383)  # existing counters unchanged

    def test_ss_limit_shares_paren_percent_and_scaled_rates(self):
        info = (" cubic rtt:1.2/0.3 mss:1448 cwnd:42 data_segs_out:9 segs_out:10 "
                "delivery_rate 48.5kbps delivered:9 busy:1000ms "
                "rwnd_limited:400ms(40.0%) cwnd_limited:0ms(0.0%) sndbuf_limited:100ms(10.5%)")
        text = (f'ESTAB 0 0 10.0.0.1:5 192.0.2.1:443 users:(("python",pid={os.getpid()},fd=4))\n\t{info}\n')
        entry = tcp.parse_ss(text, os.getpid())["10.0.0.1:5 192.0.2.1:443"]
        self.assertEqual(entry["busy_pct"], 100.0)
        self.assertEqual(entry["rwnd_limited_pct"], 40.0)
        self.assertEqual(entry["cwnd_limited_pct"], 0.0)
        self.assertEqual(entry["sndbuf_limited_pct"], 10.5)
        self.assertEqual(entry["delivery_rate_bps"], 48500.0)
        self.assertEqual(entry["cwnd"], 42)

    def test_ss_limit_shares_defensive_formats_and_malformed(self):
        def entry(info):
            text = f"ESTAB 0 0 10.0.0.1:5 192.0.2.1:443\n\t cubic data_segs_out:9 {info}\n"
            return tcp.parse_ss(text)["10.0.0.1:5 192.0.2.1:443"]
        # Older token shape: usec durations without a printed share derive it from busy.
        old = entry("busy:142841usec rwnd_limited:578usec")
        self.assertEqual(old["busy_pct"], 100.0)
        self.assertAlmostEqual(old["rwnd_limited_pct"], 100 * .578 / 142.841)
        # Percent tokens and sec durations.
        self.assertEqual(entry("busy:88% rwnd_limited:12.5% sndbuf_limited:25%")["sndbuf_limited_pct"], 25.0)
        self.assertEqual(entry("busy:2.5sec sndbuf_limited:500ms(20%)")["sndbuf_limited_pct"], 20.0)
        # A limited duration without any busy denominator stays zero, not a guess.
        self.assertEqual(entry("cwnd_limited:400ms")["cwnd_limited_pct"], 0.0)
        # Scaled delivery rates.
        self.assertEqual(entry("busy:1ms delivery_rate 1.2Mbps")["delivery_rate_bps"], 1.2e6)
        self.assertEqual(entry("busy:1ms delivery_rate 65.2Gbps cwnd:55")["delivery_rate_bps"], 65.2e9)
        # Malformed tokens never raise and never invent a value.
        broken = entry("busy:soon rwnd_limited: cwnd_limited:-3ms delivery_rate fast cwnd:x")
        self.assertEqual((broken["busy_pct"], broken["rwnd_limited_pct"], broken["cwnd_limited_pct"]),
                         (0.0, 0.0, 0.0))
        self.assertIsNone(broken["delivery_rate_bps"])
        self.assertIsNone(broken["cwnd"])

    def test_limit_ticks_and_stats_medians_and_dominant_states(self):
        def socket(busy=0.0, rwnd=0.0, cwnd=0.0, sndbuf=0.0):
            return {"segments": 1, "retransmits": 0, "rtt_ms": 1.0, "window_bytes": None,
                    "receive_window_bytes": None, "busy_pct": busy, "rwnd_limited_pct": rwnd,
                    "cwnd_limited_pct": cwnd, "sndbuf_limited_pct": sndbuf,
                    "delivery_rate_bps": 1000.0, "cwnd": 10}
        first = {"a b": socket(busy=100.0), "c d": socket(busy=100.0, rwnd=40.0),
                 "e f": socket(busy=100.0, rwnd=80.0)}
        second = {"a b": socket(busy=100.0, cwnd=30.0)}
        ticks = tcp.limit_ticks([{}, first, second])
        self.assertEqual([tick["sockets"] for tick in ticks], [2 + 1, 1])  # socket-less ticks stay absent
        self.assertEqual(ticks[0]["busy_pct"], 100.0)
        self.assertEqual(ticks[0]["rwnd_limited_pct"], 40.0)  # median of 0, 40, 80
        self.assertEqual(ticks[0]["dominant_states"], {"busy": 1, "rwnd_limited": 2})
        self.assertEqual(ticks[1]["dominant_states"], {"cwnd_limited": 1})
        self.assertEqual(ticks[0]["delivery_rate_bps"], 1000.0)
        stats_aggregate = tcp.limit_stats(ticks)
        self.assertEqual(stats_aggregate["ticks"], 2)
        self.assertEqual(stats_aggregate["busy_pct_median"], 100.0)
        self.assertEqual(stats_aggregate["rwnd_limited_pct_median"], 20.0)  # median of 40 and 0
        self.assertEqual(stats_aggregate["cwnd_limited_pct_median"], 15.0)
        self.assertEqual(stats_aggregate["sockets_per_dominant_state"],
                         {"busy": 1, "rwnd_limited": 2, "cwnd_limited": 1})
        self.assertEqual(stats_aggregate["dominant_state"], "rwnd_limited")
        self.assertEqual(stats_aggregate["delivery_rate_bps_median"], 1000.0)
        self.assertEqual(stats_aggregate["cwnd_median"], 10)
        empty = tcp.limit_stats(tcp.limit_ticks([{}, {}]))
        self.assertEqual(empty["ticks"], 0)
        self.assertIn("no sample tick", empty["reason"])

    def test_tcp_window_limits_in_detail_with_and_without_owned_sockets(self):
        info = (" cubic rtt:1/1 mss:1448 cwnd:10 data_segs_out:5 segs_out:6 "
                "delivery_rate 65208000000bps busy:3529ms rwnd_limited:1411ms(40.0%)")
        text = f'ESTAB 0 0 127.0.0.1:1 192.0.2.1:443 users:(("python",pid={os.getpid()},fd=4))\n\t{info}\n'
        with patch.object(tcp.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("192.0.2.1", 443))]):
            with tcp.TCPWindow("example.invalid", command=lambda args, timeout: text, interval=1000) as window:
                pass
        limits = window.detail["limits"]
        self.assertEqual(limits["ticks"], 2)  # enter and exit samples
        self.assertEqual(limits["busy_pct_median"], 100.0)
        self.assertEqual(limits["rwnd_limited_pct_median"], 40.0)
        self.assertEqual(limits["sockets_per_dominant_state"], {"rwnd_limited": 2})
        self.assertEqual(limits["dominant_state"], "rwnd_limited")
        self.assertEqual(limits["delivery_rate_bps_median"], 65208000000.0)
        # ss yielding no matching sockets: limits carry a reason, nothing raises.
        with patch.object(tcp.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("192.0.2.1", 443))]):
            with tcp.TCPWindow("example.invalid", command=lambda args, timeout: "", interval=1000) as window:
                pass
        self.assertEqual(window.detail["limits"]["ticks"], 0)
        self.assertIn("no sample tick", window.detail["limits"]["reason"])


if __name__ == "__main__":
    unittest.main()
