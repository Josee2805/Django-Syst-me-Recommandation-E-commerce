import numpy as np
from collections import defaultdict


def build_user_item_matrix(ratings_qs):
    """Build user-item matrix from ratings queryset."""
    ratings_list = list(ratings_qs)
    user_ids = list({r.user_id for r in ratings_list})
    item_ids = list({r.product_id for r in ratings_list})

    user_idx = {uid: i for i, uid in enumerate(user_ids)}
    item_idx = {iid: i for i, iid in enumerate(item_ids)}

    matrix = np.zeros((len(user_ids), len(item_ids)))
    for r in ratings_list:
        matrix[user_idx[r.user_id]][item_idx[r.product_id]] = r.score

    return matrix, user_ids, item_ids, user_idx, item_idx


def cosine_similarity_matrix(matrix):
    """Compute cosine similarity between rows."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized = matrix / norms
    return normalized @ normalized.T


def user_based_recommendations(target_user_id, ratings_qs, n=10, n_similar=5):
    """
    User-based collaborative filtering avec boost profil CustomUser.
    Si 2+ intérêts communs → +0.2 similarité.
    Si même budget ET même genre → +0.1 similarité.
    """
    from .models import CustomUser

    if ratings_qs.count() < 2:
        return []

    matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)

    if target_user_id not in user_idx:
        return []

    sim_matrix = cosine_similarity_matrix(matrix)
    target_idx = user_idx[target_user_id]
    similarities = sim_matrix[target_idx].copy()

    # ── Boost profil ──────────────────────────────────────────────────────────
    try:
        users_map = {u.pk: u for u in CustomUser.objects.filter(pk__in=user_ids)}
        target_user = users_map.get(target_user_id)

        if target_user:
            target_interests = set(target_user.interests_list())

            for uid, uidx in user_idx.items():
                if uid == target_user_id:
                    continue
                other = users_map.get(uid)
                if not other:
                    continue

                # Boost intérêts communs
                common = target_interests & set(other.interests_list())
                if len(common) >= 2:
                    similarities[uidx] = min(similarities[uidx] + 0.2, 1.0)

                # Boost même budget + même genre
                if (target_user.budget and target_user.budget == other.budget and
                        target_user.gender and target_user.gender == other.gender):
                    similarities[uidx] = min(similarities[uidx] + 0.1, 1.0)
    except Exception:
        pass

    # ── Calcul des recommandations ────────────────────────────────────────────
    similar_indices = np.argsort(similarities)[::-1][1:n_similar + 1]
    target_rated = set(np.where(matrix[target_idx] > 0)[0])

    scores    = defaultdict(float)
    sim_sums  = defaultdict(float)

    for sidx in similar_indices:
        sim = similarities[sidx]
        if sim <= 0:
            continue
        for iidx, rating in enumerate(matrix[sidx]):
            if rating > 0 and iidx not in target_rated:
                scores[iidx]   += sim * rating
                sim_sums[iidx] += sim

    predicted = {
        item_ids[iidx]: score / sim_sums[iidx]
        for iidx, score in scores.items()
        if sim_sums[iidx] > 0
    }

    return [pid for pid, _ in sorted(predicted.items(), key=lambda x: x[1], reverse=True)[:n]]


def item_based_recommendations(target_user_id, ratings_qs, n=10):
    """Item-based collaborative filtering."""
    if ratings_qs.count() < 2:
        return []

    matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)

    if target_user_id not in user_idx:
        return []

    item_sim     = cosine_similarity_matrix(matrix.T)
    target_idx   = user_idx[target_user_id]
    target_ratings = matrix[target_idx]

    rated_items   = np.where(target_ratings > 0)[0]
    unrated_items = np.where(target_ratings == 0)[0]

    scores = {}
    for iidx in unrated_items:
        weighted_sum = 0
        sim_sum      = 0
        for rated_iidx in rated_items:
            sim = item_sim[iidx][rated_iidx]
            if sim > 0:
                weighted_sum += sim * target_ratings[rated_iidx]
                sim_sum      += sim
        if sim_sum > 0:
            scores[item_ids[iidx]] = weighted_sum / sim_sum

    return [pid for pid, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]]
