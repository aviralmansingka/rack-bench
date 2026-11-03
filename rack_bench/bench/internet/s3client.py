"""Small, IPv4-only S3 transport; no credential discovery or probe policy.

Paths and query pairs passed to the signer are *unescaped*. S3 paths are encoded
once, without dot-segment or slash normalization. Credential values never appear
in errors. Payload preparation (hashing) is outside request timing.
"""

from __future__ import annotations

import base64
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import http.client
import os
import re
import socket
import threading
import time
from typing import Callable, Iterable, Mapping
import xml.etree.ElementTree as ET
import zlib


class CredentialError(ValueError):
    """A required environment variable is absent."""


@dataclass(frozen=True, repr=False)
class Credentials:
    access_key: str
    secret_key: str
    token: str | None = None

    @classmethod
    def from_env(cls, provider: str = "s3") -> Credentials:
        """Env-only credentials; gcs interop HMAC keys use their own names."""
        if provider == "gcs":
            # Static GCS HMAC keys (console Interoperability tab or
            # `gcloud storage hmac create`): no session-token concept.
            return cls(required_env("GCS_ACCESS_KEY_ID"),
                       required_env("GCS_SECRET_ACCESS_KEY"))
        return cls(required_env("AWS_ACCESS_KEY_ID"),
                   required_env("AWS_SECRET_ACCESS_KEY"),
                   os.environ.get("AWS_SESSION_TOKEN") or None)


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise CredentialError(f"missing environment variable: {name}")
    return value


def encode(value: str, *, path: bool = False) -> str:
    safe = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~"
    if path:
        safe += b"/"
    return "".join(chr(c) if c in safe else f"%{c:02X}"
                   for c in value.encode("utf-8"))


def encoded_query(query: Iterable[tuple[str, str]]) -> str:
    return "&".join(f"{key}={value}" for key, value in sorted(
        (encode(key), encode(value)) for key, value in query))


def canonical_request(method: str, path: str,
                      query: Iterable[tuple[str, str]],
                      headers: Mapping[str, str], payload_hash: str) -> str:
    normalized = {key.lower(): " ".join(value.split())
                  for key, value in headers.items()}
    names = sorted(normalized)
    return "\n".join((method, encode(path or "/", path=True),
                      encoded_query(query),
                      "".join(f"{key}:{normalized[key]}\n" for key in names),
                      ";".join(names), payload_hash))


def signing_key(secret: str, date: str, region: str, service: str = "s3") -> bytes:
    key = ("AWS4" + secret).encode()
    for value in (date, region, service, "aws4_request"):
        key = hmac.new(key, value.encode(), hashlib.sha256).digest()
    return key


def string_to_sign(canonical: str, timestamp: str, region: str,
                   service: str = "s3") -> str:
    scope = f"{timestamp[:8]}/{region}/{service}/aws4_request"
    return f"AWS4-HMAC-SHA256\n{timestamp}\n{scope}\n" + hashlib.sha256(
        canonical.encode()).hexdigest()


def authorization(credentials: Credentials, canonical: str, timestamp: str,
                  region: str, service: str = "s3") -> str:
    signature = hmac.new(signing_key(credentials.secret_key, timestamp[:8],
                                     region, service),
                         string_to_sign(canonical, timestamp, region,
                                        service).encode(), hashlib.sha256).hexdigest()
    scope = f"{timestamp[:8]}/{region}/{service}/aws4_request"
    return (f"AWS4-HMAC-SHA256 Credential={credentials.access_key}/{scope}, "
            f"SignedHeaders={canonical.split(chr(10))[-2]}, Signature={signature}")


def sign_headers(credentials: Credentials, method: str, path: str,
                 query: Iterable[tuple[str, str]], headers: Mapping[str, str],
                 payload_hash: str, region: str,
                 timestamp: str | None = None) -> dict[str, str]:
    """Sign a real SHA256 payload digest; the transport always uses this entrypoint."""
    if not re.fullmatch(r"[0-9a-f]{64}", payload_hash):
        raise ValueError("payload_hash must be a real SHA256 hex digest")
    timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    signed = {key.lower(): value for key, value in headers.items()}
    signed["x-amz-date"] = timestamp
    signed["x-amz-content-sha256"] = payload_hash
    if credentials.token:
        signed["x-amz-security-token"] = credentials.token
    canonical = canonical_request(method, path, query, signed, payload_hash)
    signed["authorization"] = authorization(credentials, canonical, timestamp, region)
    return signed


