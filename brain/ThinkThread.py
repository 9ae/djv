from threading import Thread
from KalturaImages import generate_images
from ReKImages import tag_images_stock
import concurrent.futures
'''
def complete_sampling():
    print 'sampling video task complete'

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(generateImages, '1_8ycl7639')
    future.add_done_callback(complete_sampling)
'''

# generate_images('1_p5vwu17n')
# tag_images_stock('1_p5vwu17n')

def process_images(entry_id):
    #needs to run and complete first
    generate_images(entry_id)

    # the following two can run in parallel
    tag_images_stock(entry_id)
    # face-recogn(entry_id)


class ThinkThread(Thread):

    def __init__(self, entry_id):
        Thread.__init__(self)
        self.entry_id = entry_id

    def run(self):
        generate_images(self.entry_id)
