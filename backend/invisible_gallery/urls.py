"""
URL Configuration for invisible_gallery project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API documentation schema
schema_view = get_schema_view(
    openapi.Info(
        title="Invisible Art Gallery API",
        default_version='v1',
        description="API for the Invisible Art Gallery platform",
        terms_of_service="https://www.invisibleartgallery.com/terms/",
        contact=openapi.Contact(email="support@invisibleartgallery.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API URL patterns
api_urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('artworks/', include('artworks.urls')),
    path('users/', include('accounts.user_urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/', include(api_urlpatterns)),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 