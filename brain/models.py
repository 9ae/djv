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
    CATEGORY = (
        ('COLOR', 'Color',),
        ('FRIEND', 'Friend',),
        ('KEYWORD', 'Keyword',),
        ('LANDMARK', 'Landmark',),
        ('SONG', 'Song',),
        ('OBJECT', 'Object',),
        ('TRANSCRIPT', 'Transcript',),
    )

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY, default='KEYWORD')

    class Meta:
        unique_together = ('name', 'category',)

class Media(models.Model):
    # this should be the same identifier as KalturaBaseEntry.id
    # see http://www.kaltura.com/api_v3/testmeDoc/index.php?object=KalturaBaseEntry
    id = models.CharField(max_length=100, primary_key=True)

    # user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.id
