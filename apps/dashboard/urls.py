from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('reservations/', views.reservations_list, name='reservations'),
    path('reservations/update/<int:res_id>/<str:status>/', views.update_reservation_status, name='update_reservation'),
    path('kitchen/', views.kitchen_screen, name='kitchen'),
    path('orders/', views.orders_list, name='orders'),
    path('orders/update/<int:order_id>/<str:status>/', views.update_order_status_htmx, name='update_order_status'),
    path('settings/', views.settings_edit, name='settings'),
    path('menu/', views.menu_edit, name='menu'),
    path('menu/stock/<int:dish_id>/', views.update_dish_stock, name='update_dish_stock'),
]
