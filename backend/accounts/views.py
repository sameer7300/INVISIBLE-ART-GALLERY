from rest_framework import status, generics, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import logging
import traceback

from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    CustomTokenObtainPairSerializer, ChangePasswordSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    
    Creates a new user with the provided information.
    """
    authentication_classes = []  # No authentication required
    permission_classes = []      # No permissions required
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Registration attempt with data: {request.data}")
        
        try:
            serializer = UserCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            user = serializer.save()
            
            # Create token for new user
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }
            
            logger.info(f"User registered successfully: {user.username}")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": "Registration failed. Please try again.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint for token authentication.
    
    Returns JWT tokens for valid users.
    """
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    API endpoint for user logout.
    
    Blacklists the refresh token to enforce logout.
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile.
    
    Returns user details for the authenticated user.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing password.
    
    Updates password for the authenticated user.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            return Response(
                {"detail": "Password updated successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 