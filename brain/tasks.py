from __future__ import absolute_import

import urlparse
from celery.result import ResultSet

from djv.celery import app
from brain.recognition import get_fb_user
from brain.recognition import get_fb_photos
from brain.recognition import process_fb_photo as _process_fb_photo
from brain.recognition import filter_fb_photos_for_training
from brain.recognition import upload_fb_photos_for_training as _upload_fb_photos_for_training
from brain.recognition import train_fb_photos

@app.task(name='brain.tasks.add')
def add(x, y):
    return x + y


@app.task(name='brain.tasks.initialise_fb_user')
def initialise_fb_user(domain_uri, access_token):
    fb_user = get_fb_user(access_token)
    group_name = fb_user.id

    photos = get_fb_photos(access_token)
    processed_photos = [p for d in photos['data'] for p in process_fb_photo(d, access_token)]

    filtered_photos = filter_fb_photos_for_training(process_fb_photo)
    media_uri = urlparse.urljoin(domain_uri, 'media/')

    upload_fb_photos_to_api(filtered_photos, group_name, media_uri)
#    results = ResultSet([upload_fb_photos_to_api.delay([p], group_name, media_uri) for p in filtered_photos])
#    results.join()

    train_fb_photos(group_name)



@app.task(name='brain.tasks.process_fb_photo')
def process_fb_photo(fb_photo_obj, access_token, user_id='me'):
    _process_fb_photo(fb_photo_obj, access_token, user_id)


@app.task(name='brain.tasks.upload_fb_photos_for_training')
def upload_fb_photos_for_training(photos, group_name, media_uri):
    _upload_fb_photos_for_training(photos, group_name, media_uri)


