import ConfigParser
import os

import log

_cached_config = None

def load_config(configfile=None):
    global _cached_config
    if _cached_config:
        return _cached_config

    config = ConfigParser.SafeConfigParser()

   # # First load the default config
   # try:
   #     config.readfp(open(os.path.join(os.path.dirname(__file__),
   #                                         "..", "data", "defaults")))
   #     log.debug("Loaded default configuration")
   # except IOError:
   #     log.error("Unable to load default configuraiton. The program"
   #             " may not work correctly.")

    # Now load the system/user specific config (if any)
    if configfile:
        loaded = config.read([configfile])
    else:
        loaded = config.read(['/etc/circonusapirc',
                                os.path.expanduser('~/.circonusapirc')])
    log.debug("Loaded config files: %s" % ', '.join(loaded))
    _cached_config = config
    return config
