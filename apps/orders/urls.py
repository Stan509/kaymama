from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:dish_id>/', views.cart_add_htmx, name='cart_add_htmx'),
    path('cart/remove/<str:cart_key>/', views.cart_remove_htmx, name='cart_remove_htmx'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
]
