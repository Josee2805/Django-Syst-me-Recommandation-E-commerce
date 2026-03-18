"""
Tests unitaires - Personne C
Couvre : collaborative.py, content_based.py, hybrid.py, evaluation.py

Lancer avec : python manage.py test recommendations
"""

import numpy as np
from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Category, Product, Rating
from .collaborative import (
    build_user_item_matrix,
    cosine_similarity_matrix,
    user_based_recommendations,
    item_based_recommendations,
)
from .content_based import (
    build_product_features,
    content_based_recommendations,
    content_based_for_user,
)
from .hybrid import hybrid_recommendations, cold_start_recommendations
from .evaluation import (
    precision_at_k,
    recall_at_k,
    f1_score,
    ndcg_at_k,
    evaluate_recommender,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Donnees de test partagees
# ---------------------------------------------------------------------------

class BaseTestCase(TestCase):
    """Cree une base commune : 2 categories, 6 produits, 3 utilisateurs, des notes."""

    def setUp(self):
        self.cat_elec = Category.objects.create(name="Electronique", slug="electronique")
        self.cat_mode = Category.objects.create(name="Mode", slug="mode")

        self.p1 = Product.objects.create(
            name="iPhone 15", category=self.cat_elec, price=1299,
            description="Smartphone Apple", tags="apple,smartphone", brand="Apple"
        )
        self.p2 = Product.objects.create(
            name="Samsung Galaxy", category=self.cat_elec, price=999,
            description="Smartphone Samsung", tags="samsung,android", brand="Samsung"
        )
        self.p3 = Product.objects.create(
            name="MacBook Pro", category=self.cat_elec, price=2499,
            description="Ordinateur Apple", tags="apple,laptop", brand="Apple"
        )
        self.p4 = Product.objects.create(
            name="Veste cuir", category=self.cat_mode, price=299,
            description="Veste en cuir vintage", tags="cuir,veste", brand="Zara"
        )
        self.p5 = Product.objects.create(
            name="Sneakers Nike", category=self.cat_mode, price=149,
            description="Chaussures de sport", tags="nike,sport", brand="Nike"
        )
        self.p6 = Product.objects.create(
            name="Robe soiree", category=self.cat_mode, price=189,
            description="Robe elegante pour soiree", tags="robe,soiree", brand="HM"
        )

        self.alice = User.objects.create_user(
            username="alice", email="alice@test.com", password="pass123"
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@test.com", password="pass123"
        )
        self.carol = User.objects.create_user(
            username="carol", email="carol@test.com", password="pass123"
        )

        # Alice et Bob aiment l'electronique, Carol aime la mode
        Rating.objects.create(user=self.alice, product=self.p1, score=5)
        Rating.objects.create(user=self.alice, product=self.p2, score=4)
        Rating.objects.create(user=self.alice, product=self.p3, score=5)

        Rating.objects.create(user=self.bob, product=self.p1, score=5)
        Rating.objects.create(user=self.bob, product=self.p2, score=3)

        Rating.objects.create(user=self.carol, product=self.p4, score=5)
        Rating.objects.create(user=self.carol, product=self.p5, score=4)
        Rating.objects.create(user=self.carol, product=self.p6, score=5)


# ---------------------------------------------------------------------------
# Tests : collaborative.py
# ---------------------------------------------------------------------------

class CollaborativeTests(BaseTestCase):

    def test_build_matrix_shape(self):
        """La matrice doit avoir autant de lignes que d'utilisateurs avec des notes."""
        ratings_qs = Rating.objects.all()
        matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)
        self.assertEqual(matrix.shape[0], 3)
        self.assertEqual(matrix.shape[1], 6)

    def test_build_matrix_values(self):
        """Les valeurs de la matrice doivent correspondre aux notes saisies."""
        ratings_qs = Rating.objects.all()
        matrix, user_ids, item_ids, user_idx, item_idx = build_user_item_matrix(ratings_qs)
        alice_idx = user_idx[self.alice.id]
        p1_idx = item_idx[self.p1.id]
        self.assertEqual(matrix[alice_idx][p1_idx], 5.0)

    def test_cosine_similarity_identical_vectors(self):
        """La similarite cosinus d'un vecteur avec lui-meme doit etre 1."""
        matrix = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])
        sim = cosine_similarity_matrix(matrix)
        self.assertAlmostEqual(sim[0][1], 1.0, places=5)

    def test_cosine_similarity_orthogonal_vectors(self):
        """La similarite cosinus de deux vecteurs orthogonaux doit etre 0."""
        matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
        sim = cosine_similarity_matrix(matrix)
        self.assertAlmostEqual(sim[0][1], 0.0, places=5)

    def test_user_based_excludes_already_rated(self):
        """Les produits deja notes ne doivent pas etre recommandes."""
        ratings_qs = Rating.objects.all()
        recs = user_based_recommendations(self.bob.id, ratings_qs, n=10)
        bob_rated = set(
            Rating.objects.filter(user=self.bob).values_list('product_id', flat=True)
        )
        for pid in recs:
            self.assertNotIn(pid, bob_rated)

    def test_user_based_cold_start_returns_empty(self):
        """Un utilisateur sans note doit recevoir une liste vide."""
        new_user = User.objects.create_user(
            username="newbie", email="newbie@test.com", password="pass"
        )
        ratings_qs = Rating.objects.all()
        recs = user_based_recommendations(new_user.id, ratings_qs, n=5)
        self.assertEqual(recs, [])

    def test_item_based_excludes_already_rated(self):
        """Item-based : les produits deja notes ne doivent pas apparaitre."""
        ratings_qs = Rating.objects.all()
        recs = item_based_recommendations(self.alice.id, ratings_qs, n=5)
        alice_rated = set(
            Rating.objects.filter(user=self.alice).values_list('product_id', flat=True)
        )
        for pid in recs:
            self.assertNotIn(pid, alice_rated)

    def test_insufficient_ratings_returns_empty(self):
        """Avec moins de 2 notes au total, les fonctions retournent une liste vide."""
        Rating.objects.all().delete()
        Rating.objects.create(user=self.alice, product=self.p1, score=5)
        ratings_qs = Rating.objects.all()
        recs = user_based_recommendations(self.alice.id, ratings_qs, n=5)
        self.assertEqual(recs, [])


