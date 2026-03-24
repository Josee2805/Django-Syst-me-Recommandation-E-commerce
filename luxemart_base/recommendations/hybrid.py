"""
LuxeMart — recommendations/hybrid.py
BRANCHE : feature/recommendations — Personne C UNIQUEMENT

Système hybride : combine collaboratif + contenu.
Gère le cold start (nouvel utilisateur sans historique).
"""

from .collaborative import get_user_based_recommendations, get_item_based_recommendations
from .content_based import get_content_based_recommendations, _get_popular_products


# Poids du système hybride (modifiables)
COLLAB_WEIGHT = 0.5
CONTENT_WEIGHT = 0.5


def get_hybrid_recommendations(user_id, n=10):
    """
    Combine les scores collaboratifs et contenu avec pondération.

    Cold start :
      - Aucune note → retourne les produits populaires
      - Peu de notes (< 3) → contenu seul
      - Assez de notes → hybride

    Retourne une liste de product_ids.
    """
    from .models import Rating

    rating_count = Rating.objects.filter(user_id=user_id).count()

    # ── Cold start total ──
    if rating_count == 0:
        return _cold_start_recommendations(user_id, n)

    # ── Cold start partiel : contenu seul ──
    if rating_count < 3:
        return get_content_based_recommendations(user_id, n)

    # ── Hybride ──
    collab_ids = get_user_based_recommendations(user_id, n * 2)
    content_ids = get_content_based_recommendations(user_id, n * 2)

    # Fusionner avec scores pondérés
    score_map = {}
    for rank, pid in enumerate(collab_ids):
        score_map[str(pid)] = score_map.get(str(pid), 0) + COLLAB_WEIGHT * (1 / (rank + 1))
    for rank, pid in enumerate(content_ids):
        score_map[str(pid)] = score_map.get(str(pid), 0) + CONTENT_WEIGHT * (1 / (rank + 1))

    ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

    # Reconvertir en PKs
    from .models import Product
    valid_pks = set(str(p.pk) for p in Product.objects.filter(is_active=True).only('pk'))
    result = [pk for pk, _ in ranked if pk in valid_pks]
    return result[:n]


def _cold_start_recommendations(user_id, n=10):
    """
    Pour un nouvel utilisateur :
    1. Utilise ses préférences d'onboarding si disponibles.
    2. Sinon retourne les produits les plus populaires.
    """
    from .models import UserPreference, Product
    from django.db.models import Avg, Count

    try:
        prefs = UserPreference.objects.get(user_id=user_id)
        if prefs.preferred_categories:
            qs = (Product.objects
                  .filter(is_active=True, category_id__in=prefs.preferred_categories)
                  .annotate(avg=Avg('ratings__score'), cnt=Count('ratings'))
                  .order_by('-avg', '-cnt')
                  .values_list('pk', flat=True)[:n])
            result = list(qs)
            if result:
                return result
    except UserPreference.DoesNotExist:
        pass

    return _get_popular_products(n)
