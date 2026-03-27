#!/usr/bin/env bash
# Script de build pour Render (Web Service)

set -o errexit

echo "==> Installation des dépendances..."
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "==> Application des migrations..."
python manage.py migrate
python manage.py seed_data

echo "==> Build terminé ✓"
