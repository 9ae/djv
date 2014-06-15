import logging
import json
import os
import tempfile
import urllib
import sys

from django.core.files import File
from PIL import Image
import unirest


def get_fb_user(access_token):
    from brain.models import FbUser

    args = urllib.urlencode(dict(access_token=access_token))
    profile = json.load(urllib.urlopen('https://graph.facebook.com/me?%(args)s' % locals()))

    fb_user, created = FbUser.objects.get_or_create(id=profile['id'])
    if created:
        fb_user.name = profile['name']

    return fb_user


def get_fb_photos(access_token, user_id='me', limit=200):
    args = urllib.urlencode(dict(access_token=access_token,
                                 limit=limit))
    return json.load(urllib.urlopen('https://graph.facebook.com/%(user_id)s/photos?%(args)s' % locals()))

def process_fb_photo(fb_photo_obj, access_token, user_id='me'):
    from brain.models import FbPhoto
    from brain.models import FbPhotoTag

    fb_user = get_fb_user(access_token)
    if user_id == 'me':
        user_id = fb_user.id

    source_fd, source_filename = tempfile.mkstemp()
    try:
        with open(source_filename, 'wb') as f:
            f.write(urllib.urlopen(fb_photo_obj['source']).read())

        photo_id = fb_photo_obj['id']
        photo_name = fb_photo_obj.get('name', '')
        logging.debug('Processing FB photo: [%(photo_id)s] %(photo_name)s' % locals())

        height = fb_photo_obj['height']
        width = fb_photo_obj['width']

        # save main photo
        fb_photo, _ = FbPhoto.objects.get_or_create(id=photo_id)
        fb_photo.name = photo_name
        fb_photo.url = fb_photo_obj['source']
        fb_photo.save()

        tags = filter(lambda x: 'id' in x, fb_photo_obj['tags']['data'])
        height = fb_photo_obj['height']
        width = fb_photo_obj['width']

        x_tolerance = max(25.0 * 1.0 / len(tags), 5.0)
        y_tolerance = x_tolerance
        if len(tags) < 4:
            # use portait aspect for less than 4 tags
            if height < width:
                x_tolerance *= (float(height) / float(width))
                y_tolerance *= (float(width) / float(height))
        else:
            # use a square crop region for 4 or more tags
            if height < width:
                x_tolerance *= (float(height) / float(width))
            else:
                y_tolerance *= (float(width) / float(height))

        fb_photo_tags = []
        for t in tags:
            source_image = Image.open(source_filename)
            tag_id = t['id']
            tag_id = '%(photo_id)s.%(tag_id)s' % locals()
            x = t['x']
            y = t['y']

            # create crop region the tag point with tolerance
            box = (
                (x - x_tolerance) * width,
                (y - y_tolerance) * height,
                (x + x_tolerance) * width,
                (y + y_tolerance) * height,
            )
            box = map(lambda x: int(round(x / 100.0)), box)
            logging.info('[%(tag_id)s] Crop Box: %(box)s, Image Dimension: %(height)s x %(width)s' % locals())

            # crop image
            cropped_image = source_image.crop(box)
            cropped_filename = os.path.join(tempfile.tempdir, '%(tag_id)s.jpg' % locals())
            try:
                # save cropped image to temporary file
                cropped_image.save(cropped_filename)

                # save cropped image to database
                with open(cropped_filename) as f:
                    fb_photo_tag, _ = FbPhotoTag.objects.get_or_create(id=tag_id, requestor=fb_user)
                    fb_photo_tag.name = t['name']
                    fb_photo_tag.image = File(f)
                    fb_photo_tag.save()
                    fb_photo_tags.append(fb_photo_tag)
            finally:
                os.unlink(cropped_filename)

        return fb_photo, fb_photo_tags

    finally:
        os.close(source_fd)
        os.unlink(source_filename)

def train_fb_photos(user_id, sample_size=20, limit=5):
    from django.db.models import Count
    from brain.models import FbPhotoTag
    from brain.models import FbUser
    from djv import get_api_secrets
    from djv import settings

    from facepp import API

    fb_user = FbUser.objects.get(id=user_id)
    api = API(get_api_secrets()['facepp']['key'],
              get_api_secrets()['facepp']['secret'])

    tags = FbPhotoTag.objects.values('name').annotate(count=Count('name')).\
        filter(count__gte=sample_size, requestor=fb_user).order_by('-count')
    if tags.count() != 0:
        # adding tagged photo to album for training
        for t in tags[:5]:
            logging.info('Processing photos for Facebook user: "%(name)s"' % t)
            for t in FbPhotoTag.objects.filter(requestor=fb_user, name=t['name']):
                logging.info('Uploading file for training: "%s"' % os.path.basename(t.image.url))
                with open(os.path.join(settings.MEDIA_ROOT, t.image.url)) as f:
                    response = unirest.post('https://lambda-face-recognition.p.mashape.com/album_train',
                                            headers={'X-Mashape-Authorization': key},
                                            params={
                                                'album': album_name,
                                                'albumkey': album_key,
                                                'entryid': t.name,
                                                'files': f,
                                            })
                    logging.info('Lambda response: "%s"' % response.body)






if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'djv.settings'
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    access_token = 'CAAUY1wWJW5wBAFlpcOkXeVYDF3CZCrDGYl0lkKJVDyVzLf9dOkxVeBUqTQZBgGIEXErOD53kYzEZA3DkYRm7ygp5GzI8xueBdb5wvtPGbZBZCfMZARIMqKZCKQzohGfuJhSY0VW7ZByhqh0OLvlMGLjcQ0BQrlLnjnpMyseFgnWwIZAdNdMo0fZAxI'
#    for d in get_fb_photos(access_token)['data']:
#        fb_photo, fb_photo_tags = process_fb_photo(d, access_token)

    train_lambda_album(get_fb_user(access_token).id)
