import numpy as np
from collections import defaultdict


def build_user_item_matrix(ratings_qs):
    """Build user-item matrix from ratings queryset."""
    user_ids = list(set(r.user_id for r in ratings_qs))
    item_ids = list(set(r.product_id for r in ratings_qs))
    

    matrix = np.zeros((len(user_ids), len(item_ids)))
    for r in ratings_qs:
        matrix[user_idx[r.user_id]][item_idx[r.product_id]] = r.score
    
    return matrix, user_ids, item_ids, user_idx, item_idx


def cosine_similarity_matrix(matrix):
    """Compute cosine similarity between rows."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    normalized = matrix / norms
    return normalized @ normalized.T


def user_based_recommendations(target_user_id, ratings_qs, n=10, n_similar=5):
    """User-based collaborative filtering."""
    from .models import Rating
    
    if ratings_qs.count() < 2:
        return []

    matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)
    
    if target_user_id not in user_idx:
        return []

    sim_matrix = cosine_similarity_matrix(matrix)
    target_idx = user_idx[target_user_id]
    
    similarities = sim_matrix[target_idx]
    similar_indices = np.argsort(similarities)[::-1][1:n_similar+1]
    
    target_rated = set(np.where(matrix[target_idx] > 0)[0])
    
    scores = defaultdict(float)
    sim_sums = defaultdict(float)
    
    for sidx in similar_indices:
        sim = similarities[sidx]
        if sim <= 0:
            continue
        for iidx, rating in enumerate(matrix[sidx]):
            if rating > 0 and iidx not in target_rated:
                scores[iidx] += sim * rating
                sim_sums[iidx] += sim
    
    predicted = {}
    for iidx, score in scores.items():
        if sim_sums[iidx] > 0:
            predicted[item_ids[iidx]] = score / sim_sums[iidx]
    
    sorted_items = sorted(predicted.items(), key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in sorted_items[:n]]


def item_based_recommendations(target_user_id, ratings_qs, n=10):
    """Item-based collaborative filtering."""
    if ratings_qs.count() < 2:
        return []

    matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)
    
    if target_user_id not in user_idx:
        return []

    item_sim = cosine_similarity_matrix(matrix.T)
    target_idx = user_idx[target_user_id]
    target_ratings = matrix[target_idx]
    
    rated_items = np.where(target_ratings > 0)[0]
    unrated_items = np.where(target_ratings == 0)[0]
    
    scores = {}
    for iidx in unrated_items:
        weighted_sum = 0
        sim_sum = 0
        for rated_iidx in rated_items:
            sim = item_sim[iidx][rated_iidx]
            if sim > 0:
                weighted_sum += sim * target_ratings[rated_iidx]
                sim_sum += sim
        if sim_sum > 0:
            scores[item_ids[iidx]] = weighted_sum / sim_sum
    
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in sorted_items[:n]]
