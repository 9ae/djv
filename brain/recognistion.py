import logging
import json
import math
import os
import tempfile
import urllib

from PIL import Image


def get_fb_photos(access_token, user_id='me'):
    args = urllib.urlencode(dict(access_token=access_token))
    return json.load(urllib.urlopen('https://graph.facebook.com/%(user_id)s/photos?%(args)s' % locals()))

def extract_tagged_area(fb_photo_obj):
    fd, name = tempfile.mkstemp()
    try:
        with open(name, 'wb') as f:
            f.write(urllib.urlopen(fb_photo_obj['source']).read())

        photo_id = fb_photo_obj['id']
        photo_name = fb_photo_obj.get('name', '')
        logging.debug('Processing FB photo: [%(photo_id)s] %(photo_name)s' % locals())

        height = fb_photo_obj['height']
        width = fb_photo_obj['width']

        result = dict(photo_id=photo_id,
                      photo_name=photo_name,
                      tags=[])
        for t in filter(lambda x: 'id' in x, fb_photo_obj['tags']['data']):
            image = Image.open(name)
            tag_id = t['id']
            x = t['x']
            y = t['y']

            # create crop region 5% from the tag point
            tolerance = 5.0
            box = (
                (x - tolerance) * width,
                (y - tolerance) * height,
                (x + tolerance) * width,
                (y + tolerance) * height,
            )
            box = map(lambda x: int(round(x / 100.0)), box)

            # crop and save image
            cropped_image = '%(photo_id)s.%(tag_id)s.jpg' % locals()
            image.crop(box).save(cropped_image)

            result['tags'].append(dict(tag_id=tag_id,
                                       name=t['name'],
                                       image=cropped_image))

    finally:
        os.close(fd)
        os.unlink(name)





access_token = 'CAAJGRBkWxtgBAJaGGZBw38DP3ZBEgwVyhdZApVBBH25kl4S1ZAZBixvxHrrje6VVXmdMYID8TGZCZADWlBcm5ivjaN6ZCZBjJwCaWHOFvytNY06c67XhJXsdNjDrjomUyZBUm67Kz0Gfvbw8HRcgSzoouWxChOnoOXToVVTDXC96shWJbMfYYCkQao'
for d in get_fb_photos(access_token)['data']:
    import pdb; pdb.set_trace()  # XXX BREAKPOINT
    result = extract_tagged_area(d)

