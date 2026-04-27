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

# Parse cron schedule and wait until next execution time
CRON_SCHEDULE="${CRON_SCHEDULE:-0 2 * * *}"
read -r MINUTE HOUR <<< "$(echo "$CRON_SCHEDULE" | awk '{print $1, $2}')"

echo "[entrypoint] Schedule: daily at ${HOUR}:${MINUTE}"
echo "[entrypoint] Starting download loop..."

run_download() {
    echo "=================================================="
    echo "[download] Started at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================="
    cd /app && python main.py 2>&1
    local exit_code=$?
    echo "=================================================="
    echo "[download] Finished at $(date '+%Y-%m-%d %H:%M:%S') (exit: $exit_code)"
    echo "=================================================="
}

# Initial run on startup
run_download

while true; do
    # Calculate seconds until next scheduled time
    NOW_MIN=$(date +%-M)
    NOW_HOUR=$(date +%-H)
    NOW_SEC=$(date +%-S)

    # Handle cron expressions like "*/5" or "*"
    if [[ "$MINUTE" == *"/"* ]]; then
        STEP=${MINUTE#*/}
        TARGET_MIN=$(( (NOW_MIN / STEP + 1) * STEP ))
        TARGET_HOUR=$NOW_HOUR
        if [ $TARGET_MIN -ge 60 ]; then
            TARGET_MIN=$((TARGET_MIN - 60))
            TARGET_HOUR=$(( (NOW_HOUR + 1) % 24 ))
        fi
    elif [[ "$HOUR" == *"/"* ]]; then
        STEP=${HOUR#*/}
        TARGET_HOUR=$(( (NOW_HOUR / STEP + 1) * STEP % 24 ))
        TARGET_MIN=0
    elif [[ "$MINUTE" == "*" ]]; then
        TARGET_HOUR=$NOW_HOUR
        TARGET_MIN=$((NOW_MIN + 1))
        if [ $TARGET_MIN -ge 60 ]; then
            TARGET_MIN=0
            TARGET_HOUR=$(( (NOW_HOUR + 1) % 24 ))
        fi
    else
        TARGET_HOUR=$HOUR
        TARGET_MIN=$MINUTE
        # If target time already passed today, schedule for tomorrow
        if [ $TARGET_HOUR -lt $NOW_HOUR ] || { [ $TARGET_HOUR -eq $NOW_HOUR ] && [ $TARGET_MIN -le $NOW_MIN ]; }; then
            TARGET_HOUR=$(( (TARGET_HOUR + 24) % 24 ))
        fi
    fi

    # Calculate sleep seconds
    TARGET_SEC=0
    TARGET_TOTAL=$(( TARGET_HOUR * 3600 + TARGET_MIN * 60 + TARGET_SEC ))
    NOW_TOTAL=$(( NOW_HOUR * 3600 + NOW_MIN * 60 + NOW_SEC ))
    SLEEP_SEC=$(( TARGET_TOTAL - NOW_TOTAL ))
    if [ $SLEEP_SEC -le 0 ]; then
        SLEEP_SEC=$((SLEEP_SEC + 86400))
    fi

    NEXT_TIME=$(date -d "@$(( $(date +%s) + SLEEP_SEC ))" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -u -d "$SLEEP_SEC seconds" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "in ${SLEEP_SEC}s")
    echo "[entrypoint] Next run: $NEXT_TIME (sleeping ${SLEEP_SEC}s)"
    echo "[entrypoint] Press Ctrl+C or 'docker compose down' to stop"

    sleep $SLEEP_SEC

    run_download
done
