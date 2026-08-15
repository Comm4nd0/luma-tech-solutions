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
├── .github/workflows/         # ci.yml (tests on every push) + deploy.yml (auto-deploy on main)
├── lumatech/                  # Django project (settings, urls, wsgi/asgi)
├── core/                      # the only app — views, content, forms, models, api, feeds, sitemaps, checks, tests/
├── templates/                 # all HTML (base, pages, partials/, services/, areas/, portfolio/, blog/, showcase/)
├── static/                    # css, js, img, fonts — collected to /staticfiles by collectstatic
└── data/                      # sqlite DB + uploaded media (gitignored, mounted as volume)
```

## Architecture

- **One app, `core`**, holds the views, the models (`ContactSubmission`,
  `JobApplication`, `QuoteRequest`, `BlogPost`), forms, the blog JSON API
  (`core/api.py`), RSS feed (`core/feeds.py`), sitemaps and the CSP middleware.
- **Marketing content lives in `core/content.py`**, not in views: PILLARS,
  TESTIMONIALS, `CARE_TIERS` + `CARE_PLAN_AUDIENCES` (merged by
  `care_plans(audience)`), CASE_STUDIES, WEBSITE_DEMOS, the FAQS_* blocks,
  JOB_ROLES, plus the `SERVICE_PAGES` / `AREA_PAGES` / `THANKS_PAGES` tables
  that drive the repetitive pages. Moving any of it to the database is the
  right call the moment a non-developer needs to edit it.
  **`core/content.py` must stay pure data** — no Django imports, no
  `reverse()`, no models. `core.urls` imports `core.views` which imports it,
  and `core.sitemaps` imports it directly; a module-level `reverse()` raises
  `AppRegistryNotReady`. Store URL *names* and reverse them in the view.
- **The service, area and thanks pages are data-driven**: `_render_service_page`,
  `_render_area_page` and `_render_thanks_page` in `core/views.py` render from
  those tables. `core/urls.py` still names every route individually, so
  `{% url %}`, `reverse()` and the sitemap are unaffected. Watch out for the
  non-uniform bits: `service_security` sits in its own `"security"` nav slot,
  and three service pages deliberately have no FAQs (adding a default would
  give them a FAQ section and a `FAQPage` JSON-LD node they've never had).
- **Pages**: home, services overview + service pages (networking, security hub
  + its cctv / access-control / alarms children, ai-cameras, development,
  automation, support), a **construction lead-gen funnel**
  (`/construction/` + capability statement), a **quote funnel**
  (`/quote/`, backed by `QuoteRequest`), local-SEO area pages (`/areas/` —
  Marlow, Maidenhead, Henley, Beaconsfield, High Wycombe), portfolio + case-study details,
  live website demos under `/showcase/<slug>/`, blog (+ RSS at `/blog/feed/`),
  about, careers, contact, camera-privacy, terms, privacy. See `core/urls.py`
  for the full map.
- **Server-rendered templates** under `templates/` extend `base.html`. The base
  template owns the nav, footer, OG/SEO meta, sticky mobile CTA bar,
  WhatsApp/call floating buttons and global stylesheet. Site-wide contact/brand
  values come from `core/context_processors.py` (`SITE_PHONE`, `SITE_EMAIL`,
  `SITE_WHATSAPP_E164`, …) — never hard-code them in templates.
- **Custom CSS** at `static/css/site.css` — no Tailwind, no build step.
  **Light-first theme** (`--bg #f7f9fc`, `--accent #0d9488`); dark mode via
  `[data-theme="dark"]` on `<html>`, toggled by `static/js/site.js` and
  persisted in localStorage as `luma-theme`. Self-hosted Inter variable font
  (`static/fonts/inter-latin-variable.woff2` — no Google Fonts request).
  **Colour tokens are split by contrast role**: `--link` (body links) and
  `--on-accent` (foreground on the accent gradient) meet WCAG AA; `--accent`
  is 3.55:1 and is for gradients, icons and focus rings only, where the bar is
  3:1. Don't point body text at `--accent`.
- **Static files** are served by WhiteNoise via gunicorn — no separate nginx layer
  in the Docker image. Caddy in front handles TLS.

### Local SEO: the search-intent rule

The single rule that governs every page title, H1 and internal anchor:

> **`/areas/<town>/` owns "[service] [town]". `/services/<x>/` owns the
> ungeographic head term. The homepage owns the brand and the region.**

It exists because breaking it cost real rankings: `/services/automation/`
(titled "Smart Home Installer — Marlow, Henley, Maidenhead") sat at position
44 for a query `/areas/henley/` was ranking 15.8 for, and the homepage
("Wi-Fi Installation Marlow, …") outcompeted `/areas/marlow/` into invisibility.

Practical consequences when editing:

