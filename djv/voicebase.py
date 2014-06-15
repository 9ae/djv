"""Interface to the VoiceBase API"""

__author__ = 'henry'

import kaltura
import logging
import requests

from api_secrets import *

logger = logging.getLogger(__name__)

API_URL = 'https://www.VoiceBase.com/services?version=1.0'

def post_entry(entry_id):
    """Post a Kaltura entry to VoiceBase for transcription"""
    entry_url = kaltura.get_entry_download_url_with_flavor(entry_id)
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'uploadMediaGet',
        'mediaURL': entry_url,
        'transcriptType': 'machine',
        'title': entry_id,
        'externalid': entry_id,
    }
    r = requests.get(API_URL, params=params)
    logger.info('VoiceBase returned for posting entry %s: %s' % (
            entry_id, r.content))

def get_transcript(entry_id):
    """Return the transcript for a Kaltura entry

    Return None if transcript is not available.
    """
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'getTranscript',
        'externalID': entry_id,
        'confidence': 0.75,
    }
    r = requests.post(API_URL, data=params)
    logger.info('VoiceBase returned for getting entry %s: %s' % (
            entry_id, r.content))
    data = r.json()
    return data.get('transcript', None)

def get_keywords(entry_id):
    """Return a list of keywords of a Kaltura entry

    Note that we are using the GetFileAnalytics API, which gives the real
    keywords. The GetKeywords/GetSEOKeywords API simply returns the transcript.
    """
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'getFileAnalytics',
        'externalID': entry_id,
        'format': 'txt',
    }
    r = requests.post(API_URL, data=params)
    logger.info('VoiceBase returned for getting entry %s: %s' % (
            entry_id, r.content))
    data = r.json()
    return [kw['name'] for kw in data.get('keywords', [])]

if __name__ == '__main__':
    entry_ids = [
        '1_p5vwu17n',  # Birdman
        '1_84cxv1si',  # Evolution of Dad
        '1_8ycl7639',  # foodnsport
    ]
    for entry_id in entry_ids:
        post_entry(entry_id)
        print get_transcript(entry_id)
        print get_keywords(entry_id)

'''
# Upload stuff

#API_URL = 'http://httpbin.org/post'
#headers = {'content-type': 'application/json'}
filename = '/home/henry/I_Have_A_Dream_sample.ogg'
params = {
    'action': 'uploadMedia',
    'transcriptType': 'machine',
    'file': 'file',
    'externalid': '1',
}
r = requests.post(
        API_URL,
        data=params,
        files={
            'file': ('audio.ogg', open(filename, 'rb'), 'audio/ogg', {'Expires': '0'}),
        },
    )
print r, r.content

def get_SEO_keywords(entry_id):
    """Return the SEO keywords for a Kaltura entry

    Return None if transcript is not available.
    """
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'getSEOKeywords',
        'externalID': entry_id,
        'format': 'txt',
    }
    r = requests.post(API_URL, data=params)
    logger.info('VoiceBase returned for getting entry %s: %s' % (
            entry_id, r.content))
    data = r.json()
    return data.get('transcript', None)
'''
