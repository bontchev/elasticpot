# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6]

### Added in version 1.0.6

* Nothing yet

### Changed in version 1.0.6

* Nothing yet

## [1.0.5]

### Added in version 1.0.5

* PostgreSQL output plugin (with documentation)
* Documentation for the SQLite3 output pllugin
* Handling some additional Elasticsearch queries

### Changed in version 1.0.5

* Fixed a typo in the change log

## [1.0.4]

### Added in version 1.0.4

* CouchDB output plugin
* SQLite3 output plugin
* Elasticsearch output plugin (ironic, I know)
* Handling some additional Elasticsearch queries

### Changed in version 1.0.4

* The MongoDB plugin was using the MySQL `geoip` setting. Fixed.
* Made the reading of username- and password-related settings using `raw=True`
* Minor fixes

## [1.0.3]

### Added in version 1.0.3

* MongoDB output plugin
* Redis database output plugin
* Rethink database output plugin (not tested!)
* Influx database (versions 1.7 and earlier only) output plugin (not tested!)
* Influx 2.0 database (requires Python 3; not tested)
* Support for the `report_public_ip` config file option

### Changed in version 1.0.3

* Minor fixes
* Fixed a JSON serialization bug when running under Python 3
* Optimized the MySQL output plugin a bit
* Improved the settings of future plugins

## [1.0.2]

### Added in version 1.0.2

* Text output plugin
* HPFeeds output plugin

## [1.0.1]

### Added in version 1.0.1

* Ability to specify a directory for the response files via the config file or a command-line option
* Updated the documentation

### Changed in version 1.0.1

* Fixed a bug when handling a query containing the substring `alias`

## [1.0.0]

### Added in version 1.0.0

* Initial release
* Implemented the honeypot using the Twisted framework
* A script for starting, stopping, and restarting the honeypot
* Config file support
* Various command-line options
* HEAD requests are now logged too
* Output plugin support
* Output plugin for JSON
* Output plugin for MySQL
* Log rotation
* Emulation of multiple Elasticsearch requests
* Data-driven responses stored in files
* Make the script compatible with Python 3.x
* Rewrote the documentation
