#!/bin/bash
set -e

echo "[entrypoint] Generating config.py from environment variables..."

cat > /app/config.py <<PYEOF
# -*- coding: utf-8 -*-
"""
Twitter/X Likes Video Downloader - Auto-generated config
Generated from environment variables at container startup
"""
import os

COOKIES = {
    "auth_token": os.environ.get("AUTH_TOKEN", ""),
    "ct0": os.environ.get("CT0", ""),
}

TARGET_USER = os.environ.get("TARGET_USER", "your_target_username")

DOWNLOAD_DIR = "/app/data"

RECORD_FILE = "/app/data/download_record.json"

API_BASE_URL = "https://x.com/i/api/graphql"

QUERY_ID_USER_BY_SCREEN_NAME = "IGgvgiOx4QZndDHuD3x9TQ"
QUERY_ID_LIKES = "KPuet6dGbC8LB2sOLx7tZQ"

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://x.com",
    "Referer": "https://x.com/",
    "X-Twitter-Auth-Type": "OAuth2Session",
    "X-Twitter-Active-User": "yes",
    "X-Twitter-Client-Language": "zh-cn",
}

REQUEST_DELAY = 1.5
MAX_RETRIES = 3
RETRY_DELAY = 30
PAGE_SIZE = 20

_proxy = os.environ.get("PROXY", "")
PROXY = _proxy if _proxy else None
PYEOF

echo "[entrypoint] config.py generated."

# Setup cron
CRON_SCHEDULE="${CRON_SCHEDULE:-0 2 * * *}"
echo "$CRON_SCHEDULE cd /app && python main.py >> /proc/1/fd/1 2>&1" > /etc/cron.d/downloader

echo "[entrypoint] Cron scheduled: $CRON_SCHEDULE"
echo "[entrypoint] Starting cron in foreground..."

exec cron -f
