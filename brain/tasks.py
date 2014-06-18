from __future__ import absolute_import

import os
import urlparse

from celery.result import ResultSet
from django.db import transaction

from brain.kaltura import get_entry_metadata
from brain.kaltura import get_entry_thumbnail
from brain.KalturaUpload import update_tags
from brain.models import Media
from brain.models import Status
from brain.ReKImages import tag_objects
from brain.ReKImages import tag_people
from brain.recognition import get_fb_user
from brain.recognition import get_fb_photos
from brain.recognition import clean_training_state
from brain.recognition import filter_fb_photos_for_training
from brain.recognition import process_fb_photo as _process_fb_photo
from brain.recognition import recognise_unknown_photo
from brain.recognition import train_fb_photos
from brain.recognition import upload_fb_photos_for_training as _upload_fb_photos_for_training
from brain.voicebase import post_entry
from brain.voicebase import get_keywords
from djv import settings
from djv.celery import app


@app.task(name='brain.tasks.add')
def add(x, y):
    return x + y


@app.task(name='brain.tasks.initialise_fb_user')
def initialise_fb_user(domain_uri, access_token):
    fb_user = get_fb_user(access_token)
    group_name = fb_user.id

    photos = get_fb_photos(access_token)

    if settings.USE_ASYNC:
        results = ResultSet([process_fb_photo.delay(d, access_token) for d in photos['data']])
        processed_photos = [p for photos in results.join() for p in photos]
    else:
        processed_photos = [process_fb_photo(d, access_token) for d in photos['data']]
        processed_photos = [p for photos in processed_photos for p in photos]

    filtered_photos = filter_fb_photos_for_training(processed_photos)
    media_uri = urlparse.urljoin(domain_uri, settings.MEDIA_URL)

    if settings.USE_ASYNC:
        results = ResultSet([upload_fb_photos_for_training.delay([p], group_name, media_uri) for p in filtered_photos])
        results.join()
    else:
        upload_fb_photos_for_training(filtered_photos, group_name, media_uri)

    train_fb_photos(group_name)

#    clean_training_state(processed_photos)


@transaction.atomic
def save_service_status(entry_id, service, state, message=''):
    status, _ = Status.objects.get_or_create(media=Media.objects.get(id=entry_id),
                                             service=service)
    status.state = state
    status.message = message
    status.save()


@app.task(name='brain.tasks.think')
def think(entry_id, services, domain_uri):
    # get Face++ group name if service is turned on
    group_name = None
    if services.get('facepp'):
        group_name = get_fb_user(services['facepp']).id

    # async get keywords from VoiceBase
    # only do this for async mode
    if services.get('voicebase') and settings.USE_ASYNC:
        save_service_status(entry_id, 'VOICEBASE', 'PROGRESS')
        generate_voice_keyword_tags.delay(entry_id)

    # get image samplings from Kaltura video
    images = generate_image_samplings_from_kaltura(entry_id)

    # process object recognition
    # process facial recognition
    is_generate_object_tags = services.get('stockpodium', False)
    is_generate_friend_tags = services.get('facepp', False)

    if is_generate_object_tags:
        save_service_status(entry_id, 'STOCKPODIUM', 'PROGRESS')
    if is_generate_friend_tags:
        save_service_status(entry_id, 'FACEPP', 'PROGRESS')

    results = []
    for i in images:
        image_url = urlparse.urljoin(domain_uri, settings.MEDIA_URL + i)
        if is_generate_object_tags:
            if settings.USE_ASYNC:
                results.append(generate_object_tags.delay(entry_id, image_url))
            else:
                generate_object_tags(entry_id, image_url)
        if is_generate_friend_tags:
            if settings.USE_ASYNC:
                results.append(generate_friend_tags.delay(entry_id, image_url, group_name))
            else:
                generate_friend_tags(entry_id, image_url, group_name)

    # wait for tagging to be complete
    if results:
        ResultSet(results).join()

    save_service_status(entry_id, 'STOCKPODIUM', 'SUCCESS')
    save_service_status(entry_id, 'FACEPP', 'SUCCESS')

    # clean generate image samplings
    for i in images:
        f = os.path.join(settings.MEDIA_ROOT, i)
        if os.path.isfile(f):
            os.unlink(f)


@app.task(name='brain.tasks.generate_object_tags')
def generate_object_tags(entry_id, image_url):
    tags = tag_objects(entry_id, image_url)
    update_tags(entry_id, tags)


@app.task(name='brain.tasks.generate_friend_tags')
def generate_friend_tags(entry_id, image_url, group_name):
    candidate = recognise_unknown_photo(group_name, image_url)
    if candidate is not None:
        update_tags(entry_id, [candidate])

@app.task(name='brain.tasks.wait_for_voice_keywords',
          max_retries=5,
          default_retry_delay=30)
def wait_for_voice_keywords(entry_id):
    tags = get_keywords(entry_id)
    if tags is not None:
        return tags

    raise Exception('No keywords found from VoiceBase: "%s"' % entry_id)

@app.task(name='brain.tasks.generate_voice_keyword_tags',
          max_retries=5,
          default_retry_delay=30,
          ignore_result=True)
def generate_voice_keyword_tags(entry_id):
    if not post_entry(entry_id):
        raise Exception('Unable to post entry to VoiceBase: "%s"' % entry_id)

    tags = get_keywords.delay(entry_id).result
    if not isinstance(tags, Excpetion):
        update_tags(entry_id, tags)
        save_service_status(entry_id, 'VOICEBASE', 'SUCCESS')
    else:
        save_service_status(entry_id, 'VOICEBASE', 'FAIL', str(tags))


@app.task(name='brain.tasks.generate_thumbnail_at_time_from_kaltura')
def generate_thumbnail_at_time_from_kaltura(entry_id, seconds):
    image_file = os.path.join(settings.MEDIA_ROOT, 'kaltura', '%(entry_id)s.%(seconds)s.jpg' % locals())
    if not os.path.isdir(os.path.dirname(image_file)):
        os.makedirs(os.path.dirname(image_file))

    with open(image_file, 'wb') as f:
        f.write(get_entry_thumbnail(entry_id, seconds))

    return os.path.relpath(image_file, settings.MEDIA_ROOT)

@app.task(name='brain.tasks.generate_image_samplings_from_kaltura')
def generate_image_samplings_from_kaltura(entry_id):
    duration = None  # duration in seconds
    attempts = 5

    while attempts > 0:
        data = get_entry_metadata(entry_id)
        if 'duration' in data:
            duration = data['duration']
            break

        time.sleep(60.0 / attempts)
        attempts -= 1

    if duration is None:
        raise Exception('Cannot find video on Kaltura: "%s"' % entry_id)

    # number of samples should be proportion to the video duration
    step = min(1, max(5, int(duration / 5.0)))
    if settings.USE_ASYNC:
        results = ResultSet([generate_thumbnail_at_time_from_kaltura.delay(entry_id, i) for i in range(0, duration, step)])
        return results.join()
    else:
        return [generate_thumbnail_at_time_from_kaltura(entry_id, i) for i in range(0, duration, step)]

@app.task(name='brain.tasks.process_fb_photo')
def process_fb_photo(fb_photo_obj, access_token, user_id='me'):
    return _process_fb_photo(fb_photo_obj, access_token, user_id)


@app.task(name='brain.tasks.upload_fb_photos_for_training')
def upload_fb_photos_for_training(photos, group_name, media_uri):
    _upload_fb_photos_for_training(photos, group_name, media_uri)


