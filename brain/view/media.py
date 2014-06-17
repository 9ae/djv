"""Defining the Media"""

from __future__ import unicode_literals

import brain
import brain.webnode as webnode
import brain.webnode.html as h

from brain.api_secrets import PARTNER_ID
from django.http import HttpResponse
from page import Page

class KVideo(webnode.Component):
    def __init__(self, entry_id, **kwargs):
        self.entry_id = entry_id
        self.id = 'kvideo_{}_{}'.format(id(self), entry_id)
        self.kwargs = kwargs

    def tree(self):
        z = []
        z += h.div(id = self.id, **self.kwargs)
        with h.script(type='text/javascript').into(z):
            z += h.Raw('''\
mw.setConfig("KalturaSupport.LeadWithHTML5",true);
kWidget.embed({
    'targetId': '%s',
    'wid': '_%s',
    'uiconf_id': '24670302',
    'entry_id': '%s',
});
''' % (self.id, PARTNER_ID, self.entry_id))
        return z

class MediaPage(Page):
    def content(self):
        z = []
        z += h.h1('List of all videos')
        for media in brain.models.Media.objects.all():
            with h.div(class_='col-md-3').into(z):
                with h.div().into(z):
                    z += KVideo(media.id)
                tags = media.get_kaltura_tags()
                with h.dl().into(z):
                    z += h.dt('tags')
                    with h.dd().into(z):
                        for tag in tags:
                            z += h.span(tag)
        return z

def mediapage(request):
    return HttpResponse(MediaPage().render())