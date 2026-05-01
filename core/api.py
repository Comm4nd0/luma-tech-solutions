"""JSON API for programmatic blog publishing.

Single-client API authenticated by a shared Bearer key from
``LUMA_BLOG_API_KEY``. Vanilla Django views (no DRF) to keep the dependency
footprint small.

Endpoints
---------
GET    /api/blog/posts/         list (paginated, includes drafts)
POST   /api/blog/posts/         create
GET    /api/blog/posts/<slug>/  fetch one
PUT    /api/blog/posts/<slug>/  full replace (acts as upsert)
PATCH  /api/blog/posts/<slug>/  partial update
DELETE /api/blog/posts/<slug>/  delete
"""
from __future__ import annotations

import hmac
import json
import logging
from functools import wraps
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import PILLAR_CHOICES, BlogPost

log = logging.getLogger(__name__)

WRITABLE_FIELDS = {
    "title",
    "slug",
    "content",
    "excerpt",
    "author",
    "pillar",
    "meta_description",
    "published_at",
}

PILLAR_KEYS = {key for key, _ in PILLAR_CHOICES}


def _json_error(message: str, status: int, **extra: Any) -> JsonResponse:
    body: dict[str, Any] = {"detail": message}
    body.update(extra)
    return JsonResponse(body, status=status)


def _check_auth(request: HttpRequest) -> JsonResponse | None:
    expected = getattr(settings, "LUMA_BLOG_API_KEY", "") or ""
    if not expected:
        return _json_error(
            "Server has no API key configured (set LUMA_BLOG_API_KEY).",
            503,
        )
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.startswith("Bearer "):
        return _json_error("auth required", 401)
    presented = header[len("Bearer "):].strip()
    if not hmac.compare_digest(presented, expected):
        return _json_error("auth required", 401)
    return None


def require_api_key(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        err = _check_auth(request)
        if err is not None:
            return err
        return view(request, *args, **kwargs)

    return wrapped


def _serialize(post: BlogPost) -> dict[str, Any]:
    return {
        "id": post.pk,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "excerpt": post.excerpt,
        "author": post.author,
        "pillar": post.pillar,
        "pillar_display": post.get_pillar_display(),
        "meta_description": post.meta_description,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
        "is_published": post.is_published,
        "absolute_url": post.get_absolute_url(),
    }


def _parse_body(request: HttpRequest) -> tuple[dict[str, Any] | None, JsonResponse | None]:
    if not request.body:
        return {}, None
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, _json_error(f"invalid JSON: {exc}", 400)
    if not isinstance(data, dict):
        return None, _json_error("body must be a JSON object", 400)
    return data, None


def _apply_fields(
    post: BlogPost, data: dict[str, Any], *, partial: bool
) -> JsonResponse | None:
    """Mutate ``post`` from request data. Returns an error response or None."""
    unknown = set(data) - WRITABLE_FIELDS
    if unknown:
        return _json_error(
            f"unknown field(s): {sorted(unknown)}",
            400,
        )

    if "pillar" in data and data["pillar"] not in PILLAR_KEYS:
        return _json_error(
            f"pillar must be one of {sorted(PILLAR_KEYS)}",
            400,
            field="pillar",
        )

    if "published_at" in data:
        raw = data["published_at"]
        if raw is None:
            data["published_at"] = None
        elif isinstance(raw, str):
            parsed = parse_datetime(raw)
            if parsed is None:
                return _json_error(
                    "published_at must be ISO 8601 datetime or null",
                    400,
                    field="published_at",
                )
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
            data["published_at"] = parsed
        else:
            return _json_error(
                "published_at must be ISO 8601 datetime or null",
                400,
                field="published_at",
            )

    for field, value in data.items():
        setattr(post, field, value)

    if not post.slug and post.title:
        post.slug = slugify(post.title)[:260]

    if not partial:
        missing = [
            f for f in ("title", "content", "excerpt") if not getattr(post, f, "")
        ]
        if missing:
            return _json_error(
                f"missing required field(s): {missing}",
                400,
            )

    try:
        post.full_clean()
    except ValidationError as exc:
        return _json_error("validation failed", 400, errors=exc.message_dict)
    return None


@csrf_exempt
@require_http_methods(["GET", "POST"])
@require_api_key
def posts_collection(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        try:
            page_size = min(max(int(request.GET.get("page_size", 20)), 1), 100)
        except (TypeError, ValueError):
            page_size = 20
        qs = BlogPost.objects.all().order_by("-updated_at")

        pillar = request.GET.get("pillar")
        if pillar:
            qs = qs.filter(pillar=pillar)

        status = request.GET.get("status")
        if status in {"draft", "scheduled", "published"}:
            now = timezone.now()
            if status == "draft":
                qs = qs.filter(published_at__isnull=True)
            elif status == "scheduled":
                qs = qs.filter(published_at__gt=now)
            else:
                qs = qs.filter(published_at__lte=now)

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(request.GET.get("page", 1))
        return JsonResponse(
            {
                "count": paginator.count,
                "page": page_obj.number,
                "page_size": page_size,
                "num_pages": paginator.num_pages,
                "results": [_serialize(p) for p in page_obj.object_list],
            }
        )

    # POST -- create
    data, err = _parse_body(request)
    if err is not None:
        return err
    assert data is not None

    declared_slug = data.get("slug")
    if declared_slug and BlogPost.objects.filter(slug=declared_slug).exists():
        return _json_error("post with this slug already exists", 409, field="slug")

    post = BlogPost()
    err = _apply_fields(post, data, partial=False)
    if err is not None:
        return err
    try:
        post.save()
    except Exception as exc:
        log.exception("failed to create blog post")
        return _json_error(f"could not create post: {exc}", 400)
    return JsonResponse(_serialize(post), status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
@require_api_key
def post_detail(request: HttpRequest, slug: str) -> HttpResponse:
    if request.method == "GET":
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            return _json_error("post not found", 404)
        return JsonResponse(_serialize(post))

    if request.method == "DELETE":
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            return _json_error("post not found", 404)
        post.delete()
        return HttpResponse(status=204)

    data, err = _parse_body(request)
    if err is not None:
        return err
    assert data is not None

    if request.method == "PUT":
        body_slug = data.get("slug")
        if body_slug and body_slug != slug:
            return _json_error("slug in body must match URL", 400, field="slug")
        data["slug"] = slug
        post = BlogPost.objects.filter(slug=slug).first()
        created = False
        if post is None:
            post = BlogPost()
            created = True
        err = _apply_fields(post, data, partial=False)
        if err is not None:
            return err
        try:
            post.save()
        except Exception as exc:
            log.exception("failed to upsert blog post slug=%s", slug)
            return _json_error(f"could not save post: {exc}", 400)
        return JsonResponse(_serialize(post), status=201 if created else 200)

    # PATCH -- partial update on existing post
    post = BlogPost.objects.filter(slug=slug).first()
    if post is None:
        return _json_error("post not found", 404)
    if "slug" in data and data["slug"] and data["slug"] != slug:
        return _json_error(
            "slug cannot be changed via PATCH (delete + recreate instead)",
            400,
            field="slug",
        )
    err = _apply_fields(post, data, partial=True)
    if err is not None:
        return err
    try:
        post.save()
    except Exception as exc:
        log.exception("failed to patch blog post slug=%s", slug)
        return _json_error(f"could not save post: {exc}", 400)
    return JsonResponse(_serialize(post))
