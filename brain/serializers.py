from rest_framework import serializers

from models import FbUser
from models import Media
from models import Status
from models import Tag


class FbUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FbUser
        fields = ('id', 'name', 'is_initialised',)

class MediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Media
        fields = ('id',)

class StatusSerializer(serializers.HyperlinkedModelSerializer):
    media_id = serializers.SerializerMethodField('get_media_id')

    class Meta:
        model = Status
        fields = ('media_id', 'service', 'state', 'message',)

    def get_media_id(self, obj):
        return obj.media.id


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'category',)


