from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
<<<<<<< Updated upstream
SECRET_KEY = 'django-insecure-luxemart-secret-key-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']
=======

load_dotenv(BASE_DIR / '.env')

# ── Sécurité ──────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
>>>>>>> Stashed changes

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recommendations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
<<<<<<< Updated upstream
=======
    'whitenoise.middleware.WhiteNoiseMiddleware',
>>>>>>> Stashed changes
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
                'recommendations.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_reco.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'recommendations' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'recommendations.CustomUser'
LOGIN_URL = '/login/'
<<<<<<< Updated upstream
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
=======
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/landing/'

# ── EMAIL ──────────────────────────────────────────────────────
# Les identifiants viennent du .env (ne jamais écrire ici)
#
# Pour tester en local avec Mailtrap :
#   EMAIL_HOST=sandbox.smtp.mailtrap.io
#   EMAIL_PORT=2525
#   EMAIL_HOST_USER=ton_user_mailtrap
#   EMAIL_HOST_PASSWORD=ton_mdp_mailtrap
#
# Pour Gmail en production :
#   EMAIL_HOST=smtp.gmail.com
#   EMAIL_PORT=587
#   EMAIL_HOST_USER=ton@gmail.com
#   EMAIL_HOST_PASSWORD=mot_de_passe_application_16_car

_email_user = os.environ.get('EMAIL_HOST_USER', '')
_email_pass = os.environ.get('EMAIL_HOST_PASSWORD', '')

if _email_user and _email_pass:
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS       = True
    EMAIL_HOST_USER     = _email_user
    EMAIL_HOST_PASSWORD = _email_pass
    DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', f'RecoShop <{_email_user}>')
else:
    # Pas de credentials → affiche les emails dans le terminal
    # + le code s'affiche sur la page de vérification (mode test)
    EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'RecoShop <noreply@recoshop.com>'
>>>>>>> Stashed changes
