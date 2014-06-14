import glob
import os
import requests
from api_secrets import *
from KalturaUpload import update_tags

BASE_URL = 'http://rekognition.com/func/api/'

IMAGES_DIR = '../static/images/'
IMAGES_BASE_URL = 'http://104.130.3.99:8000/static/images/'

SCENE_THRESHOLD = 0.05
OBJECT_THRESHOLD = 0.05

def recon_scene(url):
    params = {'api_key':REK_KEY,
              'api_secret':REK_SECRET,
              'jobs':'scene_understanding_3',
              'urls':url}
    resp = requests.post(BASE_URL, data=params)
    response = resp.json()
    return response['scene_understanding']['matches']


def tag_tmages(entry_id):
    os.chdir(IMAGES_DIR)
    files_list = glob.glob(entry_id+'-*.jpg')

    tags = []

    for filename in files_list:
        url = IMAGES_BASE_URL+filename
        scene_tags = recon_scene(url)
        for tag in scene_tags:
            if tags['score']>OBJECT_THRESHOLD and not(tag['tag'] in tags):
                tags.append(tag['tag'])

    update_tags(entry_id,tags)

