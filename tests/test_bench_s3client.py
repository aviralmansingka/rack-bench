"""Offline signing vectors and loopback-only transport tests."""

import base64
from collections import Counter
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
import socket
import threading
import tracemalloc
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zlib

from rack_bench.bench.internet import s3client as s3


EMPTY_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

# Literal fixtures from AWS's SDK test suite (never downloaded at test time):
# https://github.com/boto/botocore/tree/develop/tests/unit/auth/aws4_testsuite
# get-vanilla, get-utf8, get-vanilla-query-order-encoded (.creq/.sts/.authz).
VECTORS = (
    ("get-vanilla", "/", (),
     "GET\n/\n\nhost:example.amazonaws.com\nx-amz-date:20150830T123600Z\n\n"
     "host;x-amz-date\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "bb579772317eb040ac9ed261061d46c1f17a8133879d6129b6e1c25292927e63",
     "5fa00fa31553b73ebf1942676e86291e8372ff2a2260956d9b8aae1d763fbf31"),
    ("get-utf8", "/ሴ", (),
     "GET\n/%E1%88%B4\n\nhost:example.amazonaws.com\nx-amz-date:20150830T123600Z\n\n"
     "host;x-amz-date\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "2a0a97d02205e45ce2e994789806b19270cfbbb0921b278ccf58f5249ac42102",
     "8318018e0b0f223aa2bbf98705b62bb787dc9c0e678f255a891fd03141be5d85"),
    ("get-vanilla-query-order-encoded", "/",
     (("Param-3", "Value3"), ("Param", "Value2"), ("ሴ", "Value1")),
     "GET\n/\n%E1%88%B4=Value1&Param=Value2&Param-3=Value3\n"
     "host:example.amazonaws.com\nx-amz-date:20150830T123600Z\n\n"
     "host;x-amz-date\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
     "868294f5c38bd141c4972a373a76654f1418a8e4fc18b2e7903ae45e8ae0ec71",
     "371d3713e185cc334048618a97f809c9ffe339c62934c032af5a0e595648fcac"),
)


