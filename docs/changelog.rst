Changelog
=========

Unreleased Changes
  - Added ./bin/caql cli tool
  - Support http/https connections to API endpoints
  - Add Sphinx based documentation at gh-pages
  - Support test-docker target, that runs tests with all supported python versions

v0.5.0
  * Date: 2020-02-07
  * Changes:

    - Add CirconusSubmit class

v0.4.0
  * Date: 2020-01-17
  * Changes:

    - Add metadata and DF4 support to CirconusData.caql()
    - Add CirconusData.caqldf() method
    - Remove CirconusData.search() method. Search functionality is provided via CirconusData.caql().
    - Deprecate config.py module
