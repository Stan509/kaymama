from rest_framework import serializers
from apps.menu.models import Category, Dish, DishVariant
from apps.reservations.models import Reservation
from apps.orders.models import Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DishVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishVariant
        fields = '__all__'

class DishSerializer(serializers.ModelSerializer):
    variants = DishVariantSerializer(many=True, read_only=True)
    class Meta:
        model = Dish
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
