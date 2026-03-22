"""SSRF prevention: block requests to private/internal IPs and metadata endpoints."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "metadata.google.internal",
        "169.254.169.254",
    }
)

ALLOWED_SCHEMES = frozenset({"http", "https"})


def validate_url(url: str) -> bool:
    """Validate URL is safe for server-side requests.

    Returns False for private IPs, loopback, link-local, metadata endpoints,
    and non-HTTP(S) schemes.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    if hostname in BLOCKED_HOSTS:
        return False

    if parsed.scheme not in ALLOWED_SCHEMES:
        return False

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        pass  # hostname is a domain name, not an IP — OK

    return True
