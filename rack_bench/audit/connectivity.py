"""Read-only service-path facts; only the last four checks make external queries."""
from contextlib import contextmanager
from contextvars import ContextVar
from http.client import HTTPException
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import threading
import time
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import urlopen

from rack_bench.common.host import Unavailable, _echo, collect_check, read_text, run_command


TIMEOUT = 5
_QUERY_CACHE = ContextVar("connectivity_queries", default=None)
FAMILIES = {"ipv4": ("-4", "1.1.1.1"), "ipv6": ("-6", "2606:4700:4700::1111")}


@contextmanager
def query_session():
    """Share successes and failures within one collection, never across runs."""
    token = _QUERY_CACHE.set({}) if _QUERY_CACHE.get() is None else None
    try:
        yield
    finally:
        if token is not None:
            _QUERY_CACHE.reset(token)


def _command_json(command, sources):
    sources.append(shlex.join(command))
    value = json.loads(run_command(command))
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("Expected ip JSON records")
    return value


def routes():
    sources = []
    def collect():
        values, errors = {}, {}
        for family, (flag, target) in FAMILIES.items():
            record = {}
            for field, args in (("default_routes", ["show", "table", "all"]),
                                ("source_selection", ["get", target])):
                try:
                    rows = _command_json(["ip", "-j", flag, "route", *args], sources)
                    record[field] = [row for row in rows if row.get("dst") == "default"] if field == "default_routes" else rows
                except (Unavailable, ValueError) as exc:
                    record[field] = None
                    errors[f"{family}.{field}"] = str(exc)
            values[family] = record
        try:
            links = _command_json(["ip", "-j", "-d", "link"], sources)
            values["vlan_vrf_interfaces"] = [row for row in links if row.get("linkinfo", {}).get("info_kind") in ("vlan", "vrf")]
        except (Unavailable, ValueError) as exc:
            values["vlan_vrf_interfaces"] = None
            errors["interfaces"] = str(exc)
        if len(errors) == 5:
            raise Unavailable("ip", "; ".join(errors.values()))
        return {**values, "unavailable": errors}
    check = collect_check("connectivity.routes", collect, sources)
    if check.status == "pass":
        check.detail = "Passive kernel route lookup only; ip route get sends no probes. Missing fields are unknown, not absent routes."
    return check


def resolver():
    sources = ["/etc/resolv.conf"]
    def collect():
        values, errors = {}, {}
        try:
            text = read_text(sources[0])
            config = {}
            for line in text.splitlines():
                parts = re.split(r"[#;]", line, maxsplit=1)[0].split()
                if len(parts) > 1:
                    config.setdefault(parts[0], []).extend(parts[1:])
            values["resolv_conf"] = config
        except Unavailable as exc:
            errors["resolv_conf"] = str(exc)
        values["resolved_status"], values["dnssec"] = None, None
        if shutil.which("resolvectl"):
            sources.append("resolvectl status --no-pager")
            try:
                text = run_command(["resolvectl", "status", "--no-pager"])
                values["resolved_status"] = text
                values["dnssec"] = [line.strip() for line in text.splitlines() if "DNSSEC" in line] or None
            except Unavailable as exc:
                errors["resolved_status"] = str(exc)
        else:
            errors["resolved_status"] = "resolvectl not installed."
        if "resolv_conf" not in values and values["resolved_status"] is None:
            raise Unavailable(sources[0], "; ".join(errors.values()))
        return {**values, "unavailable": errors}
    check = collect_check("connectivity.resolver", collect, sources)
    if check.status == "pass":
        check.detail = "Resolver/DNSSEC configuration as reported locally; no validation query sent. Null DNSSEC means unknown."
    return check


def ipv6():
    sources = []
    def collect():
        addresses = _command_json(["ip", "-j", "-6", "addr"], sources)
        addresses = [{"interface": row["ifname"], **addr} for row in addresses for addr in row.get("addr_info", [])
                     if addr.get("family") == "inet6" and addr.get("scope") == "global"]
        routes = _command_json(["ip", "-j", "-6", "route", "show", "default"], sources)
        try:
            sources.append("/etc/resolv.conf")
            lines = [re.split(r"[#;]", line, maxsplit=1)[0].split() for line in read_text("/etc/resolv.conf").splitlines()]
            options = [parts[1:] for parts in lines if parts[:1] == ["options"]]
            aaaa = not any("no-aaaa" in row for row in options)
        except Unavailable:
            aaaa = None
        return {"global_addresses": addresses, "default_routes": routes, "aaaa_queries_enabled": aaaa}
    check = collect_check("connectivity.ipv6", collect, sources)
    if check.status == "pass":
        check.detail = "AAAA capability is the libc resolver no-aaaa setting, not a live resolution or IPv6 reachability test. AAAA can resolve over IPv4; null means unknown."
    return check


