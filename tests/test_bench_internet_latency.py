"""In-memory S3 objects and transport: no sockets, clocks or cloud credentials."""
from contextlib import redirect_stdout
import io
from itertools import count
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from rack_bench.bench import runner
from rack_bench.bench.internet import CHECKS, Options, before_run
from rack_bench.bench.internet import latency, s3client as s3

ENV = {"AWS_ACCESS_KEY_ID": "test", "AWS_SECRET_ACCESS_KEY": "test", "R2_ACCOUNT_ID": "test"}


class MemoryS3:
    def __init__(self):
        self.objects = {"user/important": b"untouched"}
        self.gets = 0
        self.puts = []
        self.deleted = []
        self.error = None
        self.cleanup_error = None
        self.timing_override = {}

    def put_object(self, key, payload):
        self.puts.append(key)
        self.objects[key] = b"".join(payload.iter_chunks())
        self.upload_headers = s3.checksum_headers(payload.iter_chunks())
        return s3.Response(200, {}, s3.Timing(bytes_sent=payload.size))

    def get_object(self, key, *, payload):
        self.gets += 1
        if self.error:
            raise self.error
        body = self.objects[key]
        payload.verify(body)
        fields = dict(connect_seconds=0.001, response_first_byte_seconds=0.002,
                      headers_seconds=0.003, first_byte_seconds=0.004, elapsed_seconds=0.005,
                      bytes_received=len(body))
        fields.update(self.timing_override)
        return s3.Response(200, {}, s3.Timing(**fields))

    def delete_object(self, key):
        self.deleted.append(key)
        if self.cleanup_error:
            raise self.cleanup_error
        self.objects.pop(key, None)


class LatencyTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, ENV, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.client = MemoryS3()
        self.factory = Mock(return_value=self.client)
        self.options = Options(buckets={"s3": "bench-bucket", "r2": "bench-r2"})

    def probe(self, provider="s3"):
        clock = count(step=0.0001)
        return latency.latency_probe(provider, self.options, client_factory=self.factory,
                                      cpu_clock=lambda: next(clock))

    def test_decomposition_baseline_percentiles_and_seeded_roundtrip(self):
        check = self.probe()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value, 2)
        self.assertIsNone(check.expected)
        detail = json.loads(check.detail)
        stats = detail["regions"][0]["runs_detail"][0]["stats"]
        for field, expected in (("connect_ms", 1), ("response_first_byte_ms", 2), ("headers_ms", 3),
                                ("body_first_byte_ms", 4), ("total_ms", 5)):
            self.assertEqual(stats[field]["p50"], expected)
            self.assertEqual(stats[field]["p95"], expected)
            self.assertEqual(stats[field]["p99"], expected)
        self.assertEqual(detail["baseline_ms"]["p95"], 2)
        self.assertEqual(self.client.gets, 20)
        self.assertNotIn("content-md5", self.client.upload_headers)  # one checksum at a time
        self.assertIn("x-amz-checksum-crc32", self.client.upload_headers)
        self.assertIn("https://bench-bucket.s3.ap-south-1.amazonaws.com/", check.source[0])

    def test_cleanup_is_owned_key_only_and_prefix_unique_per_run(self):
        first = json.loads(self.probe().detail)["prefix"]
        self.assertTrue(first.startswith("rack-bench/"))
        self.assertEqual(self.client.deleted, self.client.puts)
        self.assertEqual(self.client.objects, {"user/important": b"untouched"})
        self.options = Options(buckets={"s3": "bench-bucket"})
        second = json.loads(self.probe().detail)["prefix"]
        self.assertNotEqual(first, second)

    def test_keep_data_retains_only_created_object(self):
        self.options.keep_data = True
        check = self.probe()
        self.assertEqual(check.status, "pass")
        self.assertEqual(self.client.deleted, [])
        self.assertEqual(len(self.client.objects), 2)
        self.assertIn("retained (--keep-data)", check.detail)

    def test_missing_credentials_bucket_and_client_credential_error_skip(self):
        with patch.dict(os.environ, {}, clear=True):
            check = self.probe()
        self.assertIn("credentials not set", check.detail)
        self.factory.assert_not_called()
        self.options.buckets = {}
        self.assertIn("--buckets s3=<name>", self.probe().detail)
        self.factory.assert_not_called()
        self.options.buckets = {"s3": "bench-bucket"}
        self.factory.side_effect = s3.CredentialError("missing environment variable: AWS_SECRET_ACCESS_KEY")
        self.assertIn("credentials not set", self.probe().detail)

    def test_typed_failures_skip_and_cleanup_without_retry(self):
        for error in (s3.TransportError("timeout"), s3.ServiceError("service 503", status=503),
                      s3.ChecksumError("CRC32 mismatch"), s3.VerificationError("corrupt body")):
            self.client.error = error
            prior_gets = self.client.gets
            check = self.probe()
            self.assertEqual(check.status, "skip")
            self.assertIsNone(check.value)
            self.assertIn(type(error).__name__, check.detail)
            self.assertEqual(self.client.gets, prior_gets + 1)
            self.assertEqual(self.client.objects, {"user/important": b"untouched"})

    def test_invalid_timing_retry_or_truncated_body_never_zero_pass(self):
        for invalid in ({"first_byte_seconds": None}, {"response_first_byte_seconds": float("nan")},
                        {"elapsed_seconds": 0}, {"bytes_received": 99}, {"attempts": 2}):
            self.client.timing_override = invalid
            check = self.probe()
            self.assertEqual(check.status, "skip")
            self.assertIsNone(check.value)
            self.assertIn("ProtocolError", check.detail)

    def test_failed_setup_still_deletes_owned_key(self):
        self.client.put_object = Mock(side_effect=s3.TransportError("PUT response lost"))
        check = self.probe()
        self.assertEqual(check.status, "skip")
        self.assertEqual(self.client.gets, 0)
        self.assertEqual(len(self.client.deleted), 1)
        self.assertTrue(self.client.deleted[0].startswith("rack-bench/"))

    def test_cleanup_failure_is_visible_without_masking_primary_error(self):
        self.client.cleanup_error = s3.ServiceError("delete denied", status=403)
        self.client.error = s3.VerificationError("corrupt body")
        check = self.probe()
        self.assertEqual(check.status, "skip")
        self.assertIn("VerificationError", check.detail)
        self.assertIn("delete denied", check.detail)

    def test_certify_far_bands_bounded_and_nearest_three_runs(self):
        self.options.profile = "certify"
        check = self.probe()
        regions = json.loads(check.detail)["regions"]
        self.assertEqual([len(r["runs_detail"]) for r in regions], [3, 1, 1])
        self.assertEqual([r["bytes_downloaded"] for r in regions], [60 * 102400, 20 * 102400, 20 * 102400])
        self.assertEqual(self.client.gets, 100)
        self.assertEqual(len(self.client.deleted), 3)

    def test_r2_far_bands_skip_without_io(self):
        self.options.profile = "certify"
        check = self.probe("r2")
        self.assertEqual(check.status, "pass")
        self.assertEqual(self.client.gets, 60)
        self.assertEqual(len(self.client.puts), 1)
        regions = json.loads(check.detail)["regions"]
        self.assertEqual([r["status"] for r in regions], ["pass", "skip", "skip"])
        self.assertIn("https://test.r2.cloudflarestorage.com/bench-r2/", check.source[0])

    def test_gcs_and_warp_are_explicitly_unsupported(self):
        self.assertEqual(self.probe("gcs").status, "skip")
        self.options.tool = "warp"
        self.assertIn("Warp execution not implemented", self.probe().detail)
        self.factory.assert_not_called()

    def test_part_two_dependencies_do_not_launch_hidden_uploads(self):
        for suffix, needed in (("download.throughput", "upload objects"),
                               ("latency.loaded", "baseline_ms.p95"),
                               ("tcp.retransmit_ratio", "transfer windows")):
            name = f"internet.s3.{suffix}"
            check = CHECKS[name](self.options)
            self.assertEqual((check.name, check.status), (name, "skip"))
            self.assertIn(needed, check.detail)

    def test_new_collection_clears_cached_path_and_prefix(self):
        self.options._internet_prefix = "rack-bench/old/"
        self.options._path_reports = {"s3": "old observation"}
        before_run(self.options)
        self.assertNotIn("_internet_prefix", vars(self.options))
        self.assertNotIn("_path_reports", vars(self.options))

    def test_measured_result_json_artifacts_and_name_filters(self):
        name = "internet.s3.latency.ttfb"
        probe = lambda options: latency.latency_probe("s3", options, client_factory=self.factory)
        excluded = Mock(side_effect=AssertionError("excluded probe ran"))
        with patch.dict(CHECKS, {name: probe, "internet.s3.latency.loaded": excluded}, clear=True), \
             tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()) as output:
            code = runner.run("internet", options=self.options, only=["internet.s3.latency.*"],
                              skip=["*.loaded"], json_target="-", run_dir=directory)
            document = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(document["schema_version"], 1)
            checks = document["results"][0]["checks"]
            self.assertEqual([c["name"] for c in checks], [name])
            self.assertEqual(checks[0]["status"], "pass")
            self.assertEqual(checks[0]["value"], 2)
            self.assertEqual((Path(directory) / "bench.values.json").read_text(), output.getvalue())
            self.assertIn("PASS=1", (Path(directory) / "bench.out").read_text())
            self.assertEqual(json.loads(checks[0]["detail"])["baseline_ms"]["p95"], 2)
        excluded.assert_not_called()

    def test_real_http_timing_surface_with_memory_socket(self):
        """Exercise HTTPResponse status-byte peek, not a fabricated response object."""
        body = b"x"
        sock = Mock()
        sock.makefile.return_value = io.BufferedReader(io.BytesIO(
            b"HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\n" + body))
        def connect(conn):
            conn.sock = sock
        clock = count(step=0.001)
        client = s3.S3Client("bench-bucket", "us-east-1", endpoint=s3.Endpoint("example.invalid", "us-east-1", True, tls=False))
        with patch.object(s3.http.client.HTTPConnection, "connect", connect), \
             patch.object(s3.time, "perf_counter", side_effect=lambda: next(clock)):
            result = client.get_object("test")
        timing = result.timing
        self.assertAlmostEqual(timing.connect_seconds, 0.001)
        self.assertLess(timing.connect_seconds, timing.response_first_byte_seconds)
        self.assertLess(timing.response_first_byte_seconds, timing.headers_seconds)
        self.assertLess(timing.headers_seconds, timing.first_byte_seconds)
        self.assertLess(timing.first_byte_seconds, timing.elapsed_seconds)
        self.assertEqual(timing.bytes_received, 1)
        self.assertEqual(timing.attempts, 1)
