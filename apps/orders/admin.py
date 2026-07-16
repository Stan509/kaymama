from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['dish', 'variant', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'last_name', 'delivery_method', 'status', 'payment_status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_method', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'total_price', 'created_at']
