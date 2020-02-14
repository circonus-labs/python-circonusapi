# Circonus API Client Library

The `circonusapi` python module contains thress classes:

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

