from django.contrib import admin
from .models import (
    UserProfile, EmailVerificationCode,
    OnboardingQuestion, OnboardingChoice, UserOnboardingAnswer, UserPreference,
    Category, Product, Rating, Comment,
    Cart, CartItem, Order, OrderItem, ProductView,
)

admin.site.register(UserProfile)
admin.site.register(EmailVerificationCode)
admin.site.register(OnboardingQuestion)
admin.site.register(OnboardingChoice)
admin.site.register(UserPreference)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'brand', 'tags']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'score', 'created_at']

admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(ProductView)
