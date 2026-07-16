from django.db import models
from django.conf import settings

class Reservation(models.Model):
    OCCASION_BIRTHDAY = 'BIRTHDAY'
    OCCASION_WEDDING = 'WEDDING'
    OCCASION_BUSINESS = 'BUSINESS'
    OCCASION_FAMILY = 'FAMILY'
    OCCASION_SALON = 'SALON'
    OCCASION_OTHER = 'OTHER'

    OCCASION_CHOICES = [
        (OCCASION_BIRTHDAY, 'Anniversaire'),
        (OCCASION_WEDDING, 'Mariage / Fiançailles'),
        (OCCASION_BUSINESS, 'Repas d\'affaires'),
        (OCCASION_FAMILY, 'Fête de famille'),
        (OCCASION_SALON, 'Salon de Beauté'),
        (OCCASION_OTHER, 'Autre événement'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_MODIFIED = 'MODIFIED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_APPROVED, 'Confirmée'),
        (STATUS_REJECTED, 'Refusée'),
        (STATUS_MODIFIED, 'Modifiée'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    
    date = models.DateField()
    time_slot = models.TimeField()
    guest_count = models.PositiveIntegerField()
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, default=OCCASION_OTHER)
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-date', '-time_slot']

    def __str__(self):
        return f"Réservation {self.first_name} {self.last_name} le {self.date} à {self.time_slot.strftime('%H:%M')} ({self.guest_count} pers.)"
