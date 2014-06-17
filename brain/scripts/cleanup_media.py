#!/usr/bin/env python

"""Delete broken media entries from database"""

import brain

for media in brain.models.Media.objects.all():
    url = brain.kaltura.get_entry_download_url(media.id)
    print media.id, url
    if url is None:
        print 'Deleting entry {}'.format(media.id)
        media.delete()