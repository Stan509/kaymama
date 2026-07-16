from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_ADMIN = 'ADMIN'
    ROLE_MANAGER = 'MANAGER'
    ROLE_KITCHEN = 'KITCHEN'
    ROLE_CASHIER = 'CASHIER'
    ROLE_DELIVERY = 'DELIVERY'
    ROLE_CUSTOMER = 'CUSTOMER'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Administrateur'),
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_MANAGER, 'Manager / Gérant'),
        (ROLE_KITCHEN, 'Cuisine'),
        (ROLE_CASHIER, 'Caissier'),
        (ROLE_DELIVERY, 'Livreur'),
        (ROLE_CUSTOMER, 'Client'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        verbose_name="Rôle"
    )
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    favorites = models.ManyToManyField('menu.Dish', blank=True, related_name='favorited_by', verbose_name="Favoris")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_staff_member(self):
        return self.role in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_MANAGER, self.ROLE_KITCHEN, self.ROLE_CASHIER, self.ROLE_DELIVERY]
