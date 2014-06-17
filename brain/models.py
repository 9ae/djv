import os

from django.db import models

from djv import settings

class FbPhoto(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    url = models.URLField()


class FbUser(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    is_initialised = models.BooleanField(default=False)


class FbPhotoTag(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='facebook')
    requestor = models.ForeignKey(FbUser)


class Tag(models.Model):
    CATEGORYS = (
        ('HASHTAG', 'HashTag',),
        ('KEYWORD', 'Keyword',),
        ('COLOR', 'Color',),
        ('FRIEND', 'Friend',),
        ('GENDER', 'Gender',),
        ('RACE', 'Race',),
        ('LANDMARK', 'Landmark',),
        ('SONG', 'Song',),
        ('OBJECT', 'Object',),
    )

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORYS, default='HASHTAG')
    timestamp = models.DateTimeField(auto_now=False, null=True)

    class Meta:
        unique_together = ('name', 'category',)

class Media(models.Model):
    # this should be the same identifier as KalturaBaseEntry.id
    # see http://www.kaltura.com/api_v3/testmeDoc/index.php?object=KalturaBaseEntry
    id = models.CharField(max_length=100, primary_key=True)
    tags = models.ManyToManyField(Tag)

class Status(models.Model):
    SERVICES = (
        ('FACEPP', 'Face++',),
        ('STOCKPODIUM', 'Stockpodium',),
        ('VOICEBASE', 'VoiceBase',),
    )

    STATES = (
        ('NULL', 'Null',),
        ('PROGRESS', 'Progress',),
        ('SUCCESS', 'Success',),
        ('FAIL', 'Fail',),
    )

    media = models.ForeignKey(Media)
    service = models.CharField(max_length=12, choices=SERVICES)
    state = models.CharField(max_length=10, choices=STATES, default=STATES)

    class Meta:
        unique_together = ('media', 'service',)
