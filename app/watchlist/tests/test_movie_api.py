"""
Tests for recipe endpoints
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import WatchList

from movie.serializers import WatchListSerializer


WATCHLIST_URL = reverse('watchlist:watchlist-list')


def detail_url(movie_id):
    return reverse('watchlist:watchlist-detail', args=[movie_id])


def create_watchlist(user, **params):
    """Create and return a new watchlist"""
    defaults = {
        'name': 'Django Unchained',
        'active': True,
        'description': 'Test desc',
    }
    defaults.update(params)

    recipe = WatchList.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated watchlist API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        payload = {
            'name': 'Django Unchained',
            'active': True,
            'description': 'Test desc',
        }
        res = self.client.post(MOVIE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='testuser123',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_movies(self):
        """Test retrieving a list of movies"""
        for i in range(9):
            create_movie(self.user)
        res = self.client.get(MOVIE_URL)

        movies = Movie.objects.all().order_by('name')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_movie_detail(self):
        movie = create_movie(self.user)
        res = self.client.get(detail_url(movie.id))
        serializer = MovieSerializer(movie)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
