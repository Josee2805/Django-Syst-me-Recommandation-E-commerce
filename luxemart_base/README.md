# ✨ LuxeMart — Système de Recommandation E-commerce

Projet Django académique — Groupe 9

---

## 🚀 Installation & démarrage

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd luxemart

# 2. Créer et activer l'environnement virtuel
python -m venv venv
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données
python manage.py migrate

# 5. Créer un superuser admin
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

→ http://127.0.0.1:8000

---

## 🌿 Workflow Git — 3 branches

### Initialisation (une seule fois, chef de projet)
```bash
git init
git add .
git commit -m "init: base LuxeMart — modèles, urls, vues stub, templates"
git branch -M main
git remote add origin <url-du-repo>
git push -u origin main
```

### Chaque personne crée SA branche depuis main
```bash
# Personne A
git checkout main
git pull origin main
git checkout -b feature/auth-onboarding

# Personne B
git checkout main
git pull origin main
git checkout -b feature/catalogue-cart

# Personne C
git checkout main
git pull origin main
git checkout -b feature/recommendations
```

### Workflow quotidien
```bash
# Avant de commencer à travailler
git pull origin main          # récupérer les dernières modifs de main

# Après avoir codé
git add <fichiers de ta section>
git commit -m "feat(auth): vérification email"
git push origin feature/auth-onboarding
```

### Merge final dans main
```bash
git checkout main
git merge feature/auth-onboarding --no-ff -m "merge: auth & onboarding"
git merge feature/catalogue-cart  --no-ff -m "merge: catalogue & cart"
git merge feature/recommendations --no-ff -m "merge: recommendation engine"
python manage.py migrate
```

---

## 📂 Structure du projet

```
luxemart/
├── manage.py
├── requirements.txt
├── .gitignore
├── ecommerce_reco/
│   ├── settings.py          ← Config Django
│   └── urls.py              ← Routes racine
└── recommendations/
    ├── models.py            ← ⚠ SECTIONS A + B + C
    ├── views.py             ← ⚠ SECTIONS A + B + C
    ├── urls.py              ← ⚠ SECTIONS A + B + C
    ├── admin.py
    ├── apps.py
    ├── context_processors.py  ← Personne B
    ├── forms.py               ← Personne A
    ├── tokens.py              ← Personne A
    ├── collaborative.py       ← Personne C
    ├── content_based.py       ← Personne C
    ├── hybrid.py              ← Personne C
    ├── evaluation.py          ← Personne C
    ├── static/css/            ← Personne B
    ├── static/js/             ← Personne B
    └── templates/
        ├── recommendations/base.html  ← Base commune (ne pas modifier)
        ├── auth/              ← Personne A
        ├── onboarding/        ← Personne A
        ├── shop/              ← Personne B
        └── recommendations/   ← Personne C
```

---

## ⚠️ Convention fichiers partagés

`models.py`, `views.py` et `urls.py` sont partagés entre les 3 personnes.

**Règle absolue** : chaque personne écrit **uniquement dans SA section balisée** :

```python
# ════════════════════════════════════
# ═══ SECTION A — AUTH & ONBOARDING ═
# ════════════════════════════════════
# ... code Personne A ...

# ════════════════════════════════════
# ═══ SECTION B — CATALOGUE & CART  ═
# ════════════════════════════════════
# ... code Personne B ...

# ════════════════════════════════════
# ═══ SECTION C — RECOMMANDATIONS   ═
# ════════════════════════════════════
# ... code Personne C ...
```

Ne **jamais** modifier la section d'une autre personne.

---

## 👥 Répartition des tâches

### Personne A — `feature/auth-onboarding`
- `forms.py` — RegisterForm, LoginForm, ProfileEditForm, OnboardingStepForm
- `tokens.py` — EmailVerificationTokenGenerator
- `templates/auth/` — login, register, verification_sent, resend_verification
- `templates/onboarding/` — start, step, complete
- `models.py` section A — UserProfile, EmailVerificationToken, OnboardingQuestion, etc.
- `views.py` section A — register, login, logout, verify_email, onboarding_*
- `settings.py` — configuration email (EMAIL_BACKEND)

### Personne B — `feature/catalogue-cart`
- `templates/shop/` — home, products, product_detail, cart, profile
- `static/css/` et `static/js/`
- `context_processors.py`
- `models.py` section B — Category, Product, Rating, Comment, Cart, Order...
- `views.py` section B — home, products, product_detail, cart_*, profile
- `admin.py` — enregistrement des modèles
- `seed_data.py` — données de test

### Personne C — `feature/recommendations`
- `collaborative.py` — filtrage collaboratif user-based & item-based
- `content_based.py` — filtrage par contenu (TF-IDF + cosinus)
- `hybrid.py` — système hybride + cold start
- `evaluation.py` — Precision@K, Recall@K, F1
- `views.py` section C — recommendations_view
- `templates/recommendations/recommendations.html`

---

## 🗃️ Commandes utiles

```bash
# Après modification des modèles
python manage.py makemigrations
python manage.py migrate

# Générer les données de test (Personne B)
python manage.py seed_data

# Générer les questions d'onboarding (Personne A)
python manage.py seed_onboarding

# Accès admin
# http://127.0.0.1:8000/admin/
# → Login : superuser créé à l'étape 5

# Compte démo après seed
# Email    : demo@luxemart.com
# Password : demo1234
```

---

## 📦 Dépendances

| Package | Usage |
|---------|-------|
| Django 4.2 | Framework web |
| numpy | Calculs matriciels |
| scikit-learn | TF-IDF, cosine_similarity |
| pandas | Manipulation de données |
| Pillow | Gestion des images |
| six | Tokens de vérification |
