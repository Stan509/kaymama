from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom project modules
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('menu/', include('apps.menu.urls')),
    path('orders/', include('apps.orders.urls')),
    path('reservations/', include('apps.reservations.urls')),
    path('events/', include('apps.events.urls')),
    path('blog/', include('apps.blog.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('payments/', include('apps.payments.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # APIs
    path('api/', include('apps.api.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
