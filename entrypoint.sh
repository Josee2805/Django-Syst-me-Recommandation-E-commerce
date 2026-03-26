#!/usr/bin/env bash
set -e

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "==> Application des migrations..."
python manage.py migrate

echo "==> Chargement des données initiales..."
python manage.py seed_data

echo "==> Création du superuser si inexistant..."
python manage.py create_superuser_if_none

echo "==> Démarrage du serveur Gunicorn..."
exec gunicorn ecommerce_reco.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
