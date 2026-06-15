# Luma Tech Solutions — repo guide

The marketing website for **lumatechsolutions.co.uk**. Server-rendered Django 5
application running in a Docker container, fronted by the shared Caddy
reverse-proxy on the Hetzner box.

## Layout

```
.
├── manage.py
├── requirements.txt           # Django 5.2 LTS, gunicorn, whitenoise, nh3
├── Dockerfile                 # python:3.12-slim → gunicorn on :8000
├── docker-compose.yml         # publishes host port 8005
├── lumatech/                  # Django project (settings, urls, wsgi/asgi)
├── core/                      # the only app — views, forms, models, sitemaps
├── templates/                 # all HTML templates (base, pages, partials/, services/)
├── static/                    # css, js, img, fonts — collected to /staticfiles by collectstatic
└── data/                      # sqlite DB + uploaded media (gitignored, mounted as volume)
```

## Architecture

- **One app, `core`**, holds every view (one function per page) plus the contact-form
  model, form, and sitemap. PILLARS, TESTIMONIALS, CARE_PLANS and CASE_STUDIES live
  as module-level constants in `core/views.py` — moving any of them to the database
  is the right call the moment they need to be edited by a non-developer.
- **Server-rendered templates** under `templates/` extend `base.html`. The base
  template owns the nav, footer, OG/SEO meta and global stylesheet.
- **Custom CSS** at `static/css/site.css` — no Tailwind, no build step. Dark/light
  theme: `--bg #0f172a`, `--accent #14b8a6`, self-hosted Inter variable font
  (`static/fonts/inter-latin-variable.woff2` — no Google Fonts request).
- **Static files** are served by WhiteNoise via gunicorn — no separate nginx layer
  in the Docker image. Caddy in front handles TLS.

### Security & front-end gotchas

- **CSP nonce — every `<script>` you add to a template MUST carry
  `nonce="{{ request.csp_nonce }}"`.** `core/middleware.py` emits a nonce-based
  Content Security Policy (`script-src 'nonce-…' 'strict-dynamic'`); an
  un-nonced inline or external script (including `application/ld+json` blocks)
  is blocked by the browser. `500.html` is the exception — it renders without a
  request context, so keep it script-free. Set `DJANGO_CSP_REPORT_ONLY=1` while
  trialling a new third-party script.
- **Blog HTML is sanitised with nh3** in `BlogPost.save()`
  (`core.models.sanitize_blog_html`). Tags/attributes outside the allowlist are
  stripped, so `{{ post.content|safe }}` is safe. Widen `ALLOWED_HTML_TAGS` /
  `ALLOWED_HTML_ATTRS` if a post legitimately needs new markup.
- **Marketing scripts are consent-gated.** Google Ads (`gtag.js`) is only loaded
  by `static/js/cookie-consent.js` after the visitor opts into "marketing".
  The `<head>` shim just queues events into the dataLayer (no cookies/network).
  Any new advertising/remarketing tag must be wired into `loadGoogleAds()` /
  `applyConsent()` the same way, and the banner copy in
  `templates/partials/_cookie_consent.html` kept truthful.
- **`DJANGO_SECRET_KEY` is mandatory in production** — settings raises
  `ImproperlyConfigured` (and `docker compose` refuses to start) if it's unset
  or left at an insecure default while `DJANGO_DEBUG=0`.
- **CVs** uploaded via `/careers/` are stored under `MEDIA_ROOT` (the data
  volume), never under `STATIC_ROOT`, and are downloaded through a staff-only
  admin view — they are not publicly served.

## Running locally

```sh
pip install -r requirements.txt
mkdir -p data
DJANGO_DEBUG=1 DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 python manage.py migrate
DJANGO_DEBUG=1 DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 python manage.py runserver 8005
```

Or via Docker:

```sh
docker compose up -d --build       # http://localhost:8005
```

## Server (Hetzner: Luma001 — 178.104.29.66)

- Project lives at `/root/luma-tech-solutions/` on the server.
- Container name: `luma-tech-solutions-web` (host port **`8005`**).
- Reachable from Caddy via `172.17.0.1:8005` (host bridge gateway).
- Sqlite DB persists in the `luma-data` Docker volume.

## Caddy reverse-proxy

Caddy runs as a separate Docker container (`caddy-caddy-1`) and owns ports 80/443
for **every** site on this server. Its config lives at `/root/caddy/Caddyfile`.

Update the existing block (was `:8004`, change to `:8005`) when this app
replaces the static holding page:

```caddyfile
lumatechsolutions.co.uk, www.lumatechsolutions.co.uk {
    reverse_proxy 172.17.0.1:8005
    encode gzip
}
```

Reload after editing:

```sh
docker exec caddy-caddy-1 caddy validate --config /etc/caddy/Caddyfile
docker exec caddy-caddy-1 caddy reload  --config /etc/caddy/Caddyfile
```

Caddy handles TLS automatically via Let's Encrypt — no manual cert work needed
as long as DNS A records point to **178.104.29.66**.

## Host-port allocation on Luma001

| Port | Service                 |
|------|-------------------------|
| 8000 | paws4thoughtdogs        |
| 8001 | oakwood-climbing-gym    |
| 8002 | for-sale-by-owner       |
| 8003 | uvl-frontend            |
| 8004 | (was: luma static holding page — retired) |
| 8005 | **luma-tech-solutions** (Django) |

