# Build stage
ARG CADDY_VERSION
FROM caddy:${CADDY_VERSION}-builder AS builder

RUN apt-get update && apt-get install -y gcc

ENV CGO_ENABLED=1

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/WeidiDeng/caddy-cloudflare-ip \
    --with github.com/fvbommel/caddy-combine-ip-ranges \
    --with github.com/AnswerDotAI/caddy-sqlite-router

# Final stage
FROM caddy:${CADDY_VERSION}

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
