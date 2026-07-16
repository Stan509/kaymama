#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Django Pre-Deployment Tasks ==="

echo "1. Running database migrations..."
python manage.py migrate --noinput

echo "2. Seeding restaurant database..."
python manage.py seed_restaurant

echo "3. Collecting static files..."
python manage.py collectstatic --noinput

echo "=== All Pre-Deployment Tasks Completed Successfully! ==="
