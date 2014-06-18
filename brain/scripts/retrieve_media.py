#!/usr/bin/env python

"""Retrieve media entries from Kaltura"""

import brain

params = {
    'service': 'media',
    'action': 'list',
}

data = {
    'page': {
        'pageSize': 100,
    }
}

ret = brain.kaltura.call_kaltura(params, post=True, data=data)
for row in ret['objects']:
    entry_id = row['rootEntryId']
    print 'Creating entry {}'.format(entry_id)
    brain.models.Media(id = entry_id).save()