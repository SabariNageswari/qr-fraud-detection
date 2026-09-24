import ssl
import socket
import time
import certifi
from urllib.parse import urlparse


def check_ssl_certificate(url: str) -> dict:
    """
    Checks HTTPS and SSL/TLS certificate validity.
    """

    parsed = urlparse(url)
    hostname = parsed.hostname

    # 1. Check HTTPS
    if parsed.scheme.lower() != "https" or not hostname:
        return {
            "uses_https": False,
            "valid_certificate": False,
            "issuer": None,
            "expires_in_days": None,
            "reason": "URL does not use HTTPS"
        }

    try:
        # 2. Use an up-to-date CA certificate bundle
        context = ssl.create_default_context(cafile=certifi.where())

        # 3. Connect to HTTPS server
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # 4. Get certificate issuer
        issuer = "Unknown"
        for item in cert.get("issuer", []):
            for key, value in item:
                if key == "organizationName":
                    issuer = value

        # 5. Get certificate expiry date (locale-independent parsing)
        expiry_str = cert.get("notAfter")

        if not expiry_str:
            return {
                "uses_https": True,
                "valid_certificate": False,
                "issuer": issuer,
                "expires_in_days": None,
                "reason": "Certificate expiry date could not be determined"
            }

        expiry_epoch = ssl.cert_time_to_seconds(expiry_str)
        days_remaining = int((expiry_epoch - time.time()) / 86400)

        # 6. Check expiry
        if days_remaining < 0:
            return {
                "uses_https": True,
                "valid_certificate": False,
                "issuer": issuer,
                "expires_in_days": days_remaining,
                "reason": "Certificate has expired"
            }

        # 7. Certificate is valid
        return {
            "uses_https": True,
            "valid_certificate": True,
            "issuer": issuer,
            "expires_in_days": days_remaining,
            "reason": None
        }

    except ssl.SSLCertVerificationError as e:
        return {
            "uses_https": True,
            "valid_certificate": False,
            "issuer": None,
            "expires_in_days": None,
            "reason": f"SSL certificate verification failed: {e}"
        }

    except (socket.timeout, socket.gaierror, ConnectionRefusedError) as e:
        return {
            "uses_https": True,
            "valid_certificate": None,
            "issuer": None,
            "expires_in_days": None,
            "reason": f"Could not connect to verify certificate: {e}"
        }

    except Exception as e:
        return {
            "uses_https": True,
            "valid_certificate": None,
            "issuer": None,
            "expires_in_days": None,
            "reason": f"Unexpected SSL error: {e}"
        }
