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
    entry_url = kaltura.get_entry_download_url('1_ziiv6fa7')
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'uploadMediaGet',
        'mediaURL': entry_url,
        'transcriptType': 'machine',
        'externalid': entry_id,
    }
    r = requests.get(API_URL, params=params)
    logger.info('VoiceBase returned for posting entry %s: %s' % (
            entry_id, r.content))

def get_script(entry_id):
    """Return the transcript for a Kaltura entry

    Return None if transcript is not available.
    """
    params = {
        'apikey': VOICEBASE_APIKEY,
        'password': VOICEBASE_PASSWD,
        'action': 'getTranscript',
        'externalID': entry_id,
        'format': 'txt',
    }
    r = requests.post(API_URL, data=params)
    logger.info('VoiceBase returned for getting entry %s: %s' % (
            entry_id, r.content))
    data = r.json()
    return data.get('transcript', None)

if __name__ == '__main__':
    post_entry('1_qq6kbapa')
    print get_script('1_qq6kbapa')

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
'''