@dataclass
class Timing:
    """Seconds from final attempt start; preparation/backoff are excluded.

    attempts makes control retries explicit; measurement requests always use 1.

    connect_seconds is TCP+TLS duration (excludes signing); other timestamps
    are cumulative from attempt start. response_first_byte_seconds observes
    the first available status-line byte through HTTPResponse's buffered reader.
    headers_seconds includes connect/TLS/upload and response headers, not body
    TTFB. first_byte_seconds is the first response body byte (None for HEAD).
    elapsed_seconds includes body consumption and verification. bytes_sent counts
    completed sendall calls: a lower bound after a failed send, never a claim of
    server acknowledgement.
    """

    headers_seconds: float | None = None
    first_byte_seconds: float | None = None
    elapsed_seconds: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    attempts: int = 1
    connect_seconds: float | None = None  # TCP + TLS, excludes signing
    response_first_byte_seconds: float | None = None  # status line, not headers/body


class _TimedHTTPResponse(http.client.HTTPResponse):
    """Peek through the existing buffered reader before parsing the status line."""

    def _read_status(self):
        if self.fp.peek(1):
            self.on_first_byte()
        return super()._read_status()


class S3Error(Exception):
    """Base for errors a probe must grade, never a fabricated zero sample."""

    def __init__(self, message: str, *, timing: Timing | None = None,
                 status: int | None = None, code: str | None = None):
        super().__init__(message)
        self.timing = timing
        self.status = status
        self.code = code
        self.cleanup_error: Exception | None = None


class TransportError(S3Error):
    """Socket, TLS, timeout, or HTTP framing failure."""


class ServiceError(S3Error):
    """Non-success service response (status/code retained)."""


class ChecksumError(ServiceError):
    """Server rejected an upload digest, or returned a different checksum."""


class VerificationError(S3Error):
    """Downloaded bytes differ from the seeded source."""


class ProtocolError(S3Error):
    """A success response had missing/invalid metadata or incomplete content."""


class _LRUCache:
    """Thread-safe LRU bounded by total value cost (bytes or entries).

    Cached values are deterministic functions of their keys, so two workers
    racing to generate the same entry produce identical bytes and the second
    put is a no-op; the lock is held only for dict moves, never generation.
    """

    def __init__(self, max_cost: int, cost: Callable[[object], int]):
        self._items: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self._cost = cost
        self._max_cost = max_cost
        self.total = 0

    def get(self, key):
        with self._lock:
            value = self._items.get(key)
            if value is None:
                return None
            self._items.move_to_end(key)
            return value

    def put(self, key, value) -> None:
        with self._lock:
            if key in self._items:
                return
            self._items[key] = value
            self.total += self._cost(value)
            while self.total > self._max_cost and len(self._items) > 1:
                _, evicted = self._items.popitem(last=False)
                self.total -= self._cost(evicted)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self.total = 0

    def resize(self, max_cost: int) -> None:
        """Re-cap immediately: evict down to the new bound, keeping one entry."""
        with self._lock:
            self._max_cost = max_cost
            while self.total > self._max_cost and len(self._items) > 1:
                _, evicted = self._items.popitem(last=False)
                self.total -= self._cost(evicted)


# Data-path caches, shared process-wide across the transfer thread pool.
# CHUNK_CACHE holds full payload chunks (<= 1 MiB each) and is capped at
# 256 MiB of chunk bytes: 64 MiB parts at a 1 MiB chunk granularity touch
# only 64 distinct chunks, so one 1 GiB-object run stays far inside the cap,
# and the cap is the hard memory bound however large the objects are.
# DIGEST_CACHE holds one (sha256 hex, crc32 base64) pair per distinct
# (seed, chunk_size, offset, size) part and is capped by entry count; each
# entry is well under 200 bytes, so 4096 entries stay near 1 MiB.
CHUNK_CACHE_LIMIT = 256 * 1024 * 1024
DIGEST_CACHE_LIMIT = 4096
READ_BLOCK = 1024 * 1024        # measured transfer bodies: one callback per MiB
CONTROL_READ_BLOCK = 64 * 1024  # control/error bodies stay under the 4 MiB cap
_CHUNK_CACHE = _LRUCache(CHUNK_CACHE_LIMIT, len)
_DIGEST_CACHE = _LRUCache(DIGEST_CACHE_LIMIT, lambda value: 1)


