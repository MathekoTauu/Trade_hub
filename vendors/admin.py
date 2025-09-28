from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'is_verified', 'phone', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('store_name', 'user__username', 'user__email', 'phone')
    list_editable = ('is_verified',)
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
