# Luma Tech Solutions — repo guide

A static holding page for **lumatechsolutions.co.uk**. Plain HTML/CSS served by an
nginx Docker container, fronted by the shared Caddy reverse-proxy on the Hetzner box.

## Layout

```
.
├── public/              # static site (this is what nginx serves)
│   ├── index.html
│   ├── robots.txt
│   └── sitemap.xml
├── nginx.conf           # nginx vhost: cache headers, gzip, /healthz
├── docker-compose.yml   # nginx:alpine on host port 8004
├── README.md
└── CLAUDE.md            # this file
```

Edits to `public/` are picked up live (bind-mounted, no rebuild needed). Changes to
`nginx.conf` need `docker compose up -d --force-recreate`.

## Server (Hetzner: Luma001 — 178.104.29.66)

- Project lives at `/root/luma-tech-solutions/` on the server.
- Container name: `luma-tech-solutions-web` (host port `8004`).
- Reachable from Caddy via `172.17.0.1:8004` (host bridge gateway).

## Caddy reverse-proxy

Caddy runs as a separate Docker container (`caddy-caddy-1`) and owns ports 80/443
for **every** site on this server. It is **not** in the same compose project — it
sits in `/root/caddy/` and reverse-proxies to each app via the docker host gateway.

- Caddyfile on host: `/root/caddy/Caddyfile`
- Mounted into container at: `/etc/caddy/Caddyfile`
- Each site is one block. Existing pattern (mirror this for new sites):

  ```caddyfile
  example.com, www.example.com {
      reverse_proxy 172.17.0.1:<host-port>
      encode gzip
  }
  ```

- Block for this site (already added):

  ```caddyfile
  lumatechsolutions.co.uk, www.lumatechsolutions.co.uk {
      reverse_proxy 172.17.0.1:8004
      encode gzip
  }
  ```

- Reload after editing the Caddyfile:

  ```sh
  docker exec caddy-caddy-1 caddy validate --config /etc/caddy/Caddyfile
  docker exec caddy-caddy-1 caddy reload  --config /etc/caddy/Caddyfile
  ```

- Caddy handles TLS automatically via Let's Encrypt — no manual cert work needed
  as long as DNS A records point to **178.104.29.66**.

## Host-port allocation on Luma001

Don't double-book. Currently used:

| Port | Service                 |
|------|-------------------------|
| 8000 | paws4thoughtdogs        |
| 8001 | oakwood-climbing-gym    |
| 8002 | for-sale-by-owner       |
| 8003 | uvl-frontend            |
| 8004 | **luma-tech-solutions** |

Pick the next free one for any new site.

## Deploy workflow

From the server:

```sh
cd /root/luma-tech-solutions
git pull
docker compose up -d            # picks up public/ changes immediately
# or, if nginx.conf or compose changed:
docker compose up -d --force-recreate
```

To purge edge cache after a content change, no action needed — `index.html` is
served with `Cache-Control: no-cache`. Static assets (`.css/.js/.svg/...`) get a
30-day immutable cache; bump filenames if you change them.

## Health & smoke-test

```sh
curl -sI http://127.0.0.1:8004/healthz       # from server: 200 OK "ok"
curl -sI https://lumatechsolutions.co.uk/    # from anywhere once DNS is correct
```

## DNS

A records (apex + `www`) must point to **178.104.29.66**. Until they do,
Caddy will keep retrying ACME with backoff — the site will simply have no
HTTPS until DNS propagates.
