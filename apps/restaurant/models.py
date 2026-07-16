from django.db import models

class RestaurantSettings(models.Model):
    name = models.CharField(max_length=100, default="Kay Mama Cuisine Créole")
    address = models.TextField(default="48 Av. François Ronjon, 97300 Cayenne")
    phone = models.CharField(max_length=20, default="694 08 12 80")
    whatsapp = models.CharField(max_length=20, default="+594694081280")
    facebook = models.CharField(max_length=100, default="Kay Mama Cuisine Créole")
    google_maps_url = models.TextField(default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3976.223841071489!2d-52.32789182390141!3d4.935747439972338!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8d12163b7ad781ff%3A0xe543df5e967a1fd7!2s48%20Av.%20Fran%C3%A7ois%20Ronjon%2C%20Cayenne%2097300%2C%20French%20Guiana!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s")
    max_guests_per_slot = models.PositiveIntegerField(default=30)
    delivery_min_dishes = models.PositiveIntegerField(default=5)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    is_ordering_enabled = models.BooleanField(default=True)
    is_reservations_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Paramètre du Restaurant"
        verbose_name_plural = "Paramètres du Restaurant"

    def __str__(self):
        return self.name

class OpeningHours(models.Model):
    DAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Horaire d'ouverture"
        verbose_name_plural = "Horaires d'ouverture"
        ordering = ['day_of_week']

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_of_week_display()} : Fermé"
        return f"{self.get_day_of_week_display()} : {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"

class BlockedDate(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Date bloquée"
        verbose_name_plural = "Dates bloquées"

    def __str__(self):
        return f"{self.date.strftime('%d/%m/%Y')} ({self.reason})"