Pick the next free port for any new site.

## Deploy workflow

```sh
cd /root/luma-tech-solutions
git pull
docker compose up -d --build
```

The container runs `python manage.py migrate --noinput` on every start, so
new migrations apply automatically.

## Environment

Production env vars are configured via the compose file (or the surrounding
shell). Required in production:

- `DJANGO_SECRET_KEY` (generate a fresh random string)
- `DJANGO_DEBUG=0` (default if not set)
- `DJANGO_ALLOWED_HOSTS=lumatechsolutions.co.uk,www.lumatechsolutions.co.uk`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://lumatechsolutions.co.uk,https://www.lumatechsolutions.co.uk`
- `SITE_URL=https://lumatechsolutions.co.uk`

For the contact form to send real emails (otherwise it logs to the container
stdout via the console backend):

- `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`
- `CONTACT_FORM_RECIPIENT`
- `CAREERS_FORM_RECIPIENT` — optional. Where `/careers/` job applications
  are emailed to. Falls back to `CONTACT_FORM_RECIPIENT` when unset.

For programmatic blog publishing via the JSON API:

- `LUMA_BLOG_API_KEY` — shared Bearer token (any random ≥32 chars). The
  endpoint returns **503** if this is unset, so prod misconfig is loud.
  Generate one with `python -c "import secrets; print(secrets.token_urlsafe(40))"`.

## Blog API

JSON API for an automation to publish/update blog posts. All endpoints
require `Authorization: Bearer $LUMA_BLOG_API_KEY`.

| Method | Path                       | Action                                  |
|--------|----------------------------|-----------------------------------------|
| GET    | `/api/blog/posts/`         | List (paginated; `?status=draft|scheduled|published`, `?pillar=`) |
| POST   | `/api/blog/posts/`         | Create — 201 with full record, 409 on slug conflict |
| GET    | `/api/blog/posts/<slug>/`  | Fetch one (drafts included)             |
| PUT    | `/api/blog/posts/<slug>/`  | Full replace; creates if absent (upsert)|
| PATCH  | `/api/blog/posts/<slug>/`  | Partial update                          |
| DELETE | `/api/blog/posts/<slug>/`  | Delete — 204                            |

Body fields: `title`, `content` (HTML), `excerpt`, `slug` (optional, derived
from title), `author` (optional), `pillar` (one of: `networking`, `security`,
`development`, `automation`, `support`, `general`), `meta_description`
(optional, falls back to excerpt), `published_at` (ISO 8601 — null/omitted
keeps as draft, future date schedules, past/now publishes).

Publishing model:

- **Draft**: `published_at: null` → not on `/blog/`, not in sitemap, not in RSS.
- **Scheduled**: `published_at` in the future → flips live automatically when due.
- **Live**: `published_at` past/now → visible everywhere.

### SEO requirements for blog articles

Every blog article **must** be optimised for search engines:

- **Title** — include the primary keyword naturally; keep under 60 characters
  where possible so it doesn't truncate in SERPs.
- **`meta_description`** — a compelling 150–160 character summary containing
  the target keyword. This is the snippet Google shows.
- **`excerpt`** — short, keyword-rich summary used on the blog listing page.
- **Heading structure** — one `<h1>` (handled by the template from the title),
  then `<h2>` for major sections and `<h3>` for sub-sections. Include
  keywords in at least one or two `<h2>` headings.
- **Image alt text** — every `<img>` must have a descriptive `alt` attribute
  that includes relevant keywords where natural.
- **Internal links** — link to relevant service pages (`/services/…`) and
  other blog posts where it adds value. Use descriptive anchor text, not
  "click here".
- **Local keywords** — reference Marlow, Maidenhead, Henley, Thames Valley,
  Berkshire or Buckinghamshire where natural to strengthen local SEO.
- **Readability** — short paragraphs (2–4 sentences), bullet lists to break
  up dense content, and a conversational tone. Google rewards content that
  keeps readers on the page.

Example — create and publish:

```sh
curl -s -X POST https://lumatechsolutions.co.uk/api/blog/posts/ \
  -H "Authorization: Bearer $LUMA_BLOG_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Why home Wi-Fi fails (and how we fix it)",
    "content": "<p>HTML body…</p>",
    "excerpt": "Three reasons most home Wi-Fi underperforms.",
    "pillar": "networking",
    "published_at": "2026-05-02T09:00:00+01:00"
  }'
```

## Health & smoke-test

```sh
curl -sI http://127.0.0.1:8005/healthz       # 200 OK "ok"
curl -sI https://lumatechsolutions.co.uk/    # from anywhere once DNS + Caddy are pointed at 8005
```

## DNS

A records (apex + `www`) must point to **178.104.29.66**. Until they do,
Caddy will keep retrying ACME with backoff — the site will simply have no
HTTPS until DNS propagates.

## History: the old holding page

The site used to be a static-nginx holding page on port 8004 (files in
`public/`, plus `nginx.conf`). That cut-over is complete and those legacy
files have been removed from the tree — the Django app on **8005** is the
only thing deployed. If Caddy ever still points at `172.17.0.1:8004`, change
it to `172.17.0.1:8005` and `docker exec caddy-caddy-1 caddy reload
--config /etc/caddy/Caddyfile`.
