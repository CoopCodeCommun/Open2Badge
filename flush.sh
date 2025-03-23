#!/bin/bash
set -e

touch db.sqlite3
rm db.sqlite3
rm -rf core/migrations/*
mkdir -p media/badges
rm -rf media/badges/*
touch core/migrations/__init__.py

poetry run python manage.py makemigrations
poetry run python manage.py migrate

poetry run python manage.py loaddata fixtures/badges.json
poetry run coverage run manage.py test core.tests -v 2