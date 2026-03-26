#!/usr/bin/env bash
# Script de build pour Render (Web Service)
# Appelé automatiquement à chaque déploiement

set -o errexit   # Quitter immédiatement si une commande échoue

echo "==> Installation des dépendances..."
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "==> Application des migrations..."
python manage.py migrate

echo "==> Chargement des données initiales (catégories + produits)..."
python manage.py seed_data

echo "==> Création du superuser si inexistant..."
python manage.py create_superuser_if_none

echo "==> Build terminé ✓"
