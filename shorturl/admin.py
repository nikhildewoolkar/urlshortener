from django.contrib import admin
from .models import * 
@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "original_url", "click_count", "created_at", "last_accessed_at")
    search_fields = ("short_code", "original_url")
    list_filter = ("created_at",)