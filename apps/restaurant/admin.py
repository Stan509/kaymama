from django.contrib import admin
from .models import RestaurantSettings, OpeningHours, BlockedDate

@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_ordering_enabled', 'is_reservations_enabled']

@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'opening_time', 'closing_time', 'is_closed']
    list_editable = ['opening_time', 'closing_time', 'is_closed']

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'reason']
