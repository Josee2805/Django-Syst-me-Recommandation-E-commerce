# ✦ LuxeMart — Système de Recommandation E-commerce

Application Django complète de boutique en ligne avec moteur de recommandation hybride.

---

## 🚀 Installation & Lancement

### 1. Prérequis
```bash
Python 3.10+
pip
```

### 2. Environnement virtuel
```bash
python -m venv venv
# Windows :
.\venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install django numpy scikit-learn pandas Pillow
```

### 4. Migrations
```bash
python manage.py migrate
```

### 5. Peupler la base de données (seed)
```bash
python manage.py seed_data
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

Accédez à : **http://127.0.0.1:8000**

---

## 🔑 Comptes de test

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| demo@luxemart.com | demo1234 | Utilisateur démo |
| alice@luxemart.com | pass1234 | Utilisateur test |
| bob@luxemart.com | pass1234 | Utilisateur test |
| admin@luxemart.com | admin1234 | Superadmin |

**Admin Django :** http://127.0.0.1:8000/admin/

---

## 🧠 Algorithmes implémentés

### 1. Filtrage Collaboratif User-Based (`collaborative.py`)
- Construit une matrice utilisateur × produit à partir des notes
- Calcule la similarité cosinus entre utilisateurs
- Recommande les produits aimés par les utilisateurs similaires

### 2. Filtrage Collaboratif Item-Based (`collaborative.py`)
- Calcule la similarité cosinus entre produits (via les notes)
- Pour chaque produit déjà noté, trouve les produits similaires
- Prédit un score pour chaque produit non encore noté

### 3. Filtrage par Contenu (`content_based.py`)
- Crée un vecteur TF-IDF pour chaque produit (nom + catégorie + tags + description + marque)
- Calcule la similarité cosinus entre produits
- Recommande les produits avec le vecteur le plus proche

### 4. Système Hybride (`hybrid.py`)
```
Score final = α × score_collaboratif + (1-α) × score_contenu
```
- Combine les scores normalisés des deux approches (α = 0.5 par défaut)
- **Cold Start** : si l'utilisateur n'a aucune note → produits populaires/vedettes

### 5. Évaluation (`evaluation.py`)
- **Precision@K** : proportion de recommandations pertinentes dans les K premières
- **Recall@K** : proportion de produits pertinents effectivement recommandés
- **F1-Score** : moyenne harmonique de precision et recall
- Un produit est "pertinent" s'il a reçu une note ≥ 4/5

---

## 🗂️ Structure du projet

```
ecommerce_reco/
├── manage.py
├── ecommerce_reco/
│   ├── settings.py
│   └── urls.py
└── recommendations/
    ├── models.py           # CustomUser, Category, Product, Rating, Comment, Cart, Purchase
    ├── views.py            # Toutes les vues
    ├── urls.py             # Routes URL
    ├── collaborative.py    # Filtrage collaboratif (user-based + item-based)
    ├── content_based.py    # Filtrage par contenu (TF-IDF + cosinus)
    ├── hybrid.py           # Système hybride + cold start
    ├── evaluation.py       # Precision, Recall, F1
    ├── context_processors.py
    ├── admin.py
    ├── management/
    │   └── commands/
    │       └── seed_data.py   # python manage.py seed_data
    ├── templates/
    │   └── recommendations/
    │       ├── base.html
    │       ├── login.html
    │       ├── register.html
    │       ├── home.html
    │       ├── products.html
    │       ├── product_detail.html
    │       ├── cart.html
    │       ├── profile.html
    │       ├── recommendations.html
    │       └── partials/
    │           └── product_card.html
    └── static/
        └── css/
            └── main.css
```

---

## 🎨 Design

- **Palette** : Or clair `#D4AF37` + Blanc/Crème — sobre et luxueux
- **Typographie** : Cormorant Garamond (titres) + Jost (corps)
- **Mode sombre/clair** : persisté dans localStorage
- **Responsive** : sidebar rétractable sur mobile
- **Animations** : fadeUp, hover effects, transitions CSS

---

## 📊 Dataset

Le dataset Amazon Reviews 2023 peut être intégré en remplaçant
les données du `seed_data` par les données CSV téléchargées depuis Kaggle.
