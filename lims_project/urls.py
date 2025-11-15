"""
URL configuration for LIMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('samples/', include('samples.urls')),
    path('tests/', include('tests.urls')),
    path('results/', include('results.urls')),
    path('inventory/', include('inventory.urls')),
    path('instruments/', include('instruments.urls')),
    path('reports/', include('reports.urls')),
    path('audit/', include('audit.urls')),
    path('auth/', include('users.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "LIMS Administration"
admin.site.site_title = "LIMS Admin Portal"
admin.site.index_title = "Welcome to LIMS Administration"
