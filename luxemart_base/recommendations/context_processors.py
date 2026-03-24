"""
LuxeMart — recommendations/context_processors.py
BRANCHE : feature/catalogue-cart — Personne B UNIQUEMENT

Injecte les catégories dans tous les templates (sidebar).
Activer dans settings.py > TEMPLATES > context_processors.
"""


def sidebar_categories(request):
    """Injecte les catégories actives dans chaque template."""
    try:
        from .models import Category
        from django.db.models import Count, Q
        categories = (Category.objects
                      .filter(is_active=True)
                      .annotate(product_count=Count(
                          'products',
                          filter=Q(products__is_active=True)
                      ))
                      .order_by('name'))
        cart_count = 0
        if request.user.is_authenticated:
            from .models import Cart
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_count = cart.items_count
        return {
            'sidebar_categories': categories,
            'cart_count': cart_count,
        }
    except Exception:
        return {'sidebar_categories': [], 'cart_count': 0}
