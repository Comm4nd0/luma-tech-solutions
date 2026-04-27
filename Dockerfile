FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=lumatech.settings

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static at build-time so the image is self-contained.
RUN DJANGO_SECRET_KEY=build-only DJANGO_DEBUG=0 python manage.py collectstatic --noinput

# Data dir for sqlite (mounted as a volume in docker-compose)
RUN mkdir -p /app/data && chmod 777 /app/data

# Run as a non-root user
RUN useradd --system --uid 1001 --gid 0 luma \
 && chown -R luma:0 /app
USER 1001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

# Run migrations on every start (idempotent), then serve via gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn lumatech.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -"]