- **No `page_title` or `page_description` in `SERVICE_PAGES` may name a town.**
  "the Thames Valley" is fine; counties are fine (no page targets them).
- **Every `page_title` in `AREA_PAGES` names its town**, on the pattern
  "Wi-Fi, CCTV & Smart Home Installation in <Town> | Luma Tech".
- **Area → service anchors are ungeographic** ("CCTV Installation"), built by
  `_area_service_links()`. **Service → area anchors carry the town**
  ("CCTV installation in Marlow"), built by `_area_links()` from each service's
  `area_anchor` format string. Reversing these puts the two page types back
  into competition.
- **H1s live in `AREA_PAGES["…"]["h1_lead"]`**, not in the template, so they
  can't drift from the title.

### Area pages must carry real local copy

`AREA_PAGES` requires four town-specific fields — `local_areas`,
`housing_stock`, `service_emphasis`, `example_jobs`. A page whose only
difference from its neighbours is the town name is a doorway page, and Google
treats it as one.

- A field may hold a `"TODO:"` placeholder while copy is being written.
- `example_jobs` placeholders are **dropped from the render**, so an unwritten
  section never ships. **Never invent a job, client or testimonial to clear
  one.**
- If `local_areas`, `housing_stock` or `service_emphasis` is still `TODO:`,
  `content.area_is_draft()` is true and the page is served **noindex** and
  kept out of `sitemap.xml` — it flips live by itself once the copy lands.
  `example_jobs` is deliberately *not* part of that gate: three area pages
  have been live for months without it, and gating on it would deindex them.
- `manage.py check --deploy` reports every outstanding placeholder
  (`core.W005`), as it does for the missing GBP URL (`core.W006`).

### We are a service-area business

There is no premises a client visits. The `ProfessionalService` JSON-LD
therefore stops at `addressLocality` / `addressRegion` / `addressCountry`
(Marlow, Buckinghamshire, GB) and publishes **no street address, postcode or
geo point**. `SITE_STREET_ADDRESS`, `SITE_POSTAL_CODE` and the two geo
settings exist and the template honours them, but leaving them empty is the
correct configuration, not an outstanding task — Google expects schema to
corroborate the Google Business Profile, and a service-area GBP hides its
address, so publishing one here would contradict it.

Entity disambiguation is carried by `sameAs` instead, which matters because
"Luma Tech Solutions Canada Ltd" (LED lighting, Burnaby BC) outranks this site
for its own brand. `SITE_GOOGLE_BUSINESS_URL` and a Companies House URL in
`SITE_EXTRA_SAME_AS` are the two highest-value entries.

### Sitemap lastmod

`PAGE_LASTMOD` in `core/content.py` carries a per-URL-name date; anything
absent falls back to `settings.SITE_STATIC_LASTMOD`. **Bump the entry for a
page when you change that page**, not the global value — stamping every URL
with one shared date is what teaches Google the field carries no information.

### Security & front-end gotchas

- **CSP nonce — every `<script>` you add to a template MUST carry
  `nonce="{{ request.csp_nonce }}"`.** `core/middleware.py` emits a nonce-based
  Content Security Policy (`script-src 'nonce-…' 'strict-dynamic'`); an
  un-nonced inline or external script (including `application/ld+json` blocks)
  is blocked by the browser. `'strict-dynamic'` lets a nonce-trusted script
  (cookie-consent.js) load its own sub-resources (gtag.js, reCAPTCHA) without
  enumerating Google hosts. `500.html` is the exception — it renders without a
  request context, so keep it script-free. Set `DJANGO_CSP_REPORT_ONLY=1` while
  trialling a new third-party script.
- **All public forms (contact, quote, careers) are protected by reCAPTCHA v3**
  — see `_verify_recaptcha` / `_passes_recaptcha` in `core/views.py`. When
  `RECAPTCHA_SECRET_KEY` is empty (local dev), verification is skipped and the
  forms behave as if reCAPTCHA wasn't there. Submissions below
  `RECAPTCHA_MIN_SCORE` get a generic "couldn't verify" form error.
- **Blog HTML is sanitised with nh3** in `BlogPost.save()`
  (`core.models.sanitize_blog_html`). Tags/attributes outside the allowlist are
  stripped, so `{{ post.content|safe }}` is safe. Widen `ALLOWED_HTML_TAGS` /
  `ALLOWED_HTML_ATTRS` if a post legitimately needs new markup.
- **Marketing scripts are consent-gated.** Google Ads (`gtag.js`,
  `window.LUMA_ADS_ID` in `base.html`) is only loaded by
  `static/js/cookie-consent.js` after the visitor opts into "marketing".
  The `<head>` shim just queues events into the dataLayer (no cookies/network).
  Any new advertising/remarketing tag must be wired into `loadGoogleAds()` /
  `applyConsent()` the same way, and the banner copy in
  `templates/partials/_cookie_consent.html` kept truthful. Plausible
  (cookieless analytics) is *not* consent-gated — it loads from `base.html`
  whenever `PLAUSIBLE_DOMAIN` is set; CTAs carry
  `plausible-event-name=…` classes for goal tracking.