# ---------------------------------------------------------------------------
# Tests : content_based.py
# ---------------------------------------------------------------------------

class ContentBasedTests(BaseTestCase):

    def test_build_product_features_contains_name(self):
        """Les features d'un produit doivent contenir son nom."""
        products = list(Product.objects.select_related('category').all())
        features = build_product_features(products)
        self.assertTrue(any("iphone" in f for f in features))

    def test_content_based_returns_list(self):
        """content_based_recommendations doit retourner une liste."""
        products = Product.objects.select_related('category').all()
        recs = content_based_recommendations(self.p1.id, products, n=3)
        self.assertIsInstance(recs, list)

    def test_content_based_excludes_target_product(self):
        """Le produit cible ne doit pas apparaitre dans ses propres recommandations."""
        products = Product.objects.select_related('category').all()
        recs = content_based_recommendations(self.p1.id, products, n=5)
        self.assertNotIn(self.p1.id, recs)

    def test_content_based_similar_category(self):
        """Les produits similaires doivent privilegier la meme categorie."""
        products = Product.objects.select_related('category').all()
        recs = content_based_recommendations(self.p1.id, products, n=2)
        rec_products = Product.objects.filter(id__in=recs)
        categories = set(p.category.slug for p in rec_products)
        self.assertIn("electronique", categories)

    def test_content_based_for_user_excludes_rated(self):
        """Les produits deja notes ne doivent pas etre recommandes."""
        products = Product.objects.select_related('category').all()
        rated_ids = [self.p1.id, self.p2.id, self.p3.id]
        recs = content_based_for_user(rated_ids, products, n=5)
        for pid in recs:
            self.assertNotIn(pid, rated_ids)

    def test_content_based_for_user_empty_rated(self):
        """Sans produits notes, content_based_for_user retourne une liste vide."""
        products = Product.objects.select_related('category').all()
        recs = content_based_for_user([], products, n=5)
        self.assertEqual(recs, [])


# ---------------------------------------------------------------------------
# Tests : hybrid.py
# ---------------------------------------------------------------------------

class HybridTests(BaseTestCase):

    def test_hybrid_returns_product_objects(self):
        """hybrid_recommendations doit retourner des objets Product."""
        recs = hybrid_recommendations(self.alice, n=5)
        self.assertIsInstance(recs, list)
        if recs:
            self.assertIsInstance(recs[0], Product)

    def test_hybrid_cold_start_for_new_user(self):
        """Un nouvel utilisateur sans note doit recevoir des produits populaires."""
        new_user = User.objects.create_user(
            username="newuser", email="newuser@test.com", password="pass"
        )
        recs = hybrid_recommendations(new_user, n=4)
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)

    def test_hybrid_respects_n_limit(self):
        """Le nombre de recommandations ne doit pas depasser n."""
        recs = hybrid_recommendations(self.alice, n=3)
        self.assertLessEqual(len(recs), 3)

    def test_cold_start_excludes_given_ids(self):
        """cold_start ne doit pas recommander les produits exclus."""
        products = Product.objects.all()
        exclude = [self.p1.id, self.p2.id]
        recs = cold_start_recommendations(products, n=5, exclude_ids=exclude)
        rec_ids = [p.id for p in recs]
        for eid in exclude:
            self.assertNotIn(eid, rec_ids)


