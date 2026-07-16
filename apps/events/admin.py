from django.contrib import admin
from .models import EventQuotation

@admin.register(EventQuotation)
class EventQuotationAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'event_date', 'guest_count', 'status', 'created_at']
    list_filter = ['status', 'event_type', 'event_date']
    search_fields = ['name', 'email', 'phone', 'notes']
    list_editable = ['status']