def clear_payload_caches() -> None:
    """Empty the data-path caches (test seam; determinism makes this optional)."""
    _CHUNK_CACHE.clear()
    _DIGEST_CACHE.clear()


def set_chunk_cache_limit(limit: int) -> None:
    """Re-cap the chunk cache. Worker processes call this with a smaller cap:
    a process-pool bulk window caches the same run-shared payload bytes once
    per process, so N workers must not each hold the full parent-side cap."""
    _CHUNK_CACHE.resize(limit)


@dataclass(frozen=True)
class SeededPayload:
    """Seekable, bounded pseudorandom source (no object-sized allocation).

    Persist seed, size and chunk_size alongside an object. chunk(index, size)
    is reproducible; iter_chunks(offset, size) supports arbitrary byte ranges.
    verify(data, offset) raises VerificationError on a regen/compare mismatch.
    SHAKE256 output is cryptographically pseudorandom, not compressible filler.
    Default 1 MiB chunks cut generator iterations 16x versus 64 KiB and match
    the socket read/send block size; chunks are served from a bounded LRU
    (CHUNK_CACHE_LIMIT), so repeated generation after warm-up is ~free.
    """

    seed: str
    size: int
    chunk_size: int = 1024 * 1024

    def __post_init__(self):
        if self.size < 0 or not 1 <= self.chunk_size <= 1024 * 1024:
            raise ValueError("size must be nonnegative; chunk_size must be 1..1048576")

    def chunk(self, chunk_index: int, size: int | None = None) -> bytes:
        size = self.chunk_size if size is None else size
        if chunk_index < 0 or not 0 <= size <= self.chunk_size:
            raise ValueError("invalid chunk index or size")
        key = (self.seed, self.chunk_size, chunk_index)
        data = _CHUNK_CACHE.get(key)
        if data is None:
            seed = self.seed.encode("utf-8")
            domain = b"rack-bench-v1\0" + len(seed).to_bytes(8, "big") + seed
            data = hashlib.shake_256(domain + chunk_index.to_bytes(8, "big")).digest(self.chunk_size)
            _CHUNK_CACHE.put(key, data)
        return data if len(data) == size else data[:size]

    def iter_chunks(self, offset: int = 0, size: int | None = None) -> Iterable[bytes]:
        size = self.size - offset if size is None else size
        if offset < 0 or size < 0 or offset + size > self.size:
            raise ValueError("payload range outside object")
        end = offset + size
        while offset < end:
            index, within = divmod(offset, self.chunk_size)
            count = min(end - offset, self.chunk_size - within)
            yield self.chunk(index, within + count)[within:]
            offset += count

    def verify(self, data: bytes, offset: int = 0) -> None:
        consumed = 0
        for expected in self.iter_chunks(offset, len(data)):
            if not hmac.compare_digest(data[consumed:consumed + len(expected)], expected):
                raise VerificationError(f"download payload mismatch at offset {offset + consumed}")
            consumed += len(expected)


def checksum_headers(chunks: Iterable[bytes]) -> dict[str, str]:
    """One bounded pre-pass; CRC32 request server verification on every PUT.

    S3 forbids combining the legacy content-md5 with a flexible x-amz-checksum-*
    header ("You can only specify one non-default checksum at a time"), so
    uploads carry CRC32 only; x-amz-content-sha256 is the SigV4 payload hash.
    """
    sha = hashlib.sha256()
    crc = 0
    for chunk in chunks:
        sha.update(chunk)
        crc = zlib.crc32(chunk, crc)
    return {"x-amz-content-sha256": sha.hexdigest(),
            "x-amz-checksum-crc32": base64.b64encode(crc.to_bytes(4, "big")).decode()}


