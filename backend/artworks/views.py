from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import F
from django.conf import settings

from .models import Artwork, Comment, ArtworkView, RevealCondition
from .serializers import (
    ArtworkListSerializer, ArtworkDetailSerializer, ArtworkCreateSerializer,
    ArtworkUpdateSerializer, CommentSerializer, CommentCreateSerializer
)
from .permissions import IsArtistOrReadOnly, IsArtistOwnerOrReadOnly

# Import the encryption service
from encryption.services import EncryptionService

# Import WebSocket event handler
from websockets.handlers import WebSocketEventHandler


class ArtworkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling artwork operations.
    
    Provides CRUD operations plus additional actions.
    """
    permission_classes = [permissions.IsAuthenticated, IsArtistOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'artist__username']
    ordering_fields = ['created_at', 'view_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return different querysets based on the action.
        
        For non-detail views, artists can see their own unrevealed artworks.
        Other users can only see revealed artworks or those they own.
        """
        user = self.request.user
        
        print(f"ArtworkViewSet.get_queryset: User: {user.username} (ID: {user.id})")
        print(f"ArtworkViewSet.get_queryset: Action: {self.action}")
        print(f"ArtworkViewSet.get_queryset: Is artist: {getattr(user, 'is_artist', False)}")
        
        if self.action in ['list', 'search']:
            if user.is_artist:
                # Artists can see their own artworks regardless of reveal status
                queryset = Artwork.objects.filter(
                    artist=user
                ).select_related('artist').prefetch_related('reveal_conditions')
                print(f"ArtworkViewSet.get_queryset: Returning {queryset.count()} artworks for artist {user.username}")
                return queryset
            else:
                # Regular users can only see revealed artworks
                queryset = Artwork.objects.filter(
                    is_revealed=True
                ).select_related('artist').prefetch_related('reveal_conditions')
                print(f"ArtworkViewSet.get_queryset: Returning {queryset.count()} revealed artworks for user {user.username}")
                return queryset
        
        # For other actions (retrieve, update, destroy), the permission classes will handle access
        queryset = Artwork.objects.all().select_related('artist').prefetch_related(
            'reveal_conditions', 'comments__user'
        )
        print(f"ArtworkViewSet.get_queryset: Returning all artworks for action {self.action}")
        return queryset

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action == 'list' or self.action == 'search':
            return ArtworkListSerializer
        elif self.action == 'create':
            return ArtworkCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArtworkUpdateSerializer
        elif self.action == 'add_comment':
            return CommentCreateSerializer
        return ArtworkDetailSerializer

    def get_permissions(self):
        """
        Return different permissions based on the action.
        
        Create requires IsArtist permission.
        Update and delete require ownership.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsArtistOwnerOrReadOnly]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single artwork and handle view tracking.
        
        Increments view count and checks if conditions are met for revealing.
        """
        artwork = self.get_object()
        
        # Track the view if the user is authenticated
        if request.user.is_authenticated:
            artwork_view = self._track_view(artwork, request)
            
            # Send notification for milestone views
            WebSocketEventHandler.notify_new_view(artwork_view)
        
        # Check if conditions should be evaluated
        was_revealed = artwork.is_revealed
        if not artwork.is_revealed:
            self._check_reveal_conditions(artwork)
            
            # Reload the artwork if revelation status has changed
            if not was_revealed and artwork.is_revealed:
                # Send notification about the artwork reveal
                WebSocketEventHandler.notify_artwork_revealed(artwork)
        
        # Get content if the artwork is revealed
        serializer = self.get_serializer(artwork)
        data = serializer.data
        
        # If the artwork is revealed, provide the decrypted content
        if artwork.is_revealed and artwork.encrypted_content:
            encryption_service = EncryptionService()
            try:
                decrypted_content = encryption_service.decrypt(
                    artwork.encrypted_content,
                    settings.ENCRYPTION_KEY
                )
                # In a real implementation, we'd return a URL to the decrypted content
                # or a data URL. For now, we'll indicate that content is available.
                data['content'] = f"/api/v1/artworks/{artwork.id}/content/"
            except Exception as e:
                # Log the error but don't expose it to the client
                print(f"Error decrypting content: {e}")
        
        return Response(data)

    def create(self, request, *args, **kwargs):
        """
        Create a new artwork with encrypted content.
        
        Handles file upload, encryption, and saving the artwork.
        """
        print(f"Artwork create request from user {request.user.username} (ID: {request.user.id})")
        print(f"Request data keys: {request.data.keys()}")
        
        # Print all form data for debugging
        for key in request.data.keys():
            if key != 'artwork_file':  # Don't print the file content
                print(f"Request data '{key}': {request.data.get(key)}")
        
        # Initialize serializer with debug context
        context = {'request': request, 'debug': True}
        serializer = self.get_serializer(data=request.data, context=context)
        
        # Debug serializer validation
        try:
            serializer.is_valid(raise_exception=False)
            if not serializer.is_valid():
                print(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception during serializer validation: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle the file and encryption
        artwork_file = request.data.get('artwork_file')
        
        if not artwork_file:
            print("Artwork file is missing in the request")
            return Response(
                {"artwork_file": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the file is valid
        if not hasattr(artwork_file, 'read'):
            print(f"Invalid artwork file: {type(artwork_file)}")
            return Response(
                {"artwork_file": ["Invalid file object."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check file size
        try:
            file_size = artwork_file.size
            print(f"Artwork file size: {file_size} bytes")
            
            if file_size == 0:
                print("Empty artwork file")
                return Response(
                    {"artwork_file": ["The uploaded file is empty."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                print(f"File too large: {file_size} bytes")
                return Response(
                    {"artwork_file": [f"The file is too large. Maximum size is 10MB."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"Error checking file size: {str(e)}")
        
        # Encrypt the file
        encryption_service = EncryptionService()
        try:
            print(f"Encrypting file of type: {type(artwork_file)}, name: {getattr(artwork_file, 'name', 'unknown')}")
            
            # Reset file pointer to beginning to ensure we read the entire file
            artwork_file.seek(0)
            
            # Read file content
            file_content = artwork_file.read()
            if not file_content:
                print("Failed to read file content - empty content")
                return Response(
                    {"artwork_file": ["Failed to read file content."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"Read {len(file_content)} bytes from the uploaded file")
            
            # Encrypt the content
            encrypted_content = encryption_service.encrypt(
                file_content,
                settings.ENCRYPTION_KEY
            )
            
            if not encrypted_content:
                print("Encryption produced empty result")
                return Response(
                    {"detail": "Failed to encrypt artwork."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            print(f"File encrypted successfully, encrypted size: {len(encrypted_content)} bytes")
            
        except Exception as e:
            print(f"Error encrypting content: {str(e)}")
            return Response(
                {"detail": f"Error encrypting content: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Save the artwork
        try:
            # Create the artwork without encrypted content first
            artwork = serializer.save()
            
            # Update the encrypted content
            artwork.encrypted_content = encrypted_content
            artwork.save()
            
            print(f"Artwork created successfully with ID: {artwork.id}")
            
            # Return the response with the artwork data
            return Response(
                ArtworkDetailSerializer(artwork).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"Error saving artwork: {str(e)}")
            return Response(
                {"detail": f"Error saving artwork: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_comment(self, request, pk=None):
        """
        Add a comment to an artwork.
        
        Requires authentication but not artist status.
        """
        artwork = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'artwork': artwork}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        # Send notification about the new comment
        WebSocketEventHandler.notify_new_comment(comment)
        
        # Check if the comment triggers an interactive condition
        was_revealed = artwork.is_revealed
        self._check_interactive_conditions(artwork)
        
        # If artwork was revealed due to this comment, send notification
        if not was_revealed and artwork.is_revealed:
            WebSocketEventHandler.notify_artwork_revealed(artwork)
        
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for artworks by title or description.
        
        Uses the search filter backend.
        """
        return self.list(request)

    @action(detail=False, methods=['get'])
    def by_artist(self, request):
        """
        Filter artworks by artist ID.
        
        Returns artworks created by the specified artist.
        """
        artist_id = request.query_params.get('artist_id')
        if not artist_id:
            return Response(
                {"detail": "Artist ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(artist_id=artist_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _track_view(self, artwork, request):
        """
        Track a view of an artwork.
        
        Records the view in ArtworkView and updates the view count.
        """
        # Extract IP and user agent
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create a view record
        artwork_view = ArtworkView.objects.create(
            artwork=artwork,
            viewer=request.user,
            ip_address=ip_address,
            device_info={'user_agent': user_agent}
        )
        
        # Update view count
        artwork.view_count = F('view_count') + 1
        artwork.save(update_fields=['view_count'])
        artwork.refresh_from_db()
        
        return artwork_view

    def _check_reveal_conditions(self, artwork):
        """
        Check if the artwork should be revealed based on conditions.
        
        Evaluates time-based and view-count-based conditions.
        """
        if artwork.is_revealed:
            return
        
        conditions = artwork.reveal_conditions.filter(is_met=False)
        
        # Track if any condition is met
        any_condition_met = False
        
        for condition in conditions:
            if condition.condition_type == 'time':
                # Check time-based condition
                reveal_time = condition.condition_value.get('reveal_at')
                if reveal_time and timezone.now() > timezone.datetime.fromisoformat(reveal_time):
                    condition.is_met = True
                    condition.save()
                    any_condition_met = True
            
            elif condition.condition_type == 'view_count':
                # Check view count condition
                view_threshold = condition.condition_value.get('count')
                if view_threshold and artwork.view_count >= int(view_threshold):
                    condition.is_met = True
                    condition.save()
                    any_condition_met = True
        
        # If any condition is met, reveal the artwork
        if any_condition_met:
            artwork.is_revealed = True
            artwork.save()

    def _check_interactive_conditions(self, artwork):
        """
        Check if interactive conditions are met.
        
        Currently handles comment-based conditions.
        """
        if artwork.is_revealed:
            return
        
        conditions = artwork.reveal_conditions.filter(
            is_met=False,
            condition_type='interactive'
        )
        
        for condition in conditions:
            condition_value = condition.condition_value
            
            if 'comment_count' in condition_value:
                # Check comment count condition
                required_comments = int(condition_value['comment_count'])
                actual_comments = artwork.comments.count()
                
                if actual_comments >= required_comments:
                    condition.is_met = True
                    condition.save()
                    
                    # Reveal the artwork
                    artwork.is_revealed = True
                    artwork.save()
                    break

    def _get_client_ip(self, request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ArtistArtworksView(generics.ListAPIView):
    """
    List artworks created by the authenticated artist.
    
    Only for artists to view their own artworks.
    """
    serializer_class = ArtworkListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return artworks created by the authenticated user."""
        print(f"ArtistArtworksView: Getting artworks for user {self.request.user.username} (ID: {self.request.user.id})")
        return Artwork.objects.filter(
            artist=self.request.user
        ).select_related('artist').prefetch_related('reveal_conditions')
    
    def list(self, request, *args, **kwargs):
        """Override list method to add logging."""
        print(f"ArtistArtworksView: Processing list request from user {request.user.username}")
        queryset = self.filter_queryset(self.get_queryset())
        
        # Log the results count
        print(f"ArtistArtworksView: Found {queryset.count()} artworks")
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 