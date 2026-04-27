# Luma Tech Solutions — repo guide

The marketing website for **lumatechsolutions.co.uk**. Server-rendered Django 5
application running in a Docker container, fronted by the shared Caddy
reverse-proxy on the Hetzner box.

## Layout

```
.
├── manage.py
├── requirements.txt           # Django, gunicorn, whitenoise
├── Dockerfile                 # python:3.12-slim → gunicorn on :8000
├── docker-compose.yml         # publishes host port 8005
├── lumatech/                  # Django project (settings, urls, wsgi/asgi)
├── core/                      # the only app — views, forms, models, sitemaps
├── templates/                 # all HTML templates (base, pages, partials/, services/)
├── static/                    # css, js, img — collected to /staticfiles by collectstatic
├── public/, nginx.conf        # legacy static holding page, kept for reference (not deployed)
└── data/                      # sqlite DB (gitignored, mounted as volume in compose)
```

## Architecture

- **One app, `core`**, holds every view (one function per page) plus the contact-form
  model, form, and sitemap. PILLARS, TESTIMONIALS, CARE_PLANS and CASE_STUDIES live
  as module-level constants in `core/views.py` — moving any of them to the database
  is the right call the moment they need to be edited by a non-developer.
- **Server-rendered templates** under `templates/` extend `base.html`. The base
  template owns the nav, footer, OG/SEO meta and global stylesheet.
- **Custom CSS** at `static/css/site.css` — no Tailwind, no build step. Dark theme:
  `--bg #0f172a`, `--accent #14b8a6`, Inter from Google Fonts.
- **Static files** are served by WhiteNoise via gunicorn — no separate nginx layer
  in the Docker image. Caddy in front handles TLS.

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

## Health & smoke-test

```sh
curl -sI http://127.0.0.1:8005/healthz       # 200 OK "ok"
curl -sI https://lumatechsolutions.co.uk/    # from anywhere once DNS + Caddy are pointed at 8005
```

## DNS

A records (apex + `www`) must point to **178.104.29.66**. Until they do,
Caddy will keep retrying ACME with backoff — the site will simply have no
HTTPS until DNS propagates.

## Migrating from the holding page

The previous static-nginx setup (port 8004, files in `public/`) is preserved
in-tree for reference but is no longer wired up. Cut-over steps:

1. `docker compose up -d --build` on the new app (binds 8005)
2. Edit `/root/caddy/Caddyfile`, change `172.17.0.1:8004` → `172.17.0.1:8005`
3. `docker exec caddy-caddy-1 caddy reload --config /etc/caddy/Caddyfile`
4. Stop and remove the old static container once you're confident.