def part_checksum_headers(payload: SeededPayload, offset: int, size: int) -> dict[str, str]:
    """Signed digests (SHA256+CRC32) for one payload part, via a bounded LRU.

    Both digests are signed headers, so a pre-pass over the part body is
    protocol-required; caching it keyed (seed, chunk_size, offset, size) makes
    the pre-pass a hit whenever the same part shape repeats. A run-shared
    payload seed makes the part at any given offset byte-identical across all
    sibling objects, so after the first object the pre-pass is ~free.
    """
    key = (payload.seed, payload.chunk_size, offset, size)
    cached = _DIGEST_CACHE.get(key)
    if cached is None:
        headers = checksum_headers(payload.iter_chunks(offset, size))
        cached = (headers["x-amz-content-sha256"], headers["x-amz-checksum-crc32"])
        _DIGEST_CACHE.put(key, cached)
    return {"x-amz-content-sha256": cached[0], "x-amz-checksum-crc32": cached[1]}


@dataclass(frozen=True)
class Endpoint:
    host: str
    region: str
    path_style: bool
    port: int | None = None
    tls: bool = True

    @property
    def authority(self) -> str:
        return self.host if self.port is None else f"{self.host}:{self.port}"


def resolve_endpoint(provider: str, region: str) -> Endpoint:
    """Region selection is the caller's policy; R2 always signs with auto."""
    if provider == "s3":
        if not re.fullmatch(r"[a-z0-9-]+", region):
            raise ValueError("invalid S3 region")
        return Endpoint(f"s3.{region}.amazonaws.com", region, False)
    if provider == "r2":
        account = required_env("R2_ACCOUNT_ID")
        if not re.fullmatch(r"[A-Za-z0-9-]+", account):
            raise ValueError("invalid R2_ACCOUNT_ID")
        return Endpoint(f"{account}.r2.cloudflarestorage.com", "auto", True)
    if provider == "gcs":
        # One global XML-interop endpoint; the pinned region is the bucket's
        # location. Google accepts any location string in the SigV4 scope of
        # an x-amz request (the service stays s3), so the location signs
        # directly. Path-style addressing keeps dotted bucket names on TLS.
        if not re.fullmatch(r"[a-z0-9-]+", region):
            raise ValueError("invalid GCS location")
        return Endpoint("storage.googleapis.com", region, True)
    raise ValueError(f"unsupported provider: {provider}")


def connect_ipv4(address, timeout, source_address=None):
    """Per-connection AF_INET resolver; never monkey-patch global socket state."""
    last_error = None
    for family, kind, proto, _, sockaddr in socket.getaddrinfo(
            address[0], address[1], socket.AF_INET, socket.SOCK_STREAM):
        sock = socket.socket(family, kind, proto)
        try:
            sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    raise last_error or OSError("no IPv4 addresses for endpoint")


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    timing: Timing
    body: bytes = b""  # Control XML only; measurement bodies never accumulate.
    upload_crc32: str | None = None