class SigningVectors(unittest.TestCase):
    def check_vector(self, vector):
        name, path, query, expected, canonical_hash, signature = vector
        credentials = s3.Credentials(
            "AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY")
        headers = {"Host": "example.amazonaws.com", "X-Amz-Date": "20150830T123600Z"}
        canonical = s3.canonical_request("GET", path, query, headers, EMPTY_HASH)
        self.assertEqual(canonical, expected, name)
        self.assertEqual(s3.string_to_sign(canonical, "20150830T123600Z", "us-east-1", "service"),
                         "AWS4-HMAC-SHA256\n20150830T123600Z\n"
                         "20150830/us-east-1/service/aws4_request\n" + canonical_hash)
        self.assertEqual(s3.authorization(credentials, canonical, "20150830T123600Z",
                                          "us-east-1", "service"),
                         "AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20150830/us-east-1/"
                         "service/aws4_request, SignedHeaders=host;x-amz-date, Signature="
                         + signature)

    def test_vector_get_vanilla(self):
        self.check_vector(VECTORS[0])

    def test_vector_get_utf8(self):
        self.check_vector(VECTORS[1])

    def test_vector_get_vanilla_query_order_encoded(self):
        self.check_vector(VECTORS[2])

    def test_vector_s3_get_range(self):
        # https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html
        # S3 example secret has /bPx, unlike the generic suite's +bPx.
        credentials = s3.Credentials(
            "AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
        expected = (
            "GET\n/test.txt\n\nhost:examplebucket.s3.amazonaws.com\nrange:bytes=0-9\n"
            "x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n"
            "x-amz-date:20130524T000000Z\n\nhost;range;x-amz-content-sha256;x-amz-date\n"
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        headers = {"host": "examplebucket.s3.amazonaws.com", "range": "bytes=0-9",
                   "x-amz-content-sha256": EMPTY_HASH, "x-amz-date": "20130524T000000Z"}
        self.assertEqual(s3.canonical_request("GET", "/test.txt", (), headers, EMPTY_HASH), expected)
        self.assertEqual(s3.string_to_sign(expected, "20130524T000000Z", "us-east-1"),
                         "AWS4-HMAC-SHA256\n20130524T000000Z\n20130524/us-east-1/s3/aws4_request\n"
                         "7344ae5b7ee6c3e7e6b0fe0640412a37625d1fbfff95c48bbb2dc43964946972")
        signed = s3.sign_headers(credentials, "GET", "/test.txt", (), headers,
                                 EMPTY_HASH, "us-east-1", "20130524T000000Z")
        self.assertEqual(signed["authorization"].replace(", ", ","),
                         "AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20130524/us-east-1/"
                         "s3/aws4_request,SignedHeaders=host;range;x-amz-content-sha256;x-amz-date,"
                         "Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41")

    def test_s3_path_not_normalized_and_query_encoded_once(self):
        canonical = s3.canonical_request("GET", "/a//.././% +/ሴ", (
            ("z", ""), ("a", "+ %"), ("a", "/")), {}, EMPTY_HASH)
        self.assertEqual(canonical.splitlines()[:3], ["GET", "/a//.././%25%20%2B/%E1%88%B4",
                                                      "a=%2B%20%25&a=%2F&z="])
        self.assertEqual(s3.encoded_query(()), "")

    def test_session_token_and_real_payload_hash_signed(self):
        digest = hashlib.sha256(b"payload").hexdigest()
        headers = s3.sign_headers(s3.Credentials("key", "secret", "token"), "PUT", "/", (),
                                  {"Host": "example.com"}, digest, "auto")
        self.assertEqual(headers["x-amz-content-sha256"], digest)
        self.assertEqual(headers["x-amz-security-token"], "token")
        self.assertIn("x-amz-security-token", headers["authorization"])
        with self.assertRaises(ValueError):
            s3.sign_headers(s3.Credentials("key", "secret"), "GET", "/", (),
                            {}, "UNSIGNED-PAYLOAD", "auto")


class PayloadTests(unittest.TestCase):
    def test_seeded_chunks_and_arbitrary_range_verification(self):
        source = s3.SeededPayload("repeatable", 10000, chunk_size=1024)
        same = s3.SeededPayload("repeatable", 10000, chunk_size=1024)
        data = b"".join(source.iter_chunks())
        self.assertEqual(data, b"".join(same.iter_chunks()))
        self.assertNotEqual(source.chunk(0), source.chunk(1))
        self.assertNotEqual(source.chunk(0), s3.SeededPayload("other", 10000, 1024).chunk(0))
        self.assertGreater(len(zlib.compress(data)), len(data) * 0.99)
        self.assertEqual(b"".join(source.iter_chunks(900, 2200)), data[900:3100])
        source.verify(data[900:3100], 900)
        with self.assertRaises(s3.VerificationError):
            source.verify(b"bad", 900)
        with self.assertRaises(ValueError):
            list(source.iter_chunks(9999, 2))
        with self.assertRaises(ValueError):
            s3.SeededPayload("x", 1, 0)

    def test_checksum_headers_known_crc32_md5_sha256(self):
        headers = s3.checksum_headers((b"123", b"456789"))
        self.assertEqual(headers["x-amz-checksum-crc32"], "y/Q5Jg==")
        self.assertEqual(headers["content-md5"], "JfnnlDI7RTiF9RgfG2JNCw==")
        self.assertEqual(headers["x-amz-content-sha256"],
                         "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225")

    def test_env_only_credentials_and_provider_endpoints(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(s3.CredentialError, "AWS_ACCESS_KEY_ID"):
                s3.Credentials.from_env()
            os.environ["AWS_ACCESS_KEY_ID"] = "key"
            with self.assertRaisesRegex(s3.CredentialError, "AWS_SECRET_ACCESS_KEY"):
                s3.Credentials.from_env()
            os.environ["AWS_SECRET_ACCESS_KEY"] = "secret"
            os.environ["AWS_SESSION_TOKEN"] = "session"
            self.assertEqual(s3.Credentials.from_env().token, "session")
            with self.assertRaisesRegex(s3.CredentialError, "R2_ACCOUNT_ID"):
                s3.resolve_endpoint("r2", "apac")
            os.environ["R2_ACCOUNT_ID"] = "account"
            self.assertEqual(s3.resolve_endpoint("r2", "apac"),
                             s3.Endpoint("account.r2.cloudflarestorage.com", "auto", True))
        self.assertEqual(s3.resolve_endpoint("s3", "ap-south-1"),
                         s3.Endpoint("s3.ap-south-1.amazonaws.com", "ap-south-1", False))
        with self.assertRaises(ValueError):
            s3.resolve_endpoint("s3", "bad/region")
        with self.assertRaises(ValueError):
            s3.resolve_endpoint("gcs", "auto")

    def test_ipv4_connection_uses_local_timeout(self):
        with patch.object(s3.socket, "getaddrinfo", return_value=[
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]) as resolve:
            with patch.object(s3.socket, "socket") as make_socket:
                before = socket.getdefaulttimeout()
                s3.connect_ipv4(("example.com", 80), 7)
                resolve.assert_called_once_with("example.com", 80, socket.AF_INET, socket.SOCK_STREAM)
                make_socket.return_value.settimeout.assert_called_once_with(7)
                make_socket.return_value.connect.assert_called_once_with(("127.0.0.1", 80))
                self.assertEqual(socket.getdefaulttimeout(), before)


class MockS3(BaseHTTPRequestHandler):
    """No object buffering: digest requests while reading at most 8 KiB at once."""

    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def reply(self, status=200, body=b"", headers=None):
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.close_connection = True
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def handle_request(self):
        state = self.server.state
        state["counts"][self.command] += 1
        headers = dict((k.lower(), v) for k, v in self.headers.items())
        record = {"method": self.command, "path": self.path, "headers": headers}
        state["requests"].append(record)
        remaining = int(headers.get("content-length", "0"))
        md5 = hashlib.md5(usedforsecurity=False)
        sha = hashlib.sha256()
        crc = 0
        xml = bytearray()
        while remaining:
            data = self.rfile.read(min(8192, remaining))
            if not data:
                return
            remaining -= len(data)
            state["max_read"] = max(state["max_read"], len(data))
            md5.update(data)
            sha.update(data)
            crc = zlib.crc32(data, crc)
            if self.command == "POST":
                xml.extend(data)
        record["body"] = bytes(xml)
        if state.get("disconnect") == self.command:
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            return
        if state.get("fail_method") == self.command:
            if state["failures"] > 0:
                state["failures"] -= 1
                self.reply(503, b"<Error><Code>SlowDown</Code></Error>")
                return
        if headers.get("x-amz-content-sha256") != sha.hexdigest():
            self.reply(400, b"<Error><Code>BadDigest</Code></Error>")
            return
        if self.command == "PUT" or xml:
            expected_md5 = base64.b64encode(md5.digest()).decode()
            expected_crc = base64.b64encode(crc.to_bytes(4, "big")).decode()
            record["crc32"] = expected_crc
            if (headers.get("content-md5") != expected_md5 or
                    self.command == "PUT" and headers.get("x-amz-checksum-crc32") != expected_crc or
                    state.get("reject_digest")):
                self.reply(400, b"<Error><Code>InvalidDigest</Code></Error>")
                return
        if self.command == "POST" and "uploads=" in self.path:
            self.reply(body=b'<InitiateMultipartUploadResult xmlns="urn:s3">'
                       b'<UploadId>upload+/=1</UploadId></InitiateMultipartUploadResult>')
        elif self.command == "POST":
            if "complete_body" in state:
                self.reply(body=state["complete_body"])
            elif state.get("complete_error"):
                self.reply(body=b"<Error><Code>InvalidPart</Code></Error>")
            else:
                self.reply(body=b"<CompleteMultipartUploadResult><ETag>done</ETag>"
                           b"</CompleteMultipartUploadResult>")
        elif self.command == "PUT":
            response_headers = {"ETag": '"part-etag"', "x-amz-checksum-crc32": expected_crc}
            if state.get("bad_returned_crc"):
                response_headers["x-amz-checksum-crc32"] = "AAAAAA=="
            if state.get("missing_etag"):
                del response_headers["ETag"]
            self.reply(headers=response_headers)
        elif self.command == "GET" and "list-type=2" in self.path:
            if "continuation-token=" in self.path:
                body = b"<ListBucketResult><IsTruncated>false</IsTruncated>" \
                       b"<Contents><Key>bench/two</Key></Contents></ListBucketResult>"
            else:
                body = b'<ListBucketResult xmlns="urn:s3"><IsTruncated>true</IsTruncated>' \
                       b'<NextContinuationToken>next+/=</NextContinuationToken>' \
                       b'<Contents><Key>bench/one</Key></Contents></ListBucketResult>'
            self.reply(body=state.get("list_body", body))
        elif self.command == "GET":
            source = state["payload"]
            start, end = 0, source.size - 1
            response_headers = {}
            status = 200
            if "range" in headers and not state.get("ignore_range"):
                start, end = map(int, headers["range"].removeprefix("bytes=").split("-"))
                response_headers["Content-Range"] = f"bytes {start}-{end}/{state.get('range_total', source.size)}"
                status = 206
            # GET test payloads are small; uploads exercise GB-scale streaming.
            body = b"".join(source.iter_chunks(start, end - start + 1))
            if state.get("corrupt_download"):
                body = bytes([body[0] ^ 1]) + body[1:]
            if state.get("truncate_download"):
                self.send_response(status)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body[:-7])
                self.close_connection = True
            else:
                self.reply(status, body, response_headers)
        else:
            self.reply(204 if self.command == "DELETE" else 200)

    do_GET = do_PUT = do_POST = do_HEAD = do_DELETE = handle_request


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MockS3)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.env = patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "key",
                             "AWS_SECRET_ACCESS_KEY": "secret", "AWS_SESSION_TOKEN": "token"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.state = {"counts": Counter(), "requests": [], "max_read": 0,
                      "payload": s3.SeededPayload("download", 200000), "failures": 1}
        self.server.state = self.state
        self.client = s3.S3Client("bucket", "auto", timeout=2, backoff=0,
                                  endpoint=s3.Endpoint("127.0.0.1", "auto", True,
                                                       self.server.server_port, False))

    def test_put_shapes_auth_and_checksums(self):
        progress = []
        response = self.client.put_object("a//../% +/ሴ", s3.SeededPayload("put", 200000),
                                          on_progress=lambda count, seconds: progress.append((count, seconds)))
        self.assertEqual([count for count, _ in progress], [65536, 131072, 196608, 200000])
        self.assertTrue(all(seconds >= 0 for _, seconds in progress))
        request = self.state["requests"][0]
        self.assertEqual(request["path"], "/bucket/a//../%25%20%2B/%E1%88%B4")
        self.assertEqual(request["headers"]["host"], f"127.0.0.1:{self.server.server_port}")
        self.assertIn("Credential=key/", request["headers"]["authorization"])
        self.assertEqual(request["headers"]["x-amz-security-token"], "token")
        self.assertEqual(response.timing.bytes_sent, 200000)
        self.assertEqual(response.timing.attempts, 1)
        self.assertIsNotNone(response.timing.headers_seconds)
        self.assertEqual(response.body, b"")

    def test_virtual_hosted_request_shape(self):
        self.client.endpoint = s3.Endpoint("localhost", "us-east-1", False,
                                           self.server.server_port, False)
        original = s3.connect_ipv4
        with patch.object(s3, "connect_ipv4", side_effect=lambda address, timeout, source=None:
                          original(("127.0.0.1", address[1]), timeout, source)):
            self.client.put_object("key", s3.SeededPayload("s", 8))
        request = self.state["requests"][0]
        self.assertEqual(request["path"], "/key")
        self.assertEqual(request["headers"]["host"], f"bucket.localhost:{self.server.server_port}")
        self.assertIn("/us-east-1/s3/aws4_request", request["headers"]["authorization"])

    def test_multipart_sequence_etags_checksums_and_completion_xml(self):
        parts = []
        self.client.multipart_upload("multi", s3.SeededPayload("large", 5 * 1024**2 + 99),
                                     part_size=5 * 1024**2, on_part=parts.append)
        requests = self.state["requests"]
        self.assertEqual([r["method"] for r in requests], ["POST", "PUT", "PUT", "POST"])
        self.assertEqual(requests[0]["path"], "/bucket/multi?uploads=")
        self.assertEqual(requests[0]["headers"]["x-amz-checksum-algorithm"], "CRC32")
        self.assertEqual(requests[1]["path"], "/bucket/multi?partNumber=1&uploadId=upload%2B%2F%3D1")
        self.assertIn("partNumber=2", requests[2]["path"])
        self.assertNotIn("x-amz-checksum-crc32", requests[-1]["headers"])
        root = ET.fromstring(requests[-1]["body"])
        self.assertEqual([part.findtext("PartNumber") for part in root], ["1", "2"])
        self.assertEqual([part.findtext("ETag") for part in root], ['"part-etag"'] * 2)
        self.assertEqual([part.findtext("ChecksumCRC32") for part in root],
                         [r["crc32"] for r in requests[1:3]])
        self.assertEqual(len(parts), 2)
        self.assertTrue(all(part.timing.attempts == 1 for part in parts))

    def test_checksum_rejection_is_typed_and_aborts_without_retry(self):
        self.state["reject_digest"] = True
        with self.assertRaises(s3.ChecksumError) as caught:
            self.client.multipart_upload("bad", s3.SeededPayload("x", 1000))
        self.assertEqual(caught.exception.code, "InvalidDigest")
        self.assertEqual(caught.exception.status, 400)
        self.assertEqual(caught.exception.timing.attempts, 1)
        self.assertEqual([r["method"] for r in self.state["requests"]], ["POST", "PUT", "DELETE"])
        self.assertIn("uploadId=", self.state["requests"][-1]["path"])

    def test_returned_checksum_mismatch_is_typed(self):
        self.state["bad_returned_crc"] = True
        with self.assertRaises(s3.ChecksumError):
            self.client.put_object("key", s3.SeededPayload("x", 123))

    def test_missing_etag_aborts(self):
        self.state["missing_etag"] = True
        with self.assertRaisesRegex(s3.ProtocolError, "ETag"):
            self.client.multipart_upload("key", s3.SeededPayload("x", 123))
        self.assertEqual(self.state["counts"]["DELETE"], 1)

    def test_complete_http_200_error_aborts(self):
        self.state["complete_error"] = True
        with self.assertRaises(s3.ServiceError) as caught:
            self.client.multipart_upload("key", s3.SeededPayload("x", 123))
        self.assertEqual(caught.exception.code, "InvalidPart")
        self.assertEqual(caught.exception.status, 200)
        self.assertEqual(self.state["counts"]["DELETE"], 1)

    def test_invalid_completion_success_aborts(self):
        for body in (b"", b"<Unexpected/>", b"<CompleteMultipartUploadResult/>"):
            with self.subTest(body=body):
                self.state["complete_body"] = body
                before = self.state["counts"]["DELETE"]
                with self.assertRaises(s3.ProtocolError):
                    self.client.multipart_upload("key", s3.SeededPayload("x", 123))
                self.assertEqual(self.state["counts"]["DELETE"] - before, 1)

    def test_completion_checksum_is_compared_to_parts(self):
        source = s3.SeededPayload("x", 123)
        part_crc = base64.b64decode(s3.checksum_headers(source.iter_chunks())["x-amz-checksum-crc32"])
        composite = base64.b64encode(zlib.crc32(part_crc).to_bytes(4, "big")) + b"-1"
        for checksum in (composite, b"AAAAAA==-1"):
            self.state["complete_body"] = (b"<CompleteMultipartUploadResult><ETag>done</ETag>"
                                           b"<ChecksumCRC32>" + checksum + b"</ChecksumCRC32>"
                                           b"</CompleteMultipartUploadResult>")
            if checksum == composite:
                self.client.multipart_upload("key", source)
            else:
                with self.assertRaises(s3.ChecksumError):
                    self.client.multipart_upload("key", source)

    def test_abort_failure_preserves_primary_error(self):
        self.state.update(reject_digest=True, fail_method="DELETE", failures=10)
        with self.assertRaises(s3.ChecksumError) as caught:
            self.client.multipart_upload("key", s3.SeededPayload("x", 123))
        self.assertIsInstance(caught.exception.cleanup_error, s3.ServiceError)
        self.assertEqual(self.state["counts"]["DELETE"], 3)

    def test_range_get_streams_verifies_offsets_and_timing(self):
        chunks = []
        response = self.client.get_object("key", byte_range=(65000, 140000),
                                          payload=self.state["payload"],
                                          consume=lambda data, offset: chunks.append((data, offset)))
        self.assertEqual(response.status, 206)
        self.assertEqual(response.body, b"")
        self.assertEqual(chunks[0][1], 65000)
        self.assertTrue(all(len(data) <= 65536 for data, _ in chunks))
        self.assertEqual(b"".join(data for data, _ in chunks),
                         b"".join(self.state["payload"].iter_chunks(65000, 75001)))
        self.assertEqual(response.timing.bytes_received, 75001)
        self.assertLessEqual(response.timing.headers_seconds, response.timing.first_byte_seconds)
        self.assertLessEqual(response.timing.first_byte_seconds, response.timing.elapsed_seconds)

    def test_full_get_and_download_corruption(self):
        result = self.client.get_object("key", payload=self.state["payload"])
        self.assertEqual(result.timing.bytes_received, self.state["payload"].size)
        self.state["corrupt_download"] = True
        with self.assertRaises(s3.VerificationError) as caught:
            self.client.get_object("key", payload=self.state["payload"])
        self.assertEqual(caught.exception.timing.attempts, 1)

    def test_ignored_range_and_truncated_get_are_protocol_errors(self):
        self.state["ignore_range"] = True
        with self.assertRaises(s3.ProtocolError):
            self.client.get_object("key", byte_range=(2, 30))
        self.state["ignore_range"] = False
        self.state["truncate_download"] = True
        with self.assertRaises(s3.ProtocolError):
            self.client.get_object("key", payload=self.state["payload"])

    def test_measurement_put_and_get_never_retry_5xx(self):
        for method in ("PUT", "GET"):
            with self.subTest(method=method):
                self.state.update(fail_method=method, failures=1)
                before = self.state["counts"][method]
                with self.assertRaises(s3.ServiceError) as caught:
                    if method == "PUT":
                        self.client.put_object("key", s3.SeededPayload("x", 123))
                    else:
                        self.client.get_object("key", byte_range=(0, 9))
                self.assertEqual(caught.exception.status, 503)
                self.assertEqual(caught.exception.timing.attempts, 1)
                self.assertEqual(self.state["counts"][method] - before, 1)

    def test_measurement_connection_failures_never_retry(self):
        for method in ("PUT", "GET"):
            with self.subTest(method=method):
                self.state["disconnect"] = method
                with self.assertRaises(s3.TransportError) as caught:
                    if method == "PUT":
                        self.client.put_object("key", s3.SeededPayload("x", 123))
                    else:
                        self.client.get_object("key", byte_range=(0, 9))
                self.assertEqual(caught.exception.timing.attempts, 1)
                self.assertEqual(self.state["counts"][method], 1)

    def test_range_total_must_match_source(self):
        for total in (9, self.state["payload"].size + 1):
            with self.subTest(total=total):
                self.state["range_total"] = total
                with self.assertRaises(s3.ProtocolError):
                    self.client.get_object("key", byte_range=(0, 9), payload=self.state["payload"])

    def test_control_retry_and_head_measurement_opt_out(self):
        self.state.update(fail_method="HEAD", failures=1)
        response = self.client.head_object("key")
        self.assertEqual(response.timing.attempts, 2)
        self.assertEqual(self.state["counts"]["HEAD"], 2)
        self.state["failures"] = 1
        with self.assertRaises(s3.ServiceError):
            self.client.head_object("key", measurement=True)
        self.assertEqual(self.state["counts"]["HEAD"], 3)

    def test_control_connection_retry_is_bounded(self):
        self.state["disconnect"] = "HEAD"
        with self.assertRaises(s3.TransportError) as caught:
            self.client.head_object("key")
        self.assertEqual(caught.exception.timing.attempts, 3)
        self.assertEqual(self.state["counts"]["HEAD"], 3)

    def test_paginated_list_cleanup_is_prefix_scoped(self):
        self.client.cleanup_prefix("bench/")
        paths = [request["path"] for request in self.state["requests"]]
        self.assertIn("list-type=2&prefix=bench%2F", paths[0])
        self.assertIn("/bucket/bench/one", paths)
        self.assertIn("/bucket/bench/two", paths)
        self.assertTrue(any("continuation-token=next%2B%2F%3D" in path for path in paths))
        self.assertEqual(self.state["counts"]["DELETE"], 2)
        with self.assertRaises(ValueError):
            self.client.cleanup_prefix("")

    def test_malformed_list_does_not_report_successful_cleanup(self):
        for body in (b"<Unexpected/>", b"<ListBucketResult/>",
                     b"<ListBucketResult><IsTruncated>maybe</IsTruncated></ListBucketResult>",
                     b"<ListBucketResult><IsTruncated>true</IsTruncated></ListBucketResult>",
                     b"<ListBucketResult><IsTruncated>false</IsTruncated>"
                     b"<Contents><Key>outside/prefix</Key></Contents></ListBucketResult>"):
            with self.subTest(body=body):
                self.state["list_body"] = body
                with self.assertRaises(s3.ProtocolError):
                    self.client.cleanup_prefix("bench/")
        self.assertEqual(self.state["counts"]["DELETE"], 0)

    def test_gib_source_upload_uses_bounded_reads_and_memory(self):
        # Source is GB-scale; transfer a 32 MiB part near its end. Both hashing
        # and socket send see <=64 KiB chunks, not a 32 MiB or 2 GiB allocation.
        source = s3.SeededPayload("gib", 2 * 1024**3)
        tracemalloc.start()
        try:
            response = self.client.upload_part("large", "id", 1, source,
                                               source.size - 32 * 1024**2, 32 * 1024**2)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(response.timing.bytes_sent, 32 * 1024**2)
        self.assertLessEqual(self.state["max_read"], 8192)
        self.assertLess(peak, 4 * 1024**2)


if __name__ == "__main__":
    unittest.main()
