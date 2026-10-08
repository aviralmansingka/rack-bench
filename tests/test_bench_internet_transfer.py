"""Fake transport, clocks and commands only: no sockets, sleeps or cloud data.

Fixture provenance (captured on the development host, 2026-10-08):
- internet-ss.txt: two loopback socket records from `ss -4tinH` (verbatim).
- internet-ping-{pass,mtu}.txt: `ping -4 -n -M do -c 1 -W 1 -s SIZE
  127.0.0.1`, SIZE=1472/65508, stdout + stderr (verbatim).
Timeout, PID ownership and counter-delta mutations below are synthetic, not
represented as captures. No capture command executes during these tests.
"""
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from rack_bench.bench import internet, runner
from rack_bench.bench.internet import download, tcp, transfer, upload
from rack_bench.bench.internet.cli import Options, before_run
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
    def __init__(self, host):
        self.host = host
        self.detail = {"segments": 1000, "retransmits": 2, "ratio_pct": .2,
                       "observations": [{"window_bytes": 1024 * 1024, "rtt_ms": 10}],
                       "sources": ["ss -4tinpH ( dst 192.0.2.1 )"], "errors": []}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class FakeClient:
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

    def get_object(self, key, payload, byte_range=None, consume=None):
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
        env = patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "fake", "AWS_SECRET_ACCESS_KEY": "fake", "R2_ACCOUNT_ID": "fake"}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.options = Options(providers=("s3",), buckets={"s3": "bench-test"}, duration=1)
        self.client = FakeClient()
        self.clock = Clock()

    def window(self, **kwargs):
        with patch.object(transfer, "PART_SIZE", 8):
            return transfer.transfer_window(self.client, direction="up", prefix="rack-bench/test/", concurrency=2,
                                          duration=.1, objects=[], owned=[], size=16, one_object=True,
                                          clock=self.clock, tcp_factory=FakeTCP, **kwargs)

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
            return transfer.transfer_window(client, direction="up", prefix="rack-bench/test/", concurrency=1,
                                          duration=.1, objects=[], owned=[], size=16 * transfer.MIB,
                                          clock=Clock(), tcp_factory=FakeTCP)[0]
        self.assertEqual(run()["status"], "pass")
        client.abort_multipart.assert_called_once_with("rack-bench/test/0-0.bin", "owned-upload-id")
        client.complete_multipart.assert_not_called()
        client.abort_multipart.side_effect = TransportError("abort denied")
        failed = run()
        self.assertEqual(failed["status"], "skip")
        self.assertIn("abort denied", failed["errors"][0]["reason"])

    def test_buckets_idle_seconds_boundary_and_partial_tail(self):
        buckets = transfer.throughput_buckets([(0.1, transfer.MIB), (2., transfer.MIB)], 2.5)
        self.assertEqual([b["mib_per_sec"] for b in buckets], [1, 0, 2])
        self.assertEqual([b["start_seconds"] for b in buckets], [0, 1, 2])

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
        key = kwargs["prefix"] + "object.bin"
        if kwargs["direction"] == "up":
            kwargs["owned"].append(key)
        run = {"status": "pass", "concurrency": kwargs["concurrency"], "bytes": size,
               "mib_per_sec": 100 if kwargs["direction"] == "up" else 50, "objs_per_sec": 2,
               "elapsed_seconds": 1, "progress_bytes_lower_bound": size, "samples": [],
               "bucket_stats": {"p50": 100, "p95": 100}, "p95_p50_ratio": 1,
               "tcp": FakeTCP("").detail, "loaded_samples": [{"response_first_byte_ms": 45}],
               "loaded_errors": [], "loaded_bytes": upload.LATENCY_SIZE}
        return run, [{"key": key, "payload": {"seed": key, "size": size, "chunk_size": 65536}}]

    def reports(self):
        self.calls = []
        return upload.upload_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)

    def baseline(self, p95=20):
        self.options._internet_checks = {"internet.s3.latency.ttfb": Check("internet.s3.latency.ttfb", "pass", 10,
                                                                       detail=json.dumps({"baseline_ms": {"p95": p95}}))}

    def test_quick_plan_and_cache_prevent_duplicate_transfers(self):
        records = self.reports()
        self.assertEqual([(c["concurrency"], c["duration"]) for c in self.calls], [(32, 1), (1, 1)])
        self.assertIs(upload.upload_reports("s3", self.options), records)
        self.assertEqual(len(self.calls), 2)

    def test_certify_sweep_three_runs_and_far_band_hard_budget(self):
        self.options = Options(profile="certify", providers=("s3",), buckets={"s3": "bench-test"})
        records = self.reports()
        self.assertEqual([len(r["runs_detail"]) for r in records], [15, 1, 1])
        self.assertEqual([c["concurrency"] for c in self.calls[:12]], [1]*3 + [8]*3 + [32]*3 + [64]*3)
        self.assertTrue(all(c["duration"] == 300 for c in self.calls))
        self.assertTrue(all(c["one_object"] and c["size"] == 32 * transfer.MIB and c["loaded"] is None for c in self.calls[-2:]))
        download.download_reports("s3", self.options, client_factory=lambda *a, **k: self.client, window=self.fake_window)
        self.assertEqual(len(self.calls), 34)
        self.assertTrue(all(c["direction"] == "up" for c in self.calls[:17]))
        self.assertTrue(all(c["direction"] == "down" for c in self.calls[17:]))
        self.assertTrue(all(c["one_object"] for c in self.calls[-2:]))

    def test_certify_explicit_concurrency_override_and_region_override(self):
        self.options = Options(profile="certify", concurrent=8, regions={"s3": "us-east-1"}, buckets={"s3": "bench-test"})
        records = self.reports()
        self.assertEqual(len(records), 1)
        self.assertEqual([c["concurrency"] for c in self.calls], [8, 8, 8, 1, 1, 1])

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
        records[0]["owned"].append("someone-elses/key")
        transfer.cleanup(self.options)
        self.assertEqual(self.client.deleted, owned)
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
        before_run(self.options)
        for key in ("_internet_prefix", "_transfer_reports", "_transfer_owners", "_internet_checks"):
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
            self.assertEqual(summary["value"]["bytes"]["uploaded"], 2 * transfer.OBJECT_SIZE)
            self.assertEqual(json.loads(summary["detail"])["cleanup"][0]["status"], "deleted exact owned keys")
            self.assertEqual(Path(tmp, "bench.values.json").read_text(), out.getvalue())
            self.assertIn("upload=100.00 MiB/s", Path(tmp, "bench.out").read_text())


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


if __name__ == "__main__":
    unittest.main()
