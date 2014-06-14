from threading import Thread
from KalturaImages import generateImages
from ReKImages import tag_images

class ThinkThread(Thread):

    def __init__(self, entry_id):
        self.entry_id = entry_id

    def run(self):
        generateImages(self.entry_id)
        tag_images(self.entry_id)
