# Caddy Cloudflare sqlite
> A fully integrated Caddy Docker image with Cloudflare DNS-01 ACME validation, IP trust, and SQLite-based dynamic routing

Deploy a production-ready Caddy server with built-in support for Cloudflare DNS-01 challenges, automatic SSL certificate management, real client IP detection, and dynamic SQLite-powered routing.

## SQLite Router

The [`caddy-sqlite-router`](https://github.com/AnswerDotAI/caddy-sqlite-router) module enables dynamic routing based on a SQLite database. Routes are resolved at request time — no Caddy reload required when routes change.

### How it works

1. Caddy queries a SQLite database with the incoming request's domain.
2. The result (`host` + `port`) is used as the upstream for `reverse_proxy`.
3. Update the database to change routing without touching the Caddy config.

### SQLite schema example

```sql
CREATE TABLE route (
  domain TEXT PRIMARY KEY,
  host   TEXT NOT NULL,
  port   INTEGER NOT NULL
);

INSERT INTO route VALUES ('app.example.com', '127.0.0.1', 8080);
INSERT INTO route VALUES ('api.example.com', '127.0.0.1', 9000);
```

### Caddy JSON config example

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":80", ":443"],
          "routes": [{
            "match": [{ "host": ["*.example.com"] }],
            "handle": [{
              "handler": "subroute",
              "routes": [{
                "handle": [
                  {
                    "handler": "sqlite_router",
                    "db_path": "/etc/caddy/routes.db",
                    "query": "SELECT host, port FROM route WHERE domain = :domain"
                  },
                  {
                    "handler": "reverse_proxy",
                    "upstreams": [{ "dial": "{http.vars.backend_upstream}" }]
                  },
                  { "handler": "encode", "encodings": { "gzip": {} } }
                ]
              }]
            }]
          }]
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [{
          "subjects": ["*.example.com"],
          "issuers": [{
            "module": "acme",
            "email": "${env.EMAIL}",
            "challenges": {
              "dns": {
                "provider": {
                  "name": "cloudflare",
                  "api_token": "${env.CLOUDFLARE_API_TOKEN}"
                }
              }
            }
          }]
        }]
      }
    }
  }
}
```

### Docker Compose with SQLite router

```yaml
services:
  caddy:
    image: ghcr.io/pratyay360/caddy-cloudflare-sqlite:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "2019:2019"
    volumes:
      - ./caddy.json:/etc/caddy/caddy.json:Z
      - ./caddy_data:/data:Z
      - ./caddy_config:/config:Z
      - ./routes.db:/etc/caddy/routes.db:Z
    command: ["caddy", "run", "--config", "/etc/caddy/caddy.json"]
    environment:
      - CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
      - EMAIL=your@email.com
```




## Configuration

### Creating a Cloudflare API Token

1. Log in at [dash.cloudflare.com](https://dash.cloudflare.com).
2. Go to **My Profile** → **API Tokens** → **Create Token**.
3. Use a **Custom Token** with these permissions:
   - `Zone - Zone - Read`
   - `Zone - DNS - Edit`
4. Under **Zone Resources**, select the zones you want to cover (or all zones).
5. Create the token and set it as the `CLOUDFLARE_API_TOKEN` environment variable.

### ACME DNS Challenge Configuration

Add to your Caddyfile global block to apply DNS challenge to all sites:

```
{
  acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Or per-site in the `tls` directive:

```
tls {
  dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

#### Troubleshooting

If you see `HTTP 403` errors during DNS challenge, try setting a custom resolver:

```
tls {
  dns cloudflare {env.CLOUDFLARE_API_TOKEN}
  resolvers 1.1.1.1
}
```

See the [official troubleshooting guide](https://github.com/caddy-dns/cloudflare?tab=readme-ov-file#troubleshooting) for more.



## Building Your Own Docker Image

### Prerequisites

- GitHub account
- DockerHub account (optional)
- GitHub Secrets:
  - `GITHUB_TOKEN` (auto-available in Actions)
  - `DOCKERHUB_USERNAME` (optional)
  - `DOCKERHUB_TOKEN` (optional)
  - `DOCKERHUB_REPOSITORY_NAME` (optional)

### Steps

1. [Fork this repository](https://github.com/caddybuilds/caddy-cloudflare/fork).
2. Add secrets under **Settings → Secrets and variables → Actions**.
3. Enable GitHub Actions if prompted in the **Actions** tab.
4. Trigger the `Build and Push Docker Image` workflow manually or wait for an automated run.
5. Pull your image:

```sh
docker pull ghcr.io/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:latest
```

The Dockerfiles are straightforward — the standard image uses `caddy:${CADDY_VERSION}-builder` on Debian, and the Alpine variant uses `caddy:${CADDY_VERSION}-builder` with `apk`. Both compile with `CGO_ENABLED=1` to support the SQLite router module.

**Standard (`Dockerfile`)**:
```dockerfile
ARG CADDY_VERSION
FROM caddy:${CADDY_VERSION}-builder AS builder

RUN apt-get update && apt-get install -y gcc
ENV CGO_ENABLED=1

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/WeidiDeng/caddy-cloudflare-ip \
    --with github.com/fvbommel/caddy-combine-ip-ranges \
    --with github.com/AnswerDotAI/caddy-sqlite-router

FROM caddy:${CADDY_VERSION}
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

**Alpine (`Dockerfile.alpine`)**:
```dockerfile
ARG CADDY_VERSION
FROM caddy:${CADDY_VERSION}-builder AS builder

RUN apk add --no-cache gcc musl-dev
ENV CGO_ENABLED=1

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/WeidiDeng/caddy-cloudflare-ip \
    --with github.com/fvbommel/caddy-combine-ip-ranges \
    --with github.com/AnswerDotAI/caddy-sqlite-router

FROM caddy:${CADDY_VERSION}-alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

## Contributing

Open issues or submit pull requests for improvements and bug fixes.

## License

MIT License. See [LICENSE](LICENSE) for details.
