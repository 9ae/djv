from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^user/(?P<user>[0-9]+)/upload_video$', 'brain.views.upload_video'),
     url(r'^user/(?P<user>\d+)/sync$', 'brain.views.sync'),
     url(r'^user/(?P<user>\d+)/get_tags/(?P<video>\d+)$', 'brain.views.get_tags'),
     url(r'^user/(?P<user>\d+)/get_video/(?P<video>\d+)$', 'brain.views.get_video'),
    # url(r'^djv/', include('djv.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
