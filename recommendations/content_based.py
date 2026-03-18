import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_product_features(products):
    """Build feature strings for each product."""
    features = []
    for p in products:
        text = f"{p.name} {p.category.name} {p.description} {p.tags} {p.brand}"
        text = text.lower().strip()
        features.append(text)
    return features


def content_based_recommendations(target_product_id, all_products, n=10):
    """Content-based filtering using TF-IDF + cosine similarity."""
    products = list(all_products)
    if len(products) < 2:
        return []
    
    product_ids = [p.id for p in products]
    
    if target_product_id not in product_ids:
        return []
    
    features = build_product_features(products)
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform(features)
    
    sim_matrix = cosine_similarity(tfidf_matrix)
    
    target_idx = product_ids.index(target_product_id)
    similarities = sim_matrix[target_idx]
    
    similar_indices = np.argsort(similarities)[::-1][1:n+1]
    
    return [product_ids[i] for i in similar_indices]


def content_based_for_user(user_rated_product_ids, all_products, n=10):
    """Content-based recs based on user's rated products."""
    products = list(all_products)
    if not products or not user_rated_product_ids:
        return []
    
    product_ids = [p.id for p in products]
    features = build_product_features(products)
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = vectorizer.fit_transform(features)
    
    rated_indices = [product_ids.index(pid) for pid in user_rated_product_ids if pid in product_ids]
    if not rated_indices:
        return []
    
    user_profile = np.mean(tfidf_matrix[rated_indices].toarray(), axis=0)
    similarities = cosine_similarity([user_profile], tfidf_matrix.toarray())[0]
    
    sorted_indices = np.argsort(similarities)[::-1]
    
    result = []
    for idx in sorted_indices:
        pid = product_ids[idx]
        if pid not in user_rated_product_ids:
            result.append(pid)
        if len(result) >= n:
            break
    
    return result
