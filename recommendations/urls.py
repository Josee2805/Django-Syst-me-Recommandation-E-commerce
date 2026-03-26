from django.urls import path
from . import views

urlpatterns = [
<<<<<<< Updated upstream
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.products_view, name='products'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('api/rate/<int:pk>/', views.api_rate, name='api_rate'),
=======
    # ── Index & Landing ──────────────────────────────────────
    path('', views.index_view, name='index'),
    path('landing/', views.landing_view, name='landing'),

    # ═══════════════════════════════════════════════════════
    # AUTH & ONBOARDING (Personne A)
    # ═══════════════════════════════════════════════════════
    path('register/',          views.register_view,          name='register'),
    path('verify-code/',       views.verify_code_view,       name='verify_code'),
    path('resend-code/',       views.resend_code_view,       name='resend_code'),
    path('login/',             views.login_view,             name='login'),
    path('logout/',            views.logout_view,            name='logout'),
    path('email-sent/',        views.email_sent_view,        name='email_sent'),
    path('onboarding/',        views.onboarding_start_view,  name='onboarding_start'),
    path('onboarding/<int:step>/', views.onboarding_step_view, name='onboarding_step'),
    path('onboarding/done/',   views.onboarding_complete_view, name='onboarding_complete'),

    # ═══════════════════════════════════════════════════════
    # CATALOGUE & PANIER (ta camarade — NE PAS MODIFIER)
    # ═══════════════════════════════════════════════════════
    path('home/',              views.home_view,              name='home'),
    path('products/',          views.products_view,          name='products'),
    path('products/<int:pk>/', views.product_detail_view,    name='product_detail'),
    path('cart/',              views.cart_view,              name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart,            name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart,         name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart,    name='remove_from_cart'),
    path('cart/checkout/',     views.checkout,               name='checkout'),
    path('profile/',           views.profile_view,           name='profile'),
    path('profile/update/',    views.update_profile,         name='update_profile'),
    path('recommendations/',   views.recommendations_view,   name='recommendations'),
    path('api/rate/<int:pk>/', views.api_rate,               name='api_rate'),
>>>>>>> Stashed changes
]
