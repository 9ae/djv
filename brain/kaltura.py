"""Kaltura API wrapper"""

__author__ = 'henry'

import logging
import requests

from KalturaClient import *
from KalturaClient.Plugins.Metadata import *

from djv.utils import get_api_secrets

logger = logging.getLogger(__name__)

API_BASE_URL = 'http://www.kaltura.com/api_v3/index.php'
SERVICE_URL = "http://www.kaltura.com"
MP3_FLAVOR_ID = 786871  # FlavorParamsID for MP3 file to be send to VoiceBase

def get_ks():
    """Start new Kaltura API session and return key"""
    secrets = get_api_secrets()['kaltura']
    config = KalturaConfiguration(secrets['partner_id'])
    config.serviceUrl = SERVICE_URL
    #config.setLogger(logger)
    client = KalturaClient(config)
    return client.generateSession(secrets['admin_secret'],
                                  secrets['username'],
                                  KalturaSessionType.ADMIN,
                                  secrets['partner_id'],
                                  86400,
                                  '')

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
        return url
    except:
        return None

def get_entry_duration(entry_id):
    ret = get_entry_metadata(entry_id)
    try:
        duration = ret['msDuration']
        return duration
    except:
        return None

def get_entry_tags(entry_id):
    ret = get_entry_metadata(entry_id)
    try:
        tags = ret['tags']
        return tags
    except:
        return None

def get_entry_asset_id(entry_id, flavor_id=MP3_FLAVOR_ID):
    """Return asset id for the MP3 version of a Kaltura video

    Kaltura stores the same video in multiple "flavors". We ask Kaltura to make
    an MP3 audio file automatically for every video we upload. This function
    finds the asset id of the MP3 file.
    """
    # Send Kaltura a command to convert the given entry. This will take some
    # time, and won't be helpful for this call, but may be useful later.
    #convert_flavor_asset(entry_id, flavor_id)
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

def convert_flavor_asset(entry_id, flavor_id=MP3_FLAVOR_ID):
    """Ask Kaltura to convert a video entry to specified flavor"""
    params = {
        'service': 'flavorAsset',
        'action': 'convert',
    }
    data = {
        'entryId': entry_id,
        'flavorParamsId': flavor_id,
        'priority': 10,
    }
    ret = call_kaltura(params, post=True, data=data)
    if isinstance(ret, dict) and ret.get(
            'objectType', '') == 'KalturaAPIException':
        logger.warning('Cannot convert entry {} to flavor {}'.format(
                entry_id, flavor_id))
        logger.warning(ret)

def get_entry_download_url_with_flavor(entry_id, flavor_id=MP3_FLAVOR_ID):
    """Return download URL for the MP3 version of a Kaltura video"""
    asset_id = get_entry_asset_id(entry_id, flavor_id)
    if asset_id is None:
        logger.warn('Cannot find asset with flavor {} for entry {}.'.format(
                flavor_id, entry_id))
        return None
    logger.debug('Found asset {} with flavor {} for entry {}.'.format(
            asset_id, flavor_id, entry_id))
    params = {
        'service': 'flavorAsset',
        'action': 'getdownloadurl',
        'id': asset_id,
    }
    ret = call_kaltura(params, post=False)
    if isinstance(ret, basestring) and ret.startswith('http'):
        url = ret
        logger.debug('Found download URL for asset {}: {}'.format(asset_id, url))
        return url
    else:
        logger.warn('Cannot find download URL for asset {}.'.format(asset_id))
        logger.warn(ret)
        return None

if __name__ == '__main__':
    print get_entry_download_url_with_flavor('1_423rtyb6')
    #print get_flavor_asset('1_kj9tltar')
    #print get_entry_download_url('1_ziiv6fa7')