- **Never `cache_page()` an HTML view.** Every page bakes `request.csp_nonce`
  into its inline `<script>` tags and every `application/ld+json` block, and
  the CSP middleware issues a fresh nonce per response — a cached body carries
  a stale nonce and the browser blocks all of it. The test client doesn't
  enforce CSP, so this fails silently. Only `sitemap.xml` and `/blog/feed/`
  are cached (`CACHES` is LocMem; `DummyCache` under test).
- **Emails must not default to the console backend.** `EMAIL_BACKEND` picks
  SMTP whenever `DEBUG` is off. The console backend makes `_notify()` return
  `True` and marks the row `notified=True`, so lead loss is completely silent.
  `core/checks.py` warns at deploy time if it's ever configured in production.
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

## Tests & CI

The test suite lives in `core/tests/` (views, forms, models, API, security
headers, sitemap/feed, construction funnel, plus page contracts, smoke tests,
accessibility, SEO, config checks, reliability and query counts). Run it with:

```sh
DJANGO_DEBUG=1 DJANGO_ALLOWED_HOSTS=localhost,testserver python manage.py test
```

`core/tests/page_contract.json` pins every page's template, `active_nav`,
breadcrumbs, Service-schema keys and FAQ list. **If you deliberately change
one of those, update the fixture in the same commit** — if you didn't mean to,
the failure is the bug. It exists because Django renders a missing context
variable as an empty string, so a dropped context key is otherwise silent.

`.github/workflows/ci.yml` runs on every push/PR: `makemigrations --check`
(fail if a model change lacks a migration), the full test suite, and
`manage.py check --deploy`. Keep all three green. `deploy.yml` runs the same
job and gates the deploy on it, so a red suite no longer ships.

## Server (Hetzner: Luma001 — 178.104.29.66)

- Project lives at `/root/luma-tech-solutions/` on the server.
- Container name: `luma-tech-solutions-web` (host port **`8005`**).
- Reachable from Caddy via `172.17.0.1:8005` (host bridge gateway).
- Sqlite DB persists in the `luma-data` Docker volume.

## Caddy reverse-proxy

Caddy runs as a separate Docker container (`caddy-caddy-1`) and owns ports 80/443
for **every** site on this server. Its config lives at `/root/caddy/Caddyfile`:

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

**Deploys are automatic**: every push to `main` triggers
`.github/workflows/deploy.yml`, which first runs the full test suite (the
deploy job `needs:` it), backs up the sqlite database to
`/root/backups/luma-tech-solutions/`, SSHes into Luma001, runs
`git pull --ff-only && docker compose up -d --build`, then smoke-tests six
paths. On failure it rolls the code back to the previous revision; it does
*not* restore the database automatically, since leads submitted between the
backup and the failure would be lost. It needs the repo secrets
`DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (optional `DEPLOY_PORT`), and
can also be run manually via *workflow_dispatch*.

Manual fallback on the server:

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

For the contact/quote/careers forms to send real emails (otherwise they log to
the container stdout via the console backend):

- `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT`, `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD`
- `CONTACT_FORM_RECIPIENT`
- `CAREERS_FORM_RECIPIENT` — optional. Where `/careers/` job applications
  are emailed to. Falls back to `CONTACT_FORM_RECIPIENT` when unset.

Spam protection and analytics:

- `RECAPTCHA_SECRET_KEY` — reCAPTCHA v3 server key; empty = verification
  skipped (dev). `RECAPTCHA_SITE_KEY` (public, has a committed default) and
  `RECAPTCHA_MIN_SCORE` (default `0.5`) tune it.
- `PLAUSIBLE_DOMAIN` — enables the Plausible analytics snippet when set;
  `PLAUSIBLE_SCRIPT_SRC` can point at a self-hosted instance.

Site identity (all have sensible defaults in settings):
`SITE_EMAIL`, `SITE_PHONE`, `SITE_PHONE_E164`, `SITE_WHATSAPP_E164`,
`SITE_LINKEDIN`, `SITE_BOOKING_URL`, `DJANGO_DEFAULT_FROM_EMAIL`,
`DJANGO_ADMINS` / `DJANGO_SERVER_EMAIL` (error emails).

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

Blog images should be self-hosted under `static/img/blog/` — don't embed
third-party CDN URLs in post bodies (see the one-shot
`rewrite_external_blog_images` management command for the historical cleanup).

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

The compose file also defines a Docker healthcheck against `/healthz`, and the
deploy workflow smoke-tests `/healthz`, `/portfolio/` and
`/showcase/maple-and-vine/` after every deploy.

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
