from django.contrib import admin
from .models import Category, Dish, DishVariant

class DishVariantInline(admin.TabularInline):
    model = DishVariant
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order_index', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order_index', 'is_active']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_specialty', 'stock_level', 'order_index']
    list_filter = ['category', 'is_available', 'is_specialty']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'is_available', 'stock_level', 'order_index']
    search_fields = ['name', 'description']
    inlines = [DishVariantInline]
