from django.test import TestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
import pytest
import json
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

from artworks.models import Artwork
from .consumers import ArtworkConsumer, NotificationConsumer
from .middleware import JWTAuthMiddleware

User = get_user_model()


class WebSocketTests(TestCase):
    """Test case for WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_artwork_consumer_connect(self):
        """Test connection to the ArtworkConsumer."""
        # Create test user and artwork
        user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='password123',
            is_artist=True
        )
        
        artwork = Artwork.objects.create(
            title='Test Artwork',
            description='This is a test artwork',
            artist=user,
            content_type='image/jpeg',
            is_revealed=True
        )
        
        # Create application with URL routing
        application = URLRouter([
            re_path(
                r'ws/artwork/(?P<artwork_id>[0-9a-f-]+)/$',
                ArtworkConsumer.as_asgi()
            ),
        ])
        
        # Create WebSocket communicator
        communicator = WebsocketCommunicator(
            application,
            f"/ws/artwork/{artwork.id}/"
        )
        
        # Connect to WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Receive initial status message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'artwork_status')
        self.assertTrue(response['is_revealed'])
        self.assertEqual(response['artwork']['id'], str(artwork.id))
        
        # Disconnect
        await communicator.disconnect()
    
    @pytest.mark.asyncio
    async def test_artwork_consumer_nonexistent_artwork(self):
        """Test connection with non-existent artwork ID."""
        # Create application with URL routing
        application = URLRouter([
            re_path(
                r'ws/artwork/(?P<artwork_id>[0-9a-f-]+)/$',
                ArtworkConsumer.as_asgi()
            ),
        ])
        
        # Create WebSocket communicator with non-existent artwork ID
        communicator = WebsocketCommunicator(
            application,
            f"/ws/artwork/{uuid.uuid4()}/"
        )
        
        # Connection should be rejected
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
    
    @pytest.mark.asyncio
    async def test_notification_consumer_authenticated(self):
        """Test connection to the NotificationConsumer with authentication."""
        # Create test user
        user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='password123'
        )
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        # Create application with JWT authentication middleware
        application = JWTAuthMiddleware(
            URLRouter([
                re_path(
                    r'ws/notifications/$',
                    NotificationConsumer.as_asgi()
                ),
            ])
        )
        
        # Create WebSocket communicator with token
        communicator = WebsocketCommunicator(
            application,
            f"/ws/notifications/?token={token}"
        )
        
        # Connect to WebSocket
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Receive welcome message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'welcome')
        
        # Disconnect
        await communicator.disconnect()
    
    @pytest.mark.asyncio
    async def test_notification_consumer_unauthenticated(self):
        """Test connection to the NotificationConsumer without authentication."""
        # Create application with JWT authentication middleware
        application = JWTAuthMiddleware(
            URLRouter([
                re_path(
                    r'ws/notifications/$',
                    NotificationConsumer.as_asgi()
                ),
            ])
        )
        
        # Create WebSocket communicator without token
        communicator = WebsocketCommunicator(
            application,
            "/ws/notifications/"
        )
        
        # Connection should be rejected (user is anonymous)
        connected, _ = await communicator.connect()
        self.assertFalse(connected) 