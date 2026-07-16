from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('request/', views.request_quotation_view, name='request_quote'),
]
