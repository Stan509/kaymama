from django.db import models
from django.conf import settings

class EventQuotation(models.Model):
    EVENT_BIRTHDAY = 'BIRTHDAY'
    EVENT_WEDDING = 'WEDDING'
    EVENT_CORPORATE = 'CORPORATE'
    EVENT_PRIVATE = 'PRIVATE_CHEF'
    EVENT_BUFFET = 'BUFFET'
    EVENT_COCKTAIL = 'COCKTAIL'
    EVENT_OTHER = 'OTHER'

    EVENT_CHOICES = [
        (EVENT_BIRTHDAY, 'Anniversaire'),
        (EVENT_WEDDING, 'Mariage / Fiançailles'),
        (EVENT_CORPORATE, 'Événement d\'entreprise'),
        (EVENT_PRIVATE, 'Chef Privé à domicile'),
        (EVENT_BUFFET, 'Service Buffet'),
        (EVENT_COCKTAIL, 'Service Cocktail'),
        (EVENT_OTHER, 'Autre'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_SENT = 'SENT'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Demande en attente'),
        (STATUS_SENT, 'Devis envoyé'),
        (STATUS_COMPLETED, 'Événement validé / effectué'),
        (STATUS_CANCELLED, 'Annulé'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_quotations')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default=EVENT_OTHER)
    event_date = models.DateField()
    guest_count = models.PositiveIntegerField()
    notes = models.TextField(verbose_name="Détails du projet / demandes particulières")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande de devis événementiel"
        verbose_name_plural = "Demandes de devis événementiels"
        ordering = ['-created_at']

    def __str__(self):
        return f"Devis {self.get_event_type_display()} par {self.name} pour le {self.event_date}"
