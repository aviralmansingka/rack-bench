"""Offline parser/probe fixtures.

internet-mtr.txt: local capture, `mtr -4 -r -w -z -b -c 2 -m 3 192.0.2.1`.
internet-traceroute.txt: IPinfo ProbeNet Chicago capture published at
https://ipinfo.io/AS394384 (`traceroute -a -n -q1 -f3 38.71.89.220`).
Both saved 2026-10-08; tests never execute tools, DNS, or download fixtures.
Additional malformed, ASN, multipath and lost-hop rows below are synthetic.
"""
from itertools import count
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from rack_bench.bench.internet import Options
from rack_bench.bench.internet import path
from rack_bench.bench.internet.targets import targets

FIXTURES = Path(__file__).parent / "fixtures"
ENV = {"AWS_ACCESS_KEY_ID": "test", "AWS_SECRET_ACCESS_KEY": "test", "R2_ACCOUNT_ID": "test"}
MTR = (FIXTURES / "internet-mtr.txt").read_text()
TRACE = (FIXTURES / "internet-traceroute.txt").read_text()
DEST = "  4. AS16509 strange.aws-name.example (192.0.2.4) 0.0% 10 25.0 25.0 20.0 30.0 1.0\n"


class PathTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, ENV, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.options = Options()
        self.run = Mock(return_value=SimpleNamespace(stdout=MTR + DEST, stderr="", returncode=0))
        self.resolve = Mock(return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.0.2.4", 443))])

    def probe(self, metric, **kwargs):
        return path.path_probe("s3", metric, self.options, run=self.run,
                               which=lambda name: "/usr/bin/" + name, resolve=self.resolve, **kwargs)

    def test_mtr_capture_loss_and_no_invented_asn(self):
        hops = path.parse_mtr(MTR)
        self.assertEqual(len(hops), 3)
        self.assertEqual(hops[0]["avg_ms"], 74)
        self.assertEqual(hops[0]["asns"], [])
        self.assertEqual(hops[2]["loss_percent"], 100)
        self.assertIsNone(hops[2]["avg_ms"])

    def test_mtr_asns_weird_hostnames_and_bad_rows(self):
        hops = path.parse_mtr("  1.|-- AS64500 AS64501 weird--router_(alias) (192.0.2.1) 1.0% 100 2 3 1 5 1\n")
        self.assertEqual(hops[0]["asns"], ["AS64500", "AS64501"])
        self.assertEqual(hops[0]["host"], "weird--router_(alias) (192.0.2.1)")
        for report in ("permission denied", " 1. broken", DEST.replace("0.0%", "NaN"),
                       DEST.replace("0.0%", "101%"), DEST.replace("25.0", "inf")):
            self.assertEqual(path.parse_mtr(report), [])

    def test_traceroute_capture_asn_and_synthetic_multipath(self):
        hops = path.parse_traceroute(TRACE)
        self.assertEqual(hops[-1]["hop"], 7)
        self.assertEqual(hops[-1]["asns"], ["AS394384"])
        self.assertEqual(hops[-1]["avg_ms"], 7.067)
        self.assertIsNone(hops[-1]["loss_percent"])
        extra = path.parse_traceroute("8 * * *\n9 rtr_weird (192.0.2.9) [AS64500] 10 ms * 12 ms !H\n")
        self.assertIsNone(extra[0]["avg_ms"])
        self.assertEqual(extra[1]["avg_ms"], 11)
        self.assertEqual(extra[1]["timeouts"], 1)
        self.assertEqual(path.parse_traceroute("traceroute: socket: Operation not permitted"), [])

    def test_three_path_checks_share_one_idle_audit(self):
        self.assertEqual(self.probe("hops").value, 4)
        self.assertEqual(self.probe("as_path").value, "1:? -> 2:? -> 3:? -> 4:AS16509")
        check = self.probe("rtt_sanity")
        self.assertEqual(check.status, "pass")
        self.assertIsNone(check.expected)
        self.run.assert_called_once()
        self.assertIn("-4", self.run.call_args.args[0])
        self.resolve.assert_called_once_with("s3.ap-south-1.amazonaws.com", 443,
                                              socket.AF_INET, socket.SOCK_STREAM)
        self.assertIn("192.0.2.4", check.detail)

    def test_only_rtt_sanity_warns_and_destination_must_be_confirmed(self):
        self.run.return_value.stdout = MTR + DEST.replace("25.0", "300.0")
        self.assertEqual(self.probe("rtt_sanity").status, "warn")
        self.assertEqual(self.probe("hops").status, "pass")
        self.options = Options()
        self.run.return_value.stdout = MTR
        self.assertEqual(self.probe("rtt_sanity").status, "skip")
        self.assertEqual(self.probe("hops").value, 3)  # Lost hops still count.
        self.assertEqual(self.probe("as_path").status, "skip")

    def test_traceroute_fallback_and_missing_tools(self):
        self.run.return_value.stdout = TRACE
        check = path.path_probe("s3", "hops", Options(), run=self.run,
                                which=lambda name: None if name == "mtr" else "/bin/traceroute",
                                resolve=self.resolve)
        self.assertEqual(check.value, 7)
        self.assertIn("traceroute -4", check.source[0])
        check = path.path_probe("s3", "hops", Options(), which=lambda name: None)
        self.assertEqual(check.status, "skip")
        self.assertIn("missing tools: mtr and traceroute", check.detail)

    def test_tool_failure_timeout_and_malformed_output_skip(self):
        for result in (SimpleNamespace(stdout="", stderr="permission denied", returncode=1),
                       SimpleNamespace(stdout="broken", stderr="", returncode=0)):
            self.options = Options()
            self.run.return_value = result
            self.assertEqual(self.probe("hops").status, "skip")
        self.options = Options()
        self.run.side_effect = subprocess.TimeoutExpired("mtr", 120)
        self.assertEqual(self.probe("hops").status, "skip")

    def test_tiered_regions_and_r2_unpinnable_far_bands(self):
        s3 = targets("s3", Options(profile="certify"))
        self.assertEqual([t["region"] for t in s3], ["ap-south-1", "ap-southeast-1", "us-east-1"])
        self.assertEqual([t["runs"] for t in s3], [3, 1, 1])
        r2 = targets("r2", Options(profile="certify"))
        self.assertEqual(r2[0]["region"], "apac")
        self.assertTrue(all(t["reason"] for t in r2[1:]))
        override = targets("s3", Options(profile="certify", regions={"s3": "eu-west-1"}))
        self.assertEqual(len(override), 1)

    def test_context_missing_credentials_no_io(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("credentials not set", self.probe("hops").detail)
            resolver = Mock()
            self.assertIn("credentials not set", path.dns_probe("s3", self.options, resolver=resolver).detail)
            resolver.assert_not_called()
        self.run.assert_not_called()


class DNSTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict(os.environ, ENV, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.calls = []

    def resolver(self, host, kind):
        self.calls.append((host, kind))
        if host.endswith(".invalid"):
            return {"rcode": 3, "answers": [], "resolver": "192.0.2.53"}
        return {"rcode": 0, "answers": [{"address": "192.0.2.4", "family": "IPv4"}]}

    def probe(self, resolver=None, options=None):
        clock = count(step=0.001)
        return path.dns_probe("s3", options or Options(), resolver=resolver or self.resolver,
                              clock=lambda: next(clock))

    def test_first_repeated_queries_families_and_nxdomain(self):
        check = self.probe()
        self.assertEqual(check.status, "pass")
        self.assertAlmostEqual(check.value, 1)
        detail = json.loads(check.detail)
        run = detail["regions"][0]["runs_detail"][0]
        self.assertEqual(run["cached_ms"]["count"], 5)
        self.assertEqual(detail["families"], ["IPv4"])
        self.assertEqual([kind for _, kind in self.calls], ["A"] * 7 + ["AAAA"])
        self.assertIn("unknown", detail["cache_state"])

    def test_invalid_a_or_aaaa_interception_is_skip_not_warn(self):
        for bad_kind in ("A", "AAAA"):
            def hijack(host, kind):
                if host.endswith(".invalid") and kind == bad_kind:
                    return {"rcode": 0, "answers": [{"address": "::1" if kind == "AAAA" else "127.0.0.1"}]}
                return self.resolver(host, kind)
            check = self.probe(hijack)
            self.assertEqual(check.status, "skip")
            self.assertIsNone(check.value)
            self.assertTrue(json.loads(check.detail)["interception"])

    def test_servfail_nodata_timeout_are_not_nxdomain(self):
        for bad in ({"rcode": 2, "answers": []}, {"rcode": 0, "answers": []}):
            check = self.probe(lambda host, kind: bad if host.endswith(".invalid") else self.resolver(host, kind))
            self.assertEqual(check.status, "skip")
            self.assertFalse(json.loads(check.detail)["interception"])
        check = self.probe(Mock(side_effect=TimeoutError("resolver timeout")))
        self.assertEqual(check.status, "skip")
        self.assertIn("TimeoutError", check.detail)

    def test_regional_matrix_and_run_counts(self):
        check = self.probe(options=Options(profile="certify"))
        detail = json.loads(check.detail)
        self.assertEqual([len(t["runs_detail"]) for t in detail["regions"]], [3, 1, 1])

    def test_failed_endpoint_records_actual_empty_families(self):
        check = self.probe(lambda host, kind: {"rcode": 2, "answers": []})
        self.assertEqual(check.status, "skip")
        self.assertEqual(json.loads(check.detail)["families"], [])

    def test_dns_wire_parser_rcodes_compression_and_invalid_packets(self):
        question = b"\x04test\x07invalid\0" + struct.pack("!HH", 1, 1)
        header = struct.pack("!6H", 7, 0x8180, 1, 1, 0, 0)
        record = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 60, 4) + b"\xc0\x00\x02\x04"
        result = path._dns_answers(header + question + record, 7, question)
        self.assertEqual(result["answers"][0]["address"], "192.0.2.4")
        for rcode in (2, 3):
            packet = struct.pack("!6H", 7, 0x8180 | rcode, 1, 0, 0, 0) + question
            self.assertEqual(path._dns_answers(packet, 7, question)["rcode"], rcode)
        for packet in (b"", header + question + record[:-1], header + question.replace(b"test", b"evil") + record):
            with self.assertRaises(ValueError):
                path._dns_answers(packet, 7, question)
        with self.assertRaises(ValueError):
            path._dns_answers(header + question + record, 9, question)

    def test_configured_resolver_transport_is_ipv4_and_preserves_nxdomain(self):
        sock = Mock()
        question = b"\x04test\x07invalid\0" + struct.pack("!HH", 1, 1)
        sock.recv.return_value = struct.pack("!6H", 7, 0x8183, 1, 0, 0, 0) + question
        context = Mock(__enter__=Mock(return_value=sock), __exit__=Mock(return_value=False))
        with patch.object(path.Path, "read_text", return_value="nameserver ::1\nnameserver 192.0.2.53\n"), \
             patch.object(path, "randbelow", return_value=7), \
             patch.object(path.socket, "socket", return_value=context) as socket_factory:
            answer = path.resolve_dns("test.invalid")
        self.assertEqual(answer["rcode"], 3)
        socket_factory.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect.assert_called_once_with(("192.0.2.53", 53))

    def test_dns_truncation_uses_same_resolver_tcp_without_network(self):
        question = b"\x04test\x07invalid\0" + struct.pack("!HH", 1, 1)
        packet = struct.pack("!6H", 7, 0x8183, 1, 0, 0, 0) + question
        udp, tcp = Mock(), Mock()
        udp.recv.return_value = struct.pack("!6H", 7, 0x8380, 1, 0, 0, 0)
        tcp.recv.side_effect = [struct.pack("!H", len(packet)), packet[:5], packet[5:]]
        contexts = [Mock(__enter__=Mock(return_value=s), __exit__=Mock(return_value=False)) for s in (udp, tcp)]
        with patch.object(path.Path, "read_text", return_value="nameserver 192.0.2.53\n"), \
             patch.object(path, "randbelow", return_value=7), \
             patch.object(path.socket, "socket", side_effect=contexts) as factory:
            result = path.resolve_dns("test.invalid")
        self.assertEqual(result["rcode"], 3)
        self.assertEqual(factory.call_args_list[1].args, (socket.AF_INET, socket.SOCK_STREAM))
        tcp.connect.assert_called_once_with(("192.0.2.53", 53))
        self.assertEqual(tcp.sendall.call_args.args[0][2:], udp.send.call_args.args[0])

    def test_dns_missing_ipv4_resolver_and_malformed_reply_skip(self):
        with patch.object(path.Path, "read_text", return_value="nameserver ::1\n"), \
             patch.object(path.socket, "socket") as factory:
            with self.assertRaisesRegex(OSError, "no configured IPv4"):
                path.resolve_dns("test.invalid")
            factory.assert_not_called()
        sock = Mock()
        sock.recv.return_value = struct.pack("!6H", 7, 0x8180, 1, 1, 0, 0)
        context = Mock(__enter__=Mock(return_value=sock), __exit__=Mock(return_value=False))
        with patch.object(path.Path, "read_text", return_value="nameserver 192.0.2.53\n"), \
             patch.object(path, "randbelow", return_value=7), \
             patch.object(path.socket, "socket", return_value=context):
            with self.assertRaisesRegex(ValueError, "malformed DNS"):
                path.resolve_dns("test.invalid")
