from django.contrib import admin
from .models import Category, Product, ProductImage, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured', 'category', 'vendor', 'created_at')
    search_fields = ('name', 'description', 'vendor__store_name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured', 'price')
    raw_id_fields = ('vendor',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_primary')
    list_filter = ('is_primary', 'product__category')
    search_fields = ('product__name', 'alt_text')
    raw_id_fields = ('product',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at', 'product__category')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    list_editable = ('is_approved',)
    raw_id_fields = ('user', 'product')
    readonly_fields = ('is_verified', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'product', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
