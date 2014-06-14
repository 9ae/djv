import requests
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *

from api_secrets import *


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

def generateImages(entry_id):
    ks = GetKS()

    r = requests.get(API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks)
    data = r.json()
    secs = data['duration']
    w = data['width']
    h = data['height']
    i = 0
    until = secs/3
    while i <= until:
        req2_url = '{0}/thumbnail/entry_id/{1}/quality/100/vid_sec/{2}/width/{3}/height/{4}'.format(PUBLIC_BASE_URL,entry_id,i,w,h)
        print req2_url
        r2 = requests.get(req2_url)
        f = open('../static/images/'+entry_id+'-'+str(i)+'.jpg','wb')
        f.write(r2.content)
        f.close()
        i+=1