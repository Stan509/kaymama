from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date', 'time_slot', 'guest_count', 'occasion', 'status']
    list_filter = ['status', 'date', 'occasion']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_editable = ['status']
