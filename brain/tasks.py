from __future__ import absolute_import

import urlparse
from celery.result import ResultSet

from djv import settings
from djv.celery import app
from brain.KalturaImages import generate_images
from brain.ReKImages import tag_images_stock
from brain.ReKImages import tag_people
from brain.recognition import get_fb_user
from brain.recognition import get_fb_photos
from brain.recognition import clean_training_state
from brain.recognition import process_fb_photo as _process_fb_photo
from brain.recognition import filter_fb_photos_for_training
from brain.recognition import upload_fb_photos_for_training as _upload_fb_photos_for_training
from brain.recognition import train_fb_photos

@app.task(name='brain.tasks.add')
def add(x, y):
    return x + y


#@app.task(name='brain.tasks.initialise_fb_user')
def initialise_fb_user(domain_uri, access_token):
    fb_user = get_fb_user(access_token)
    group_name = fb_user.id

    photos = get_fb_photos(access_token)
    results = ResultSet([process_fb_photo.delay(d, access_token) for d in photos['data']])
    processed_photos = [p for photos in results.join() for p in photos]

#    processed_photos = [process_fb_photo(d, access_token) for d in photos['data']]
#    processed_photos = [p for photos in processed_photos for p in photos]

    filtered_photos = filter_fb_photos_for_training(processed_photos)
    media_uri = urlparse.urljoin(domain_uri, settings.MEDIA_URL)

#    upload_fb_photos_for_training(filtered_photos, group_name, media_uri)
    results = ResultSet([upload_fb_photos_to_api.delay([p], group_name, media_uri) for p in filtered_photos])
    results.join()

    train_fb_photos(group_name)

#    clean_training_state(processed_photos)

@app.task(name='brain.tasks.think')
def think(entry_id, access_token):
    fb_user = get_fb_user(access_token)
    group_name = fb_user.id

    # async get keywords from VoiceBase

    # get image samplings from Kaltura video
    generate_images(entry_id)

    # async process facial recognition


    # async process object recognition


@app.task(name='brain.tasks.generate_image_samplings_from_kaltura')
def generate_image_samplings_from_kaltura(entry_id):
    generate_images(entry_id)


@app.task(name='brain.tasks.process_fb_photo')
def process_fb_photo(fb_photo_obj, access_token, user_id='me'):
    return _process_fb_photo(fb_photo_obj, access_token, user_id)


@app.task(name='brain.tasks.upload_fb_photos_for_training')
def upload_fb_photos_for_training(photos, group_name, media_uri):
    _upload_fb_photos_for_training(photos, group_name, media_uri)


