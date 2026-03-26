from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Rating, Comment, CartItem, Purchase, UserCluster

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_staff', 'date_joined']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (('Extra', {'fields': ('profile_pic', 'bio')}),)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_featured', 'stock', 'average_rating']
    list_filter = ['category', 'is_featured']
    search_fields = ['name', 'brand', 'tags']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'score', 'created_at']
    list_filter = ['score']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'purchased_at']

@admin.register(UserCluster)
class UserClusterAdmin(admin.ModelAdmin):
    list_display = ['user', 'cluster_id', 'updated_at']
    list_filter = ['cluster_id']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['updated_at']
