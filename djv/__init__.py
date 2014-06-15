import datetime
import logging
import os
import json

import kaltura
import voicebase

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)

def get_api_secrets():
    with open(os.path.join(os.path.dirname(__file__), 'secret.json')) as f:
        return json.load(f)


def set_cookie(response, key, value, days_expire=7):
    secrets = get_api_secrets()['djv']
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=secrets['cookie_domain'], secure=secrets.get('cookie_secure', None))


