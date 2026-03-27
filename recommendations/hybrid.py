from .collaborative import user_based_recommendations, item_based_recommendations
from .content_based import content_based_for_user_with_source
from .models import Rating, Product
from django.db.models import Avg, Count


def hybrid_recommendations(user, n=12):
    """
    Hybrid: 40% user-based + 30% item-based + 30% content-based.
    Returns list of dicts: {product, score, source, reason}.
    """
    all_products = Product.objects.select_related('category').all()
    ratings_qs = Rating.objects.all()
    user_ratings = ratings_qs.filter(user=user)

    user_rating_count = user_ratings.count()
    if user_rating_count == 0:
        return cold_start_recommendations(user, all_products, n)

    rated_ids = list(user_ratings.values_list('product_id', flat=True))

    # ── Récupérer les recommandations de chaque source ────────────────────────
    try:
        user_recs = user_based_recommendations(user.id, ratings_qs, n=n * 3)
    except Exception:
        user_recs = []
    try:
        item_recs = item_based_recommendations(user.id, ratings_qs, n=n * 3)
    except Exception:
        item_recs = []
    try:
        content_recs, content_sources = content_based_for_user_with_source(rated_ids, all_products, n=n * 3)
    except Exception:
        content_recs, content_sources = [], {}

    # ── Scores par rang normalisés ─────────────────────────────────────────────
    def rank_scores(id_list):
        return {pid: len(id_list) - i for i, pid in enumerate(id_list)}

    def normalize(d):
        max_v = max(d.values(), default=1) or 1
        return {k: v / max_v for k, v in d.items()}

    user_scores    = normalize(rank_scores(user_recs))
    item_scores    = normalize(rank_scores(item_recs))
    content_scores = normalize(rank_scores(content_recs))

    candidate_ids = (set(user_scores) | set(item_scores) | set(content_scores)) - set(rated_ids)

    if not candidate_ids:
        return cold_start_recommendations(user, all_products, n, exclude_ids=rated_ids)

    # ── Score final : 40% user + 30% item + 30% content ──────────────────────
    final_scores = {
        pid: (
            0.4 * user_scores.get(pid, 0) +
            0.3 * item_scores.get(pid, 0) +
            0.3 * content_scores.get(pid, 0)
        )
        for pid in candidate_ids
    }

    sorted_ids = sorted(final_scores, key=final_scores.get, reverse=True)[:n]
    products_map = {p.id: p for p in all_products.filter(id__in=sorted_ids)}

    # ── Pré-chargement en bulk ─────────────────────────────────────────────────
    # Comptes de notes ≥4 pour les produits retenus
    high_rating_counts = dict(
        Rating.objects.filter(product_id__in=sorted_ids, score__gte=4)
        .values('product_id')
        .annotate(c=Count('id'))
        .values_list('product_id', 'c')
    )

    # Produits sources du content-based (produits notés par l'user)
    source_pids = [v for v in (content_sources.get(pid) for pid in sorted_ids) if v]
    rated_products_map = {p.id: p for p in Product.objects.filter(id__in=source_pids)}

    # ── Construction du résultat avec explications ────────────────────────────
    result = []
    for pid in sorted_ids:
        if pid not in products_map:
            continue

        score  = final_scores[pid]
        u_val  = 0.4 * user_scores.get(pid, 0)
        it_val = 0.3 * item_scores.get(pid, 0)
        c_val  = 0.3 * content_scores.get(pid, 0)

        collab_val = u_val + it_val
        has_collab = collab_val > 0
        has_content = c_val > 0

        # Déterminer la source dominante
        if has_collab and has_content:
            source = 'hybrid'
        elif has_collab:
            source = 'collaborative'
        else:
            source = 'content'

        # Générer la raison
        if source in ('collaborative', 'hybrid'):
            count = high_rating_counts.get(pid, 0)
            if count >= 3:
                reason = f"{count} utilisateurs avec un profil similaire l'ont noté 4+/5"
            elif count > 0:
                reason = "Recommandé par des utilisateurs avec des intérêts similaires"
            else:
                reason = "Recommandé d'après votre historique de notation"
        else:
            source_pid = content_sources.get(pid)
            source_product = rated_products_map.get(source_pid) if source_pid else None
            if source_product:
                reason = f"Similaire à « {source_product.name} » que vous avez aimé"
            else:
                reason = "Similaire à vos produits préférés"

        result.append({
            'product': products_map[pid],
            'score':   round(score, 3),
            'source':  source,
            'reason':  reason,
        })

    return result


def cold_start_recommendations(user, all_products, n=12, exclude_ids=None):
    """
    Cold start personnalisé : priorité aux catégories d'intérêt de l'utilisateur.
    Deux utilisateurs avec des intérêts différents obtiennent des produits différents.
    """
    exclude_ids    = exclude_ids or []
    user_interests = user.interests_list() if hasattr(user, 'interests_list') else []

    base_qs = (
        all_products
        .exclude(id__in=exclude_ids)
        .annotate(
            avg_rating   = Avg('ratings__score'),
            rating_count = Count('ratings'),
        )
    )

    products  = []
    seen_ids  = set()

    # ── 1. Produits dans les catégories d'intérêt ─────────────────────────────
    if user_interests:
        interest_products = list(
            base_qs
            .filter(category__slug__in=user_interests)
            .order_by('-avg_rating', '-rating_count')[:n]
        )
        for p in interest_products:
            if p.id not in seen_ids:
                products.append(p)
                seen_ids.add(p.id)

    # ── 2. Compléter avec des produits vedettes d'autres catégories ───────────
    if len(products) < n:
        featured = list(
            base_qs
            .filter(is_featured=True)
            .exclude(id__in=list(seen_ids))
            .order_by('-avg_rating', '-rating_count')[:n - len(products)]
        )
        for p in featured:
            if p.id not in seen_ids:
                products.append(p)
                seen_ids.add(p.id)

    # ── 3. Compléter avec les produits les mieux notés toutes catégories ──────
    if len(products) < n:
        filler = list(
            base_qs
            .exclude(id__in=list(seen_ids))
            .order_by('-avg_rating', '-rating_count')[:n - len(products)]
        )
        for p in filler:
            if p.id not in seen_ids:
                products.append(p)
                seen_ids.add(p.id)

    # ── Construction du résultat ───────────────────────────────────────────────
    result = []
    for p in products[:n]:
        if user_interests and p.category.slug in user_interests:
            reason = f"Dans votre catégorie préférée : {p.category.name}"
        elif p.is_featured:
            reason = "Produit vedette de la boutique"
        else:
            reason = f"Populaire dans {p.category.name}"

        result.append({
            'product': p,
            'score':   0.0,
            'source':  'cold_start',
            'reason':  reason,
        })

    return result
