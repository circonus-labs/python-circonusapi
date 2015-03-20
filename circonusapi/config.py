import os
import logging

try:
    from ConfigParser import SafeConfigParser
except ImportError:
    # python 3.2+
    from configparser import ConfigParser as SafeConfigParser


log = logging.getLogger(__name__)

_cached_config = None

def load_config(configfile=None, nocache=False):
    global _cached_config
    if _cached_config and not nocache:
        return _cached_config

    config = SafeConfigParser()
    config_files = configfile or [
        '/etc/circonusapirc',
        os.path.expanduser('~/.circonusapirc')
    ]
    if not config.read(config_files):
        log.warning(
            "Unable to load default configuraiton. "
            "The program  may not work correctly."
        )
    _cached_config = config
    return config
