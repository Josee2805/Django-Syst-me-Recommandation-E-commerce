from .collaborative import user_based_recommendations, item_based_recommendations, cluster_based_recommendations
from .content_based import content_based_for_user
from .models import Rating, Product


def hybrid_recommendations(user, n=12, alpha=0.5):
    """
    Hybrid recommender: alpha * collaborative + (1-alpha) * content_based.
    Handles cold start automatically.
    """
    all_products = Product.objects.select_related('category').all()
    ratings_qs   = Rating.objects.all()
    user_ratings = ratings_qs.filter(user=user)

    # Cold start: user has no ratings yet
    if user_ratings.count() == 0:
        return cold_start_recommendations(user, all_products, n)

    rated_ids = list(user_ratings.values_list('product_id', flat=True))

    # Collaborative scores (user-based + item-based combined)
    user_recs = user_based_recommendations(user.id, ratings_qs, n=n * 2)
    item_recs = item_based_recommendations(user.id, ratings_qs, n=n * 2)

    collab_scores = {}
    for i, pid in enumerate(user_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(user_recs) - i)
    for i, pid in enumerate(item_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(item_recs) - i)

    # Content-based scores
    content_recs = content_based_for_user(rated_ids, all_products, n=n * 2)
    content_scores = {}
    for i, pid in enumerate(content_recs):
        content_scores[pid] = len(content_recs) - i

    # Normalize and merge
    max_c  = max(collab_scores.values(), default=1) or 1
    max_cb = max(content_scores.values(), default=1) or 1

    all_ids = set(collab_scores.keys()) | set(content_scores.keys())

    final_scores = {}
    for pid in all_ids:
        if pid in rated_ids:
            continue
        c_score  = collab_scores.get(pid, 0) / max_c
        cb_score = content_scores.get(pid, 0) / max_cb
        final_scores[pid] = alpha * c_score + (1 - alpha) * cb_score

    sorted_ids = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

    if not sorted_ids:
        return cold_start_recommendations(user, all_products, n, exclude_ids=rated_ids)

    top_ids  = [pid for pid, _ in sorted_ids[:n]]
    products = {p.id: p for p in all_products.filter(id__in=top_ids)}
    return [products[pid] for pid in top_ids if pid in products]


# ── Mapping interet onboarding -> slug categorie ──────────────────────────────

INTEREST_TO_SLUG = {
    'mode':          'mode',
    'electronique':  'electronique',
    'maison':        'maison',
    'sport':         'sport',
    'beaute':        'beaute',
    'alimentation':  'cuisine',
}

BUDGET_MAX_PRICE = {
    'petit':  30000,
    'moyen':  100000,
    # 'illimite': pas de filtre
}


def cold_start_recommendations(user, all_products, n=12, exclude_ids=None):
    """
    Pour un nouvel utilisateur sans notes:
    1. Essaie les recommandations basees sur le cluster de profil.
    2. Sinon, filtre par profil (interet, budget, priorite).
    3. Sinon, produits populaires/vedettes.
    """
    from .models import CustomUser

    exclude_ids = exclude_ids or []

    if user and getattr(user, 'onboarding_done', False):
        # Tentative cluster
        cluster_recs = cluster_based_recommendations(
            user,
            CustomUser.objects.all(),
            Rating.objects.all(),
            all_products,
            n=n,
        )
        if cluster_recs:
            return cluster_recs

        # Fallback: filtre par profil
        return _profile_based_recommendations(user, all_products, n, exclude_ids)

    # Aucun profil: popularite
    return _popular_recommendations(all_products, n, exclude_ids)


def _profile_based_recommendations(user, all_products, n, exclude_ids):
    """Filtre les produits selon les preferences du profil utilisateur."""
    from django.db.models import Avg, Count

    interests = user.interests_list()
    budget    = user.budget
    priority  = user.purchase_priority

    qs = all_products.exclude(id__in=exclude_ids).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings'),
    )

    # Filtre par categories d'interet
    if interests:
        slugs = [INTEREST_TO_SLUG.get(i, i) for i in interests]
        qs = qs.filter(category__slug__in=slugs)

    # Filtre par budget
    max_price = BUDGET_MAX_PRICE.get(budget)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    # Tri selon la priorite
    if priority == 'prix':
        qs = qs.order_by('price')
    elif priority == 'qualite':
        qs = qs.order_by('-avg_rating', '-is_featured')
    elif priority == 'promotions':
        qs = qs.filter(original_price__isnull=False).order_by('-is_featured', '-avg_rating')
    elif priority == 'nouveautes':
        qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('-is_featured', '-avg_rating', '-rating_count')

    result = list(qs[:n])

    # Completement avec des produits populaires si pas assez de resultats
    if len(result) < n:
        existing_ids = [p.id for p in result] + list(exclude_ids)
        result += _popular_recommendations(all_products, n - len(result), existing_ids)

    return result


def _popular_recommendations(all_products, n, exclude_ids):
    """Produits populaires/vedettes, sans critere de profil."""
    from django.db.models import Avg, Count

    return list(
        all_products.exclude(id__in=exclude_ids).annotate(
            avg_rating=Avg('ratings__score'),
            rating_count=Count('ratings'),
        ).order_by('-is_featured', '-avg_rating', '-rating_count')[:n]
    )
