import requests
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *
from api_secrets import *

API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php?'
PUBLIC_BASE_URL = 'http://www.kaltura.com/p/'+str(PARTNER_ID)

def GetConfig():
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    return config

def generateImages(entry_id):
    client = KalturaClient(GetConfig())

    # start new session (client session is enough when we do operations in a users scope)
    ks = client.generateSession(ADMIN_SECRET, USER_NAME, KalturaSessionType.ADMIN, PARTNER_ID, 86400, "")

    r = requests.get(API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks)
    data = r.json()
    secs = data['duration']

    i = 0
    until = secs/3
    while i <= until:
        imageAtSecond(entry_id, i)
        i+=1


def imageAtSecond(entry_id, s):
    r = requests.get(PUBLIC_BASE_URL+'/thumbnail/entry_id/'+entry_id+'/quality/100/vid_sec/'+str(s))
    print r.headers
    f = open('../static/images/'+entry_id+'-'+str(s)+'.jpg','wb')
    f.write(r.content)
    f.close()

generateImages('1_423rtyb6')