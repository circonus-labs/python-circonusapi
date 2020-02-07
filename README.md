# Circonus API Client Library

The `circonusapi` python module contains thress classes:

- CirconusAPI

- CirconusData

- CirconusSubmit

The CirconusAPI class contains methods to manage the Circonus Account (e.g. create checks, graphs, etc).
The CirconusData class contains higher-level methods for fetching data. 
In particular it comes with a method that returns CAQL results as Pandas DataFrames.
The CirconusSubmit class contains methods for submitting data to Circonus via a JSON HTTPTrap.

## Changelog

### 0.5.0 2020-02-07

- Add CirconusSubmit class

### 0.4.0 2020-01-17

- Add metadata and DF4 support to CirconusData.caql()

- Add CirconusData.caqldf() method

- Remove CirconusData.search() method. Search functionality is provided via CirconusData.caql().

- Deprecate config.py module

## Dependencies

Python 2.6,2.7 and 3.x are supported. We recommend using python >3.5.

Optional Dependencies:

* Histogram functionality depends on [libcircllhist](github.com/circonus-labs/libcircllhist) being installed on the system.
* The method `CirconusData.caqldf()` depends on [pandas](https://pandas.pydata.org/) being installed.

## Installation

Via Pip
```
pip install circonusapi
```

Manual Install
```
python setup.py install
```

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
   'meta': [{'kind': 'numeric', 'label': 'A'}],
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

More examples can be found in the ./examples folder in this repository.

## CirconusSubmit

```
from circonusapi import circonussubmit

# Option A: Create a new check to submit data to
sub = circonussubmit.CirconusSubmit()
sub.auth("65669d6b-edfe-4ede-bc51-7f3cae6419cf")
sub.check_create("circ-submit-1")

# Option B: Use a existing submission URL:
sub = circonussubmit.CirconusSubmit("<submission url>")

# Add data to batch
from datetime import datetime
sub.add_number(datetime(2020, 1, 1, 0, 0, 0), "test-metric-1", 20)
sub.add_number(datetime(2020, 1, 1, 0, 1, 0), "test-metric-1", 40)
sub.add_number(datetime(2020, 1, 1, 0, 2, 0), "test-metric-1", 50)

# Submit batch of data
sub.submit()
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

### Methods

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
