#!/bin/sh
# Dev entrypoint for React frontend:
#   Runs npm install only when package.json changes, then starts the dev server.
#
# node_modules lives in a named Docker volume at /app/node_modules so
# packages survive container restarts without reinstalling.

set -e

HASH_FILE=/app/node_modules/.pkg-hash

if [ -f "/app/package.json" ]; then
    CURRENT_HASH=$(sha256sum /app/package.json | cut -d' ' -f1)
    CACHED_HASH=$(cat "${HASH_FILE}" 2>/dev/null || echo "")

    if [ "${CURRENT_HASH}" != "${CACHED_HASH}" ]; then
        echo "[dev] package.json changed — running npm install..."
        npm install
        echo "${CURRENT_HASH}" > "${HASH_FILE}"
        echo "[dev] npm install done."
    else
        echo "[dev] package.json unchanged — skipping npm install."
    fi
else
    echo "[dev] No package.json at /app — skipping npm install."
fi

exec "$@"
