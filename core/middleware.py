"""Content Security Policy middleware.

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
