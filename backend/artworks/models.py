import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Artwork(models.Model):
    """
    Model representing an artwork in the Invisible Art Gallery.
    
    Artworks are encrypted and stored with conditions for revelation.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(
        max_length=255
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    artist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='artworks'
    )
    encrypted_content = models.BinaryField(
        null=True,
        blank=True,
        editable=True
    )
    placeholder_image = models.ImageField(
        upload_to='placeholders/',
        null=True,
        blank=True
    )
    content_type = models.CharField(
        max_length=100,
        help_text=_('MIME type of the artwork content')
    )
    is_revealed = models.BooleanField(
        default=False,
        help_text=_('Whether the artwork has been revealed')
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of times this artwork has been viewed')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class RevealCondition(models.Model):
    """
    Model representing conditions for when an artwork should be revealed.
    
    Each artwork can have multiple reveal conditions.
    """
    CONDITION_TYPES = (
        ('time', 'Time-based'),
        ('view_count', 'View Count-based'),
        ('location', 'Location-based'),
        ('interactive', 'Interactive')
    )
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name='reveal_conditions'
    )
    condition_type = models.CharField(
        max_length=20,
        choices=CONDITION_TYPES
    )
    condition_value = models.JSONField(
        help_text=_('JSON data for the condition parameters')
    )
    is_met = models.BooleanField(
        default=False,
        help_text=_('Whether this condition has been met')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_condition_type_display()} condition for {self.artwork.title}"


class ArtworkView(models.Model):
    """
    Model tracking each view of an artwork.
    
    Used for analytics and revealing based on view count.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name='views'
    )
    viewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_artworks'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    device_info = models.JSONField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-viewed_at']
        # Ensure unique view per user+artwork combo for a time window
        unique_together = [['artwork', 'viewer', 'viewed_at']]


class Comment(models.Model):
    """
    Model representing a comment on an artwork.
    
    Users can comment on artworks, visible to other viewers.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.artwork.title}" 