"""
Tests for watchlist endpoints
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import WatchList, StreamingPlatform

from watchlist.serializers import WatchListSerializer, StreamingPlatformSerializer

from unittest.mock import Mock


WATCHLIST_URL = reverse('watch:watchlist-list')


def detail_url(watch_id, **kwargs):
    return reverse('watch:watchlist-detail', args=[watch_id], **kwargs)


def create_watchlist(user, **params):
    """Create and return a new watchlist"""
    defaults = {
        'title': 'Django Unchained',
        'active': True,
        'description': 'Test desc',
        'platform': StreamingPlatform.objects.create(
                user=user,
                name='Test SP',
                about='Test About SP',
                website='http://www.test.com'
            )
    }
    defaults.update(params)

    watch = WatchList.objects.create(user=user, **defaults)
    return watch


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicWatchlistApiTests(TestCase):
    """Test unauthenticated watchlist API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        payload = {
            'title': 'Django Unchained',
            'active': True,
            'description': 'Test desc',
            'platform': Mock()
        }
        res = self.client.post(WATCHLIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWatchlistApiTests(TestCase):
    """Test authenticated recipe API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='testuser123@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_list_wathlist(self):
        """Test retrieving a wathlist"""
        for i in range(5):
            create_watchlist(self.user)
        res = self.client.get(WATCHLIST_URL)

        watchlist = WatchList.objects.all()
        serializer = WatchListSerializer(watchlist, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('results'), serializer.data)

    def test_view_movie_detail(self):
        """Test viewing a wathlist detail"""
        watchlist = create_watchlist(self.user)
        res = self.client.get(detail_url(watchlist.id))
        serializer = WatchListSerializer(watchlist)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_watchlist(self):
        """Test creating a new watchlist"""
        sp_object = StreamingPlatform.objects.create(
            user=self.user,
            name='Test SP',
            about='Test About SP',
            website='http://www.test.com',
        )

        payload = {
            'title': 'Django Unchained',
            'active': True,
            'description': 'Test desc',
            'platform_name': 'Test SP',
            'platform': sp_object.id,
        }

        res = self.client.post(WATCHLIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        watchlist = WatchList.objects.get(title=payload['title'])
        self.assertEqual(watchlist.title, payload['title'])
        self.assertEqual(watchlist.description, payload['description'])
        self.assertEqual(watchlist.platform.id, payload['platform'])

    def test_retrieve_watchlist(self):
        """Test retrieving a watchlist"""
        watchlist = create_watchlist(self.user)
        serializer = WatchListSerializer(watchlist)
        res = self.client.get(detail_url(watchlist.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_alter_watchlist(self):
        """Test updating a watchlist"""
        watchlist = create_watchlist(self.user)
        sp_object = StreamingPlatform.objects.create(
            user=self.user,
            name='Test SP 2',
            about='Test About SP',
            website='http://www.test.com',
        )

        payload = {
            'title': 'Django Unchained',
            'active': True,
            'description': 'Test desc',
            'platform_name': 'Test SP',
            'platform': sp_object.id,
        }
        res = self.client.patch(detail_url(watchlist.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_watchlist = WatchList.objects.get(title=payload['title'])
        new_watchlist.refresh_from_db()
        serializer = WatchListSerializer(new_watchlist)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_title(self):
        """Test filtering by title"""
        create_watchlist(self.user)
        res = self.client.get(WATCHLIST_URL, {'title': 'Django Unchained'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results')), 1)

    def test_delete_watchlist(self):
        """Test deleting a watchlist"""
        watchlist = create_watchlist(self.user)
        res = self.client.delete(detail_url(watchlist.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(WatchList.objects.all()), 0)
