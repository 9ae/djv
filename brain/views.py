import atexit
import concurrent
import json
import urllib

from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from models import FbUser, Media
from serializers import FbUserSerializer
from serializers import MediaSerializer
from tasks import initialise_fb_user

from djv.utils import get_api_secrets

from KalturaImages import GetKS
from ThinkThread import ThinkThread
from ThinkThread import think


#EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)
#def shutdown():
#    EXECUTOR.shutdown(wait=True)
#atexit.register(shutdown)


class MediaList(APIView):
    """
    List all media, or upload a new media.
    """

    def get(self, request, format=None):
        medias = Media.objects.all()
        serializer = MediaSerializer(medias, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # TODO: begin process of accessing external APIs and tagging
        # currently only creates a dummy media object

        import pdb; pdb.set_trace()

        entry_id = request.DATA.get('id')
        services = request.DATA.get('services', {})

        query = Media.objects.filter(id=entry_id)
        media = None
        if query.count():
            media = query.get()

        serializer = MediaSerializer(media, data={'id': entry_id})
        if serializer.is_valid():
            serializer.save()
            think(entry_id, services)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FbProfileDetail(APIView):
    """
    Retrieve Facebook user details and initialise facial recognition services.
    """

    def get(self, request, format=None):
        args = urllib.urlencode(dict(access_token=request.GET.get('access_token', '')))
        profile = json.load(urllib.urlopen('https://graph.facebook.com/me?%(args)s' % locals()))

        serializer = FbUserSerializer()
        if 'id' in profile:
            fb_user = FbUser(id=profile['id'],
                            name=profile['name'],
                            is_initialised=False)
            serializer = FbUserSerializer(fb_user)

        return Response(serializer.data)

    def post(self, request, format=None):
        access_token = str(request.DATA.get('access_token', ''))
        force_initialise = bool(request.DATA.get('force_initialise', False))

        args = urllib.urlencode(dict(access_token=access_token))
        url = 'https://graph.facebook.com/me?%(args)s' % locals()
        profile = json.load(urllib.urlopen(url))
        fb_user, created = FbUser.objects.get_or_create(id=profile['id'])
        if force_initialise or created or not fb_user.is_initialised:
            initialise_fb_user('http://%s' % request.get_host(), access_token)
            fb_user.is_initialised = True
            fb_user.name = profile['name']
            fb_user.save()

        return Response(FbUserSerializer(fb_user).data, status=status.HTTP_201_CREATED)


class FbFriendList(APIView):
    """
    List all Facebook current user friends.
    """

    def get(self, request, format=None):
        access_token = request.GET.get('access_token', '')
        friends = json.load(urllib.urlopen('https://graph.facebook.com/me/friends?%s' % urllib.urlencode(dict(access_token=access_token))))

        serializer = FbUserSerializer([], many=True)
        return Response(serializer.data)

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'medias': reverse('media-list', request=request, format=format),
        'fb_friends': reverse('fb-friends-list', request=request, format=format),
        'fb_profile_detail': reverse('fb-profile-detail', request=request, format=format),
    })

def webview(request):
    return render(request, 'brain/webview.html')


def list(request):
    secrets = get_api_secrets()['kaltura']
    content = {'ks':GetKS(),'tag': request.GET.get('tag') , 'partnerId': secrets['partner_id']}
    return render(request, 'brain/list.html', content)
