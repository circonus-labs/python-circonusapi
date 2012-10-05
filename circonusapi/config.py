import ConfigParser
import os

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
   # except IOError:
   #     print "Unable to load default configuraiton. The program"
   #             " may not work correctly."

    # Now load the system/user specific config (if any)
    if configfile:
        config.read([configfile])
    else:
        config.read(['/etc/circonusapirc',
                                os.path.expanduser('~/.circonusapirc')])
    _cached_config = config
    return config
