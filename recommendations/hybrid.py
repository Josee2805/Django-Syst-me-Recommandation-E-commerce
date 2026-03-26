from .collaborative import user_based_recommendations, item_based_recommendations, cluster_based_recommendations
from .content_based import content_based_for_user
from .models import Rating, Product


def hybrid_recommendations(user, n=12, alpha=0.5):
    """
    Recommandeur hybride: alpha * collaboratif + (1-alpha) * contenu.
    Gere le cold start automatiquement.
    """
    all_products = Product.objects.select_related('category').all()
    ratings_qs   = Rating.objects.all()
    user_ratings = ratings_qs.filter(user=user)

    # Cold start: l'utilisateur n'a pas encore de notes
    if user_ratings.count() == 0:
        return cold_start_recommendations(user, all_products, n)

    rated_ids = list(user_ratings.values_list('product_id', flat=True))

    # Scores collaboratifs (user-based + item-based combines)
    user_recs = user_based_recommendations(user.id, ratings_qs, n=n * 2)
    item_recs = item_based_recommendations(user.id, ratings_qs, n=n * 2)

    collab_scores = {}
    for i, pid in enumerate(user_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(user_recs) - i)
    for i, pid in enumerate(item_recs):
        collab_scores[pid] = collab_scores.get(pid, 0) + (len(item_recs) - i)

    # Scores contenu
    content_recs = content_based_for_user(rated_ids, all_products, n=n * 2)
    content_scores = {pid: len(content_recs) - i for i, pid in enumerate(content_recs)}

    # Normaliser et fusionner
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


# ── Cold Start ────────────────────────────────────────────────────────────────

BUDGET_MAX_PRICE = {
    'petit': 30000,
    'moyen': 100000,
    # 'illimite': pas de filtre prix
}

PRIORITY_SORT = {
    'prix':       'price',
    'qualite':    '-avg_rating',
    'promotions': '-discount_flag',
    'nouveautes': '-created_at',
}


def _resolve_category_slugs(interests):
    """
    Resout les mots-cles d'interet en slugs de categories existantes dans la DB.
    Essaie d'abord un match exact sur le slug, puis un match insensible a la casse
    sur le nom. Retourne uniquement les slugs trouves.
    """
    from .models import Category

    # Mapping direct interet → slug probable (ajustable sans migration)
    SLUG_HINTS = {
        'mode':         'mode',
        'electronique': 'electronique',
        'maison':       'maison',
        'sport':        'sport',
        'beaute':       'beaute',
        'alimentation': 'cuisine',
    }

    resolved = []
    for interest in interests:
        hint = SLUG_HINTS.get(interest, interest)

        # 1. Match exact sur le slug
        if Category.objects.filter(slug=hint).exists():
            resolved.append(hint)
            continue

        # 2. Match partiel sur le slug
        cat = Category.objects.filter(slug__icontains=interest).first()
        if cat:
            resolved.append(cat.slug)
            continue

        # 3. Match sur le nom
        cat = Category.objects.filter(name__icontains=interest).first()
        if cat:
            resolved.append(cat.slug)

    return resolved


def cold_start_recommendations(user, all_products, n=12, exclude_ids=None):
    """
    Pour un nouvel utilisateur sans notes:
    1. Cluster de profil  → notes des membres du cluster.
    2. Filtrage par profil (interet + budget + priorite).
    3. Produits populaires/vedettes.
    """
    from .models import CustomUser

    exclude_ids = list(exclude_ids or [])

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
            # Exclure les produits deja vus
            cluster_recs = [p for p in cluster_recs if p.id not in exclude_ids]
        if cluster_recs:
            return cluster_recs

        # Fallback: filtrage par profil
        return _profile_based_recommendations(user, all_products, n, exclude_ids)

    # Aucun profil: popularite
    return _popular_recommendations(all_products, n, exclude_ids)


def _profile_based_recommendations(user, all_products, n, exclude_ids):
    """
    Filtre et trie les produits selon le profil onboarding:
    - Categories correspondant aux centres d'interet
    - Prix max selon le budget
    - Tri selon la priorite d'achat
    Complemente avec des produits populaires si insuffisant.
    """
    from django.db.models import Avg, Count, Case, When, IntegerField

    interests = user.interests_list()
    budget    = user.budget
    priority  = user.purchase_priority

    qs = all_products.exclude(id__in=exclude_ids).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings'),
        has_discount=Case(
            When(original_price__isnull=False, then=1),
            default=0,
            output_field=IntegerField(),
        ),
    )

    # Filtre categories selon les centres d'interet
    interest_slugs = _resolve_category_slugs(interests) if interests else []
    if interest_slugs:
        qs = qs.filter(category__slug__in=interest_slugs)

    # Filtre budget
    max_price = BUDGET_MAX_PRICE.get(budget)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    # Tri selon la priorite d'achat
    if priority == 'prix':
        qs = qs.order_by('price', '-avg_rating')
    elif priority == 'qualite':
        qs = qs.order_by('-avg_rating', '-is_featured', '-rating_count')
    elif priority == 'promotions':
        qs = qs.filter(original_price__isnull=False).order_by('-avg_rating', '-is_featured')
    elif priority == 'nouveautes':
        qs = qs.order_by('-created_at', '-avg_rating')
    else:
        qs = qs.order_by('-is_featured', '-avg_rating', '-rating_count')

    result = list(qs[:n])

    # Completer avec des produits populaires si pas assez de resultats
    if len(result) < n:
        existing_ids = [p.id for p in result] + list(exclude_ids)
        # Essayer sans le filtre categorie si peu de resultats
        if interest_slugs and len(result) < n // 2:
            result += _profile_based_no_category(user, all_products, n - len(result), existing_ids)
        else:
            result += _popular_recommendations(all_products, n - len(result), existing_ids)

    return result[:n]


def _profile_based_no_category(user, all_products, n, exclude_ids):
    """Meme logique que _profile_based mais sans filtre de categorie (fallback)."""
    from django.db.models import Avg, Count

    budget   = user.budget
    priority = user.purchase_priority

    qs = all_products.exclude(id__in=exclude_ids).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings'),
    )

    max_price = BUDGET_MAX_PRICE.get(budget)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    if priority == 'prix':
        qs = qs.order_by('price', '-avg_rating')
    elif priority == 'qualite':
        qs = qs.order_by('-avg_rating', '-is_featured')
    elif priority == 'promotions':
        qs = qs.filter(original_price__isnull=False).order_by('-avg_rating')
    elif priority == 'nouveautes':
        qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('-is_featured', '-avg_rating', '-rating_count')

    return list(qs[:n])


def _popular_recommendations(all_products, n, exclude_ids):
    """Produits populaires/vedettes, sans critere de profil."""
    from django.db.models import Avg, Count

    return list(
        all_products.exclude(id__in=exclude_ids).annotate(
            avg_rating=Avg('ratings__score'),
            rating_count=Count('ratings'),
        ).order_by('-is_featured', '-avg_rating', '-rating_count')[:n]
    )
