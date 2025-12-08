#!/bin/sh

echo "Applying migrations..."
uv run alembic upgrade head

uv run python scripts/seed_db.py

echo "Starting the application..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
