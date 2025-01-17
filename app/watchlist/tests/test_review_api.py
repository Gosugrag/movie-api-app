"""
Tests for the streaming platform API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, RequestFactory

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Review, WatchList, StreamingPlatform
from watchlist.serializers import ReviewSerializer


def REVIEW_URL(pk):
    reverse('watch:reviews-list', kwargs={'pk': pk})


def create_user(**params):
    """Create a test user"""
    return get_user_model().objects.create_user(**params)


def create_review(user, **params):
    defaults = {
        'rating': '5',
        'description': 'Normis',
        'active': True,
        'watchlist': WatchList.objects.create(
            user=user,
            title='Normis',
            active=True,
            description='Normis',
            platform=StreamingPlatform.objects.create(
                user=user,
                name='Test SP',
                about='Test About SP',
                website='http://www.test.com'
            )
        )
    }
    defaults.update(params)

    review = Review.objects.create(user=user, **defaults)
    return review


def create_watchlist(user):
    watchlist = WatchList.objects.create(
        user=user,
        title='Normis',
        active=True,
        description='Normis',
        platform=StreamingPlatform.objects.create(
            user=user,
            name='Test SP',
            about='Test About SP',
            website='http://www.test.com',
        )
    )
    return watchlist


def detail_url(watch_pk, review_pk):
    return reverse('watch:reviews-detail',
                   kwargs={'watch_pk': watch_pk, 'review_pk': review_pk})


class ReviewPublicAPITests(TestCase):
    """Test the publicly available API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        self.user = create_user(
            email='testuser123@test.com',
            password='testpass123',
            is_staff=True,
        )
        watchlist = create_watchlist(self.user)
        payload = {
            'rating': 5,
            'description': 'Normis',
            'active': True,
            'watchlist': watchlist.id,
        }
        res = self.client.post(REVIEW_URL(watchlist.id), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewPrivateAPITests(TestCase):
    """Test the private API"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser123@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_list_reviews(self):
        """Test listing reviews"""
        watchlist = create_watchlist(self.user)
        for _ in range(5):
            create_review(user=self.user, watchlist=watchlist)

        res = self.client.get(REVIEW_URL(watchlist.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify pagination and data
        reviews = Review.objects.filter(watchlist=watchlist).order_by(
            '-created_at'
        )
        serializer = ReviewSerializer(reviews, many=True)

        self.assertEqual(res.data['results'], serializer.data)
        self.assertEqual(res.data['count'], reviews.count())

    def test_create_second_review_existing_user(self):
        """Test creating a second review with an existing user"""
        watchlist = create_watchlist(self.user)
        create_review(user=self.user, watchlist=watchlist)
        payload = {
            'watchlist': watchlist.id,
            'description': 'Normis',
            'active': True,
            'rating': 5,
        }
        res = self.client.post(REVIEW_URL(watchlist.id), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review(self):
        """Test creating a review"""
        watchlist = create_watchlist(self.user)
        user = create_user(
            email='testuser1123@test.com',
            password='testpass123',
        )
        payload = {
            'watchlist': watchlist.id,
            'description': 'Normis',
            'active': True,
            'rating': 5,
        }
        self.client.force_authenticate(user=user)
        res = self.client.post(REVIEW_URL(watchlist.id), payload)
        review = create_review(user=self.user, watchlist=watchlist)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        serializer = ReviewSerializer(review)
        reviews = Review.objects.filter(watchlist=watchlist)
        self.assertEqual(reviews.count(), 2)
        self.assertEqual(res.data['description'],
                         serializer.data['description'])

    def test_alter_review(self):
        """Test updating a review"""
        watchlist = create_watchlist(self.user)
        review = create_review(user=self.user, watchlist=watchlist)
        payload = {
            'watchlist': watchlist.id,
            'description': 'Normis2',
            'active': False,
            'rating': 5,
        }

        res = self.client.put(detail_url(watch_pk=watchlist.id,
                                         review_pk=review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        review.refresh_from_db()
        serializer = ReviewSerializer(review)

        self.assertEqual(res.data['description'],
                         serializer.data['description'])
        self.assertEqual(res.data['active'], serializer.data['active'])

    def test_retrieve_review(self):
        """Test retrieving a review"""
        watchlist = create_watchlist(self.user)
        review = create_review(user=self.user, watchlist=watchlist)
        res = self.client.get(detail_url(watchlist.id, review_pk=review.id))
        serializer = ReviewSerializer(review)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_delete_review(self):
        """Test deleting a review"""
        watchlist = create_watchlist(self.user)
        review = create_review(user=self.user, watchlist=watchlist)
        res = self.client.delete(detail_url(watchlist.id, review_pk=review.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())
