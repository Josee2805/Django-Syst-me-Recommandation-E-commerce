"""
LuxeMart — recommendations/evaluation.py
BRANCHE : feature/recommendations — Personne C UNIQUEMENT

Calcul de Precision@K et Recall@K.
"""


def precision_at_k(recommended, relevant, k=10):
    """
    Precision@K : parmi les K recommandations, combien sont pertinentes ?
    recommended : liste de product_ids recommandés
    relevant    : ensemble de product_ids pertinents (ex: notés >= 4)
    """
    if not recommended or k == 0:
        return 0.0
    top_k = recommended[:k]
    hits = len(set(str(pid) for pid in top_k) & set(str(pid) for pid in relevant))
    return hits / k


def recall_at_k(recommended, relevant, k=10):
    """
    Recall@K : parmi tous les éléments pertinents, combien ont été recommandés ?
    """
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    hits = len(set(str(pid) for pid in top_k) & set(str(pid) for pid in relevant))
    return hits / len(relevant)


def evaluate_user(user_id, k=10):
    """
    Évalue le système pour un utilisateur donné.
    Stratégie leave-one-out : on retire les produits notés >= 4
    et on vérifie si le système les recommande.

    Retourne {'precision': float, 'recall': float, 'f1': float}
    """
    from .models import Rating
    from .hybrid import get_hybrid_recommendations

    # Produits pertinents = notes >= 4
    relevant = list(
        Rating.objects.filter(user_id=user_id, score__gte=4)
                      .values_list('product_id', flat=True)
    )
    if not relevant:
        return {'precision': 0, 'recall': 0, 'f1': 0}

    recommended = get_hybrid_recommendations(user_id, n=k)

    p = precision_at_k(recommended, relevant, k)
    r = recall_at_k(recommended, relevant, k)
    f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0

    return {'precision': round(p, 4), 'recall': round(r, 4), 'f1': round(f1, 4)}


def evaluate_all_users(k=10):
    """
    Évalue le système sur tous les utilisateurs actifs.
    Retourne les métriques moyennes.
    """
    from django.contrib.auth.models import User

    users = User.objects.filter(is_active=True)
    results = []
    for user in users:
        metrics = evaluate_user(user.id, k)
        if metrics['precision'] > 0 or metrics['recall'] > 0:
            results.append(metrics)

    if not results:
        return {'precision': 0, 'recall': 0, 'f1': 0, 'users_evaluated': 0}

    return {
        'precision': round(sum(r['precision'] for r in results) / len(results), 4),
        'recall':    round(sum(r['recall']    for r in results) / len(results), 4),
        'f1':        round(sum(r['f1']        for r in results) / len(results), 4),
        'users_evaluated': len(results),
    }
