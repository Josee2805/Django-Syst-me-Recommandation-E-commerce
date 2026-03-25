"""
LuxeMart — recommendations/collaborative.py
BRANCHE : feature/recommendations — Personne C UNIQUEMENT

Filtrage collaboratif user-based et item-based.
Utilise : Rating, Product (définis dans models.py section B)
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def build_user_item_matrix():
    """
    Construit la matrice utilisateur × produit à partir des notes.
    Retourne (matrix, user_ids, product_ids).
    """
    from .models import Rating
    ratings = list(Rating.objects.select_related('user', 'product').all())
    if not ratings:
        return None, [], []

    user_ids = list({r.user_id for r in ratings})
    product_ids = list({r.product_id for r in ratings})

    u_idx = {uid: i for i, uid in enumerate(user_ids)}
    p_idx = {pid: i for i, pid in enumerate(product_ids)}

    matrix = np.zeros((len(user_ids), len(product_ids)))
    for r in ratings:
        matrix[u_idx[r.user_id]][p_idx[r.product_id]] = r.score

    return matrix, user_ids, product_ids


def get_user_based_recommendations(user_id, n=10):
    """
    Recommandations basées sur les utilisateurs similaires.
    Retourne une liste de product_ids.

    TODO Personne C : implémenter
    """
    matrix, user_ids, product_ids = build_user_item_matrix()
    if matrix is None or user_id not in user_ids:
        return []

    u_idx = {uid: i for i, uid in enumerate(user_ids)}
    target_idx = u_idx[user_id]

    # Similarité cosinus entre tous les utilisateurs
    sim = cosine_similarity(matrix)

    # Scores des utilisateurs similaires (excluant l'utilisateur cible)
    sim_scores = list(enumerate(sim[target_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [(i, s) for i, s in sim_scores if i != target_idx and s > 0]

    # Produits déjà notés par la cible
    already_rated = set(
        j for j, v in enumerate(matrix[target_idx]) if v > 0
    )

    # Agréger les scores pondérés des voisins
    score_map = {}
    for neighbor_idx, sim_score in sim_scores[:20]:
        for prod_idx, rating in enumerate(matrix[neighbor_idx]):
            if rating > 0 and prod_idx not in already_rated:
                score_map[prod_idx] = score_map.get(prod_idx, 0) + sim_score * rating

    # Trier par score et retourner les product_ids
    top = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:n]
    return [product_ids[i] for i, _ in top]


def get_item_based_recommendations(user_id, n=10):
    """
    Recommandations basées sur les produits similaires.
    Retourne une liste de product_ids.

    TODO Personne C : implémenter
    """
    matrix, user_ids, product_ids = build_user_item_matrix()
    if matrix is None or user_id not in user_ids:
        return []

    u_idx = {uid: i for i, uid in enumerate(user_ids)}
    target_idx = u_idx[user_id]

    # Similarité item-item (transposée)
    item_sim = cosine_similarity(matrix.T)

    # Produits notés par la cible
    rated = [(j, matrix[target_idx][j]) for j in range(len(product_ids))
             if matrix[target_idx][j] > 0]

    score_map = {}
    for rated_idx, rating in rated:
        for prod_idx, sim_score in enumerate(item_sim[rated_idx]):
            if prod_idx not in {r[0] for r in rated} and sim_score > 0:
                score_map[prod_idx] = score_map.get(prod_idx, 0) + sim_score * rating

    top = sorted(score_map.items(), key=lambda x: x[1], reverse=True)[:n]
    return [product_ids[i] for i, _ in top]
