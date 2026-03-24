from django.urls import path
from . import views

urlpatterns = [
    # ══ SECTION A — AUTH & ONBOARDING ══
    path('login/',                          views.login_view,               name='login'),
    path('logout/',                         views.logout_view,              name='logout'),
    path('register/',                       views.register_view,            name='register'),
    path('verify-code/',                    views.verify_code_view,         name='verify_code'),
    path('resend-code/',                    views.resend_code_view,         name='resend_code'),
    path('onboarding/',                     views.onboarding_start_view,    name='onboarding_start'),
    path('onboarding/step/<int:step>/',     views.onboarding_step_view,     name='onboarding_step'),
    path('onboarding/complete/',            views.onboarding_complete_view, name='onboarding_complete'),

    # ══ SECTION B — CATALOGUE & PANIER ══
    path('',                                views.home_view,                name='home'),
    path('products/',                       views.products_view,            name='products'),
    path('products/<slug:slug>/',           views.product_detail_view,      name='product_detail'),
    path('products/<slug:slug>/rate/',      views.rate_product_view,        name='rate_product'),
    path('products/<slug:slug>/comment/',   views.comment_product_view,     name='comment_product'),
    path('products/<slug:slug>/del-comment/',views.delete_comment_view,    name='delete_comment'),
    path('cart/',                           views.cart_view,                name='cart'),
    path('cart/add/<slug:slug>/',           views.add_to_cart_view,         name='add_to_cart'),
    path('cart/update/<int:item_id>/',      views.update_cart_view,         name='update_cart'),
    path('cart/remove/<int:item_id>/',      views.remove_from_cart_view,    name='remove_from_cart'),
    path('cart/clear/',                     views.clear_cart_view,          name='clear_cart'),
    path('cart/checkout/',                  views.checkout_view,            name='checkout'),
    path('profile/',                        views.profile_view,             name='profile'),

    # ══ SECTION C — RECOMMANDATIONS ══
    path('recommendations/',               views.recommendations_view,      name='recommendations'),
]
