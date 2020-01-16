# Circonus API Client Library


The `circonusapi` python module contains two classes:

- CirconusData

- CirconusAPI

The CirconusAPI class contains methods to manage the Circonus Account (e.g. create checks, graphs, etc) the CirconusData
class contains higher-level methods for working with data. In particular it comes with a CAQL data fetching method, that
returns Pandas DataFrames.

## CirconusData

### Example


Create a CirconusData Object
```
from circonusapi import circonusdata
circ = circonusdata.CirconusData(api_token)
```

Run a CAQL query
```
from datetime import datetime
circ.caql('''

  1 + 2 | label("A")
    
''', datetime(2020,1,1), 60, 10)
```
Result:
```
{
  'version': 'DF4',
   'head': {'count': 10, 'start': 1577836800, 'period': 60},
   'meta': [{'kind': 'numeric', 'label': 'CAQL|op:sum()'}],
   'data': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]
}
```

Fetch CAQL as DataFrame
```
circ.caqldf("""

    find("duration", limit=10) | label("%tv{__check_target}")

""", datetime(2020, 1, 1), 60, 60 * 24)
```
Result:
```
                     xkcd.com  xkcd.com  151.101.64.67  k8sdemo2
2020-01-01 00:00:00         3         3              3        49
2020-01-01 00:01:00         3         3              3        55
2020-01-01 00:02:00         3         3              3        61
2020-01-01 00:03:00         3         3              3        48
2020-01-01 00:04:00         3         3              3        44
2020-01-01 00:05:00         3         3              3        38
2020-01-01 00:06:00         3         3              3        44
2020-01-01 00:07:00         3         3              3        42
...
```

## CirconusAPI

### Example

    from circonusapi import circonusapi

    # Initialize the API
    api = circonusapi.CirconusAPI(<api_token>)

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

# ## Methods

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
