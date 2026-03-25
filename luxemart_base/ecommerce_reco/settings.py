"""
LuxeMart — settings.py
Fichier de configuration principal (branche main).
Chaque personne ajoute ses paramètres dans SA section balisée.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-luxemart-dev-key-change-in-production-123456'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ─────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Notre app principale
    'recommendations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_reco.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'recommendations' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # ═══ PERSONNE B ajoutera ici son context_processor ═══
                # 'recommendations.context_processors.sidebar_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_reco.wsgi.application'

# ─────────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ─────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# FICHIERS STATIQUES & MEDIA
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'recommendations' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# EMAIL CONFIGURATION
# ─────────────────────────────────────────────
#
# ══ OPTION 1 : Console (défaut) ══
# Le code s'affiche dans le terminal. Aucun vrai mail envoyé.
# Utile pour tester sans config.
#
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#
# ══ OPTION 2 : Gmail SMTP (recommandé en local) ══
# Envoie de vrais emails. Nécessite un mot de passe d'application Gmail.
# Étapes :
#   1. Aller sur https://myaccount.google.com/security
#   2. Activer la validation en 2 étapes
#   3. Chercher "Mots de passe des applications"
#   4. Créer un mot de passe pour "LuxeMart"
#   5. Copier le code à 16 caractères dans EMAIL_HOST_PASSWORD
#
EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST       = 'smtp.gmail.com'
EMAIL_PORT       = 587
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = 'votre.email@gmail.com'   # ← remplacer par ton Gmail
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # ← mot de passe d'application (16 car.)
DEFAULT_FROM_EMAIL = 'LuxeMart <votre.email@gmail.com>'  # ← même adresse

#
# ══ OPTION 3 : Mailtrap (test sans spam) ══
# Capte les emails dans une boîte de test en ligne. Gratuit sur mailtrap.io
#
# EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST       = 'sandbox.smtp.mailtrap.io'
# EMAIL_PORT       = 2525
# EMAIL_USE_TLS    = True
# EMAIL_HOST_USER  = 'ton_user_mailtrap'    # dans Settings > SMTP
# EMAIL_HOST_PASSWORD = 'ton_mdp_mailtrap'
# DEFAULT_FROM_EMAIL = 'LuxeMart <noreply@luxemart.com>'

# ─────────────────────────────────────────────
# MESSAGES
# ─────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
