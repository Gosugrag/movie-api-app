"""
Serializers for movie API
"""
from rest_framework import serializers

from core.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie object"""
    class Meta:
        model = Movie
        fields = ('name', 'description', 'active',)
        read_only_fields = ('id',)
