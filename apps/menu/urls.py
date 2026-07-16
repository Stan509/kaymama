from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('items-htmx/', views.menu_items_htmx, name='items_htmx'),
    path('favorite/<int:dish_id>/', views.toggle_favorite, name='toggle_favorite'),
]
