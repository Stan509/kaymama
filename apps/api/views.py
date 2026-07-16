from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.menu.models import Category, Dish
from apps.reservations.models import Reservation
from apps.orders.models import Order
from .serializers import CategorySerializer, DishSerializer, ReservationSerializer, OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        # Customers can only see their own reservations, staff can see all
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff_member:
                return Reservation.objects.all()
            return Reservation.objects.filter(user=user)
        return Reservation.objects.none()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff_member:
                return Order.objects.all()
            return Order.objects.filter(user=user)
        return Order.objects.none()
