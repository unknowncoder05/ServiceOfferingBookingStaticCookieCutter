#!/bin/bash
# Database sync script for S3

set -e

DB_S3_BUCKET="${DB_S3_BUCKET:-}"
DB_S3_KEY="${DB_S3_KEY:-db.sqlite3}"
DB_LOCAL_PATH="${DB_LOCAL_PATH:-/app/db.sqlite3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to download DB from S3
download_db() {
    if [ -z "$DB_S3_BUCKET" ]; then
        log_warn "DB_S3_BUCKET not set. Skipping DB download."
        return 0
    fi

    log_info "Checking for existing database in S3..."

    if aws s3 ls "s3://${DB_S3_BUCKET}/${DB_S3_KEY}" 2>/dev/null; then
        log_info "Database found in S3. Downloading..."

        if aws s3 cp "s3://${DB_S3_BUCKET}/${DB_S3_KEY}" "$DB_LOCAL_PATH"; then
            log_info "Database downloaded successfully from s3://${DB_S3_BUCKET}/${DB_S3_KEY}"

            # Create a backup
            BACKUP_PATH="${DB_LOCAL_PATH}.backup"
            cp "$DB_LOCAL_PATH" "$BACKUP_PATH"
            log_info "Backup created at $BACKUP_PATH"

            # Set proper permissions
            chmod 644 "$DB_LOCAL_PATH"

            return 0
        else
            log_error "Failed to download database from S3"
            return 1
        fi
    else
        log_warn "No existing database found in S3. Starting with fresh database."
        return 0
    fi
}

# Function to upload DB to S3
upload_db() {
    if [ -z "$DB_S3_BUCKET" ]; then
        log_warn "DB_S3_BUCKET not set. Skipping DB upload."
        return 0
    fi

    if [ ! -f "$DB_LOCAL_PATH" ]; then
        log_warn "Local database file not found at $DB_LOCAL_PATH. Nothing to upload."
        return 0
    fi

    log_info "Uploading database to S3..."

    # Create a timestamped backup in S3
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_KEY="${DB_S3_KEY}.backup.${TIMESTAMP}"

    # First, backup the current S3 version (if it exists)
    if aws s3 ls "s3://${DB_S3_BUCKET}/${DB_S3_KEY}" 2>/dev/null; then
        log_info "Creating timestamped backup in S3..."
        aws s3 cp "s3://${DB_S3_BUCKET}/${DB_S3_KEY}" "s3://${DB_S3_BUCKET}/${BACKUP_KEY}" || log_warn "Failed to create backup"
    fi

    # Upload the current database
    if aws s3 cp "$DB_LOCAL_PATH" "s3://${DB_S3_BUCKET}/${DB_S3_KEY}"; then
        log_info "Database uploaded successfully to s3://${DB_S3_BUCKET}/${DB_S3_KEY}"
        return 0
    else
        log_error "Failed to upload database to S3"
        return 1
    fi
}

# Function to sync on startup
sync_startup() {
    log_info "=== Starting Database Sync (Startup) ==="
    download_db
    log_info "=== Database Sync Complete ==="
}

# Function to sync on shutdown
sync_shutdown() {
    log_info "=== Starting Database Sync (Shutdown) ==="
    upload_db
    log_info "=== Database Sync Complete ==="
}

# Main execution
case "${1:-}" in
    startup)
        sync_startup
        ;;
    shutdown)
        sync_shutdown
        ;;
    download)
        download_db
        ;;
    upload)
        upload_db
        ;;
    *)
        echo "Usage: $0 {startup|shutdown|download|upload}"
        exit 1
        ;;
esac