class S3Client:
    """Env-only credentials. One pooled keep-alive socket per thread; per-socket timeout.

    All PUTs and GET object operations are measurement ops and never retry.
    Initiate/complete/abort/list/HEAD/DELETE retry bounded 5xx/connection errors.
    A timed HEAD probe should pass measurement=True to disable control retries.
    The optional Endpoint is also the loopback-test seam, not credential config.
    """

    def __init__(self, bucket: str, region: str, *, provider: str = "s3",
                 timeout: float = 30, control_retries: int = 2,
                 backoff: float = 0.1, endpoint: Endpoint | None = None):
        self.credentials = Credentials.from_env(provider)
        self.endpoint = endpoint or resolve_endpoint(provider, region)
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket):
            raise ValueError("bucket must be a DNS-compatible name")
        if not self.endpoint.path_style and "." in bucket:
            raise ValueError("virtual-hosted TLS buckets must not contain dots")
        if timeout <= 0 or control_retries < 0 or backoff < 0:
            raise ValueError("invalid timeout or retry policy")
        self.bucket = bucket
        self.timeout = timeout
        self.control_retries = control_retries
        self.backoff = backoff
        # S3 flexible checksums (x-amz-checksum-crc32 on parts, the initiate
        # checksum headers, and completion ChecksumCRC32 elements) request
        # server-side zlib-CRC32 verification. GCS validates only CRC32C
        # natively and mishandles the S3-style headers, so gcs uploads carry
        # the signed SHA256 payload digest only; downloads still verify every
        # byte against the seeded payload client-side.
        self.s3_checksums = provider != "gcs"
        self._connections = threading.local()

    def _pooled(self, host, port, cls):
        """Live keep-alive connection for this thread and endpoint, or None."""
        entry = getattr(self._connections, "entry", None)
        if entry is None:
            return None
        if (entry[0] == host and entry[1] == port and entry[2] is cls
                and entry[3].sock is not None):
            return entry[3]
        entry[3].close()
        self._connections.entry = None
        return None

    def close(self) -> None:
        """Close the calling thread's pooled connection. Threads own sockets."""
        entry = getattr(self._connections, "entry", None)
        if entry is not None:
            self._connections.entry = None
            entry[3].close()

    def _request(self, method: str, key: str = "", *, query=(), headers=None,
                 body: Callable[[], Iterable[bytes]] = lambda: (), size: int = 0,
                 measurement: bool = False,
                 consume: Callable[[bytes, int], None] | None = None,
                 on_progress: Callable[[int, float], None] | None = None,
                 fresh_connection: bool = False) -> Response:
        endpoint = self.endpoint
        host = endpoint.host if endpoint.path_style else f"{self.bucket}.{endpoint.host}"
        authority = host if endpoint.port is None else f"{host}:{endpoint.port}"
        path = f"/{self.bucket}/{key}" if endpoint.path_style else f"/{key}"
        target = encode(path, path=True)
        query = tuple(query)
        if query:
            target += "?" + encoded_query(query)
        # content-length is sent but never signed: providers canonicalize
        # zero-length bodies inconsistently (R2 signs it as an empty value),
        # and known-good signers (aws cli/botocore) leave it unsigned.
        request_headers = dict(headers or {})
        request_headers.update({"host": authority})
        transport_only = {"content-length": str(size)}
        digest = request_headers.get("x-amz-content-sha256", hashlib.sha256(b"").hexdigest())
        attempts = 1 if measurement else self.control_retries + 1
        cls = http.client.HTTPSConnection if endpoint.tls else http.client.HTTPConnection
        conn = None if fresh_connection else self._pooled(host, endpoint.port, cls)
        for attempt in range(1, attempts + 1):
            error = None
            # One resend when an idle pooled socket died before any measured
            # byte existed. That is connection setup, never a hidden retry:
            # timing restarts and the recorded attempt count stays unchanged.
            for stale_attempt in (1, 2):
                timing = Timing(attempts=attempt)
                start = time.perf_counter()
                reused = conn is not None and conn.sock is not None
                if reused:
                    timing.connect_seconds = 0.0
                else:
                    conn = cls(host, endpoint.port, timeout=self.timeout)
                    conn._create_connection = connect_ipv4
                    connect_start = time.perf_counter()
                    conn.connect()
                    timing.connect_seconds = time.perf_counter() - connect_start
                    if not fresh_connection:
                        self._connections.entry = (host, endpoint.port, cls, conn)

                def response_class(*args, **kwargs):
                    response = _TimedHTTPResponse(*args, **kwargs)

                    def first_byte():
                        if timing.response_first_byte_seconds is None:
                            timing.response_first_byte_seconds = time.perf_counter() - start

                    response.on_first_byte = first_byte
                    return response

                conn.response_class = response_class
                keep = False
                try:
                    signed = sign_headers(self.credentials, method, path, query,
                                          request_headers, digest, endpoint.region)
                    conn.putrequest(method, target, skip_host=True, skip_accept_encoding=True)
                    for name, value in {**signed, **transport_only}.items():
                        conn.putheader(name, value)
                    conn.endheaders()
                    for chunk in body():
                        conn.send(chunk)
                        timing.bytes_sent += len(chunk)
                        if on_progress:
                            on_progress(timing.bytes_sent, time.perf_counter() - start)
                    if timing.bytes_sent != size:
                        raise ProtocolError("upload source length differs from Content-Length")
                    response = conn.getresponse()
                    timing.headers_seconds = time.perf_counter() - start
                    result = Response(response.status, dict((k.lower(), v)
                                      for k, v in response.getheaders()), timing)
                    collect = consume is None or not 200 <= response.status < 300
                    collected = bytearray()
                    # read(1) exposes body TTFB, unlike a blocking full-chunk read.
                    # Measured transfer bodies then read in 1 MiB blocks (one
                    # Python callback per MiB, matching the payload chunk size);
                    # control/error bodies keep small reads under the 4 MiB cap.
                    read_size = CONTROL_READ_BLOCK if collect else READ_BLOCK
                    block = response.read(1)
                    if block:
                        timing.first_byte_seconds = time.perf_counter() - start
                    while block:
                        offset = timing.bytes_received
                        timing.bytes_received += len(block)
                        if collect:
                            if len(collected) + len(block) > 4 * 1024 * 1024:
                                raise ProtocolError("control/error response exceeds 4 MiB")
                            collected.extend(block)
                        else:
                            consume(block, offset)
                        block = response.read(read_size)
                    result.body = bytes(collected)
                    content_length = result.headers.get("content-length")
                    if method != "HEAD" and content_length is not None:
                        if not content_length.isdigit() or int(content_length) != timing.bytes_received:
                            raise ProtocolError("truncated or invalid Content-Length")
                    if not 200 <= result.status < 300:
                        self._raise_service(result)
                    # Multipart completion may report an Error inside HTTP 200.
                    if result.body and method == "POST":
                        root = self._xml(result)
                        if root.tag.rsplit("}", 1)[-1] == "Error":
                            self._raise_service(result)
                    keep = True
                    return result
                except (OSError, http.client.HTTPException) as exc:
                    if (stale_attempt == 1 and reused
                            and timing.bytes_sent == 0 and timing.bytes_received == 0):
                        # The peer closed its idle keep-alive socket. No measured
                        # byte ever existed; the finally block closes it and the
                        # next pass reconnects with fresh timing.
                        continue
                    error = TransportError(f"{method} transport failed: {type(exc).__name__}", timing=timing)
                    error.__cause__ = exc
                except S3Error as exc:
                    error = exc
                    error.timing = timing
                finally:
                    timing.elapsed_seconds = time.perf_counter() - start
                    if not keep or fresh_connection:
                        # One-shot connections are closed as soon as their body is
                        # consumed; they never enter the pool, so rely on nothing.
                        conn.close()
                        entry = getattr(self._connections, "entry", None)
                        if not fresh_connection and entry is not None and entry[3] is conn:
                            self._connections.entry = None
                if error is not None:
                    break
            if error is not None and (attempt == attempts or not (
                    isinstance(error, TransportError) or
                    isinstance(error, ServiceError) and error.status is not None and error.status >= 500)):
                raise error
            if error is not None:
                time.sleep(self.backoff * 2 ** (attempt - 1))
            conn = None
        raise AssertionError("unreachable")

    @staticmethod
    def _xml(response: Response, expected_root: str | None = None) -> ET.Element:
        try:
            root = ET.fromstring(response.body)
        except ET.ParseError as exc:
            raise ProtocolError("invalid service XML", timing=response.timing,
                                status=response.status) from exc
        if expected_root and root.tag.rsplit("}", 1)[-1] != expected_root:
            raise ProtocolError(f"expected {expected_root} XML", timing=response.timing)
        return root

    @staticmethod
    def _text(root: ET.Element, name: str) -> str | None:
        return root.findtext(f".//{{*}}{name}")

    def _raise_service(self, response: Response):
        try:
            code = self._text(ET.fromstring(response.body), "Code")
        except ET.ParseError:
            code = None
        cls = ChecksumError if code in {
            "InvalidDigest", "BadDigest", "ChecksumMismatch", "XAmzContentSHA256Mismatch"
        } else ServiceError
        raise cls(f"S3 response {response.status}: {code or 'unknown error'}",
                  timing=response.timing, status=response.status, code=code)

    def _upload(self, key: str, payload: SeededPayload, offset: int, size: int,
                query=(), on_progress=None) -> Response:
        body = lambda: payload.iter_chunks(offset, size)
        headers = part_checksum_headers(payload, offset, size)
        if not self.s3_checksums:
            del headers["x-amz-checksum-crc32"]
        result = self._request("PUT", key, query=query, headers=headers,
                               body=body, size=size, measurement=True, on_progress=on_progress)
        result.upload_crc32 = headers.get("x-amz-checksum-crc32")
        returned = result.headers.get("x-amz-checksum-crc32")
        if (returned is not None and result.upload_crc32 is not None
                and returned != result.upload_crc32):
            raise ChecksumError("server CRC32 differs from upload", timing=result.timing,
                                status=result.status)
        return result

    def put_object(self, key: str, payload: SeededPayload, *,
                   on_progress: Callable[[int, float], None] | None = None) -> Response:
        """on_progress(bytes_sent, seconds) runs after each bounded socket send."""
        return self._upload(key, payload, 0, payload.size, on_progress=on_progress)

    def initiate_multipart(self, key: str) -> str:
        headers = ({"x-amz-checksum-algorithm": "CRC32",
                    "x-amz-checksum-type": "COMPOSITE"} if self.s3_checksums else {})
        response = self._request("POST", key, query=(("uploads", ""),),
                                 headers=headers)
        upload_id = self._text(self._xml(response, "InitiateMultipartUploadResult"), "UploadId")
        if not upload_id:
            raise ProtocolError("missing UploadId", timing=response.timing)
        return upload_id

    def upload_part(self, key: str, upload_id: str, part_number: int,
                    payload: SeededPayload, offset: int, size: int, *,
                    on_progress: Callable[[int, float], None] | None = None) -> Response:
        if not 1 <= part_number <= 10000:
            raise ValueError("part_number must be 1..10000")
        response = self._upload(key, payload, offset, size,
                                (("partNumber", str(part_number)), ("uploadId", upload_id)),
                                on_progress=on_progress)
        if not response.headers.get("etag"):
            raise ProtocolError("missing part ETag", timing=response.timing)
        return response

    def complete_multipart(self, key: str, upload_id: str,
                           parts: Iterable[tuple[int, str, str | None]]) -> Response:
        """Parts are (number, ETag, base64 CRC32 or None), preserving digests.

        GCS uploads carry no part CRC32; their completion XML documents only
        PartNumber and ETag elements, so ChecksumCRC32 is sent where computed.
        """
        root = ET.Element("CompleteMultipartUpload")
        parts = sorted(parts)
        if not 1 <= len(parts) <= 10000 or [part[0] for part in parts] != list(range(1, len(parts) + 1)):
            raise ValueError("completion requires 1..10000 consecutive parts from 1")
        for number, etag, crc32 in parts:
            if not etag or crc32 is not None and len(base64.b64decode(crc32, validate=True)) != 4:
                raise ValueError("completion requires ETags and base64 CRC32 digests where sent")
            part = ET.SubElement(root, "Part")
            ET.SubElement(part, "PartNumber").text = str(number)
            ET.SubElement(part, "ETag").text = etag
            if crc32 is not None:
                ET.SubElement(part, "ChecksumCRC32").text = crc32
        body = ET.tostring(root, encoding="utf-8")
        headers = checksum_headers((body,))
        # Complete's CRC32 header describes the assembled object, NOT this XML.
        # The XML body is covered by Content-MD5 and the real SigV4 SHA256.
        del headers["x-amz-checksum-crc32"]
        headers["content-type"] = "application/xml"
        response = self._request("POST", key, query=(("uploadId", upload_id),),
                                 body=lambda: (body,), size=len(body), headers=headers)
        result = self._xml(response, "CompleteMultipartUploadResult")
        if not self._text(result, "ETag"):
            raise ProtocolError("missing completion ETag", timing=response.timing)
        returned = self._text(result, "ChecksumCRC32")
        if returned is not None and all(part[2] for part in parts):
            crc = zlib.crc32(b"".join(base64.b64decode(part[2], validate=True) for part in parts))
            expected = base64.b64encode(crc.to_bytes(4, "big")).decode() + f"-{len(parts)}"
            if returned != expected:
                raise ChecksumError("completion CRC32 differs from parts", timing=response.timing)
        return response

    def abort_multipart(self, key: str, upload_id: str) -> Response:
        return self._request("DELETE", key, query=(("uploadId", upload_id),))

    def multipart_upload(self, key: str, payload: SeededPayload,
                         part_size: int = 8 * 1024 * 1024,
                         on_part: Callable[[Response], None] | None = None,
                         on_progress: Callable[[int, float], None] | None = None) -> Response:
        """Bounded memory even for GB objects; abort preserves the primary error.

        on_progress counters/timing reset for each part; on_part marks its end.
        A lost initiation response can orphan an unknown ID: use a bucket lifecycle
        rule for incomplete uploads in addition to active cleanup of known IDs.
        """
        if part_size < 5 * 1024 * 1024 or part_size > 5 * 1024**3:
            raise ValueError("part_size must be 5 MiB..5 GiB")
        if payload.size <= 0 or (payload.size + part_size - 1) // part_size > 10000:
            raise ValueError("multipart needs 1..10000 nonempty parts")
        upload_id = self.initiate_multipart(key)
        parts = []
        try:
            for number, offset in enumerate(range(0, payload.size, part_size), 1):
                response = self.upload_part(key, upload_id, number, payload, offset,
                                            min(part_size, payload.size - offset),
                                            on_progress=on_progress)
                parts.append((number, response.headers["etag"], response.upload_crc32))
                if on_part:
                    on_part(response)
            return self.complete_multipart(key, upload_id, parts)
        except BaseException as exc:
            try:
                self.abort_multipart(key, upload_id)
            except Exception as cleanup_error:
                if isinstance(exc, S3Error):
                    exc.cleanup_error = cleanup_error
                exc.add_note(f"multipart abort failed: {type(cleanup_error).__name__}")
            raise

    def get_object(self, key: str, *, byte_range: tuple[int, int] | None = None,
                   payload: SeededPayload | None = None,
                   consume: Callable[[bytes, int], None] | None = None,
                   fresh_connection: bool = False) -> Response:
        """Stream/discard body; optional verify then consume(data, absolute_offset).

        Range ends are inclusive. Supplying payload verifies size as well as bytes.
        Neither range nor full-object GET retries, including callback failures.
        fresh_connection bypasses the pooled socket so latency samples keep
        TCP+TLS setup inside their timing, as on a cold client.
        """
        start = 0
        headers = {}
        if byte_range is not None:
            start, end = byte_range
            if start < 0 or end < start:
                raise ValueError("invalid byte range")
            headers["range"] = f"bytes={start}-{end}"

        def receive(data, offset):
            if payload is not None:
                if start + offset + len(data) > payload.size:
                    raise VerificationError("download exceeds seeded object size")
                payload.verify(data, start + offset)
            if consume:
                consume(data, start + offset)

        response = self._request("GET", key, headers=headers, measurement=True,
                                 consume=receive, fresh_connection=fresh_connection)
        if byte_range is not None:
            expected_size = end - start + 1
            content_range = response.headers.get("content-range", "")
            match = re.fullmatch(rf"bytes {start}-{end}/([0-9]+)", content_range)
            if response.status != 206 or not match or int(match[1]) <= end:
                raise ProtocolError("server did not honor requested range", timing=response.timing)
            if payload is not None and int(match[1]) != payload.size:
                raise ProtocolError("range total differs from seeded object size", timing=response.timing)
        else:
            expected_size = payload.size if payload is not None else None
        if expected_size is not None and response.timing.bytes_received != expected_size:
            raise ProtocolError("download length differs from expected range/object", timing=response.timing)
        return response

    def head_object(self, key: str, *, measurement: bool = False) -> Response:
        return self._request("HEAD", key, measurement=measurement)

    def delete_object(self, key: str) -> Response:
        return self._request("DELETE", key)

    def list_objects(self, prefix: str) -> Iterable[str]:
        """List only a nonempty bench prefix; follow every continuation token."""
        if not prefix:
            raise ValueError("cleanup requires a nonempty prefix")
        token = None
        seen = set()
        while True:
            query = [("list-type", "2"), ("prefix", prefix)]
            if token:
                query.append(("continuation-token", token))
            response = self._request("GET", query=query)
            root = self._xml(response, "ListBucketResult")
            truncated = self._text(root, "IsTruncated")
            if truncated not in {"true", "false"}:
                raise ProtocolError("missing/invalid IsTruncated", timing=response.timing)
            for contents in root.findall(".//{*}Contents"):
                key = self._text(contents, "Key")
                if key is None or not key.startswith(prefix):
                    raise ProtocolError("listed key outside cleanup prefix", timing=response.timing)
                yield key
            if truncated == "false":
                return
            token = self._text(root, "NextContinuationToken")
            if not token or token in seen:
                raise ProtocolError("missing/repeated continuation token", timing=response.timing)
            seen.add(token)

    def cleanup_prefix(self, prefix: str) -> None:
        for key in self.list_objects(prefix):
            self.delete_object(key)
