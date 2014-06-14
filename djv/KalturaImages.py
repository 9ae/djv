import requests
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *
from api_secrets import *

API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php?'

def GetConfig():
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    return config

def generateImages(entry_id):
    client = KalturaClient(GetConfig())

    # start new session (client session is enough when we do operations in a users scope)
    ks = client.generateSession(ADMIN_SECRET, USER_NAME, KalturaSessionType.ADMIN, api_secrets.PARTNER_ID, 86400, "")

    r = requests.get(+API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks)
    data = r.json()
    print data['msDuration']
