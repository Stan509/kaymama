from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order_index', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes', verbose_name="Catégorie")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    is_specialty = models.BooleanField(default=False, verbose_name="Spécialité Créole")
    stock_level = models.IntegerField(default=100, verbose_name="Niveau de stock")
    order_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
        ordering = ['order_index', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_level > 0

class DishVariant(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='variants', verbose_name="Plat")
    name = models.CharField(max_length=100) # e.g. "Grand", "Petit", "Sauce supplémentaire"
    additional_price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Variante de plat"
        verbose_name_plural = "Variantes de plats"

    def __str__(self):
        return f"{self.dish.name} - {self.name} (+{self.additional_price} €)"
