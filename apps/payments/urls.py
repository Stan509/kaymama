from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.payment_checkout_view, name='checkout'),
]
