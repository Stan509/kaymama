from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('book/', views.reserve_table_view, name='book'),
    path('success/<int:reservation_id>/', views.reservation_success_view, name='success'),
]
