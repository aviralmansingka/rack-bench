"""Connectivity observations from fixtures only: no network access in tests."""
from contextlib import redirect_stdout
from copy import deepcopy
from http.client import IncompleteRead
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import signal
import socket
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit

from rack_bench.audit import connectivity, runner
from rack_bench.cli import main
from rack_bench.common.host import Unavailable


FIXTURE = json.loads((Path(__file__).parent / "fixtures/connectivity.json").read_text())


class ConnectivityTests(unittest.TestCase):
    def command(self, args, **kwargs):
        return json.dumps(FIXTURE["commands"][" ".join(args)])

    def response(self, url, **kwargs):
        self.assertEqual(kwargs, {"timeout": connectivity.TIMEOUT})
        if url == "https://api.ipify.org":
            return BytesIO(b"193.0.0.1\n")
        if url == "https://api6.ipify.org":
            return BytesIO(b"2001:67c:2e8::1\n")
        parsed = urlsplit(url)
        query = parse_qs(parsed.query)
        if "/network-info/" in parsed.path:
            key = "network6" if ":" in query["resource"][0] else "network4"
        elif "/rpki-validation/" in parsed.path:
            self.assertEqual(query["resource"], ["3333"])
            self.assertIn("prefix", query)
            key = "roa"
        elif "/routing-status/" in parsed.path:
            self.assertEqual(query["min_peers_seeing"], ["1"])
            key = "ris"
        else:
            raise AssertionError(f"Unexpected endpoint: {url}")
        return BytesIO(json.dumps(FIXTURE[key]).encode())

    def test_registration_and_cli(self):
        self.assertIs(runner.SCOPES["connectivity"], connectivity)
        self.assertEqual(list(connectivity.CHECKS), ["connectivity." + name for name in
                         ("routes", "resolver", "ipv6", "proxies", "egress_ip", "asn", "roa", "ris")])
        self.assertFalse(any("system.clock" in module.CHECKS for module in runner.SCOPES.values()))
        with tempfile.TemporaryDirectory() as tmp, patch.object(connectivity, "run_command", side_effect=self.command), \
             patch.object(connectivity, "urlopen") as request, redirect_stdout(StringIO()) as out:
            code = main(["audit", "connectivity", "--only", "*.routes", "--json", "--run-dir", tmp])
        self.assertEqual(code, 0)
        checks = json.loads(out.getvalue())["results"][0]["checks"]
        self.assertEqual([row["name"] for row in checks], ["connectivity.routes"])
        request.assert_not_called()

    def test_routes_defaults_source_selection_vlan_and_vrf(self):
        with patch.object(connectivity, "run_command", side_effect=self.command):
            check = connectivity.routes()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["ipv4"]["default_routes"][0]["gateway"], "192.0.2.1")
        self.assertEqual(check.value["ipv6"]["default_routes"][0]["gateway"], "fe80::1")
        self.assertEqual(check.value["ipv4"]["source_selection"][0]["prefsrc"], "192.0.2.10")
        self.assertEqual(check.value["ipv6"]["source_selection"][0]["src"], "2001:db8::10")
        self.assertEqual([row["ifname"] for row in check.value["vlan_vrf_interfaces"]], ["eth0.100", "vrf-service"])
        self.assertEqual(check.value["policy_rules"], FIXTURE["commands"]["ip -j rule"])
        self.assertEqual(check.value["policy_rules"][1], {"priority": 100, "src": "192.0.2.0/24", "table": 100})
        self.assertIn("ip -j rule", check.source)
        self.assertEqual(len(check.source), 6)
        self.assertIn("no probes", check.detail)

    def test_routes_policy_rules_degrade_independently(self):
        for error in (Unavailable("ip -j rule", "Rules unavailable"), ValueError("Malformed rules")):
            def command(args, **kwargs):
                if args == ["ip", "-j", "rule"]:
                    raise error
                return self.command(args, **kwargs)
            with self.subTest(error=error), patch.object(connectivity, "run_command", side_effect=command):
                check = connectivity.routes()
            self.assertEqual(check.status, "pass")
            self.assertIsNone(check.value["policy_rules"])
            self.assertEqual(check.value["unavailable"], {"policy_rules": str(error)})
            self.assertEqual(check.value["ipv4"]["default_routes"][0]["gateway"], "192.0.2.1")
            self.assertIn("ip -j rule", check.source)

    def test_routes_policy_rules_alone_prevent_all_failed_skip(self):
        with patch.object(connectivity, "run_command", side_effect=[Unavailable("ip", "Unavailable")] * 5 +
                          [json.dumps(FIXTURE["commands"]["ip -j rule"])]):
            check = connectivity.routes()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["policy_rules"], FIXTURE["commands"]["ip -j rule"])
        self.assertEqual(len(check.value["unavailable"]), 5)

    def test_routes_empty_missing_and_malformed(self):
        with patch.object(connectivity, "run_command", return_value="[]"):
            check = connectivity.routes()
            self.assertEqual(check.status, "pass")
            self.assertEqual(check.value["ipv6"]["default_routes"], [])
        for error in (Unavailable("ip", "Command not found: ip."), "bad json", "{}"):
            with self.subTest(error=error), patch.object(connectivity, "run_command", side_effect=[error] * 6) as command:
                check = connectivity.routes()
                self.assertEqual(check.status, "skip")
                self.assertEqual(command.call_count, 6)
                self.assertIn("ip -j rule", check.source)

    def test_resolver_from_files_and_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resolv.conf"
            path.write_text(FIXTURE["resolv_conf"])
            with patch.object(connectivity, "read_text", side_effect=lambda _: path.read_text()), \
                 patch.object(connectivity.shutil, "which", return_value="/usr/bin/resolvectl"), \
                 patch.object(connectivity, "run_command", return_value=FIXTURE["resolved_status"]):
                check = connectivity.resolver()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["resolv_conf"]["nameserver"], ["192.0.2.53", "2001:db8::53"])
        self.assertEqual(check.value["resolv_conf"]["search"], ["customer.example"])
        self.assertIn("DNSSEC=yes/supported", check.value["dnssec"][0])
        self.assertIn("resolvectl status --no-pager", check.source)

    def test_resolver_missing_resolved_is_unknown_not_false(self):
        with patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "read_text", return_value=FIXTURE["resolv_conf"]):
            check = connectivity.resolver()
            self.assertEqual(check.status, "pass")
            self.assertIsNone(check.value["dnssec"])
        with patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "read_text", side_effect=Unavailable("/etc/resolv.conf", "unreadable")):
            self.assertEqual(connectivity.resolver().status, "skip")

    def test_ipv6_global_addresses_route_and_aaaa_capability(self):
        for text, expected in ((FIXTURE["resolv_conf"], True), ("options no-aaaa\n", False),
                               ("options edns0 # no-aaaa is not enabled\n", True)):
            with self.subTest(aaaa=expected), patch.object(connectivity, "run_command", side_effect=self.command), \
                 patch.object(connectivity, "read_text", return_value=text):
                check = connectivity.ipv6()
            self.assertEqual(check.status, "pass")
            self.assertEqual(len(check.value["global_addresses"]), 1)
            self.assertEqual(check.value["global_addresses"][0]["local"], "2001:db8::10")
            self.assertEqual(check.value["default_routes"][0]["gateway"], "fe80::1")
            self.assertEqual(check.value["aaaa_queries_enabled"], expected)
        with patch.object(connectivity, "run_command", return_value="[]"), \
             patch.object(connectivity, "read_text", side_effect=Unavailable("resolv.conf", "missing")):
            check = connectivity.ipv6()
            self.assertIsNone(check.value["aaaa_queries_enabled"])
            self.assertEqual(check.value["global_addresses"], [])

    def test_proxy_facts_from_fixture_files_redact_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in (("etc/environment", FIXTURE["environment"]),
                               ("home/test/.docker/config.json", json.dumps(FIXTURE["docker_config"])),
                               ("etc/docker/daemon.json", json.dumps(FIXTURE["daemon_config"]))):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            def read(path):
                return (root / str(path).lstrip("/")).read_text()
            with patch.dict(os.environ, {"HOME": "/home/test", "http_proxy": "http://alice:process-secret@proxy.example:80"}, clear=True), \
                 patch.object(connectivity, "read_text", side_effect=read), \
                 patch.object(connectivity.shutil, "which", return_value="/usr/bin/git"), \
                 patch.object(connectivity, "run_command", return_value=FIXTURE["git_proxy"]):
                check = connectivity.proxies()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["etc_environment"]["no_proxy"], "localhost,.customer.example")
        self.assertIn("[redacted]@proxy.example", check.value["environment"]["http_proxy"])
        self.assertIn("git-proxy.example", check.value["git"]["http.proxy"])
        self.assertIn("/home/test/.docker/config.json", check.source)
        rendered = json.dumps(check.value)
        self.assertNotIn("secret", rendered)
        self.assertNotIn("UNRELATED", rendered)
        self.assertIn("customer service path", check.detail)

    def test_optional_proxy_files_absent_or_invalid(self):
        for response in (Unavailable("file", "missing"), "not json"):
            with patch.dict(os.environ, {}, clear=True), patch.object(connectivity.shutil, "which", return_value=None), \
                 patch.object(connectivity, "read_text", side_effect=[response, response, response]):
                check = connectivity.proxies()
            self.assertEqual(check.status, "pass")
            self.assertEqual(check.value["environment"], {})
            self.assertTrue(check.value["unavailable"])

    def test_external_parsing_and_per_run_cache(self):
        with patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "urlopen", side_effect=self.response) as request:
            result, = runner.collect("connectivity", only=["*.egress_ip", "*.asn", "*.roa", "*.ris"])
            self.assertEqual(request.call_count, 8)
            egress, asn, roa, ris = result.checks
            self.assertTrue(all(check.status == "pass" for check in result.checks))
            self.assertEqual(egress.value["ipv4"], "193.0.0.1")
            self.assertEqual(egress.value["ipv6"], "2001:67c:2e8::1")
            self.assertEqual(asn.value["ipv4"]["prefix"], "193.0.0.0/21")
            self.assertEqual(asn.value["ipv4"]["asns"], ["3333"])
            self.assertTrue(roa.value["ipv4"]["origins"]["3333"]["covering_roa_exists"])
            self.assertTrue(ris.value["ipv4"]["origins"]["3333"]["visible"])
            self.assertTrue(any("/rpki-validation/data.json?" in url for url in roa.source))
            self.assertTrue(any("/routing-status/data.json?" in url for url in ris.source))
            runner.collect("connectivity", only=["*.egress_ip", "*.asn", "*.roa", "*.ris"])
            self.assertEqual(request.call_count, 16)
        self.assertIsNone(connectivity._QUERY_CACHE.get())

    def test_direct_dns_preferred_and_bounded(self):
        with patch.object(connectivity.shutil, "which", return_value="/usr/bin/dig"), \
             patch.object(connectivity, "run_command", side_effect=["193.0.0.1", "2001:67c:2e8::1"]) as command, \
             patch.object(connectivity, "urlopen") as request:
            check = connectivity.egress_ip()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["ipv4"], "193.0.0.1")
        self.assertIn("@208.67.222.222", command.call_args_list[0].args[0])
        self.assertIn("@2620:119:35::35", command.call_args_list[1].args[0])
        self.assertTrue(all(call.kwargs["timeout"] == 5 for call in command.call_args_list))
        self.assertTrue(all(url.startswith("dns://") for url in check.source))
        request.assert_not_called()

    def test_dns_failure_or_bad_answer_falls_back_to_https(self):
        for response in (Unavailable("dig", "timeout"), "127.0.0.1", "not an address"):
            with self.subTest(response=response), patch.object(connectivity.shutil, "which", return_value="dig"), \
                 patch.object(connectivity, "run_command", side_effect=[response, response]), \
                 patch.object(connectivity, "urlopen", side_effect=self.response):
                check = connectivity.egress_ip()
            self.assertEqual(check.status, "pass")
            self.assertEqual(check.value["ipv4"], "193.0.0.1")
            self.assertEqual(len(check.source), 4)

    def test_all_external_checks_skip_offline_and_timeout(self):
        for error in (TimeoutError("timed out"), URLError("offline"), socket.gaierror("DNS unavailable"), IncompleteRead(b"")):
            for name in ("egress_ip", "asn", "roa", "ris"):
                with self.subTest(error=error, name=name), patch.object(connectivity.shutil, "which", return_value=None), \
                     patch.object(connectivity, "urlopen", side_effect=error):
                    check = getattr(connectivity, name)()
                self.assertEqual(check.status, "skip")
                self.assertTrue(check.detail)
                self.assertIn("https://api.ipify.org", check.source)

    def test_offline_failures_are_shared_within_run(self):
        with patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "urlopen", side_effect=URLError("offline")) as request:
            result, = runner.collect("connectivity", only=["*.egress_ip", "*.asn", "*.roa", "*.ris"])
        self.assertEqual(request.call_count, 2)
        self.assertTrue(all(check.status == "skip" for check in result.checks))

    def test_partial_family_failure_skips_but_preserves_success(self):
        def response(url, **kwargs):
            if url == "https://api6.ipify.org":
                raise URLError("no IPv6 route")
            return self.response(url, **kwargs)
        with patch.object(connectivity.shutil, "which", return_value=None), patch.object(connectivity, "urlopen", side_effect=response):
            check = connectivity.egress_ip()
        self.assertEqual(check.status, "skip")
        self.assertEqual(check.value["ipv4"], "193.0.0.1")
        self.assertIn("no IPv6 route", check.detail)
        self.assertIn("ipv6", check.value["unavailable"])

    def test_socket_resolution_has_a_hard_deadline(self):
        # urllib's timeout alone does not bound getaddrinfo; simulate a stuck DNS
        # resolver without ever opening a socket or sending a packet.
        previous = signal.getsignal(signal.SIGALRM)
        with patch.dict(os.environ, {}, clear=True), patch.object(connectivity, "TIMEOUT", 0.02), \
             patch.object(connectivity.shutil, "which", return_value=None), \
             patch("socket.getaddrinfo", side_effect=lambda *args, **kwargs: time.sleep(1)):
            start = time.monotonic()
            check = connectivity.egress_ip()
            elapsed = time.monotonic() - start
        self.assertEqual(check.status, "skip")
        self.assertIn("timed out", check.detail)
        self.assertLess(elapsed, 0.8)
        self.assertEqual(signal.getsignal(signal.SIGALRM), previous)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))

    def test_slow_http_body_has_a_hard_deadline(self):
        class SlowBody(BytesIO):
            def read(self, size=-1):
                time.sleep(1)
                return super().read(size)
        with patch.object(connectivity, "TIMEOUT", 0.02), patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "urlopen", side_effect=lambda *args, **kwargs: SlowBody(b"193.0.0.1")):
            start = time.monotonic()
            check = connectivity.egress_ip()
            elapsed = time.monotonic() - start
        self.assertEqual(check.status, "skip")
        self.assertIn("timed out", check.detail)
        self.assertLess(elapsed, 0.8)

    def test_wrong_family_private_ip_and_bad_ripe_payloads_skip(self):
        for body in (b"127.0.0.1", b"192.0.2.1", b"garbage", b"{broken json"):
            with self.subTest(body=body), patch.object(connectivity.shutil, "which", return_value=None), \
                 patch.object(connectivity, "urlopen", side_effect=lambda *a, **k: BytesIO(body)):
                self.assertEqual(connectivity.egress_ip().status, "skip")
        for body in ({"status": "error", "data": {}}, {"status": "ok", "data": {"prefix": None, "asns": []}}, {"status": "ok", "data": {}}):
            def response(url, **kwargs):
                return BytesIO(json.dumps(body).encode()) if "stat.ripe.net" in url else self.response(url, **kwargs)
            with self.subTest(body=body), patch.object(connectivity.shutil, "which", return_value=None), \
                 patch.object(connectivity, "urlopen", side_effect=response):
                self.assertEqual(connectivity.asn().status, "skip")

    def test_roa_coverage_is_not_origin_validity(self):
        for status, exists in (("valid", True), ("invalid_asn", True), ("invalid_length", True), ("unknown", False)):
            fixture = deepcopy(FIXTURE["roa"])
            fixture["data"]["status"] = status
            with self.subTest(status=status), patch.dict(FIXTURE, {"roa": fixture}), \
                 patch.object(connectivity.shutil, "which", return_value=None), patch.object(connectivity, "urlopen", side_effect=self.response):
                check = connectivity.roa()
            self.assertEqual(check.status, "pass")
            self.assertEqual(check.value["ipv4"]["origins"]["3333"]["covering_roa_exists"], exists)

    def test_each_ripe_endpoint_failure_skips_instead_of_negative_fact(self):
        for probe, endpoint in ((connectivity.asn, "network-info"), (connectivity.roa, "rpki-validation"),
                                (connectivity.ris, "routing-status")):
            for error in (TimeoutError("timed out"), URLError("offline")):
                def response(url, **kwargs):
                    if "/" + endpoint + "/" in url:
                        raise error
                    return self.response(url, **kwargs)
                with self.subTest(endpoint=endpoint, error=error), patch.object(connectivity.shutil, "which", return_value=None), \
                     patch.object(connectivity, "urlopen", side_effect=response):
                    check = probe()
                self.assertEqual(check.status, "skip")
                self.assertIsNone(check.value)
                self.assertTrue(any("/" + endpoint + "/data.json?" in source for source in check.source))

    def test_multiple_origins_are_all_checked(self):
        fixture = deepcopy(FIXTURE["network4"])
        fixture["data"]["asns"] = ["3333", "64496"]
        def response(url, **kwargs):
            if "/rpki-validation/" in url and "resource=64496" in url:
                return BytesIO(json.dumps({"status": "ok", "data": {"status": "invalid_asn"}}).encode())
            return self.response(url, **kwargs)
        with patch.dict(FIXTURE, {"network4": fixture}), patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "urlopen", side_effect=response) as request:
            check = connectivity.roa()
        self.assertEqual(check.status, "pass")
        self.assertEqual(list(check.value["ipv4"]["origins"]), ["3333", "64496"])
        self.assertEqual(check.value["ipv4"]["origins"]["64496"]["status"], "invalid_asn")
        self.assertEqual(request.call_count, 7)

    def test_filtered_ris_observes_exact_origin_not_related_prefixes(self):
        fixture = deepcopy(FIXTURE["ris"])
        fixture["data"]["origins"] = [{"origin": 64496, "route_objects": []}]
        fixture["data"]["less_specifics"] = [{"prefix": "193.0.0.0/16", "origin": 3333}]
        with patch.dict(FIXTURE, {"ris": fixture}), patch.object(connectivity.shutil, "which", return_value=None), \
             patch.object(connectivity, "urlopen", side_effect=self.response) as request:
            result, = runner.collect("connectivity", only=["*.ris"])
        self.assertEqual(request.call_count, 6)
        self.assertEqual(result.checks[0].status, "pass")
        self.assertFalse(result.checks[0].value["ipv4"]["origins"]["3333"]["visible"])


if __name__ == "__main__":
    unittest.main()
