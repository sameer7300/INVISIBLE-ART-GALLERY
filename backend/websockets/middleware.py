from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom JWT authentication middleware for WebSockets.
    
    Extracts the JWT token from the query parameters and authenticates the user.
    """
    
    def __init__(self, inner):
        super().__init__(inner)
    
    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()
        
        # Get the token from query string
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        
        # Set the default user
        scope["user"] = AnonymousUser()
        
        # If token is present, try to authenticate
        if token:
            try:
                # Verify the token
                UntypedToken(token)
                
                # Decode the token
                decoded_data = jwt_decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=["HS256"])
                
                # Get the user using the user_id from the token
                user = await self.get_user(decoded_data["user_id"])
                if user:
                    scope["user"] = user
            
            except (InvalidToken, TokenError) as e:
                # Token is invalid, user remains anonymous
                pass
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        """
        Get the user by ID from the database.
        
        Returns User object or None if not found.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None 