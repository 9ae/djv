import logging

# For Henry's Webnode rendering system
import webnode
import view

# For VoiceBase integration
import kaltura
import voicebase

# For calling think from shell
import ThinkThread

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Do not log messages from requests below WARNING
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)