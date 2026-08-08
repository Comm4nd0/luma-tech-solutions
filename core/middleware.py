"""Request/response middleware: canonical host, then Content Security Policy.

A nonce-based CSP is the defense-in-depth backstop behind nh3 sanitisation of
blog content: even if unsanitised HTML reached a page, an injected
``<script>`` would lack the per-request nonce and the browser would refuse to
run it. The nonce is exposed to templates as ``request.csp_nonce`` — every
first-party inline/external ``<script>`` tag carries
``nonce="{{ request.csp_nonce }}"``.

``'strict-dynamic'`` lets a nonce-trusted script (e.g. cookie-consent.js)
load further scripts it needs — Google Tag, reCAPTCHA — without us having to
enumerate every Google host. Modern browsers honour the nonce + strict-dynamic
and ignore the host allowlist / ``'unsafe-inline'``; older browsers ignore the
nonce and fall back to those, so the page keeps working everywhere.
"""
from __future__ import annotations

import secrets

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """301 ``www.example.com`` → ``example.com``.

    Caddy serves both hostnames from one site block, so without this every
    page exists twice with a 200. Google folds the pair using our
    ``<link rel="canonical">`` (which always points at ``SITE_URL``) and files
    the www copy under "Alternative page with proper canonical tag" — nothing
    is lost, but every www URL is crawled and then discarded. A 301 spends the
    crawl budget once instead.

    Belt and braces with the ``redir`` block in the server's Caddyfile: this
    one ships through the normal deploy, so the site is right even if the
    proxy config drifts. Runs ahead of WhiteNoise so static-file URLs redirect
    too, and ahead of CommonMiddleware so a www request for a slash-less path
    makes one hop here rather than two.

    Set ``DJANGO_REDIRECT_WWW=0`` to disable (e.g. if the apex ever stops
    being the canonical host).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "REDIRECT_WWW_TO_APEX", True):
            # get_host() is already validated against ALLOWED_HOSTS, so the
            # host we echo into Location can't be attacker-controlled.
            host = request.get_host()
            if host.lower().startswith("www."):
                return HttpResponsePermanentRedirect(
                    f"{request.scheme}://{host[4:]}{request.get_full_path()}"
                )
        return self.get_response(request)


def _build_policy(nonce: str) -> str:
    script_src = (
        f"'nonce-{nonce}' 'strict-dynamic' https: 'unsafe-inline'"
    )
    # script-src is the strict part (nonce + strict-dynamic) — that's the XSS
    # defense. The non-script directives stay permissive over https: because
    # they aren't meaningful injection vectors and the site pulls styles,
    # fonts, images and tiles from a few third parties (Leaflet/unpkg,
    # CARTO tiles, Google reCAPTCHA, Plausible).
    directives = [
        "default-src 'self'",
        f"script-src {script_src}",
        "style-src 'self' 'unsafe-inline' https:",
        "img-src 'self' data: https:",
        "font-src 'self' https: data:",
        "connect-src 'self' https:",
        "frame-src https:",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'self'",
    ]
    return "; ".join(directives)


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = secrets.token_urlsafe(16)
        request.csp_nonce = nonce
        response = self.get_response(request)
        header = (
            "Content-Security-Policy-Report-Only"
            if getattr(settings, "CSP_REPORT_ONLY", False)
            else "Content-Security-Policy"
        )
        # Don't clobber a policy a view set deliberately.
        if "Content-Security-Policy" not in response and header not in response:
            response[header] = _build_policy(nonce)
        return response
