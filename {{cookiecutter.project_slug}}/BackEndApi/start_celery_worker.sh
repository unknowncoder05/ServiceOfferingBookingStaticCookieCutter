#!/bin/bash
# Start Celery worker for local development

set -o errexit
set -o pipefail
set -o nounset

cd src

echo "Starting Celery worker..."
celery -A config.celery_app worker -l INFO --pool=solo
