import requests
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *
import concurrent.futures
from api_secrets import *
import os
import os.path

from djv import settings

HERE = os.path.abspath(os.path.dirname(__file__))
API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php?'
PUBLIC_BASE_URL = 'http://www.kaltura.com/p/'+str(PARTNER_ID)

def GetClient():
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    return KalturaClient(config)

def GetKS():
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    client = KalturaClient(config)
    return client.generateSession(ADMIN_SECRET, USER_NAME, KalturaSessionType.ADMIN, PARTNER_ID, 86400, "")

def get_image(entry_id,i):
    req2_url = '{0}/thumbnail/entry_id/{1}/quality/100/vid_sec/{2}/width/800'.format(PUBLIC_BASE_URL,entry_id,i)
    print req2_url
    r2 = requests.get(req2_url)
    file_location = entry_id+'-'+str(i)+'.jpg'
    f = open(file_location,'w+')
    f.write(r2.content)
    f.close()

def generate_images(entry_id):
    import time
    ks = GetKS()
    os.chdir(os.path.join(settings.MEDIA_ROOT, 'static/images/'))

    entry_url = API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks
    r = requests.get(entry_url)
    data = r.json()

    retry = 5
    while 'duration' not in data:
        time.sleep(60)
        r = requests.get(entry_url)
        data = r.json()
        retry -= 1

        if retry < 0:
            raise Excpetion('Cannot find video on Kaltura')

    secs = data['duration']

    i = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        while i <= secs:
            executor.submit(get_image, entry_id, i)
            i+=3
    '''
    while i <= until:
        get_image(entry_id,i)
        i += 1
    '''
    os.chdir(HERE)
