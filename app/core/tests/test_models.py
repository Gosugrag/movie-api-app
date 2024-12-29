from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Tests cases for models"""
    def test_create_movie(self):
        """Test creating a new Movie."""
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        movie = models.Movie.objects.create(
            user=user,
            name='Test Movie',
            description='Test Movie Description',
            active=True
        )

        self.assertEqual(movie.name, 'Test Movie')
        self.assertEqual(movie.description, 'Test Movie Description')
        self.assertEqual(movie.active, True)
        self.assertEqual(str(movie), movie.name)
