import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Do not log messages from requests below WARNING
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)