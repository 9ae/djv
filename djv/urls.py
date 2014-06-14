from django.conf.urls import patterns, include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from brain import views

from django.contrib import admin
admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = format_suffix_patterns(patterns('brain.views',
    url(r'^$', 'api_root'),
    url(r'^media/$', views.MediaList.as_view(), name='media-list'),
))

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'djv.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('djv.urls', namespace='rest_framework')),

    url(r'^', include(router.urls)),
)
