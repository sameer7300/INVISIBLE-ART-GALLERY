from rest_framework import permissions

class IsArtistOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow artists to create artworks.
    
    Read-only access is allowed for all authenticated users.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to artists
        return request.user.is_artist


class IsArtistOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow artist owners to update or delete their artworks.
    
    Read-only access is allowed for all authenticated users.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the artist who owns the artwork
        return obj.artist == request.user and request.user.is_artist 