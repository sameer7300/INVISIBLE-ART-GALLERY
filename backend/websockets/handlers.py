from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class WebSocketEventHandler:
    """
    Handler for WebSocket events.
    
    Provides methods to send notifications and updates to clients.
    """
    
    @staticmethod
    def notify_artwork_revealed(artwork):
        """
        Send a notification when an artwork is revealed.
        
        Args:
            artwork: The Artwork model instance that was revealed
        """
        channel_layer = get_channel_layer()
        
        # Artwork group message (for viewers watching the artwork)
        artwork_group_name = f'artwork_{artwork.id}'
        artwork_data = {
            'id': str(artwork.id),
            'title': artwork.title,
            'artist': artwork.artist.username,
            'is_revealed': artwork.is_revealed
        }
        
        async_to_sync(channel_layer.group_send)(
            artwork_group_name,
            {
                'type': 'artwork_revealed',
                'artwork': artwork_data
            }
        )
        
        # Notify the artist
        user_group_name = f'user_{artwork.artist.id}'
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'notification',
                'message': f'Your artwork "{artwork.title}" has been revealed!',
                'data': {
                    'type': 'artwork_revealed',
                    'artwork_id': str(artwork.id)
                }
            }
        )
    
    @staticmethod
    def notify_new_comment(comment):
        """
        Send a notification when a new comment is added to an artwork.
        
        Args:
            comment: The Comment model instance that was created
        """
        channel_layer = get_channel_layer()
        artwork = comment.artwork
        
        # Notify the artist
        if artwork.artist.id != comment.user.id:  # Don't notify if artist comments on their own work
            user_group_name = f'user_{artwork.artist.id}'
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification',
                    'message': f'New comment on your artwork "{artwork.title}"',
                    'data': {
                        'type': 'new_comment',
                        'artwork_id': str(artwork.id),
                        'comment_id': str(comment.id),
                        'user': comment.user.username
                    }
                }
            )
    
    @staticmethod
    def notify_new_view(artwork_view):
        """
        Send a notification when an artwork is viewed.
        
        Args:
            artwork_view: The ArtworkView model instance that was created
        """
        # Only notify for milestone view counts (10, 50, 100, etc.)
        artwork = artwork_view.artwork
        if artwork.view_count in [10, 50, 100, 500, 1000]:
            channel_layer = get_channel_layer()
            
            # Notify the artist
            user_group_name = f'user_{artwork.artist.id}'
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification',
                    'message': f'Your artwork "{artwork.title}" has reached {artwork.view_count} views!',
                    'data': {
                        'type': 'view_milestone',
                        'artwork_id': str(artwork.id),
                        'view_count': artwork.view_count
                    }
                }
            )
    
    @staticmethod
    def broadcast_system_message(message):
        """
        Broadcast a system message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        channel_layer = get_channel_layer()
        
        # Get all users (in a real system with many users, 
        # you'd want to optimize this to avoid loading all users at once)
        users = User.objects.all()
        
        for user in users:
            user_group_name = f'user_{user.id}'
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification',
                    'message': message,
                    'data': {
                        'type': 'system_message'
                    }
                }
            ) 