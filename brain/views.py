from django.http import HttpResponse

def upload_video(request,user=1):
	return HttpResponse("your video id is 1")

def sync(request,user=1):
	#check user has all the tags they neeed for the video
	return HttpResponse("here are your new tags and videos")

def get_tags(request,user=1,video=1):
	# get tags for given video id
	return HttpResponse("tags list for "+video)

def get_video(request,user=1,video=1):
	# get url to download video for kaltura and its tag as well
	return HttpResponse("http://...kalura.com/safsdfawe/...")