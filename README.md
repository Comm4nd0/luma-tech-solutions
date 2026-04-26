# Luma Tech Solutions

Holding page for [lumatechsolutions.co.uk](https://lumatechsolutions.co.uk).

## Stack

Static HTML served by nginx in Docker, fronted by the shared Caddy reverse-proxy on the Hetzner server.

## Local preview

```sh
docker compose up -d
# open http://localhost:8004
```

## Deployment (Hetzner: Luma001)

The site lives at `/root/luma-tech-solutions/` on the server and is reverse-proxied by the shared Caddy
container at `/root/caddy/Caddyfile`.

```sh
# from the server
cd /root/luma-tech-solutions
git pull
docker compose up -d --force-recreate
```

To pick up Caddy changes:

```sh
docker exec caddy-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

## Files

- `public/` — static site (edit `index.html` for content changes)
- `nginx.conf` — nginx vhost (cache headers, gzip, healthcheck)
- `docker-compose.yml` — runs nginx on host port `8004`
