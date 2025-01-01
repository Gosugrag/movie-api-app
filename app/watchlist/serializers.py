"""
Serializers for WatchList API
"""
from rest_framework import serializers
from core.models import WatchList, StreamingPlatform
from profanity.extras import ProfanityFilter


pf = ProfanityFilter()


def check_string_len(value):
    if len(value) < 5:
        raise serializers.ValidationError('The Length for '
                                          'the field is to short')


class StreamingPlatformSerializer(serializers.ModelSerializer):
    """Serializer for StreamingPlatform object"""
    class Meta:
        model = StreamingPlatform
        read_only_fields = ('id',)
        exclude = ('id', 'user')



class WatchListSerializer(serializers.ModelSerializer):
    """Serializer for WatchList object"""
    len_title = serializers.SerializerMethodField()
    title = serializers.CharField(validators=[check_string_len],
                                  max_length=50)
    streaming_platforms = StreamingPlatformSerializer(many=True, required=False)

    class Meta:
        model = WatchList
        read_only_fields = ('id',)
        exclude = ('id', 'user')

    def create(self, validated_data):
        streaming_platforms = validated_data.pop('streaming_platforms', [])
        watchlist = WatchList.objects.create(**validated_data)
        auth_user = self.context['request'].user
        if streaming_platforms:
            for streaming_platform in streaming_platforms:
                sp_object, created = StreamingPlatform.objects.get_or_create(
                    user=auth_user,
                    **streaming_platform)
                watchlist.streaming_platforms.add(sp_object)
        return watchlist

    def get_len_title(self, obj):
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
