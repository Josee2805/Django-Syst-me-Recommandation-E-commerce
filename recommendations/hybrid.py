from .collaborative import user_based_recommendations, item_based_recommendations
from .content_based import content_based_for_user
from .models import Rating, Product


def hybrid_recommendations(user, n=12, alpha=0.5):
    """
    Hybrid recommender: alpha * collaborative + (1-alpha) * content_based.
    Handles cold start automatically.
    """
    all_products = Product.objects.select_related('category').all()
    ratings_qs = Rating.objects.all()
    user_ratings = ratings_qs.filter(user=user)
    
    # Cold start: user has no ratings
    if user_ratings.count() == 0:
        return cold_start_recommendations(all_products, n)
    
    rated_ids = list(user_ratings.values_list('product_id', flat=True))
    
    # Collaborative scores (user-based + item-based combined)
    user_recs = user_based_recommendations(user.id, ratings_qs, n=n*2)
    item_recs = item_based_recommendations(user.id, ratings_qs, n=n*2)
    
    collab_scores = {}
    for i, pid in enumerate(user_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(user_recs) - i)
    for i, pid in enumerate(item_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(item_recs) - i)
    
    # Content-based scores
    content_recs = content_based_for_user(rated_ids, all_products, n=n*2)
    content_scores = {}
    for i, pid in enumerate(content_recs):
        content_scores[pid] = len(content_recs) - i
    
    # Normalize
    max_c = max(collab_scores.values(), default=1) or 1
    max_cb = max(content_scores.values(), default=1) or 1
    
    all_ids = set(collab_scores.keys()) | set(content_scores.keys())
    
    final_scores = {}
    for pid in all_ids:
        if pid in rated_ids:
            continue
        c_score = collab_scores.get(pid, 0) / max_c
        cb_score = content_scores.get(pid, 0) / max_cb
        final_scores[pid] = alpha * c_score + (1 - alpha) * cb_score
    
    sorted_ids = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_ids:
        return cold_start_recommendations(all_products, n, exclude_ids=rated_ids)
    
    top_ids = [pid for pid, _ in sorted_ids[:n]]
    products = {p.id: p for p in all_products.filter(id__in=top_ids)}
    return [products[pid] for pid in top_ids if pid in products]


def cold_start_recommendations(all_products, n=12, exclude_ids=None):
    """For new users: recommend popular/featured products."""
    from django.db.models import Avg, Count
    exclude_ids = exclude_ids or []
    
    products = all_products.exclude(id__in=exclude_ids).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).order_by('-is_featured', '-avg_rating', '-rating_count')[:n]
    
    return list(products)
