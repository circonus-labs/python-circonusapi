"""
Circonus API Client for Circonus API v2

API calls are mapped onto methods as an action, followed by an underscore,
folowed by an object. For example, to list checks, you would use the
list_check_bundle method, where 'list' is the action, and 'check_bundle' is
the object type that you want to list (in other words, the circonus API
endpoint specified in the docs).

Methods take two parameters where appropriate:

    resource_id - the ID of whatever you are fetching/modifying/deleting. This
                  isn't required  for list_X and add_X methods.
    data - Either a json string or python dict containing the data as required
           by the circonus API.

The available actions are list, get, add, edit and delete. They  map onto the
appropriate circonus API call methods and endpoints (providing an ID as part
of the endpoint or not as required)

Examples:

    >>> api = CirconusAPI('12345678-1234-1234-abcd-123456789abc')
    >>> bundles = api.list_check_bundle()
    >>> some_bundle = api.get_check_bundle(123)

You can also make API calls directly without using methods. For example:

    List check bundles:
    >>> api.api_call("GET", "/check_bundle")

    Get a specific check bundle:
    >>> api.api_call("GET", "/check_bundle/1")

The alternate method of making an API call is especially useful when
de-referencing a value you get back from the api. For example, the
_last_modified_by parameter is of the form '/user/XYZ', and you can find out
who this is by running api.api_call("GET", my_result['_last_modified_by']) and
not have to parse out the user number to use the regular api.get_user(123)
method.
"""

import json
import logging
import time

from contextlib import closing

try:
    from urllib.request import Request, build_opener, HTTPSHandler
    from urllib.parse import quote, urlencode
    from urllib.error import HTTPError, URLError
    from http.client import IncompleteRead
except ImportError:
    # Python 2
    from urllib2 import Request, build_opener, HTTPSHandler, HTTPError, URLError
    from urllib import quote, urlencode
    from httplib import IncompleteRead

log = logging.getLogger(__name__)


class CirconusAPI(object):

    def __init__(self, token):
        self.debug = False # Set api.debug = True to enable debug messages
        self.hostname = 'api.circonus.com'
        self.appname = 'python-circonusapi' # Set api.appname to use a different appname
        self.token = token
        self.endpoints = [
            'check_bundle',
            'rule_set',
            'rule_set_group',
            'graph',
            'template',
            'contact_group',
            'broker',
            'user',
            'account',
            'data',
            'maintenance',
            'alert',
            'annotation',
            'tag',
            'template'
        ]

        self.methods = {
            'add': {
                'method': 'POST',
                'id': False
            },
            'edit': {
                'method': 'PUT',
                'id': True
            },
            'delete': {
                'method': 'DELETE',
                'id': True
            },
            'list': {
                'method': 'GET',
                'id': False
            },
            'get': {
                'method': 'GET',
                'id': True
            }
        }

    def __getattr__(self, name):
        method, endpoint = name.split('_', 1)
        if method in self.methods and endpoint in self.endpoints:
            if self.methods[method]['id']:
                def f(resource_id=None, data=None, params=None):
                    return self.api_call(
                        self.methods[method]['method'],
                        "%s/%s" % (endpoint, resource_id),
                        data=data,
                        params=params
                    )
                return f
            else:
                def g(data=None, params={}):
                    return self.api_call(
                        self.methods[method]['method'],
                        endpoint,
                        data=data,
                        params=params
                    )
                return g
        else:
            raise AttributeError("%s instance has no attribute '%s'" % (
                self.__class__.__name__, name))

    def api_call(self, method, endpoint, data=None, params=None):
        """Performs a circonus api call."""

        # Encode data as json if it isn't already. You can pass a json encoded
        # string or python dict here.
        if isinstance(data, dict):
            data = json.dumps(data)

        # converting str to bytes in PY3 or str to str PY2
        if data:
            data = data.encode('utf-8')

        # Allow specifying an endpoint both with and without a leading /
        endpoint = endpoint.lstrip('/')
        endpoint = quote(endpoint)
        if params:
            endpoint = '%s?%s' % (endpoint, urlencode(
                [(i, params[i]) for i in params]))
        url = "https://%s/v2/%s" % (self.hostname, endpoint)
        req = Request(url=url, data=data,
            headers={
                "X-Circonus-Auth-Token": self.token,
                "X-Circonus-App-Name": self.appname,
                "Content-Type": "application/json",
                "Accept": "application/json"})
        req.get_method = lambda: method
        if self.debug:
            debuglevel = 1
        else:
            debuglevel = 0
        opener = build_opener(
            HTTPSHandler(debuglevel=debuglevel)
        )
        for i in range(5):
            # Retry 5 times until we succeed
            try:
                with closing(opener.open(req)) as fh:
                    response_data = fh.read().decode('utf-8')
                    code = fh.code
                    # We succeeded, exit the for loop
                    break
            except HTTPError as e:
                if e.code == 401:
                    raise TokenNotValidated
                if e.code == 403:
                    raise AccessDenied
                if e.code == 429:
                    # We got a rate limit error, retry
                    if self.debug:
                        log.debug("Rate limited. Retrying: %d", i)
                    time.sleep(1)
                    continue
                # Deal with other API errors
                try:
                    response_data = e.read().decode('utf-8')
                    e.close()
                    data_dict = json.loads(response_data)
                except ValueError:
                    data_dict = {}
                raise CirconusAPIError(e.code, data_dict, debug=self.debug)
            except (URLError, IncompleteRead):
                log.exception('Endpoint failed. Retrying. %s', url)
                time.sleep(1)
                continue
        else:
            # We have been rate limited, retried several times and still got
            # rate limited, so give up and raise an exception.
            raise RateLimitRetryExceeded()

        if self.debug:
            log.debug("data: %s", str(response_data))

        if code == 204:
            # Deal with empty response
            response = {}
        else:
            response = json.loads(response_data)
        # Deal with the unlikely case that we get an error with a 200 return
        # code
        if isinstance(response, dict) and not response.get('success', True):
            raise CirconusAPIError(200, response)
        return response


class CirconusAPIException(Exception):
    pass


class TokenNotValidated(CirconusAPIException):
    pass


class AccessDenied(CirconusAPIException):
    pass

class RateLimitRetryExceeded(CirconusAPIException):
    pass


class CirconusAPIError(CirconusAPIException):
    """Exception class for any errors thrown by the circonus API.

    Attributes:
        code -- the http code returned
        data -- the json object returned by the API
        success -- whether the request succeeded or failed (this is usually
                    false)
        error -- the error message returned by the API
    """
    def __init__(self, code, data, debug=False):
        self.code = code
        self.data = data
        self.debug = debug
        if hasattr(data, 'get'):
            self.success = data.get('success', False)
            self.message = data.get('message', '')
            self.explanation = data.get('explanation')
        else:
            self.message = str(data)

    def __str__(self):
        debuginfo = ""
        if self.debug:
            debuginfo = "\n%s" % json.dumps(self.data)
        return "HTTP %s - %s - %s%s" % (self.code, self.explanation,
                self.message, debuginfo)
