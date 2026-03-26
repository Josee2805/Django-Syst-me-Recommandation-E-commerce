import numpy as np
from collections import defaultdict
from django.db.models import Avg, Count


def build_user_item_matrix(ratings_qs):
    """Build user-item matrix from ratings queryset."""
    user_ids = list(set(r.user_id for r in ratings_qs))
    item_ids = list(set(r.product_id for r in ratings_qs))

    user_idx = {uid: i for i, uid in enumerate(user_ids)}
    item_idx = {iid: i for i, iid in enumerate(item_ids)}

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
    if ratings_qs.count() < 2:
        return []

    matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)

    if target_user_id not in user_idx:
        return []

    sim_matrix = cosine_similarity_matrix(matrix)
    target_idx = user_idx[target_user_id]

    similarities = sim_matrix[target_idx]
    similar_indices = np.argsort(similarities)[::-1][1:n_similar + 1]

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


# ── CLUSTERING (Cold Start) ───────────────────────────────────────────────────

INTEREST_ORDER = ['mode', 'electronique', 'maison', 'sport', 'beaute', 'alimentation']
BUDGET_ORDER   = ['petit', 'moyen', 'illimite']
PRIORITY_ORDER = ['prix', 'qualite', 'promotions', 'nouveautes']
GENDER_ORDER   = ['homme', 'femme']

# Poids pour accentuer l'importance des centres d'interet dans le vecteur
FEATURE_WEIGHTS = np.array(
    [1.0, 1.0]               # genre (2)
    + [2.0] * 6              # centres d'interet (6) — poids double
    + [1.5] * 3              # budget (3)
    + [1.0] * 4,             # priorite (4)
    dtype=float
)


def build_user_profile_vector(user):
    """
    Encode le profil onboarding en vecteur numerique pondere (15 dims).
    Les centres d'interet ont un poids x2 pour mieux differencier les clusters.
    """
    gender_vec   = [1.0 if user.gender == g else 0.0 for g in GENDER_ORDER]
    interests    = user.interests_list()
    interest_vec = [1.0 if cat in interests else 0.0 for cat in INTEREST_ORDER]
    budget_vec   = [1.0 if user.budget == b else 0.0 for b in BUDGET_ORDER]
    priority_vec = [1.0 if user.purchase_priority == p else 0.0 for p in PRIORITY_ORDER]
    raw = np.array(gender_vec + interest_vec + budget_vec + priority_vec, dtype=float)
    return raw * FEATURE_WEIGHTS


def assign_to_cluster(user, n_clusters=5):
    """
    Calcule le cluster de profil pour l'utilisateur et persiste l'affectation
    de TOUS les utilisateurs profiles dans UserCluster.
    Appele apres la completion de l'onboarding.
    Retourne le cluster_id de l'utilisateur, ou None si pas assez de donnees.
    """
    from .models import CustomUser, UserCluster

    try:
        from sklearn.cluster import KMeans
    except ImportError:
        return None

    profiled_users = list(CustomUser.objects.filter(onboarding_done=True))
    if len(profiled_users) < 3:
        # Pas assez d'utilisateurs: assigner au cluster 0 par defaut
        UserCluster.objects.update_or_create(user=user, defaults={'cluster_id': 0})
        return 0

    X = np.array([build_user_profile_vector(u) for u in profiled_users])

    if X.std() < 1e-9:
        # Tous les profils sont identiques
        for u in profiled_users:
            UserCluster.objects.update_or_create(user=u, defaults={'cluster_id': 0})
        return 0

    actual_k = min(n_clusters, len(profiled_users))
    km = KMeans(n_clusters=actual_k, n_init=15, random_state=42)
    labels = km.fit_predict(X)

    # Persister le cluster de chaque utilisateur profile
    for i, u in enumerate(profiled_users):
        UserCluster.objects.update_or_create(user=u, defaults={'cluster_id': int(labels[i])})

    # Cluster du nouvel utilisateur
    user_vec = build_user_profile_vector(user).reshape(1, -1)
    return int(km.predict(user_vec)[0])


def cluster_based_recommendations(user, all_users_qs, ratings_qs, all_products, n=12, n_clusters=5):
    """
    Recommande des produits a partir des notes des membres du meme cluster.

    Strategie:
    1. Cherche l'affectation persistee dans UserCluster.
    2. Si absente, recalcule le cluster via K-means et le persiste.
    3. Recupere les notes des membres du cluster.
    4. Retourne les produits les mieux notes par le cluster.
    """
    from .models import UserCluster

    # 1. Recuperer le cluster depuis le cache DB
    cluster_id = None
    try:
        cluster_id = UserCluster.objects.get(user=user).cluster_id
    except UserCluster.DoesNotExist:
        pass

    # 2. Recalculer si necessaire
    if cluster_id is None:
        cluster_id = assign_to_cluster(user, n_clusters=n_clusters)
        if cluster_id is None:
            return []

    # 3. Membres du meme cluster (hors utilisateur courant)
    cluster_user_ids = list(
        UserCluster.objects.filter(cluster_id=cluster_id)
        .exclude(user=user)
        .values_list('user_id', flat=True)
    )
    if not cluster_user_ids:
        return []

    # 4. Agreger les notes du cluster
    cluster_ratings = ratings_qs.filter(user_id__in=cluster_user_ids)
    if not cluster_ratings.exists():
        return []

    top_products = (
        cluster_ratings
        .values('product_id')
        .annotate(avg_score=Avg('score'), votes=Count('id'))
        .filter(avg_score__gte=3.5)   # uniquement les produits bien notes
        .order_by('-avg_score', '-votes')
    )

    top_ids = [r['product_id'] for r in top_products[:n]]
    if not top_ids:
        # Pas de produits bien notes: prendre quand meme les mieux notes
        top_products_all = (
            cluster_ratings
            .values('product_id')
            .annotate(avg_score=Avg('score'), votes=Count('id'))
            .order_by('-avg_score', '-votes')
        )
        top_ids = [r['product_id'] for r in top_products_all[:n]]

    if not top_ids:
        return []

    products_map = {p.id: p for p in all_products.filter(id__in=top_ids)}
    return [products_map[pid] for pid in top_ids if pid in products_map]