# ---------------------------------------------------------------------------
# Tests : evaluation.py
# ---------------------------------------------------------------------------

class EvaluationTests(BaseTestCase):

    def test_precision_perfect(self):
        """Precision parfaite quand toutes les recommandations sont pertinentes."""
        recs = [1, 2, 3]
        relevant = [1, 2, 3, 4, 5]
        self.assertEqual(precision_at_k(recs, relevant, k=3), 1.0)

    def test_precision_zero(self):
        """Precision nulle quand aucune recommandation n'est pertinente."""
        recs = [10, 11, 12]
        relevant = [1, 2, 3]
        self.assertEqual(precision_at_k(recs, relevant, k=3), 0.0)

    def test_precision_empty_recs(self):
        """Precision vaut 0 si la liste de recommandations est vide."""
        self.assertEqual(precision_at_k([], [1, 2], k=5), 0.0)

    def test_recall_perfect(self):
        """Rappel parfait quand tous les produits pertinents sont recommandes."""
        recs = [1, 2, 3]
        relevant = [1, 2, 3]
        self.assertEqual(recall_at_k(recs, relevant, k=3), 1.0)

    def test_recall_empty_relevant(self):
        """Rappel vaut 0 s'il n'y a aucun produit pertinent."""
        self.assertEqual(recall_at_k([1, 2], [], k=5), 0.0)

    def test_f1_balanced(self):
        """F1 vaut precision=recall quand les deux sont egaux."""
        result = f1_score(0.6, 0.6)
        self.assertAlmostEqual(result, 0.6, places=5)

    def test_f1_zero_when_both_zero(self):
        """F1 vaut 0 quand precision et recall sont tous les deux nuls."""
        self.assertEqual(f1_score(0.0, 0.0), 0.0)

    def test_ndcg_perfect_order(self):
        """NDCG vaut 1.0 quand tous les pertinents sont en tete de liste."""
        recs = [1, 2, 3, 4, 5]
        relevant = [1, 2, 3]
        self.assertEqual(ndcg_at_k(recs, relevant, k=5), 1.0)

    def test_ndcg_zero_no_relevant_found(self):
        """NDCG vaut 0 quand aucun produit pertinent n'est dans les recommandations."""
        recs = [10, 11, 12]
        relevant = [1, 2, 3]
        self.assertEqual(ndcg_at_k(recs, relevant, k=3), 0.0)

    def test_ndcg_penalizes_bad_order(self):
        """NDCG doit etre plus eleve quand les pertinents sont en debut de liste."""
        relevant = [1, 2]
        recs_good = [1, 2, 3, 4, 5]
        recs_bad  = [3, 4, 5, 1, 2]
        ndcg_good = ndcg_at_k(recs_good, relevant, k=5)
        ndcg_bad  = ndcg_at_k(recs_bad,  relevant, k=5)
        self.assertGreater(ndcg_good, ndcg_bad)

    def test_ndcg_empty_inputs(self):
        """NDCG vaut 0 si l'une des listes est vide."""
        self.assertEqual(ndcg_at_k([], [1, 2], k=5), 0.0)
        self.assertEqual(ndcg_at_k([1, 2], [], k=5), 0.0)

    def test_evaluate_recommender_returns_all_keys(self):
        """evaluate_recommender doit retourner toutes les metriques attendues."""
        rec_ids = [self.p4.id, self.p5.id, self.p6.id]
        result = evaluate_recommender(self.carol, rec_ids, threshold=4)
        for key in ['precision', 'recall', 'f1', 'ndcg', 'relevant_count', 'recommended_count']:
            self.assertIn(key, result)

    def test_evaluate_recommender_values_in_range(self):
        """Toutes les metriques doivent etre comprises entre 0 et 1."""
        rec_ids = [self.p1.id, self.p2.id, self.p3.id]
        result = evaluate_recommender(self.alice, rec_ids, threshold=4)
        for key in ['precision', 'recall', 'f1', 'ndcg']:
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)
