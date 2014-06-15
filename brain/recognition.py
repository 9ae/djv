from collections import Counter
import logging
import json
import os
from pprint import pformat
import tempfile
import urllib
import sys
import time
import urlparse

from PIL import Image


def log_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')])

def get_fb_user(access_token):
    from brain.models import FbUser

    args = urllib.urlencode(dict(access_token=access_token))
    profile = json.load(urllib.urlopen('https://graph.facebook.com/me?%(args)s' % locals()))

    fb_user, created = FbUser.objects.get_or_create(id=profile['id'])
    if created:
        fb_user.name = profile['name']

    return fb_user

def get_facepp_api():
    from facepp import API
    from djv.utils import get_api_secrets

    return API(get_api_secrets()['facepp']['key'],
               get_api_secrets()['facepp']['secret'])


def get_fb_photos(access_token, user_id='me', limit=200):
    args = urllib.urlencode(dict(access_token=access_token,
                                 limit=limit))
    return json.load(urllib.urlopen('https://graph.facebook.com/%(user_id)s/photos?%(args)s' % locals()))


def process_fb_photo(fb_photo_obj, access_token, user_id='me'):
    from djv import settings

    fb_photo_tags = []

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
            cropped_filename = os.path.join(settings.MEDIA_ROOT, '%(tag_id)s.jpg' % locals())

            # save cropped image to media location
            cropped_image.save(cropped_filename)

            # save cropped image to database
            fb_photo_tags.append(dict(id=tag_id,
                                      name=t['name'],
                                      image=os.path.basename(cropped_filename)))
    except Exception, e:
        logging.error(str(e))
    finally:
        os.close(source_fd)
        os.unlink(source_filename)

    return fb_photo_tags

def filter_fb_photos_for_training(fb_photo_tags, min_sample_size=20):
    name_counts = Counter([t['name'] for t in fb_photo_tags])
    name_counts = sorted(name_counts.items(), cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
    names = map(lambda x: x[0], filter(lambda x: x[1] >= min_sample_size, name_counts))

    return filter(lambda x: x['name'] in names, fb_photo_tags)


#    fb_user = FbUser.objects.get(id=user_id)
#
#    tags = FbPhotoTag.objects.values('name').annotate(count=Count('name')).\
#        filter(count__gte=sample_size, requestor=fb_user).order_by('-count')
#    return [pt for t in tags[:limit] for pt in FbPhotoTag.objects.filter(requestor=fb_user, name=t['name'])] \
#        if tags.count() != 0 else []


def upload_fb_photos_for_training(photos, group_name, media_uri):
    from facepp import APIError

    api = get_facepp_api()

    # create group for training
    try:
        api.group.create(group_name=group_name)
    except APIError, e:
        if e.code not in (453,):
            raise

    for p in photos:
        logging.info('Uploading file for training: "%s"' % os.path.basename(p['image']))

        # upload images for associated names to recognise face
        url = urlparse.urljoin(media_uri, p['image'])
        result = api.detection.detect(url=url, mode='oneface')
        log_result('Detection result for {}:'.format(p['name']), result)

        # create person with associated face
        if len(result['face']) > 0:
            face_id = result['face'][0]['face_id']
            try:
                api.person.create(person_name=p['name'], group_name=group_name, face_id=face_id)
            except APIError, e:
                if e.code not in (453,):
                    raise
                else:
                    api.person.add_face(person_name=p['name'], face_id=face_id)


def train_fb_photos(group_name):
    api = get_facepp_api()

    # train the group with faces
    result = api.recognition.train(group_name=group_name, type='all')
    log_result('Train result:', result)

    session_id = result['session_id']
    sleep_duration = 1
    while True:
        result = api.info.get_session(session_id=session_id)
        if result['status'] == u'SUCC':
            log_result('Async train result:', result)
            break
        time.sleep(sleep_duration)
        sleep_duration = min(sleep_duration * 2, 60)

def recognise_unknown_photo(group_name, url):
    api = get_facepp_api()
    result = api.recognition.recognize(url=url, group_name=group_name)
    log_result('Recognize Result:', result)
    print '=' * 60
    print 'The person with highest confidence:', result['face'][0]['candidate'][0]['person_name']
    return result['face'][0]['candidate'][0]['person_name']


def clean_training_state(fb_photo_tags=[], group_name=None):
    from djv import settings
    api = get_facepp_api()

    if group_name is not None:
        try:
            api.group.delete(group_name=group_name)
        except APIError, e:
            logging.error(str(e))

    for p in fb_photo_tags:
        f = os.path.join(settings.MEDIA_ROOT, p['image'])
        os.unlink(f)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'djv.settings'
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    access_token = ''
#    for d in get_fb_photos(access_token)['data']:
#        fb_photo, fb_photo_tags = process_fb_photo(d, access_token)

#    train_fb_photos(get_fb_user(access_token).id, 'http://104.130.3.99/media/')
#    recognise_unknown_photo(get_fb_user(access_token).id, 'https://scontent-a.xx.fbcdn.net/hphotos-frc3/t1.0-9/581275_10152858785155611_74591350_n.jpg')
