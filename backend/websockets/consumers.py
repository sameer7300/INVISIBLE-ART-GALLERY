import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from artworks.models import Artwork

User = get_user_model()

class ArtworkConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for artwork updates.
    
    Sends real-time updates when artworks are revealed.
    """
    
    async def connect(self):
        """
        Accept the connection and join the artwork-specific group.
        
        Each artwork has its own group for updates.
        """
        self.artwork_id = self.scope['url_route']['kwargs']['artwork_id']
        self.artwork_group_name = f'artwork_{self.artwork_id}'
        
        # Check if the artwork exists
        artwork_exists = await self._get_artwork()
        if not artwork_exists:
            # Reject the connection if artwork doesn't exist
            await self.close()
            return
        
        # Join the artwork-specific group
        await self.channel_layer.group_add(
            self.artwork_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send initial status
        await self._send_artwork_status()
    
    async def disconnect(self, close_code):
        """
        Leave the artwork-specific group when disconnecting.
        """
        # Leave the artwork group
        await self.channel_layer.group_discard(
            self.artwork_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle messages from the WebSocket.
        
        Currently not used, but could be extended for client-initiated actions.
        """
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            # Handle different message types
            if message_type == 'check_status':
                await self._send_artwork_status()
        except json.JSONDecodeError:
            # Invalid JSON, ignore the message
            pass
    
    async def artwork_revealed(self, event):
        """
        Handle artwork_revealed event from the channel layer.
        
        Sends a message to the WebSocket when an artwork is revealed.
        """
        # Send the revelation message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'artwork_revealed',
            'artwork': event['artwork']
        }))
    
    async def _send_artwork_status(self):
        """
        Send the current status of the artwork to the WebSocket.
        """
        artwork = await self._get_artwork()
        if artwork:
            await self.send(text_data=json.dumps({
                'type': 'artwork_status',
                'is_revealed': artwork['is_revealed'],
                'artwork': {
                    'id': str(artwork['id']),
                    'title': artwork['title']
                }
            }))
    
    @database_sync_to_async
    def _get_artwork(self):
        """
        Get the artwork from the database.
        
        Returns dict with artwork data or None if not found.
        """
        try:
            artwork = Artwork.objects.get(id=self.artwork_id)
            return {
                'id': artwork.id,
                'title': artwork.title,
                'is_revealed': artwork.is_revealed
            }
        except Artwork.DoesNotExist:
            return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user notifications.
    
    Sends real-time notifications to users about their artworks and interactions.
    """
    
    async def connect(self):
        """
        Accept the connection and join the user-specific group.
        
        Each user has their own group for notifications.
        """
        # Get the user from the scope
        user = self.scope.get('user', AnonymousUser())
        
        # Only allow authenticated users
        if user.is_anonymous:
            await self.close()
            return
        
        self.user_id = str(user.id)
        self.user_group_name = f'user_{self.user_id}'
        
        # Join the user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()
        
        # Send a welcome message
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': 'Connected to notification service'
        }))
    
    async def disconnect(self, close_code):
        """
        Leave the user-specific group when disconnecting.
        """
        # Leave the user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle messages from the WebSocket.
        
        Currently not used, but could be extended for client-initiated actions.
        """
        pass
    
    async def notification(self, event):
        """
        Handle notification event from the channel layer.
        
        Sends a notification to the WebSocket.
        """
        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'data': event.get('data', {})
        })) 