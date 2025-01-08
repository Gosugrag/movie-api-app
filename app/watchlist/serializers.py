"""
Serializers for WatchList API
"""
from django.urls import reverse
from rest_framework import serializers
from core.models import WatchList, StreamingPlatform, Review
from profanity.extras import ProfanityFilter


pf = ProfanityFilter()


def check_string_len(value):
    if len(value) < 5:
        raise serializers.ValidationError('The Length for '
                                          'the field is to short')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review object"""
    class Meta:
        model = Review
        read_only_fields = ('id', 'user')
        exclude = ('watchlist',)


class WatchListSerializer(serializers.ModelSerializer):
    """Serializer for WatchList object"""
    len_title = serializers.SerializerMethodField()
    title = serializers.CharField(validators=[check_string_len],
                                  max_length=50)
    platform_name = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)


    class Meta:
        model = WatchList
        read_only_fields = ('id', 'total_reviews', 'average_rating',)
        exclude = ('user',)

    def get_platform_name(self, obj):
        return obj.platform.name

    # def create(self, validated_data):
    #     """Create a watchlist object and create a streaming platform as needed"""
    #     streaming_platforms = validated_data.pop('streaming_platforms', [])
    #     watchlist = WatchList.objects.create(**validated_data)
    #     auth_user = self.context['request'].user
    #     if streaming_platforms:
    #         for streaming_platform in streaming_platforms:
    #             sp_object, created = StreamingPlatform.objects.get_or_create(
    #                 user=auth_user,
    #                 **streaming_platform)
    #             watchlist.streaming_platforms.add(sp_object)
    #     return watchlist

    def get_len_title(self, obj):
        """"""
        return len(obj.title)

    def validate_title(self, value):
        if pf.is_profane(value):
            raise serializers.ValidationError("Title contains profanity!")
        return value

    def validate(self, data):
        if data['title'] == data['description']:
            raise serializers.ValidationError("Title and description "
                                              "cannot be the same!")
        return data


class StreamingPlatformSerializer(serializers.ModelSerializer):
    """Serializer for StreamingPlatform object"""
    watchlist = WatchListSerializer(many=True, read_only=True)
    watchlist_links = serializers.SerializerMethodField()

    class Meta:
        model = StreamingPlatform
        read_only_fields = ('id',)
        exclude = ('id', 'user')

    def get_watchlist_links(self, obj):
        request = self.context.get('request')
        url_scheme = request.scheme
        hostname = request.get_host()

        if obj.watchlist.exists():
            return [
                f'{url_scheme}://{hostname}{reverse("watch:watchlist-detail", kwargs={"pk": watch.pk})}'
                for watch in obj.watchlist.all()
            ]
        return []
