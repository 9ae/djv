from django.contrib.auth.models import User
from django.db import models


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

    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)
