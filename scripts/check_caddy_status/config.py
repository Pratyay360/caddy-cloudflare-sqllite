import os
from pathlib import Path

# GitHub
GITHUB_REPO = "caddyserver/caddy"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

_github_repository = os.environ.get("GITHUB_REPOSITORY", "").lower()


OFFICIAL_CADDY_IMAGE = "library/caddy"
CUSTOM_IMAGE = os.environ.get("DOCKERHUB_REPOSITORY_NAME", "") or _github_repository

GHCR_IMAGE = os.environ.get("GHCR_IMAGE", "") or _github_repository

# Platforms required in both official and custom images
REQUIRED_PLATFORMS = {
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v7",
    "linux/ppc64le",
    "linux/s390x",
}

# Modules built into the Docker image — must match Dockerfile
MODULES = [
    {"module": "github.com/caddy-dns/cloudflare", "repo": "caddy-dns/cloudflare"},
    {"module": "github.com/WeidiDeng/caddy-cloudflare-ip", "repo": "WeidiDeng/caddy-cloudflare-ip"},
    {"module": "github.com/fvbommel/caddy-combine-ip-ranges", "repo": "fvbommel/caddy-combine-ip-ranges"},
    {"module": "github.com/AnswerDotAI/caddy-sqlite-router", "repo": "AnswerDotAI/caddy-sqlite-router" }
]

# Path to module version tracking file (repo root)
MODULE_VERSIONS_FILE = Path(__file__).resolve().parent.parent.parent / "module-versions.json"

# HTTP retry settings
MAX_RETRIES = 3
BACKOFF_BASE = 2
