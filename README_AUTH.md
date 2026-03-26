# 🔐 Branche feature/auth-onboarding

## Ce que cette branche ajoute

Système complet d'authentification avec :
- Inscription (email + username + mot de passe)
- Vérification par **code OTP à 6 chiffres** envoyé par email
- Connexion par email + mot de passe
- **Questionnaire d'onboarding** (6 questions de préférences)
- Gestion du fallback si SMTP non configuré (code affiché à l'écran)

---

## Fichiers modifiés / ajoutés

| Fichier | Action |
|---------|--------|
| `recommendations/models.py` | Ajout de `EmailVerificationCode` et `OnboardingAnswer` |
| `recommendations/views.py` | Remplacement auth + ajout onboarding |
| `recommendations/urls.py` | Ajout routes `/verify-code/`, `/resend-code/`, `/onboarding/` |
| `ecommerce_reco/settings.py` | Config email intelligente (Gmail / Mailtrap / console) |
| `templates/recommendations/register.html` | Nouveau design inscription |
| `templates/recommendations/login.html` | Mise à jour connexion |
| `templates/recommendations/verify_code.html` | Page saisie du code OTP |
| `templates/recommendations/emails/otp_code.html` | Email HTML avec le code |
| `templates/recommendations/onboarding/start.html` | Introduction onboarding |
| `templates/recommendations/onboarding/step.html` | Étape questionnaire |
| `templates/recommendations/onboarding/complete.html` | Fin onboarding |

---

## Installation

```bash
# 1. Se placer sur la branche
git checkout feature/auth-onboarding

# 2. Installer les dépendances (si pas déjà fait)
pip install -r requirements.txt

# 3. Créer les migrations pour les nouveaux modèles
python manage.py makemigrations
python manage.py migrate

# 4. Lancer le serveur
python manage.py runserver
```

---

## Configuration email

Créer un fichier `.env` à la racine du projet :

```bash
# Option A — Mailtrap (test en local, recommandé)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=ton_user_mailtrap
EMAIL_HOST_PASSWORD=ton_mdp_mailtrap

# Option B — Gmail (production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=ton@gmail.com
EMAIL_HOST_PASSWORD=mot_de_passe_application_16_car
```

Sans `.env` → le code apparaît directement sur la page de vérification (bandeau jaune).

---

## Flux utilisateur

```
/register/     → Saisie email + username + mot de passe
      ↓
/verify-code/  → Saisie du code à 6 chiffres reçu par email
      ↓
/onboarding/   → Page de bienvenue
      ↓
/onboarding/1/ → Question 1 : genre
/onboarding/2/ → Question 2 : catégories (max 3)
/onboarding/3/ → Question 3 : budget
/onboarding/4/ → Question 4 : priorité d'achat
/onboarding/5/ → Question 5 : fréquence d'achat
/onboarding/6/ → Question 6 : mode de découverte
      ↓
/onboarding/done/ → Confirmation + redirect /home/
```

---

## Git — merger avec main

```bash
git checkout main
git merge feature/auth-onboarding --no-ff -m "feat(auth): OTP + onboarding"
python manage.py migrate
```
