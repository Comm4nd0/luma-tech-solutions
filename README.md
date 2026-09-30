# Luma Tech Solutions

The full marketing website for [lumatechsolutions.co.uk](https://lumatechsolutions.co.uk).

## Stack

- **Django 5.2 LTS** (server-rendered templates) — one app, `core`, with all pages.
- **Custom CSS** — dark/light theme (slate/teal), self-hosted Inter variable font.
- **WhiteNoise** — static-file serving (gzip + brotli), no separate CDN needed.
- **nh3** — sanitises author-supplied blog HTML; a nonce-based CSP is the backstop.
- **Gunicorn** in a Docker container, fronted by the shared Caddy reverse-proxy on Hetzner (port `8005`).

## Layout

```
.
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml          # runs gunicorn on host port 8005
├── lumatech/                   # Django project (settings, urls, wsgi)
├── core/                       # main app
│   ├── views.py                # page views + form handling
│   ├── content.py              # all marketing content + page tables (pure data)
│   ├── forms.py                # contact / quote / careers, CV validation
│   ├── models.py               # submissions + BlogPost
│   ├── api.py, feeds.py, sitemaps.py
│   ├── checks.py               # deploy-time config warnings
│   ├── middleware.py           # nonce-based Content Security Policy
│   └── tests/                  # 139 tests
├── templates/
│   ├── base.html               # nav, footer, OG/SEO meta, JSON-LD
│   ├── partials/               # icons, pillars, CTA, breadcrumbs, area sidebar/schema
│   ├── services/               # overview + 6 detail pages
│   ├── areas/                  # index + 4 town landing pages
│   ├── portfolio/, blog/, showcase/
│   └── robots.txt
└── static/
    ├── css/site.css            # all styles
    ├── js/site.js              # nav, theme, reveal, inline validation
    ├── js/cookie-consent.js    # consent banner + Google Ads gating
    ├── fonts/                  # self-hosted Inter variable woff2
    └── img/                    # favicons, OG image, service + blog photos
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
| `DJANGO_EMAIL_BACKEND` | defaults to SMTP when `DJANGO_DEBUG` is off, console in dev — do not pin it to console in production |
| `DJANGO_EMAIL_TIMEOUT` | SMTP socket timeout in seconds, default `10` |
| `DJANGO_EMAIL_HOST` etc. | SMTP creds for the contact form |
| `CONTACT_FORM_RECIPIENT` | where contact-form notifications go |
| `CAREERS_FORM_RECIPIENT` | optional; careers inbox (falls back to `CONTACT_FORM_RECIPIENT`) |
| `DJANGO_ADMINS` | comma-separated emails that receive 500-error reports |
| `DJANGO_SERVER_EMAIL` | From address for error mail (defaults to `DJANGO_DEFAULT_FROM_EMAIL`) |
| `DJANGO_LOG_LEVEL` | app log level, default `INFO` |
| `DJANGO_CSP_REPORT_ONLY` | `1` to send the CSP as report-only (useful when adding a script) |
| `LUMA_BLOG_API_KEY` | Bearer token for the blog publishing API (503 if unset) |
| `DJANGO_MEDIA_ROOT` | where uploaded CVs are stored (defaults to `data/media`) |

## Deployment (Hetzner: Luma001)

The site lives at `/root/luma-tech-solutions/` on the server and is reverse-proxied by the shared Caddy container at `/root/caddy/Caddyfile` on host port **8005** (replacing the previous static `8004` holding page).

```sh
# from the server
cd /root/luma-tech-solutions
git pull
docker compose up -d --build
```

> `DJANGO_SECRET_KEY` is **mandatory** — `docker compose` refuses to start
> without it. Before deploying, it's worth running the deployment checks and
> the test suite locally:
>
> ```sh
> DJANGO_DEBUG=0 DJANGO_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(50))") \
>   python manage.py check --deploy
> python manage.py test
> ```

After updating the Caddyfile to point `lumatechsolutions.co.uk` at `172.17.0.1:8005`:

```sh
docker exec caddy-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

## Pages

`/`, `/services/`, `/services/{networking,security,ai-cameras,development,automation,support}/`, `/our-approach-to-camera-privacy/`, `/construction/`, `/construction/capability-statement/`, `/about/`, `/portfolio/`, `/portfolio/<slug>/`, `/showcase/<slug>/`, `/areas/{,marlow,maidenhead,henley,beaconsfield}/`, `/quote/`, `/quote/thanks/`, `/contact/`, `/contact/thanks/`, `/careers/`, `/careers/thanks/`, `/blog/`, `/blog/feed/`, `/blog/<slug>/`, `/terms/`, `/privacy/`, `/api/blog/posts/`, `/healthz`, `/sitemap.xml`, `/robots.txt`, `/admin/`.

