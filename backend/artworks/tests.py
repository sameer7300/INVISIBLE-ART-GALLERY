from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import io
from PIL import Image

from .models import Artwork, RevealCondition, Comment

User = get_user_model()

class ArtworkTests(TestCase):
    """Test case for the Artwork model and API endpoints."""

    def setUp(self):
        """Set up test client and test users."""
        self.client = APIClient()
        
        # Create artist user
        self.artist = User.objects.create_user(
            username='testartist',
            email='artist@example.com',
            password='password123',
            is_artist=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='user@example.com',
            password='password123',
            is_artist=False
        )
        
        # Create test artwork
        self.artwork = Artwork.objects.create(
            title='Test Artwork',
            description='This is a test artwork',
            artist=self.artist,
            content_type='image/jpeg',
        )
        
        # Create reveal condition
        self.condition = RevealCondition.objects.create(
            artwork=self.artwork,
            condition_type='view_count',
            condition_value={'count': 3},
            is_met=False
        )
        
        # URL endpoints
        self.artworks_url = reverse('artwork-list')
        self.detail_url = reverse('artwork-detail', args=[str(self.artwork.id)])
        self.comment_url = reverse('artwork-add-comment', args=[str(self.artwork.id)])
        self.my_artworks_url = reverse('my-artworks')

    def _get_temporary_image(self):
        """Create a temporary image for testing file uploads."""
        image = Image.new('RGB', (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.name = 'test_image.jpg'
        image_io.seek(0)
        return image_io

    def test_create_artwork(self):
        """Test creating a new artwork as an artist."""
        self.client.force_authenticate(user=self.artist)
        
        # Create artwork data
        artwork_data = {
            'title': 'New Artwork',
            'description': 'This is a new artwork',
            'content_type': 'image/jpeg',
            'artwork_file': self._get_temporary_image(),
            'reveal_conditions': json.dumps([{
                'condition_type': 'time',
                'condition_value': {
                    'reveal_at': '2025-01-01T00:00:00Z'
                }
            }])
        }
        
        response = self.client.post(self.artworks_url, artwork_data, format='multipart')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artwork.objects.count(), 2)  # Original + new artwork
        
        # Check that the artwork was created with the correct data
        new_artwork = Artwork.objects.filter(title='New Artwork').first()
        self.assertIsNotNone(new_artwork)
        self.assertEqual(new_artwork.artist, self.artist)
        self.assertEqual(new_artwork.title, artwork_data['title'])
        self.assertEqual(new_artwork.description, artwork_data['description'])
        self.assertEqual(new_artwork.content_type, artwork_data['content_type'])
        
        # Check that a reveal condition was created
        self.assertEqual(new_artwork.reveal_conditions.count(), 1)
        condition = new_artwork.reveal_conditions.first()
        self.assertEqual(condition.condition_type, 'time')

    def test_non_artist_cannot_create_artwork(self):
        """Test that non-artists cannot create artworks."""
        self.client.force_authenticate(user=self.user)
        
        artwork_data = {
            'title': 'New Artwork',
            'description': 'This is a new artwork',
            'content_type': 'image/jpeg',
            'artwork_file': self._get_temporary_image(),
            'reveal_conditions': json.dumps([{
                'condition_type': 'view_count',
                'condition_value': {'count': 5}
            }])
        }
        
        response = self.client.post(self.artworks_url, artwork_data, format='multipart')
        
        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Check that no new artwork was created
        self.assertEqual(Artwork.objects.count(), 1)

    def test_artist_can_only_update_own_artwork(self):
        """Test that artists can only update their own artworks."""
        # Create another artist
        other_artist = User.objects.create_user(
            username='otherartist',
            email='other@example.com',
            password='password123',
            is_artist=True
        )
        
        # Create artwork for the other artist
        other_artwork = Artwork.objects.create(
            title='Other Artwork',
            description='This is another artist\'s artwork',
            artist=other_artist,
            content_type='image/jpeg',
        )
        
        other_detail_url = reverse('artwork-detail', args=[str(other_artwork.id)])
        
        # Try to update the other artist's artwork
        self.client.force_authenticate(user=self.artist)
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
        }
        
        response = self.client.patch(other_detail_url, update_data, format='json')
        
        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the artwork wasn't updated
        other_artwork.refresh_from_db()
        self.assertEqual(other_artwork.title, 'Other Artwork')

    def test_add_comment(self):
        """Test adding a comment to an artwork."""
        self.client.force_authenticate(user=self.user)
        
        comment_data = {
            'content': 'This is a test comment.'
        }
        
        response = self.client.post(self.comment_url, comment_data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the comment was created
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, comment_data['content'])
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.artwork, self.artwork)

    def test_view_count_condition(self):
        """Test that view count conditions trigger artwork revelation."""
        self.client.force_authenticate(user=self.user)
        
        # Initial view - count should be 1
        response = self.client.get(self.detail_url)
        self.artwork.refresh_from_db()
        self.assertEqual(self.artwork.view_count, 1)
        self.assertFalse(self.artwork.is_revealed)
        
        # Second view - count should be 2
        response = self.client.get(self.detail_url)
        self.artwork.refresh_from_db()
        self.assertEqual(self.artwork.view_count, 2)
        self.assertFalse(self.artwork.is_revealed)
        
        # Third view - count should be 3 and artwork should be revealed
        response = self.client.get(self.detail_url)
        self.artwork.refresh_from_db()
        self.assertEqual(self.artwork.view_count, 3)
        self.assertTrue(self.artwork.is_revealed)
        
        # Check that the condition is marked as met
        self.condition.refresh_from_db()
        self.assertTrue(self.condition.is_met)

    def test_my_artworks_endpoint(self):
        """Test that artists can view their own artworks."""
        self.client.force_authenticate(user=self.artist)
        
        response = self.client.get(self.my_artworks_url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.artwork.id)) 