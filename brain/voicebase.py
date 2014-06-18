"""Interface to the VoiceBase API"""

__author__ = 'henry'

import datetime
import logging
import requests
import kaltura

from djv.utils import get_api_secrets
from models import Media
from KalturaUpload import update_tags
from time import sleep

logger = logging.getLogger(__name__)

API_URL = 'https://www.VoiceBase.com/services?version=1.0'

class VoiceBasePostGiveUp(Exception): pass

def post_entry(entry_id, transcription_type='human'):
    """Post a Kaltura entry to VoiceBase for transcription

    Transcription type can be either human or machine.

    Return True of video is posted, False if not (meaning that we should retry
    a little later). Raises an exception to signal that task is not doable.
    """
    duration = kaltura.get_entry_duration(entry_id)
    if duration is None:
        raise VoiceBasePostGiveUp('Cannot find entry {}'.format(entry_id))
    if duration <= 4000:
        raise VoiceBasePostGiveUp(
                'Entry {} is too short for voice tagging'.format(entry_id))
    entry_url = kaltura.get_entry_download_url_with_flavor(entry_id)
    if entry_url is None: return False

    secrets = get_api_secrets()['voicebase']
    params = {
        'apikey': secrets['key'],
        'password': secrets['password'],
        'action': 'uploadMediaGet',
        'mediaURL': entry_url,
        'transcriptType': transcription_type,
        'title': entry_id,
        'externalid': entry_id,
    }
    ret = requests.get(API_URL, params=params).json()
    if ret.get('requestStatus', '') == 'SUCCESS':
        logger.debug('Successfully post entry {}'.format(entry_id))
        return True
    elif ret.get('statusMessage', '') == 'External ID is not unique':
        logger.debug('Entry {} already exists.'.format(entry_id))
        return True
    else:
        logger.warn('Failed to post entry {}'.format(entry_id))
        logger.warn(ret)
        return False

def get_transcript(entry_id):
    """Return the transcript for a Kaltura entry

    Return None if transcript is not available.
    """
    secrets = get_api_secrets()['voicebase']
    params = {
        'apikey': secrets['key'],
        'password': secrets['password'],
        'action': 'getTranscript',
        'externalID': entry_id,
        'confidence': 0.75,
    }
    ret = requests.post(API_URL, data=params).json()
    try:
        return ret['transcript']
    except:
        logger.warn('Cannot find transcript for entry {}.'.format(entry_id))
        logger.warn(ret)
        return None

def get_keywords(entry_id):
    """Return a list of keywords of a Kaltura entry

    Note that we are using the GetFileAnalytics API, which gives the real
    keywords. The GetKeywords/GetSEOKeywords API simply returns the transcript.
    """
    secrets = get_api_secrets()['voicebase']
    params = {
        'apikey': secrets['key'],
        'password': secrets['password'],
        'action': 'getFileAnalytics',
        'externalID': entry_id,
        'format': 'txt',
    }
    ret = requests.post(API_URL, data=params).json()
    try:
        keywords = [kw['name'] for kw in ret['keywords']]
        logging.debug(keywords)
        return keywords
    except:
        logger.warn('Cannot find keywords for entry {}.'.format(entry_id))
        logger.warn(ret)
        return None

def tag_voice(entry_id, timeout=3600):
    """Interface with ThinkThread"""
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    try:
        while datetime.datetime.now() < end_time:
            if post_entry(entry_id): break
            sleep(10)

        while datetime.datetime.now() < end_time:
            tags = get_keywords(entry_id)
            if tags is not None: break
            sleep(10)

        if tags is not None and len(tags) > 0:
            update_tags(entry_id, tags)
    except VoiceBasePostGiveUp as e:
        print e

def main():
    for media in Media.objects.all():
        entry_id = media.id
        logging.debug('Processing entry: {}'.format(entry_id))
        if post_entry(entry_id):
            tags = get_keywords(entry_id)
            transcript = get_transcript(entry_id)
            print 'Transcript:'
            print transcript
            if transcript is not None:
                tags += transcript.split(' ')
            if tags is not None and len(tags) > 0:
                update_tags(entry_id, tags)

if __name__ == '__main__':
    main()

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
    secrets = get_api_secrets()['voicebase']
    params = {
        'apikey': secrets['key'],
        'password': secrets['password'],
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
