from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Artwork, RevealCondition, Comment, ArtworkView
import json

User = get_user_model()

class ArtistSerializer(serializers.ModelSerializer):
    """Serializer for minimal artist information."""
    
    class Meta:
        model = User
        fields = ('id', 'username')


class RevealConditionSerializer(serializers.ModelSerializer):
    """Serializer for reveal conditions."""
    
    class Meta:
        model = RevealCondition
        fields = ('id', 'condition_type', 'condition_value', 'is_met')
        read_only_fields = ('id', 'is_met')
    
    def to_internal_value(self, data):
        """Debug and process incoming data format."""
        print(f"RevealConditionSerializer received data: {data}")
        
        # Check if we need to convert condition_value from string to dict
        if 'condition_value' in data and isinstance(data['condition_value'], str):
            try:
                data = data.copy() if hasattr(data, 'copy') else dict(data)
                data['condition_value'] = json.loads(data['condition_value'])
                print(f"Converted condition_value from string to: {data['condition_value']}")
            except json.JSONDecodeError:
                print(f"Failed to parse condition_value as JSON: {data['condition_value']}")
        
        # Remove any [condition_type] key if it exists (from form data format)
        if '[condition_type]' in data:
            print("Cleaning up form data format keys")
            new_data = {}
            for key, value in data.items():
                new_key = key.replace('[', '').replace(']', '')
                new_data[new_key] = value
            data = new_data
            print(f"Cleaned data: {data}")
        
        return super().to_internal_value(data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    
    user = ArtistSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class ArtworkListSerializer(serializers.ModelSerializer):
    """Serializer for listing artworks."""
    
    artist = ArtistSerializer(read_only=True)
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'description', 'artist', 'placeholder_image',
            'content_type', 'is_revealed', 'view_count', 'created_at'
        )
        read_only_fields = ('id', 'is_revealed', 'view_count', 'created_at')


class ArtworkDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed artwork view."""
    
    artist = ArtistSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reveal_conditions = RevealConditionSerializer(many=True, read_only=True)
    content = serializers.SerializerMethodField()
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'description', 'artist', 'content',
            'placeholder_image', 'content_type', 'is_revealed',
            'reveal_conditions', 'view_count', 'comments', 'created_at'
        )
        read_only_fields = (
            'id', 'is_revealed', 'view_count', 'created_at',
            'comments', 'content'
        )
    
    def get_content(self, obj):
        """
        Return content URL if artwork is revealed.
        
        This method will be replaced with actual decryption logic in the view.
        """
        # In the serializer, we just return None as the decryption
        # will be handled by the view/encryption service
        return None


class ArtworkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating artworks."""
    
    artwork_file = serializers.FileField(write_only=True)
    reveal_conditions = RevealConditionSerializer(many=True, required=True)

    class Meta:
        model = Artwork
        fields = (
            'title', 'description', 'content_type', 'artwork_file',
            'placeholder_image', 'reveal_conditions'
        )

    def validate(self, attrs):
        """Validate the artwork data and handle form data format for reveal_conditions."""
        # Get request data directly for debugging
        request_data = self.context['request'].data
        print(f"Raw request data keys: {request_data.keys()}")

        # Check if we need to parse reveal_conditions from form data format
        if not attrs.get('reveal_conditions') and request_data:
            reveal_conditions = []
            condition_index = 0
            
            # Check for form-encoded array syntax (reveal_conditions[0][condition_type], etc)
            while True:
                type_key = f'reveal_conditions[{condition_index}][condition_type]'
                value_key = f'reveal_conditions[{condition_index}][condition_value]'
                
                if type_key in request_data and value_key in request_data:
                    print(f"Found form data condition at index {condition_index}")
                    try:
                        # Parse the condition value from JSON string if needed
                        condition_value = request_data[value_key]
                        if isinstance(condition_value, str):
                            try:
                                condition_value = json.loads(condition_value)
                            except json.JSONDecodeError:
                                print(f"Error parsing JSON for condition value: {condition_value}")
                                # Keep as is if not valid JSON
                        
                        condition = {
                            'condition_type': request_data[type_key],
                            'condition_value': condition_value
                        }
                        reveal_conditions.append(condition)
                        print(f"Parsed condition: {condition}")
                    except Exception as e:
                        print(f"Error parsing condition at index {condition_index}: {str(e)}")
                    
                    condition_index += 1
                else:
                    break
            
            if reveal_conditions:
                # Validate each condition using the RevealConditionSerializer
                condition_serializers = []
                for condition_data in reveal_conditions:
                    condition_serializer = RevealConditionSerializer(data=condition_data)
                    if condition_serializer.is_valid():
                        condition_serializers.append(condition_serializer)
                    else:
                        print(f"Condition validation errors: {condition_serializer.errors}")
                        raise serializers.ValidationError({
                            'reveal_conditions': condition_serializer.errors
                        })
                
                # Add the validated conditions to attrs
                attrs['reveal_conditions'] = [
                    serializer.validated_data for serializer in condition_serializers
                ]
                print(f"Final reveal_conditions: {attrs['reveal_conditions']}")
        
        return attrs

    def create(self, validated_data):
        """Create a new artwork with encrypted content and reveal conditions."""
        # Pop the reveal conditions and artwork file from validated data
        reveal_conditions_data = validated_data.pop('reveal_conditions', [])
        artwork_file = validated_data.pop('artwork_file')
        
        # Encryption should happen in the view since it requires settings.ENCRYPTION_KEY
        # Just create the artwork model here
        artwork = Artwork.objects.create(
            artist=self.context['request'].user,
            **validated_data
        )
        
        # Create the reveal conditions
        for condition_data in reveal_conditions_data:
            RevealCondition.objects.create(artwork=artwork, **condition_data)
        
        return artwork


class ArtworkUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating artworks."""
    
    reveal_conditions = RevealConditionSerializer(many=True, required=False)
    
    class Meta:
        model = Artwork
        fields = (
            'title', 'description', 'placeholder_image',
            'reveal_conditions'
        )
    
    def update(self, instance, validated_data):
        """Update artwork and associated conditions."""
        reveal_conditions_data = validated_data.pop('reveal_conditions', None)
        
        # Update artwork fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update reveal conditions if provided
        if reveal_conditions_data is not None:
            # Remove existing conditions
            instance.reveal_conditions.all().delete()
            
            # Create new conditions
            for condition_data in reveal_conditions_data:
                RevealCondition.objects.create(
                    artwork=instance,
                    **condition_data
                )
        
        return instance


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ('content',)
    
    def create(self, validated_data):
        """Create a comment associated with an artwork and user."""
        artwork = self.context['artwork']
        user = self.context['request'].user
        
        return Comment.objects.create(
            artwork=artwork,
            user=user,
            **validated_data
        ) 