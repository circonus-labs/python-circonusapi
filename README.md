# Circonus API Client Library

The `circonusapi` python module contains three classes:

- CirconusAPI

- CirconusData

- CirconusSubmit

The CirconusAPI class contains methods to manage the Circonus Account (e.g. create checks, graphs, etc).
The CirconusData class contains higher-level methods for fetching data. 
In particular it comes with a method that returns CAQL results as Pandas DataFrames.
The CirconusSubmit class contains methods for submitting data to Circonus via a JSON HTTPTrap.

## Installation

via pip

    pip install circonusapi
   
Manual Install

    python setup.py install

## Requirements and Dependencies

- CirconusAPI supports Python 2.6, 2.7 and 3.x

- CirconusSubmit and CirconusData are tested against python 3.x

**Optional Dependencies:**

* Histogram functionality depends on [libcircllhist](github.com/circonus-labs/libcircllhist) being installed.

* The method `CirconusData.caqldf()` depends on [pandas](https://pandas.pydata.org/) being installed.
