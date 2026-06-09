#!/usr/bin/env bash
# build.sh — Run by Render during deployment
#
# This script runs ONCE every time you deploy.
# It prepares the app for production.
set -o errexit  # Exit immediately if any command fails

# Install Python dependencies
pip install -r requirements.txt

# Collect all static files into /staticfiles/ (served by WhiteNoise)
python manage.py collectstatic --no-input

# Run database migrations (creates/updates tables in PostgreSQL)
python manage.py migrate
