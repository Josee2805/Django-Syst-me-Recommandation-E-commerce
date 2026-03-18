def precision_at_k(recommended_ids, relevant_ids, k=10):
    """Precision@K: fraction of top-K recs that are relevant."""
    if not recommended_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / k


def recall_at_k(recommended_ids, relevant_ids, k=10):
    """Recall@K: fraction of relevant items that appear in top-K."""
    if not relevant_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / len(relevant_ids)


def f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluate_recommender(user, recommendation_ids, threshold=4):
    """Evaluate recommendations for a given user."""
    from .models import Rating
    high_rated = Rating.objects.filter(user=user, score__gte=threshold).values_list('product_id', flat=True)
    relevant_ids = list(high_rated)

    p = precision_at_k(recommendation_ids, relevant_ids)
    r = recall_at_k(recommendation_ids, relevant_ids)
    f1 = f1_score(p, r)

    return {
        'precision': round(p, 3),
        'recall': round(r, 3),
        'f1': round(f1, 3),
        'relevant_count': len(relevant_ids),
        'recommended_count': len(recommendation_ids),
    }
