
```yaml
version: "3.9"
services:
  caddy:
    image: ghcr.io/pratyay360/caddy-cloudflare-sqllite:alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "8080:80"
      - "8443:443"
      - "2019:2019"
    environment:
      - CLOUDFLARE_API_TOKEN=${env.CLOUDFLARE_API_TOKEN}
    volumes:
      - ./caddy.json:/etc/caddy/caddy.json:Z
      - ./caddy_data:/data:Z
      - ./caddy_config:/config:Z
      - ./routes.db:/etc/caddy/routes.db:Z
    command: ["caddy", "run", "--config", "/etc/caddy/caddy.json"]
    networks: 
      -  mdebzoti
networks:
    mdebzoti:
       driver: bridge
       expose: true
```


```sql

CREATE TABLE route (
  domain TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  port INTEGER NOT NULL
)


INSERT INTO route VALUES('app1', 'testhost', 5173);



```

Cloudflare api ...

Zone Zone Read


Zone Dns Edit




```json


{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":80", ":443"],
          "routes": [
            {
              "match": [{ "host": ["*.example.com"] }],
              "handle": [
                {
                  "handler": "subroute",
                  "routes": [
                    {
                      "handle": [
                        {
                          "handler": "sqlite_router",
                          "db_path": "/etc/caddy/routes.db",
                          "query": "SELECT host, port FROM route WHERE domain = :domain"
                        },
                        {
                          "handler": "reverse_proxy",
                          "upstreams": [
                            { "dial": "{http.vars.backend_upstream}" }
                          ]
                        },
                        { "handler": "encode", "encodings": { "gzip": {} } }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      }
    },
    "tls": {
      "automation": {
        "policies": [
          {
            "subjects": ["*.example.com"],
            "issuers": [
              {
                "module": "acme",
                "email": "${{ secrets.ACME_EMAIL }}",
                "challenges": {
                  "dns": {
                    "provider": {
                      "name": "cloudflare",
                      "api_token": "${{ secrets.CLOUDFLARE_API_TOKEN }}"
                    }
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}

```