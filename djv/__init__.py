from __future__ import absolute_import

import logging

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