_PROXY_KEYS = {"http_proxy", "https_proxy", "ftp_proxy", "all_proxy", "no_proxy"}


def _redact_proxy(value):
    """Retain destination/path facts without persisting embedded credentials."""
    if not isinstance(value, str):
        raise ValueError("Proxy value is not a string")
    if "@" not in value and "?" not in value and "#" not in value:
        return value
    try:
        parts = urlsplit(value if "://" in value else "//" + value)
        netloc = "[redacted]@" + parts.netloc.rsplit("@", 1)[1] if "@" in parts.netloc else parts.netloc
        return urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    except ValueError:
        return "[redacted malformed proxy]"


def proxies():
    sources = ["environment", "/etc/environment"]
    def collect():
        values = {"environment": {key: _redact_proxy(value) for key, value in os.environ.items() if key.lower() in _PROXY_KEYS}}
        errors = {}
        try:
            entries = shlex.split(read_text("/etc/environment"), comments=True)
            values["etc_environment"] = {key: _redact_proxy(value) for entry in entries if "=" in entry
                                         for key, value in [entry.split("=", 1)] if key.lower() in _PROXY_KEYS}
        except (Unavailable, ValueError) as exc:
            errors["etc_environment"] = str(exc)
        if shutil.which("git"):
            command = ["git", "config", "--get-regexp", r"^(http\..*proxy|remote\..*\.proxy)$"]
            sources.append(shlex.join(command))
            try:
                values["git"] = {_redact_proxy(key): _redact_proxy(value) for line in run_command(command, ok_codes=(0, 1)).splitlines()
                                 if len(parts := line.split(None, 1)) == 2 for key, value in [parts]}
            except Unavailable as exc:
                errors["git"] = str(exc)
        paths = [Path(os.environ.get("DOCKER_CONFIG", str(Path.home() / ".docker"))) / "config.json",
                 Path("/etc/docker/daemon.json")]
        for path in paths:
            sources.append(str(path))
            try:
                config = json.loads(read_text(path)).get("proxies", {})
                # Never return Docker auths or unrelated configuration.
                values[str(path)] = {_redact_proxy(key): {k: _redact_proxy(v) for k, v in value.items()} if isinstance(value, dict)
                                     else _redact_proxy(value) for key, value in config.items()}
            except (Unavailable, ValueError, TypeError, AttributeError) as exc:
                errors[str(path)] = str(exc)
        return {**values, "unavailable": errors}
    check = collect_check("connectivity.proxies", collect, sources)
    if check.status == "pass":
        check.detail = "Proxies may be part of the customer service path. Read-only facts; URL credentials redacted. No proxy settings changed."
    return check


@contextmanager
def _deadline():
    """Bound DNS resolution and slow HTTP bodies too, not just socket I/O.

    The Linux CLI collects on the main thread. Do not leave unkillable resolver
    threads behind or change process-wide socket defaults.
    """
    if threading.current_thread() is not threading.main_thread():
        raise Unavailable("external query", "Hard query deadline requires the main thread.")
    def expired(signum, frame):
        raise TimeoutError(f"External query timed out after {TIMEOUT:g}s.")
    previous = signal.signal(signal.SIGALRM, expired)
    old_timer = signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    started = time.monotonic()
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        if old_timer[0]:
            signal.setitimer(signal.ITIMER_REAL, max(0.001, old_timer[0] - (time.monotonic() - started)), old_timer[1])


def _cached(source, collect, sources):
    if source not in sources:
        sources.append(source)
    cache = _QUERY_CACHE.get()
    if cache is None or source not in cache:
        _echo(source)
        try:
            value = collect()
        except (OSError, HTTPException, ValueError, KeyError, TypeError, IndexError, AttributeError, Unavailable) as exc:
            value = Unavailable(source, f"External observation unavailable: {exc}")
        if cache is not None:
            cache[source] = value
    else:
        value = cache[source]
    if isinstance(value, Unavailable):
        raise value
    return value


def _https(url, sources):
    def collect():
        with _deadline(), urlopen(url, timeout=TIMEOUT) as response:
            body = response.read(1024 * 1024 + 1)
            if len(body) > 1024 * 1024:
                raise ValueError("Response exceeds 1 MiB")
            return body.decode("utf-8").strip()
    return _cached(url, collect, sources)


def _public_ip(text, version):
    address = ipaddress.ip_address(text)
    if address.version != version or not address.is_global:
        raise ValueError(f"Not a public IPv{version} address")
    return str(address)


