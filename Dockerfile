FROM docker.io/caddy:builder AS builder

ARG CADDY_VERSION

RUN apk add --no-cache gcc musl-dev build-base

ENV CGO_ENABLED=1

RUN if [ -n "$CADDY_VERSION" ]; then CADDY_REF="v${CADDY_VERSION}"; else CADDY_REF=""; fi; \
    xcaddy build ${CADDY_REF} \
    --output /usr/bin/caddy \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/WeidiDeng/caddy-cloudflare-ip \
    --with github.com/fvbommel/caddy-combine-ip-ranges \
    --with github.com/AnswerDotAI/caddy-sqlite-router


# Final stage
FROM docker.io/caddy:latest

# Copy the custom-built Caddy binary
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
