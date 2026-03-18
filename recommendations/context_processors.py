def cart_count(request):
    count = 0
    sidebar_categories = []
    if request.user.is_authenticated:
        from .models import CartItem, Category
        count = CartItem.objects.filter(user=request.user).count()
        sidebar_categories = list(Category.objects.all()[:12])
    return {
        'cart_count': count,
        'sidebar_categories': sidebar_categories,
    }
