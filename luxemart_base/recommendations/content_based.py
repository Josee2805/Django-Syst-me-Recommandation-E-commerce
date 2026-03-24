"""
LuxeMart — recommendations/content_based.py
BRANCHE : feature/recommendations — Personne C UNIQUEMENT

Filtrage par contenu (similarité cosinus sur les attributs produits).
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


def build_product_feature_matrix():
    """
    Construit la matrice de features produits.
    Features = nom + catégorie + tags + marque + description courte.
    Retourne (matrix, product_ids).
    """
    from .models import Product
    products = list(Product.objects.filter(is_active=True).select_related('category'))
    if not products:
        return None, []

    product_ids = [p.pk for p in products]
    corpus = []
    for p in products:
        text = ' '.join([
            p.name,
            p.category.name,
            p.tags,
            p.brand,
            p.short_description,
        ]).lower()
        corpus.append(text)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
    matrix = vectorizer.fit_transform(corpus).toarray()
    return matrix, product_ids


def get_content_based_recommendations(user_id, n=10):
    """
    Recommande des produits similaires à ceux que l'utilisateur a bien notés (>= 3).
    Retourne une liste de product_ids.

    TODO Personne C : implémenter
    """
    from .models import Rating

    matrix, product_ids = build_product_feature_matrix()
    if matrix is None:
        return []

    p_idx = {str(pid): i for i, pid in enumerate(product_ids)}

    # Produits bien notés par l'utilisateur
    good_ratings = Rating.objects.filter(user_id=user_id, score__gte=3).values_list('product_id', flat=True)
    liked_indices = [p_idx[str(pid)] for pid in good_ratings if str(pid) in p_idx]

    if not liked_indices:
        return _get_popular_products(n)

    # Profil utilisateur = moyenne des vecteurs TF-IDF des produits aimés
    user_profile = matrix[liked_indices].mean(axis=0).reshape(1, -1)
    sim = cosine_similarity(user_profile, matrix).flatten()

    # Exclure les produits déjà notés
    already = set(str(pid) for pid in good_ratings)
    scored = [(product_ids[i], s) for i, s in enumerate(sim)
              if str(product_ids[i]) not in already]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [pid for pid, _ in scored[:n]]


def get_similar_products(product_id, n=6):
    """
    Retourne les n produits les plus similaires à product_id.
    Utilisé sur la page détail produit.
    """
    matrix, product_ids = build_product_feature_matrix()
    if matrix is None:
        return []

    p_idx = {str(pid): i for i, pid in enumerate(product_ids)}
    key = str(product_id)
    if key not in p_idx:
        return []

    target_vec = matrix[p_idx[key]].reshape(1, -1)
    sim = cosine_similarity(target_vec, matrix).flatten()
    scored = [(product_ids[i], s) for i, s in enumerate(sim) if str(product_ids[i]) != key]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in scored[:n]]


def _get_popular_products(n=10):
    """Fallback cold start : produits les mieux notés."""
    from .models import Product
    from django.db.models import Avg, Count
    qs = (Product.objects
          .filter(is_active=True)
          .annotate(avg=Avg('ratings__score'), cnt=Count('ratings'))
          .filter(cnt__gte=1)
          .order_by('-avg', '-cnt')
          .values_list('pk', flat=True)[:n])
    return list(qs)
