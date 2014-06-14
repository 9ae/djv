import cgi
import json
import urllib

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect

from djv import get_api_secrets
from djv import set_cookie


def facebook(request):
    if request.method == 'GET':
        secrets = get_api_secrets()['facebook']
        verification_code = request.GET.get('code')
        args = dict(client_id=secrets['app_id'],
                    scope='email,user_friends,user_photos',
                    redirect_uri=request.build_absolute_uri())

        if verification_code:
            args['client_secret'] = secrets['app_secret']
            args['code'] = verification_code
            response = cgi.parse_qs(urllib.urlopen('https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode(args)).read())
            access_token = response['access_token'][-1]

            # Download the user profile and cache a local instance of the
            # basic profile info

            profile = json.load(urllib.urlopen('https://graph.facebook.com/me?%s' % urllib.urlencode(dict(access_token=access_token))))
            data = dict(fb_user=profile['id'],
                        profile_url=profile['link'],
                        access_token=access_token)
            response = HttpResponse(json.dumps(data))
            set_cookie(response, 'fb_user', str(profile['id']))
            return response
        else:
            return redirect('https://graph.facebook.com/oauth/authorize?%s' % urllib.urlencode(args))

    return HttpResponseBadRequest()
