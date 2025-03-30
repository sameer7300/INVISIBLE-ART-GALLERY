from django.contrib import admin
from .models import Artwork, RevealCondition, ArtworkView, Comment

class RevealConditionInline(admin.TabularInline):
    """Inline admin for Reveal Conditions."""
    model = RevealCondition
    extra = 1

class CommentInline(admin.TabularInline):
    """Inline admin for Comments."""
    model = Comment
    extra = 0
    readonly_fields = ('user', 'content', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    """Admin configuration for the Artwork model."""
    list_display = ('title', 'artist', 'content_type', 'is_revealed', 'view_count', 'created_at')
    list_filter = ('is_revealed', 'content_type', 'created_at')
    search_fields = ('title', 'description', 'artist__username')
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    inlines = [RevealConditionInline, CommentInline]

@admin.register(RevealCondition)
class RevealConditionAdmin(admin.ModelAdmin):
    """Admin configuration for the RevealCondition model."""
    list_display = ('artwork', 'condition_type', 'is_met', 'created_at')
    list_filter = ('condition_type', 'is_met')
    search_fields = ('artwork__title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ArtworkView)
class ArtworkViewAdmin(admin.ModelAdmin):
    """Admin configuration for the ArtworkView model."""
    list_display = ('artwork', 'viewer', 'viewed_at', 'ip_address')
    list_filter = ('viewed_at',)
    search_fields = ('artwork__title', 'viewer__username')
    readonly_fields = ('viewed_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for the Comment model."""
    list_display = ('artwork', 'user', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('artwork__title', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    
    def short_content(self, obj):
        """Return a truncated version of the content for the list display."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content' 