from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

# from app.core.models import StreamingPlatform


class ModelTests(TestCase):
    """Tests cases for models"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@mail.com',
            password='testpassword123'
        )

    def test_create_watchlist(self):
        """Test creating a new Movie."""
        watchlist = models.WatchList.objects.create(
            user=self.user,
            title='Test Movie',
            description='Test Movie Description',
            active=True,
            platform=models.StreamingPlatform.objects.create(
                user=self.user,
                name='Test SP',
                about='Test About SP',
                website='http://www.test.com'
            )
        )

        self.assertEqual(watchlist.title, 'Test Movie')
        self.assertEqual(watchlist.description, 'Test Movie Description')
        self.assertEqual(watchlist.active, True)
        self.assertEqual(str(watchlist), watchlist.title)

    def test_create_streaming_platform(self):
        """Test creating a new Streaming Platform."""
        streaming_platform = models.StreamingPlatform.objects.create(
            user=self.user,
            name='Test Streaming Platform',
            about='Test About Streaming Platform',
            website='http://www.test.com'
        )

        self.assertEqual(streaming_platform.name, 'Test Streaming Platform')
        self.assertEqual(streaming_platform.about,
                         'Test About Streaming Platform')
        self.assertEqual(streaming_platform.website, 'http://www.test.com')
        self.assertEqual(str(streaming_platform), streaming_platform.name)

    def test_create_review(self):
        """Test creating a new Review."""
        review = models.Review.objects.create(
            user=self.user,
            rating=5,
            active=True,
            description='Test Review Description',
            watchlist=models.WatchList.objects.create(
                user=self.user,
                title='Test Movie',
                description='Test Movie Description',
                active=True,
                platform=models.StreamingPlatform.objects.create(
                    user=self.user,
                    name='Test SP',
                    about='Test About SP',
                    website='http://www.test.com'
                )
            )
        )

        self.assertEqual(review.rating, 5)
        self.assertEqual(review.active, True)
        self.assertEqual(str(review), str(review.rating) + ' | ' +
                         review.watchlist.title)
