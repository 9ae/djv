import uuid

from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from models import Media
from serializers import UserSerializer, GroupSerializer, MediaSerializer

#def upload_video(request,user=1):
#	return HttpResponse("your video id is 1")
#
#def sync(request,user=1):
#	#check user has all the tags they neeed for the video
#	return HttpResponse("here are your new tags and videos")
#
#def get_tags(request,user=1,video=1):
#	# get tags for given video id
#	return HttpResponse("tags list for "+video)
#
#def get_video(request,user=1,video=1):
#	# get url to download video for kaltura and its tag as well
#	return HttpResponse("http://...kalura.com/safsdfawe/...")




class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MediaList(APIView):
    """
    List all media, or upload a new media.
    """
    model = Media

    def get(self, request, format=None):
        medias = Media.objects.all()
        serializer = MediaSerializer(medias, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # TODO: begin process of accessing external APIs and tagging
        # currently only creates a dummy media object
        media = Media(id=str(uuid.uuid4()),
                      user=request.user)
        serializer = MediaSerializer(media)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'medias': reverse('media-list', request=request, format=format)
    })
