from django.urls import path

from .views import (
    UserProfileView, ChangePasswordView
)

urlpatterns = [
    # User endpoints
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change_password'),
] 