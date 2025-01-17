"""
Tests for the streaming platform API
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import StreamingPlatform
from watchlist.serializers import StreamingPlatformSerializer

from django.test import RequestFactory


SP_URL = reverse('watch:streaming-list')


def create_user(**params):
    """Create a test user"""
    return get_user_model().objects.create_user(**params)


def create_streaming_platform(user,**params):
    defaults = {
        'name': 'SP1',
        'about': 'About SP1',
        'website': 'www.sp1.com'
    }

    defaults.update(params)

    sp = StreamingPlatform.objects.create(user=user, **defaults)
    return sp


def detail_url(sp_id):
    return reverse('watch:streaming-detail', args=[sp_id])


class StreamingPlatformPublicAPITests(TestCase):
    """Test the publicly available API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        payload = {
            'name': 'SP1',
            'about': 'About SP1',
            'website': 'http://www.sp1.com',
        }
        res = self.client.post(SP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class StreamingPlatformPrivateAPITests(TestCase):
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

    def test_list_streaming_platform(self):
        """Test list SP"""
        for i in range(5):
            create_streaming_platform(self.user)
        res = self.client.get(SP_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sps = StreamingPlatform.objects.all()
        serializer = StreamingPlatformSerializer(sps, many=True, context={'request': self.request})
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_streaming_platform(self):
        """Test create SP"""
        payload = {
            'name': 'SP1',
            'about': 'About SP1',
            'website': 'http://www.sp1.com',
        }
        res = self.client.post(SP_URL, payload)
        sp = StreamingPlatform.objects.get(name=payload['name'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sp.name, payload['name'])

    def test_retrieve_streaming_platform(self):
        """Test retrieve SP"""
        sp = create_streaming_platform(self.user)
        res = self.client.get(detail_url(sp.pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = StreamingPlatformSerializer(sp, context={'request': self.request})
        self.assertEqual(res.data, serializer.data)

    def test_update_streaming_platform(self):
        """Test update SP"""
        sp = create_streaming_platform(self.user)
        payload = {
            'name': 'SP100',
            'about': 'About SP1',
            'website': 'http://www.sp1.com',
        }
        res = self.client.patch(detail_url(sp.pk), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sp = StreamingPlatform.objects.get(name=payload['name'])
        sp.refresh_from_db()
        serializer = StreamingPlatformSerializer(sp, context={'request': self.request})
        self.assertEqual(res.data, serializer.data)

    def test_delete_streaming_platform(self):
        """Test delete SP"""
        sp = create_streaming_platform(self.user)
        res = self.client.delete(detail_url(sp.pk))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StreamingPlatform.objects.filter(id=sp.id).exists())
