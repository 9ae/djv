from threading import Thread
from KalturaImages import generate_images
from ReKImages import tag_images
import concurrent.futures
'''
def complete_sampling():
    print 'sampling video task complete'

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(generateImages, '1_8ycl7639')
    future.add_done_callback(complete_sampling)
'''

generate_images('1_8ycl7639')