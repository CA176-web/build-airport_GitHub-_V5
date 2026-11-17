"""Generate a pinned, Salamander Hysteria 2 URI offline from a public certificate."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import ssl
import sys
from urllib.parse import quote, urlencode


def dns_name(value):
    return len(value) <= 253 and all(
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
        for label in value.rstrip(".").split(".")
    )


def validate_settings(settings):
    keys = {"host", "external_port", "auth", "sni", "obfs_password", "name"}
    if not isinstance(settings, dict) or set(settings) != keys:
        raise ValueError("Expected exactly the six documented settings fields.")
    for key in keys - {"external_port"}:
        value = settings[key]
        if (not isinstance(value, str) or not value
                or any(ord(c) < 32 or ord(c) == 127 for c in value)):
            raise ValueError("Text fields must be nonempty and contain no controls.")
    port = settings["external_port"]
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("external_port must be an integer from 1 to 65535.")
    host = settings["host"]
    if ":" in host:
        if host.startswith("[") and host.endswith("]"):
            host = host[1:-1]
        if "%" in host:
            raise ValueError("IPv6 zone identifiers are not supported.")
        try:
            host = f"[{ipaddress.IPv6Address(host)}]"
        except ValueError:
            raise ValueError("Invalid IPv6 host.") from None
    elif not dns_name(host):
        raise ValueError("host must be an IP address or ASCII DNS name, without a URL.")
    if not dns_name(settings["sni"]):
        raise ValueError("sni must be an ASCII DNS name matching the certificate.")
    return host


def create_link(settings, certificate):
    host = validate_settings(settings)
    # One public leaf certificate: never accidentally pin a CA bundle or private key.
    if re.findall(r"-----BEGIN [^-]+-----", certificate) != ["-----BEGIN CERTIFICATE-----"]:
        raise ValueError("Provide exactly one PEM public server certificate.")
    ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).load_verify_locations(cadata=certificate)
    der = ssl.PEM_cert_to_DER_cert(certificate)
    pin = hashlib.sha256(der).hexdigest().upper()
    query = urlencode({
        "sni": settings["sni"], "insecure": "1", "pinSHA256": pin,
        "obfs": "salamander", "obfs-password": settings["obfs_password"],
    })
    return (
        f"hysteria2://{quote(settings['auth'], safe='')}@"
        f"{host}:{settings['external_port']}/?{query}"
        f"#{quote(settings['name'], safe='')}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        settings = json.loads(args.settings.read_text(encoding="utf-8-sig"))
        certificate = args.certificate.read_text(encoding="ascii")
        uri = create_link(settings, certificate)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(uri + "\n")
    except (OSError, ValueError, UnicodeError, TypeError):
        print("Cannot create link: check settings, public certificate and output path.", file=sys.stderr)
        return 2
    print("Created link TXT. Connectivity has not been tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
