from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Artwork updates - for viewing real-time reveals
    re_path(r'ws/artwork/(?P<artwork_id>[0-9a-f-]+)/$', consumers.ArtworkConsumer.as_asgi()),
    
    # User notifications - for real-time notifications for artists and viewers
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
] 