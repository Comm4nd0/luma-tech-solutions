# Luma Tech Solutions

The full marketing website for [lumatechsolutions.co.uk](https://lumatechsolutions.co.uk).

## Stack

- **Django 5** (server-rendered templates) — one app, `core`, with all pages.
- **Custom CSS** — dark professional theme (slate/teal), Inter font.
- **WhiteNoise** — static-file serving, no separate CDN needed.
- **Gunicorn** in a Docker container, fronted by the shared Caddy reverse-proxy on Hetzner (port `8005`).

## Layout

```
.
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml          # runs gunicorn on host port 8005
├── lumatech/                   # Django project (settings, urls, wsgi)
├── core/                       # main app: views, forms, models, sitemaps
├── templates/
│   ├── base.html               # nav, footer, OG/SEO meta
│   ├── home.html
│   ├── about.html
│   ├── portfolio.html
│   ├── contact.html
│   ├── contact_thanks.html
│   ├── blog.html
│   ├── robots.txt
│   ├── partials/               # icons, pillars grid, CTA banner
│   └── services/               # overview + 4 detail pages
├── static/
│   ├── css/site.css            # all styles
│   ├── js/site.js              # nav toggle + IntersectionObserver
│   └── img/                    # favicon + OG image
└── public/, nginx.conf         # legacy holding-page assets, kept for reference
```

## Local development

```sh
python -m venv .venv && source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

mkdir -p data
DJANGO_DEBUG=1 DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  python manage.py migrate

DJANGO_DEBUG=1 DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  python manage.py runserver 8005
# open http://localhost:8005
```

## Docker

```sh
docker compose up -d --build      # builds image, runs gunicorn on host port 8005
docker compose logs -f web
curl -sI http://127.0.0.1:8005/healthz   # 200 OK
```

The container runs migrations on every start (idempotent) and serves via gunicorn. SQLite lives in the `luma-data` named volume.

## Environment variables

All optional in dev — sensible defaults are baked in.

| Variable | Purpose |
|---|---|
| `DJANGO_DEBUG` | `1` for dev, unset/`0` in production |
| `DJANGO_SECRET_KEY` | **required in production** |
| `DJANGO_ALLOWED_HOSTS` | comma-separated, e.g. `lumatechsolutions.co.uk,www.lumatechsolutions.co.uk` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | comma-separated `https://...` |
| `SITE_URL` | e.g. `https://lumatechsolutions.co.uk` |
| `SITE_EMAIL`, `SITE_PHONE` | shown on the site |
| `DJANGO_EMAIL_BACKEND` | default `console`; in prod use `django.core.mail.backends.smtp.EmailBackend` |
| `DJANGO_EMAIL_HOST` etc. | SMTP creds for the contact form |
| `CONTACT_FORM_RECIPIENT` | where contact-form notifications go |

## Deployment (Hetzner: Luma001)

The site lives at `/root/luma-tech-solutions/` on the server and is reverse-proxied by the shared Caddy container at `/root/caddy/Caddyfile` on host port **8005** (replacing the previous static `8004` holding page).

```sh
# from the server
cd /root/luma-tech-solutions
git pull
docker compose up -d --build
```

After updating the Caddyfile to point `lumatechsolutions.co.uk` at `172.17.0.1:8005`:

```sh
docker exec caddy-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

## Pages

`/`, `/services/`, `/services/{networking,development,automation,support}/`, `/about/`, `/portfolio/`, `/contact/`, `/contact/thanks/`, `/blog/`, `/healthz`, `/sitemap.xml`, `/robots.txt`, `/admin/`.

## Contact form

`POST /contact/` validates a `ContactSubmission` (name, email, phone, service, message), saves it to the DB, and emails `CONTACT_FORM_RECIPIENT`. A hidden `website` field acts as a honeypot for bots. Submissions are visible in `/admin/`.

## Health

`GET /healthz` → `200 ok`. Wired up to both the Docker healthcheck and the gunicorn check.
