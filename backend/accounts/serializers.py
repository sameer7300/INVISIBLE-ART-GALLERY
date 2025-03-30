from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile_picture', 'bio', 'is_artist', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'is_artist'
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        """Validate that the passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        # Remove password_confirm as it's not needed for creating the user
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user."""
    
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name',
            'profile_picture', 'bio'
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user details."""
    
    def validate(self, attrs):
        """Add user data to the token response."""
        try:
            data = super().validate(attrs)
            
            # Add user data to response
            user = self.user
            data['user'] = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'is_artist': user.is_artist
            }
            
            # Rename token fields for frontend consistency
            data['access_token'] = data.pop('access')
            data['refresh_token'] = data.pop('refresh')
            
            return data
        except Exception as e:
            print(f"Token validation error: {str(e)}")
            raise


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate that the new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs 