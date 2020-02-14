.. Circonusapi documentation master file, created by
   sphinx-quickstart on Fri Feb 14 12:47:33 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents

   api
   submit
   data

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Notes

   changelog

Welcome to Circonusapi
======================

The `circonusapi` python module contains three classes:

CirconusAPI
  The CirconusAPI class contains methods to manage the Circonus Account (e.g. create checks, graphs, etc).

CirconusSubmit
  The CirconusSubmit class contains methods for submitting data to Circonus via a JSON HTTPTrap.

CirconusData
  The CirconusData class contains higher-level methods for fetching data.
  In particular it comes with a method that returns CAQL results as Pandas DataFrames.
