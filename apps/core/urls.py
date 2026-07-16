from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('salon-de-beaute/', views.salon_view, name='salon'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
    # PWA and SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('manifest.json', views.pwa_manifest, name='manifest_json'),
    path('sw.js', views.pwa_service_worker, name='service_worker'),
]
