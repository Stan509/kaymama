from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'dishes', views.DishViewSet, basename='dish')
router.register(r'reservations', views.ReservationViewSet, basename='reservation')
router.register(r'orders', views.OrderViewSet, basename='order')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
