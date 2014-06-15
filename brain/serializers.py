from rest_framework import serializers

from models import FbPhoto
from models import FbUser
from models import Media
from models import Tag


class FbPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FbPhoto
        fields = ('id', 'url',)

class FbUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FbUser
        fields = ('id', 'name', 'is_initialised',)

class MediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Media
        fields = ('id',)

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'category',)


