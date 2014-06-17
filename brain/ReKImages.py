import glob
import os
import requests
from KalturaUpload import update_tags
from recognition import recognise_unknown_photo, get_fb_user

from djv import settings
from djv.utils import get_api_secrets

BASE_URL = 'http://rekognition.com/func/api/'
STOCKPODIUM_URL = 'http://labs.stockpodium.com/adapi/tagging.php?'

IMAGES_DIR = os.path.join(settings.MEDIA_ROOT)
IMAGES_BASE_URL = 'http://104.130.3.99/media/'

SCENE_THRESHOLD = 0.05
OBJECT_THRESHOLD = 30.0

def recon_scene(url):
    params = {'api_key':REK_KEY,
              'api_secret':REK_SECRET,
              'jobs':'scene_understanding_3',
              'urls':url}
    resp = requests.post(BASE_URL, data=params)
    response = resp.json()
    return response['scene_understanding']['matches']

def tag_images(entry_id):
    os.chdir(IMAGES_DIR)
    files_list = glob.glob(entry_id+'-*.jpg')

    tags = []

    for filename in files_list:
        url = IMAGES_BASE_URL+filename
        scene_tags = recon_scene(url)
        for tag in scene_tags:
            if tag['score']>SCENE_THRESHOLD and not(tag['tag'] in tags):
                tags.append(tag['tag'])

    update_tags(entry_id,tags)

#use this instead
def tag_images_stock(entry_id):
    secrets = get_api_secrets()['stockpodium']
    os.chdir(IMAGES_DIR)
    files_list = glob.glob(entry_id+'-*.jpg')

    tags = []

    for filename in files_list:
        url = STOCKPODIUM_URL+'api_key='+secrets['key']+'&url='+IMAGES_BASE_URL+filename
        r = requests.get(url).json()
        scene_tags = r['tags']
        for tag in scene_tags:
            if tag['confidence']>OBJECT_THRESHOLD and not(tag['tag'] in tags):
                tags.append(tag['tag'])

    update_tags(entry_id,tags)

def tag_people(entry_id,access_token):
    os.chdir(IMAGES_DIR)
    files_list = glob.glob(entry_id+'-*.jpg')

    tags = []

    for filename in files_list:
        candidate = recognise_unknown_photo(get_fb_user(access_token).id, IMAGES_BASE_URL+filename)
        if candidate is not None and candidate not in tags:
            tags.append(candidate)

    update_tags(entry_id,tags)
