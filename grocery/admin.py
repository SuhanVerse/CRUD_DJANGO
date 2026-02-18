from django.contrib import admin
from .models import GroceryItem


@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'completed', 'created_at')
    list_filter = ('completed',)
    search_fields = ('name',)
    list_editable = ('completed',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
