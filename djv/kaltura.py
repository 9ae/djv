"""Kaltura API wrapper"""

import logging
import requests

from api_secrets import *
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *

logger = logging.getLogger(__name__)

API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php?'

def GetConfig():
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    config.setLogger(logger)
    return config

def get_entry_metadata(entry_id):
    client = KalturaClient(GetConfig())
    # start new session (client session is enough when we do operations in a users scope)
    ks = client.generateSession(ADMIN_SECRET, USER_NAME,
            KalturaSessionType.ADMIN, PARTNER_ID, 86400, "")
    r = requests.get(API_BASE_URL +
        'service=media&action=get&format=1&entryId=' + entry_id + '&ks=' + ks)
    return  r.json()

def get_entry_download_url(entry_id):
    data = get_entry_metadata(entry_id)
    url = data['downloadUrl']
    logger.info('Found Download URL for entry %s: %s' % (entry_id, url))
    return url

if __name__ == '__main__':
    pass
    #print get_entry_download_url('1_ziiv6fa7')
