# Sending the Output of the Honeypot to an SQLite3 Database

- [Sending the Output of the Honeypot to an SQLite3 Database](#sending-the-output-of-the-honeypot-to-an-sqlite3-database)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [SQLite3 Database Creation](#sqlite3-database-creation)
  - [Honeypot Configuration](#honeypot-configuration)
  - [Restart the honeypot](#restart-the-honeypot)

## Prerequisites

- Working honeypot installation
- SQLite3 (Can be downloaded from the [official site](https://sqlite.org/download.html))

## Installation

When writing to an SQLite3 database, the honeypot uses the free databases
provided by MaxMind for the purposes of geoloacting the IP addresses.
Start by installing the library necessary to work with these databases
from an account that can sudo (i.e., not from the user `elasticpot`):

```bash
sudo add-apt-repository ppa:maxmind/ppa
sudo apt-get update
sudo apt-get install sqlite3 geoipupdate
```

Now switch to the `elasticpot` user:

```bash
sudo su - elasticpot
cd elasticpot
```

Go to the directory `data`, where the gelolocation databases will reside:

```bash
cd data
```

Create in this directory a file named `geoip.cfg` with the following contents:

```geoip.cfg
AccountID <ACCOUNT>
LicenseKey <KEY>
EditionIDs GeoLite2-City GeoLite2-ASN
DatabaseDirectory /home/elasticpot/elasticpot/data
LockFile /home/elasticpot/elasticpot/data/.geoipupdate.lock
```

Change the paths in the options `DatabaseDirectory` and `LockFile` if you
have opted to use paths different from the ones suggested by the
honeypot installation documentation. Make sure you replace `<ACCOUNT>`
and `<KEY>` with the account and API key obtained from MaxMind.

In order to be able to download the MaxMind geolocation databases (either
manually or in an automated way), you need a (free) account at their site.
You can create such an account [there](https://www.maxmind.com/en/geolite2/signup).
Creating it involves choosing a user name and a password, providing some
personal data like country of residence, industry in which you're working,
intended use for their databases, an e-mail address, and also agreeing with
their terms and conditions. Once the account is created, you can get your
AccountID and LicenseKey from it.

Download the latest version of the Maxmind geolocation databases:

```bash
geoipupdate -f geoip.cfg
```

To have the database updated automatically (it is updated on MaxMind's site
every second Tuesday of each month, so download it every second Wednesday),
create a crontab job (`crontab -e`) and enter the following:

```crontab
# Update the geoIP database at midnight on the 2nd Wednesday of each month:
0 0 8-14 * * [ $(/bin/date +\%u) -eq 3 ] && /usr/bin/geoipupdate -f /home/elasticpot/elasticpot/data/geoip.cfg
```

Alternatively, if you already have the MaxMind geolocation databases installed
and updated on your machine in some other place, use their respective paths in
the `[output_sqlite]` section of the file `honeyot.cfg`, as mentioned
below.

Finally, return to the main directory of the project:

```bash
cd ..
```

## SQLite3 Database Creation

First create a database named `elasticpot` residing in the `data` directory and
based on the schema `docs/sqlite3/sqlite3.sql`:

```bash
sqlite3 ~/elasticpot/data/elasticpot.db < docs/sqlite3/sqlite3.sql
```

If you have opted on keeping the database elsewhere, use its proper path
instead of `~/elasticpot/data/elasticpot.sql`.

## Honeypot Configuration

Add the following entries to the file `~/elasticpot/etc/honeypot.cfg`

```honeypot.cfg
[output_sqlite]
enabled = true
debug = false
db_file = data/elasticpot.db
# Whether to store geolocation data in the database
geoip = true
# Location of the databases used for geolocation
geoip_citydb = data/GeoLite2-City.mmdb
geoip_asndb = data/GeoLite2-ASN.mmdb
```

Make sure the options `geoip_citydb` and `geoip_asndb` point to the correct
paths of the two MaxMind geolocation databases. Also, if you prefer to keep
the SQLite3 database elsewhere, make sure that you specify its correct path
with the `db_file` option.

## Restart the honeypot

```bash
./bin/honeypot restart
```
