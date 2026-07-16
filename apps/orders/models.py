from django.db import models
from django.conf import settings
import uuid

class Order(models.Model):
    STATUS_INCOMING = 'INCOMING'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY = 'READY'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_INCOMING, 'Reçue / En attente'),
        (STATUS_PREPARING, 'En préparation'),
        (STATUS_READY, 'Prête'),
        (STATUS_DELIVERED, 'En livraison'),
        (STATUS_COMPLETED, 'Terminée'),
        (STATUS_CANCELLED, 'Annulée'),
    ]

    PAY_STATUS_PENDING = 'PENDING'
    PAY_STATUS_PAID = 'PAID'
    PAY_STATUS_FAILED = 'FAILED'

    PAY_STATUS_CHOICES = [
        (PAY_STATUS_PENDING, 'En attente'),
        (PAY_STATUS_PAID, 'Payé'),
        (PAY_STATUS_FAILED, 'Échoué'),
    ]

    DELIVERY_PICKUP = 'PICKUP'
    DELIVERY_HOME = 'DELIVERY'

    DELIVERY_CHOICES = [
        (DELIVERY_PICKUP, 'À emporter (sur place)'),
        (DELIVERY_HOME, 'Livraison à domicile'),
    ]

    PAY_METHOD_CARD = 'CARD'
    PAY_METHOD_CASH = 'CASH'
    PAY_METHOD_DELIVERY = 'ON_DELIVERY'

    PAY_METHOD_CHOICES = [
        (PAY_METHOD_CARD, 'Carte bancaire en ligne'),
        (PAY_METHOD_CASH, 'Espèces au comptoir'),
        (PAY_METHOD_DELIVERY, 'À la livraison'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_PICKUP)
    delivery_address = models.TextField(blank=True)
    delivery_time = models.DateTimeField()
    special_instructions = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INCOMING)
    payment_status = models.CharField(max_length=20, choices=PAY_STATUS_CHOICES, default=PAY_STATUS_PENDING)
    payment_method = models.CharField(max_length=20, choices=PAY_METHOD_CHOICES, default=PAY_METHOD_CARD)
    
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"KM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.order_number} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey('menu.Dish', on_delete=models.PROTECT)
    variant = models.ForeignKey('menu.DishVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} @ {self.price} €"

    @property
    def total_item_price(self):
        return self.price * self.quantity
