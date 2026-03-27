import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_product_features(products):
    """Build feature strings for each product."""
    features = []
    for p in products:
        text = f"{p.name} {p.category.name} {p.description} {p.tags} {p.brand}"
        features.append(text.lower().strip())
    return features


def content_based_recommendations(target_product_id, all_products, n=10):
    """Content-based filtering using TF-IDF + cosine similarity (for product detail page)."""
    products = list(all_products)
    if len(products) < 2:
        return []

    product_ids = [p.id for p in products]
    if target_product_id not in product_ids:
        return []

    features    = build_product_features(products)
    vectorizer  = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform(features)
    sim_matrix  = cosine_similarity(tfidf_matrix)

    target_idx  = product_ids.index(target_product_id)
    similarities = sim_matrix[target_idx]
    similar_indices = np.argsort(similarities)[::-1][1:n + 1]

    return [product_ids[i] for i in similar_indices]


def content_based_for_user(user_rated_product_ids, all_products, n=10):
    """Content-based recs based on user's rated products (sans source tracking)."""
    result, _ = content_based_for_user_with_source(user_rated_product_ids, all_products, n)
    return result


def content_based_for_user_with_source(user_rated_product_ids, all_products, n=10):
    """
    Content-based recs based on user's rated products.
    Returns:
        - list of recommended product IDs
        - dict mapping pid -> source_rated_pid (quel produit noté a causé la reco)
    """
    products = list(all_products)
    if not products or not user_rated_product_ids:
        return [], {}

    product_ids = [p.id for p in products]
    features    = build_product_features(products)

    vectorizer   = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform(features)
    tfidf_array  = tfidf_matrix.toarray()

    rated_indices = [product_ids.index(pid) for pid in user_rated_product_ids if pid in product_ids]
    if not rated_indices:
        return [], {}

    # Profil utilisateur = moyenne des vecteurs des produits notés
    user_profile        = np.mean(tfidf_array[rated_indices], axis=0)
    profile_similarities = cosine_similarity([user_profile], tfidf_array)[0]

    # Similarité de chaque produit avec chaque produit noté (en bulk)
    # shape: (num_products, num_rated)
    all_vs_rated      = cosine_similarity(tfidf_array, tfidf_array[rated_indices])
    best_source_col   = np.argmax(all_vs_rated, axis=1)  # index dans rated_indices

    sorted_indices = np.argsort(profile_similarities)[::-1]

    result  = []
    sources = {}
    for idx in sorted_indices:
        pid = product_ids[idx]
        if pid in user_rated_product_ids:
            continue

        # Produit noté le plus similaire → source de la raison
        source_rated_idx = rated_indices[best_source_col[idx]]
        sources[pid]     = product_ids[source_rated_idx]

        result.append(pid)
        if len(result) >= n:
            break

    return result, sources
