from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'rating', 'stock')  # Mostrar stock en la lista
    search_fields = ('title', 'category')  # Buscar por título o categoría
    list_filter = ('category',)  # Filtrar por categoría