def _egress(family, sources):
    version = 4 if family == "ipv4" else 6
    resolver = "208.67.222.222" if version == 4 else "2620:119:35::35"
    authority = resolver if version == 4 else f"[{resolver}]"
    endpoint = f"dns://{authority}/myip.opendns.com?type={'A' if version == 4 else 'AAAA'}"
    # getaddrinfo(whoami) uses the configured recursive resolver, so its answer
    # can be that resolver's egress, not this host's. Query OpenDNS directly.
    if shutil.which("dig"):
        def query():
            text = run_command(["dig", f"-{version}", "+short", "+time=4", "+tries=1", "@" + resolver,
                                "myip.opendns.com", "A" if version == 4 else "AAAA"], timeout=TIMEOUT)
            return _public_ip(text, version)
        try:
            return _cached(endpoint, query, sources)
        except Unavailable:
            pass
    url = "https://api.ipify.org" if version == 4 else "https://api6.ipify.org"
    return _public_ip(_https(url, sources), version)


def _ripe(endpoint, parameters, sources):
    url = "https://stat.ripe.net/data/" + endpoint + "/data.json?" + urlencode(parameters)
    payload = json.loads(_https(url, sources))
    if payload.get("status") != "ok" or not isinstance(payload.get("data"), dict):
        raise Unavailable(url, "RIPEstat did not return successful data.")
    return payload["data"]


def _network(family, sources):
    address = _egress(family, sources)
    data = _ripe("network-info", {"resource": address}, sources)
    prefix = str(ipaddress.ip_network(data["prefix"]))
    if ipaddress.ip_address(address) not in ipaddress.ip_network(prefix):
        raise ValueError("Announced prefix does not cover egress address")
    if not isinstance(data["asns"], list):
        raise ValueError("Expected an ASN list")
    origins = list(dict.fromkeys(str(int(asn)) for asn in data["asns"]))
    if any(not 0 < int(origin) <= 4294967295 for origin in origins):
        raise ValueError("Invalid origin ASN")
    if not origins:
        raise Unavailable(sources[-1], "No announced origin ASN found for egress address.")
    return {"egress_ip": address, "prefix": prefix, "asns": origins}


def _external(name, probe, detail):
    sources = []
    def collect():
        values, errors = {}, {}
        for family in FAMILIES:
            try:
                values[family] = probe(family, sources)
            except (Unavailable, OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
                errors[family] = str(exc)
        if not values:
            raise Unavailable(sources[-1] if sources else name, "; ".join(f"{key}: {value}" for key, value in errors.items()))
        return {**values, "unavailable": errors}
    with query_session():
        check = collect_check(name, collect, sources)
    if check.status == "pass":
        check.detail = detail + " No certification profile applied."
        if check.value["unavailable"]:
            check.status = "skip"
            check.detail += " Partial observation; " + "; ".join(f"{key}: {value}" for key, value in check.value["unavailable"].items())
    return check


def egress_ip():
    return _external("connectivity.egress_ip", _egress,
                     "Public egress per family (direct OpenDNS when dig is installed, otherwise HTTPS ipify). HTTPS may traverse configured proxies.")


def asn():
    return _external("connectivity.asn", _network, "RIPEstat announced prefix and origin ASNs for the observed egress, not necessarily the host's own network.")


def roa():
    def probe(family, sources):
        network = _network(family, sources)
        origins = {}
        for origin in network["asns"]:
            data = _ripe("rpki-validation", {"resource": origin, "prefix": network["prefix"]}, sources)
            status = data["status"]
            if status not in ("valid", "invalid_asn", "invalid_length", "unknown"):
                raise ValueError("Unknown RPKI validation state")
            origins[origin] = {"status": status, "covering_roa_exists": status != "unknown",
                               "validating_roas": data.get("validating_roas", [])}
        return {**network, "origins": origins}
    return _external("connectivity.roa", probe, "RPKI covering-ROA existence is separate from origin/maxLength validity; unknown means no covering ROA in RIPEstat's view.")


def ris():
    def probe(family, sources):
        network = _network(family, sources)
        data = _ripe("routing-status", {"resource": network["prefix"], "min_peers_seeing": 1}, sources)
        origins = data["origins"]
        if not isinstance(origins, list):
            raise ValueError("Expected a RIS origin list")
        visible = {str(int(row["origin"])): row for row in origins}
        return {**network, "origins": {origin: {"visible": origin in visible, "collector_observation": visible.get(origin)}
                                       for origin in network["asns"]}, "visibility": data.get("visibility"),
                "query_time": data.get("query_time")}
    return _external("connectivity.ris", probe, "Prefix/origin visibility in RIPE RIS collectors is not end-to-end reachability or global propagation proof.")


CHECKS = {
    "connectivity.routes": routes, "connectivity.resolver": resolver,
    "connectivity.ipv6": ipv6, "connectivity.proxies": proxies,
    "connectivity.egress_ip": egress_ip, "connectivity.asn": asn,
    "connectivity.roa": roa, "connectivity.ris": ris,
}
