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

from ThinkThread import ThinkThread

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
        entry_id = request.DATA.get('id')
        access_token = request.DATA.get('access_token')

        Media.objects.get_or_create(id=entry_id)

        serializer = MediaSerializer(data=request.DATA, partial=True)
#        if serializer.is_valid():
#            serializer.save()

        main_thread = ThinkThread(entry_id,access_token)
        main_thread.start()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        fb_user, created = FbUser.objects.get_or_create(id=profile['id'],
                                                        name = profile['name'])
        if force_initialise or created or not fb_user.is_initialised:
            initialise_fb_user('http://%s' % request.get_host(), access_token)
            fb_user.is_initialised = True
            fb_user.save()

        serializer = FbUserSerializer(fb_user, data=request.DATA, partial=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

def list(request, tag=''):
    return render(request, 'brain/list.html')
