#!/bin/sh

echo "Applying migrations..."
alembic upgrade head

python scripts/seed_db.py

echo "Starting the application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
