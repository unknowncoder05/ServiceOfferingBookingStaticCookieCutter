#!/bin/bash
# Entrypoint script with DB sync and graceful shutdown

set -e

# Sync database on startup
/db-sync.sh startup

# Trap SIGTERM signal for graceful shutdown
trap 'echo "Received SIGTERM, syncing database..."; /db-sync.sh shutdown; exit 0' SIGTERM

# Start the application in the background
/start &

# Get the PID of the background process
APP_PID=$!

# Wait for the application process
wait $APP_PID
