import glob
import os
import requests
from api_secrets import *
from KalturaImages import GetKS

BASE_URL = 'http://rekognition.com/func/api/'

IMAGES_DIR = '../static/images/'
IMAGES_BASE_URL = 'http://104.130.3.99:8000/static/images/'


def findImages(entry_id):
    os.chdir(IMAGES_DIR)
    files_list = glob.glob(entry_id+'-*.jpg')

    threshold = 0.05
    tags = []

    for filename in files_list:
        url = IMAGES_BASE_URL+filename
        params = {'api_key':REK_KEY,
                  'api_secret':REK_SECRET,
                  'jobs':'scene_understanding_3',
                  'urls':url}
        resp = requests.post(BASE_URL, data=params)
        response = resp.json()
        result_tags = response['scene_understanding']['matches']
        for tag in result_tags:
            if tag['score']>threshold:
                tags.append(tag['tag'])

    ks = GetKS()



findImages('1_423rtyb6')
