#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Applying migrations..."
python manage.py migrate

echo "Importing products..."
python manage.py import_products products_ru_500.csv

echo "Creating or updating admin user..."
python manage.py create_admin

echo "Build finished successfully."