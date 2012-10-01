# Circonus API client library

## Example usage

    from circonusapi import circonusapi
    from circonusapi import config

    # Get the api token from the rc file
    c = config.load_config()
    account = config.get('general', 'default_account')
    # You should provide a way to specify an alternative account here. See
    # the config file section below for some example code.
    api_token = config.get('tokens', account)
    # Now initialize the API
    api = circonusapi.CirconusAPI(api_token)

    # Uncomment below to enable debug output
    # api.debug = True

    # List all check bundles
    checks = api.list_check_bundle()

    # Alternative (lower level) method
    api.api_call("GET", "/check_bundle")

    # Add a rule set
    data = {
        "check": "/check/12345",
        "contact_groups": {
            "1": ["On Call"],
            "2": [],
            "3": [],
            "4": [],
            "5": []
        },
        "derive": null,
        "link": null,
        "metric_name": "foo",
        "metric_type": "numeric",
        "notes": null,
        "parent": null,
        "rules": [
            {
                "criteria": "on absence",
                "severity": "1",
                "value": 1,
                "wait": "0"
            }
        ]
    }
    api.add_rule_set(data)

## Methods

All methods begin with a verb, then and underscore, and the circonus API
endpoint that you wish to operate on. For example, to view a check_bundle,
you would use api.get_check_bundle(1234), and to list all rule sets, use
api.list_rule_set().

The verbs/actions, and the associated HTTP methods are:

 * add - POST
 * edit - PUT
 * delete - DELETE
 * list - GET (without an ID specified)
 * get - GET (with an ID specified)

And the valid endpoints are (currently):

 * check_bundle
 * rule_set
 * graph
 * template
 * contact_group
 * broker
 * user
 * account

### Method parameters

Where appropriate, methods take a resource_id parameter, specifying which
resource to operate on. Only list_* and add_* don't take a resource ID.

Where appropriate, methods also take a data parameter specifying the data to
pass to the API call. This parameter can either be a python dictionary, or a
string containing the json encoded object that you wish to pass along.

## Configuration file

In order to not have to specify the API token every time, it can be stored in
a configuration file. The API library provides functions to load the
configuration file and find the token. The config module is based on python's
ConfigParser module.

The config file is: '~/.circonusapirc'. The config module also looks for
configuration inside /etc/circonusapirc.

Config file format:

    [general]
    default_account=foo

    [tokens]
    foo=12345678-9abc-def0-123456789abcdef01
    bar=12345678-90bc-def0-123456789abcdef01

If you have multiple circonus accounts and/or tokens, you can add them in the
tokens section. Your app should provide a method to list which token to use,
and use the value of default_account if one is not specified.

Example code for obtaining the api token:

    import getopt
    import sys

    from circonusapi import config

    c = config.load_config()
    account = config.get('general', 'default_account')

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "a:")
    except getopt.GetoptError, err:
        print str(err)
        print "Usage: %s [-a account] ..." % sys.argv[0]
        sys.exit(2)

    for o,a in opts:
        if o == '-a':
            account = a

    api_token = config.get('tokens', account)

    # Now initialize the API
    api = circonusapi.CirconusAPI(api_token)
