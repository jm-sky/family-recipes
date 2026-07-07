"""Fetch and extract readable text from recipe web pages."""

from __future__ import annotations

import ipaddress
import logging
import re
import socket
from html import unescape
from urllib.parse import urlparse

import httpx

from app.modules.ai.exceptions import RecipeImportError

logger = logging.getLogger(__name__)

_MAX_BYTES = 512_000
_TIMEOUT_SECONDS = 15.0
_MAX_TEXT_CHARS = 15_000
_USER_AGENT = "FamilyRecipesBot/1.0 (+recipe-import)"

_BLOCKED_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})


def _validate_url(url: str) -> str:
    """Validate URL scheme and host before fetching."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise RecipeImportError("Only http and https URLs are supported")
    if not parsed.netloc:
        raise RecipeImportError("Invalid URL")
    hostname = parsed.hostname
    if not hostname:
        raise RecipeImportError("Invalid URL host")
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise RecipeImportError("URL host is not allowed")
    # Block literal private IPs in the hostname
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise RecipeImportError("URL host is not allowed")
    return url.strip()


def _validate_resolved_ips(hostname: str) -> None:
    """Reject hosts that resolve to private or loopback addresses."""
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise RecipeImportError("Could not resolve URL host") from exc

    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise RecipeImportError("URL host is not allowed")


def html_to_text(html: str) -> str:
    """Strip HTML tags and collapse whitespace for AI consumption."""
    without_scripts = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    text = unescape(without_tags)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:_MAX_TEXT_CHARS]


async def fetch_page_text(url: str) -> tuple[str, str]:
    """Fetch a URL and return (final_url, extracted_text)."""
    validated = _validate_url(url)
    parsed = urlparse(validated)
    if parsed.hostname:
        _validate_resolved_ips(parsed.hostname)

    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        ) as client:
            async with client.stream("GET", validated) as response:
                response.raise_for_status()
                final_url = str(response.url)
                final_host = urlparse(final_url).hostname
                if final_host:
                    _validate_resolved_ips(final_host)

                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > _MAX_BYTES:
                        raise RecipeImportError("Page is too large to import")
                    chunks.append(chunk)
    except httpx.HTTPStatusError as exc:
        raise RecipeImportError(f"Could not fetch page (HTTP {exc.response.status_code})") from exc
    except httpx.RequestError as exc:
        logger.warning("Recipe import fetch failed for %s: %s", validated, exc)
        raise RecipeImportError("Could not fetch page") from exc

    html = b"".join(chunks).decode("utf-8", errors="replace")
    text = html_to_text(html)
    if len(text) < 50:
        raise RecipeImportError("Page does not contain enough readable content")
    return final_url, text
