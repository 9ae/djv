"""Kaltura API wrapper"""

__author__ = 'henry'

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

def get_entry_download_url_with_flavor(entry_id, flavorParamsId=786152):
    """Return download URL for the MP3 version of a Kaltura video

    Kaltura stores the same video in multiple "flavors". We ask Kaltura to make
    an MP3 audio file automatically for every video we upload. This function
    finds the download URL of the MP3 file.

    MP3 audio file has flavorParamsId = 786152.
    """
    client = KalturaClient(GetConfig())
    # start new session (client session is enough when we do operations in a users scope)
    ks = client.generateSession(ADMIN_SECRET, USER_NAME,
            KalturaSessionType.ADMIN, PARTNER_ID, 86400, "")

    # First we need first the asset ID corresponding to the MP3 asset (786152)
    params = {'entryId': entry_id}
    r = requests.post('http://www.kaltura.com/api_v3/?service=flavorAsset' +
            '&action=getbyentryid&format=1&ks=' + ks, data=params)
    asset_id = None
    for row in r.json():
        if 'flavorParamsId' in row and row['flavorParamsId'] == flavorParamsId:
            asset_id = row['id']
            break
    if asset_id is None:
        logger.warning('Cannot find Asset ID for Entry ID (%s) with Flavor (%s)' % (
            entry_id, flavorParamsId))
        return
    logger.info('Found Asset ID (%s) for Entry ID (%s) with Flavor (%s).' % (
            asset_id, entry_id, flavorParamsId))

    # Next we find the URL for the MP3 asset
    params = {'id': asset_id}
    r = requests.post('http://www.kaltura.com/api_v3/?service=flavorAsset' +
            '&action=getdownloadurl&format=1', data = params)
    url = r.json()
    logger.info('Found URL (%s) for entry (%s).' % (url, entry_id))
    return url

if __name__ == '__main__':
    print get_entry_download_url_with_flavor('1_423rtyb6')
    #print get_flavor_asset('1_kj9tltar')
    #print get_entry_download_url('1_ziiv6fa7')
