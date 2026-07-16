from django.test import TestCase
from apps.menu.models import Category, Dish

class MenuModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Plats Principaux")
        
    def test_category_slug(self):
        self.assertEqual(self.category.slug, "plats-principaux")

    def test_dish_stock_availability(self):
        dish = Dish.objects.create(
            category=self.category,
            name="Poulet colombo",
            price=15.00,
            stock_level=5
        )
        self.assertTrue(dish.is_in_stock)
        
        dish.stock_level = 0
        dish.save()
        self.assertFalse(dish.is_in_stock)
