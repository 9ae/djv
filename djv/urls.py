from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from brain import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = format_suffix_patterns(patterns('brain.views',
    url(r'^$', 'api_root'),
    url(r'^media/$', views.MediaList.as_view(), name='media-list'),
    url(r'^fb_friend/$', views.FbFriendList.as_view(), name='fb-friends-list'),
    url(r'^fb_profile/$', views.FbProfileDetail.as_view(), name='fb-profile-detail'),
))

urlpatterns += patterns('oauth.views',
    url(r'^oauth/facebook/$', 'facebook'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('djv.urls', namespace='rest_framework')),
)
