"""
Serializers for movie API
"""
from rest_framework import serializers
from core.models import Movie
from profanity.extras import ProfanityFilter


pf = ProfanityFilter()


def check_string_len(value):
    if len(value) < 5:
        raise serializers.ValidationError('The Length for the field is to short')


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie object"""
    name = serializers.CharField(validators=[check_string_len],
                                 max_length=50)
    description = serializers.CharField(validators=[check_string_len],
                                        max_length=200)


    class Meta:
        model = Movie
        fields = ('name', 'description', 'active',)
        read_only_fields = ('id',)

    def validate_name(self, value):
        if pf.is_profane(value):
            raise serializers.ValidationError("Title contains profanity!")
        return value

    def validate(self, data):
        if data['name'] == data['description']:
            raise serializers.ValidationError("Title and description "
                                              "cannot be the same!")
        return data
