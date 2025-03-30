from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ArtworkViewSet, ArtistArtworksView

# Create a router for the viewset
router = DefaultRouter()
router.register(r'', ArtworkViewSet, basename='artwork')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Artwork listing for artists
    path('my-artworks/', ArtistArtworksView.as_view(), name='my-artworks'),
] 