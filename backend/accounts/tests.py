from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(TestCase):
    """Test case for the User model and API endpoints."""

    def setUp(self):
        """Set up test client and test user."""
        self.client = APIClient()
        
        # Create test user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword123',
            'password_confirm': 'strongpassword123',
            'is_artist': True
        }
        
        # URL endpoints
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('user_profile')

    def test_user_registration(self):
        """Test user registration with valid data."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertEqual(response.data['user']['username'], self.user_data['username'])
        self.assertEqual(response.data['user']['is_artist'], self.user_data['is_artist'])
        
        # Check user was created in the database
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_user_login(self):
        """Test user login with valid credentials."""
        # Create user first
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_artist=self.user_data['is_artist']
        )
        
        # Login credentials
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('user' in response.data)

    def test_user_profile_get(self):
        """Test retrieving user profile when authenticated."""
        # Create and authenticate user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_artist=self.user_data['is_artist']
        )
        
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_user_profile_update(self):
        """Test updating user profile when authenticated."""
        # Create and authenticate user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_artist=self.user_data['is_artist']
        )
        
        self.client.force_authenticate(user=user)
        
        # Update data
        update_data = {
            'username': 'updateduser',
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'This is a test user bio.'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], update_data['username'])
        self.assertEqual(response.data['first_name'], update_data['first_name'])
        self.assertEqual(response.data['last_name'], update_data['last_name'])
        self.assertEqual(response.data['bio'], update_data['bio'])
        
        # Refresh user from database
        user.refresh_from_db()
        self.assertEqual(user.username, update_data['username'])
        self.assertEqual(user.first_name, update_data['first_name'])
        self.assertEqual(user.last_name, update_data['last_name'])
        self.assertEqual(user.bio, update_data['bio']) 