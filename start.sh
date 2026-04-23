#!/usr/bin/env bash
set -o errexit

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
MEDIA_ROOT="${DISK_MEDIA_ROOT:-}"
SEED_MEDIA_ROOT="${RENDER_MEDIA_SEED_PATH:-${PROJECT_ROOT}/media}"

if [ -n "$MEDIA_ROOT" ] && [ -d "$SEED_MEDIA_ROOT" ]; then
  mkdir -p "$MEDIA_ROOT"

  if [ -z "$(find "$MEDIA_ROOT" -mindepth 1 -print -quit 2>/dev/null)" ]; then
    echo "Bootstrapping media files into persistent storage..."
    cp -R "$SEED_MEDIA_ROOT"/. "$MEDIA_ROOT"/
  fi
fi

python manage.py migrate --no-input
python manage.py bootstrap_render_data

exec gunicorn seago.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --access-logfile -
