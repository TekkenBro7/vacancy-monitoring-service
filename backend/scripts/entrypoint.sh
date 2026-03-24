#!/bin/sh
set -e

export PATH="/app/.venv/bin:$PATH"

if echo "$1" | grep -q "uvicorn"; then
    echo "Applying migrations..."
    alembic upgrade head
    
    echo "Cleaning database..."
    python scripts/clean_db.py
    
    echo "Seeding database..."
    python scripts/seed_db.py
fi

echo "Starting: $@"
exec "$@"