## Contact form

`POST /contact/` validates a `ContactSubmission` (name, email, phone, service, message), saves it to the DB, and emails `CONTACT_FORM_RECIPIENT`. A hidden `website` field acts as a honeypot for bots. Submissions are visible in `/admin/`.

## Health

`GET /healthz` → `200 ok`. Wired up to both the Docker healthcheck and the gunicorn check.

## Residential enquiries and follow-up

The homepage focuses on home Wi-Fi, CCTV and smart-home help. Installation
prices are assessed from the equipment, access points and cable runs required;
there is no advertised minimum installation price. Installation quotation
surveys are free. Diagnostic visits and standalone reports are separately
priced and agreed before booking. Care-plan prices remain in `CARE_PLAN_AUDIENCES`.

Both **Contact submissions** and **Quote requests** in `/admin/` now include:

- Progress: new → qualified → survey booked → survey completed → quote sent →
  accepted → installed, or closed/not proceeding.
- A follow-up date, installation date, optional care-plan selection and review
  request date. Marking a project installed sets a 14-day follow-up unless a
  different date is supplied in the same edit. No scheduled job or email is sent.
- Project revenue and direct delivery cost excluding VAT; margin is shown only
  where both have been recorded. Include a labour allowance in direct costs.
- Page/CTA source, optional referral answer and explicit campaign tags.

Use the **Due today or overdue** filter to work through follow-ups. Discuss care
plans when quoting and at handover; check in during the included support period,
then ask every customer for honest feedback. Each enquiry's edit screen has
check-in, review-request and partner-introduction drafts to personalise and send.
There are no incentives or automated outreach messages.

The list summary respects filters and groups sources/services. It shows current
stages, not historical funnel conversion rates. Review old records (which begin
as “new”) and close duplicate enquiries before interpreting totals. Compare a
consistent date window and service, and record accepted work rather than judging
performance from clicks alone. Contact and quote totals are separate.

The public `/partners/` page explains introductions for electricians, builders,
renovation teams and estate agents. Actual introductions, Business Profile photo
updates and review requests are manual business tasks.

### Analytics

Plausible receives `Enquiry started` once per form page interaction and
`Enquiry received` only after a valid submission has been saved. Add these exact
custom-event goals in the Plausible dashboard and compare them by the `form`
property (`contact` / `quote`). Existing click events remain separate from success.
Google Ads conversion events stay marketing-consent gated; successful submissions
have a random transaction ID, and refreshes/direct thank-you-page visits do not
emit another conversion. No form answers are sent to analytics.

Optional `utm_source`, `utm_medium` and `utm_campaign` URL tags are carried along
internal links in memory (no attribution cookie/localStorage), prefilled into the
forms and saved with the enquiry. Existing `source` tags identify the final CTA.
Use campaign tags without personal information. The public privacy page describes
this processing. There is no new third-party analytics service.

### Adding real photographs later

Until photos are supplied, the pages render without empty photo slots. Portfolio
cards no longer use generic stock images labelled as photographs of a client job.

- Put a portrait under `static/img/`, then set `SITE_FOUNDER_PHOTO` to its static
  path (for example `img/marco.jpg`) in the deployment environment. It appears on
  the homepage, About page and engineer introduction cards.
- Add optional `photo` and `photo_alt` keys to a case in `core/content.py`, with
  a self-hosted path and a description of the actual installation.
- An optional `photos` list adds a case-study gallery. Each entry has `path`,
  `alt` and optional `caption` keys. Record only real project details; add measured
  before/after results and duration when available, without inventing figures.
- `AREA_PAGES[...]['example_jobs']` remains the source for real town-specific jobs.
  Existing TODOs stay hidden until genuine details are available. Maidenhead links
  to its existing LittleWick case study. Keep town terms on town pages.
- Bump `PAGE_LASTMOD` for the affected page and `case_study:<slug>` when adding
  photographs or substantive project details. Rebuild to collect static files.

The read-reviews link uses `SITE_GOOGLE_BUSINESS_URL`; the review-request draft
uses `SITE_GOOGLE_REVIEW_URL`. The production Compose defaults now retain the
public phone and WhatsApp numbers rather than replacing them with blank values.
