# Sending the Output of the Honeypot to an PostgreSQL Database

- [Sending the Output of the Honeypot to an PostgreSQL Database](#sending-the-output-of-the-honeypot-to-an-postgresql-database)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [PostgreSQL Database Creation](#postgresql-database-creation)
  - [Honeypot Configuration](#honeypot-configuration)
  - [Restart the honeypot](#restart-the-honeypot)

## Prerequisites

- Working honeypot installation
- PostgreSQL

## Installation

When writing to an PostgreSQL database, the honeypot uses the free databases
provided by MaxMind for the purpose of geoloacting the IP addresses.
Start by installing the library necessary to work with these databases
from an account that can sudo (i.e., not from the user `elasticpot`):

```bash
sudo add-apt-repository ppa:maxmind/ppa
sudo apt-get update
sudo apt-get install PostgreSQL geoipupdate
```

Then, make sure that the PostgreSQL database and the `psql` command-line
utility for managing it are installed:

```bash
sudo apt-get install postgresql-12 postgresql-client
```

Log in as the user `postgres` (the super-user in PostgreSQL) and create
the honeypot-related database users, the database, and grant proper
privileges to it to the users:

```psql
$ sudo su - postgres
$ psql
postgres=# create user elasticpot with password 'PASSWORD HERE';
postgres=# create database elasticpot;
postgres=# grant all privileges on database elasticpot to elasticpot;
```

(Make sure you specify a proper password that you want to use for the user
`elasticpot` instead of 'PASSWORD HERE'.)

If you're going to use a third-party tool for accessing the data from the
database (e.g., [Grafana](https://www.grafana.com) for visualizing the data),
it is advisable also to create a separate user that has read-only privileges
to the database and have the third-party tool access the database as that
user, so that in case the third-party tool contains some kind of vulnerability
and is breached (and the attacker obtains the database user password from it),
the attacker cannot modify the database:

```psql
postgres=# create user elasticpotReadOnly with password 'OTHER PASSWORD HERE';
postgres=# grant select on database elasticpot to elasticpot;
```

(Make sure you specify a proper password that you want to use for the user
`elasticpotReadOnly` instead of 'OTHER PASSWORD HERE'.)

Finally, exit `psql`:

```psql
postgres=# \q
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

## PostgreSQL Database Creation

The database is already created but it is completely empty. Now we have to
specify its schema (tables and indexes):

```bash
psql -f docs/postgres/postgres.sql -W elasticpot elasticpot
```

You will be prompted for the password of the database user `elasticpot`.

If your database does not reside on your local machine but is on some remote
database server, use the options `-h host` and `-p port` of `psql` to
specify how to connect to it.

## Honeypot Configuration

Add the following entries to the file `~/elasticpot/etc/honeypot.cfg`

```honeypot.cfg
[output_postgres]
enabled = true
debug = false
host = localhost
port = 5432
username = elasticpot
password = secret
database = elasticpot
# Whether to store geolocation data in the database
geoip = true
# Location of the databases used for geolocation
geoip_citydb = data/GeoLite2-City.mmdb
geoip_asndb = data/GeoLite2-ASN.mmdb
```

Make sure that you specify the correct information needed to connect to the
database (the options `host`, `port`, `username`, and `password`) and that the
options `geoip_citydb` and `geoip_asndb` point to the correct paths of the two
MaxMind geolocation databases. Also, if you prefer to keep the PostgreSQL
database under a different name, make sure that you specify its correct name
with the `database` option.

## Restart the honeypot

```bash
./bin/honeypot restart
```
