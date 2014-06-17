"""Kaltura API wrapper"""

__author__ = 'henry'

import logging
import requests

from api_secrets import *
from KalturaClient import *
from KalturaClient.Plugins.Metadata import *

logger = logging.getLogger(__name__)

API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php'

def get_ks():
    """Start new Kaltura API session and return key"""
    config = KalturaConfiguration(PARTNER_ID)
    config.serviceUrl = SERVICE_URL
    #config.setLogger(logger)
    client = KalturaClient(config)
    ks = client.generateSession(ADMIN_SECRET, USER_NAME,
            KalturaSessionType.ADMIN, PARTNER_ID, 86400, "")
    return ks

def call_kaltura(params, post=False, **kwargs):
    _params = {
        'ks': get_ks(),
        'format': 1,  # ask for return in JSON format
    }
    params.update(_params)
    if not post:
        r = requests.get(API_BASE_URL, params=params, **kwargs)
    else:
        r = requests.post(API_BASE_URL, params=params, **kwargs)
    ret = r.json()
    return ret

def get_entry_metadata(entry_id):
    params = {
        'service': 'media',
        'action': 'get',
        'entryId': entry_id,
    }
    return call_kaltura(params)

def get_entry_download_url(entry_id):
    ret = get_entry_metadata(entry_id)
    try:
        url = ret['downloadUrl']
        return URL
    except:
        return None

def get_entry_asset_id(entry_id, flavor_id=786152):
    """Return asset id for the MP3 version of a Kaltura video

    Kaltura stores the same video in multiple "flavors". We ask Kaltura to make
    an MP3 audio file automatically for every video we upload. This function
    finds the asset id of the MP3 file.

    MP3 audio file has flavorParamsId = 786152.
    """
    params = {
        'service': 'flavorAsset',
        'action': 'getbyentryid',
    }
    data = {'entryId': entry_id}
    ret = call_kaltura(params, post=True, data=data)
    try:
        for row in ret:
            if row.get('flavorParamsId', '') == flavor_id:
                return row['id']
    except:
        return None

def get_entry_download_url_with_flavor(entry_id, flavor_id=786152):
    """Return download URL for the MP3 version of a Kaltura video"""
    asset_id = get_entry_asset_id(entry_id, flavor_id)
    if asset_id is None:
        logger.warn('Cannot find asset with flavor {} for entry {}.'.format(
                flavor_id, entry_id))
        return None
    logger.info('Found asset {} with flavor {} for entry {}.'.format(
            asset_id, flavor_id, entry_id))
    params = {
        'service': 'flavorAsset',
        'action': 'getdownloadurl',
        'id': asset_id,
    }
    ret = call_kaltura(params, post=False)
    if ret.startswith('http'):
        return ret
    else:
        logger.warn('Cannot find download URL for asset {}.'.format(asset_id))
        logger.warn(ret)
        return None

if __name__ == '__main__':
    print get_entry_download_url_with_flavor('1_423rtyb6')
    #print get_flavor_asset('1_kj9tltar')
    #print get_entry_download_url('1_ziiv6fa7')
