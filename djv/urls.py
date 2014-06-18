from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from brain import views

from djv import settings

from django.contrib import admin
admin.autodiscover()

import brain.view

urlpatterns = patterns('',
    url(r'^status/$', views.StatusList.as_view(), name='status-list'),
)

urlpatterns += format_suffix_patterns(patterns('brain.views',
    url(r'^$', 'api_root'),
    url(r'^media/$', views.MediaList.as_view(), name='media-list'),
    url(r'^status/$', views.StatusList.as_view(), name='status-list'),
    url(r'^status/(?P<entry_id>[a-zA-Z0-9_.-]+)/$', views.StatusDetail.as_view(), name='status-detail'),
    url(r'^fb_friend/$', views.FbFriendList.as_view(), name='fb-friends-list'),
    url(r'^fb_profile/$', views.FbProfileDetail.as_view(), name='fb-profile-detail'),
    url(r'^about$', views.webview, name='webview'),
    url(r'^list$', views.list, name='list'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^webnode/media$', brain.view.media.mediapage, name='webnode_mediapage'),
))

urlpatterns += patterns('oauth.views',
    url(r'^oauth/facebook/$', 'facebook'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('djv.urls', namespace='rest_framework')),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
