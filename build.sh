#!/usr/bin/env bash
# Script de build pour Render (Web Service)

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrat

echo "==> Installation des dépendances..."
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "==> Application des migrations..."
python manage.py migrate

echo "==> Build terminé ✓"
