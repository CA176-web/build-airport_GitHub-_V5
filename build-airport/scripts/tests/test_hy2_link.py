"""Offline CLI tests; fixture is a public synthetic certificate, without its key."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, unquote, urlsplit

SCRIPT = Path(__file__).resolve().parents[1] / "hy2_link.py"
CERT = Path(__file__).parent / "fixtures" / "public-test.crt"
# Recorded independently from cryptography's X.509 fingerprint when creating fixture.
PIN = "267E043CCA08A18B79A3F123094D977A840CC50B40D177F09F8A0E2295E3D5CC"


class LinkCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.settings = {
            "host": "example.com", "external_port": 50001,
            "auth": "a:b@c /?#%", "sni": "hy2-test.invalid",
            "obfs_password": "x&y=+?#% z", "name": "测试 HY2/节点",
        }
        self.output = self.folder / "node_V1.txt"

    def run_cli(self, certificate=CERT):
        settings = self.folder / "private.json"
        settings.write_text(json.dumps(self.settings), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--settings", str(settings),
             "--certificate", str(certificate), "--output", str(self.output)],
            capture_output=True, text=True, encoding="utf-8",
        )

    def test_link_roundtrips_credentials_and_pins_certificate(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        uri = urlsplit(self.output.read_text(encoding="utf-8").strip())
        self.assertEqual(uri.scheme, "hysteria2")
        self.assertEqual((uri.hostname, uri.port), ("example.com", 50001))
        self.assertEqual(unquote(uri.username), self.settings["auth"])
        self.assertIsNone(uri.password)
        self.assertEqual(unquote(uri.fragment), "测试 HY2/节点")
        self.assertEqual(parse_qs(uri.query), {
            "sni": ["hy2-test.invalid"], "insecure": ["1"],
            "pinSHA256": [PIN], "obfs": ["salamander"],
            "obfs-password": [self.settings["obfs_password"]],
        })
        self.assertNotIn(self.settings["auth"], result.stdout + result.stderr)

    def test_ipv6_uses_bracketed_authority(self):
        self.settings["host"] = "2001:db8::1"
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        uri = urlsplit(self.output.read_text(encoding="utf-8").strip())
        self.assertEqual((uri.hostname, uri.port), ("2001:db8::1", 50001))

    def test_rejects_unusable_connection_parameters(self):
        valid = self.settings.copy()
        cases = [
            {"external_port": 0}, {"external_port": 65536},
            {"external_port": True}, {"external_port": "50001"},
            {"host": "https://example.com"}, {"host": "a@example.com"},
            {"host": "example.com/path"}, {"sni": "bad name"},
            {"auth": ""}, {"obfs_password": ""}, {"name": "bad\nname"},
            {"internal_port": 50002},
        ]
        for update in cases:
            with self.subTest(update=update):
                self.settings = valid | update
                result = self.run_cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertNotIn(valid["auth"], result.stdout + result.stderr)

    def test_rejects_pem_wrapped_non_certificate(self):
        fake = self.folder / "fake.crt"
        fake.write_text("-----BEGIN CERTIFICATE-----\nMTIz\n-----END CERTIFICATE-----\n", encoding="ascii")
        result = self.run_cli(fake)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())

    def test_existing_delivery_is_preserved(self):
        original = b"previous-delivery-do-not-replace\n"
        self.output.write_bytes(original)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
