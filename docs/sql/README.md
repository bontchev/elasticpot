# Sending the Output of the honeypot to a MySQL Database

- [Sending the Output of the honeypot to a MySQL Database](#sending-the-output-of-the-honeypot-to-a-mysql-database)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [MySQL Configuration](#mysql-configuration)
  - [Honeypot Configuration](#honeypot-configuration)
  - [Restart the honeypot](#restart-the-honeypot)

## Prerequisites

- Working honeypot installation
- MySQL Server installation

## Installation

When writing to a MySQL database, the honeypot uses the free databases
provided by MaxMind for the purposes of geoloacting the IP addresses.
Start by installing the library necessary to work with these databases
from an account that can sudo (i.e., not from the user `elasticpot`):

```bash
sudo add-apt-repository ppa:maxmind/ppa
sudo apt-get update
sudo apt-get install python-mysqldb libmysqlclient-dev geoipupdate
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
the `[mysql_output]` section of the file `honeyot.cfg`, as mentioned
below.

## MySQL Configuration

First create a database named `elasticpot` and grant access to it to a user
named `elasticpot`:

```bash
$ mysql -p -u root
MySQL> CREATE DATABASE IF NOT EXISTS elasticpot;
MySQL> CREATE USER IF NOT EXISTS 'elasticpot'@'localhost' IDENTIFIED BY 'PASSWORD HERE' PASSWORD EXPIRE NEVER;
MySQL> GRANT ALTER, ALTER ROUTINE, CREATE, CREATE ROUTINE, CREATE TEMPORARY TABLES, CREATE VIEW, DELETE, DROP, EXECUTE, INDEX, INSERT, LOCK TABLES, SELECT, SHOW VIEW, TRIGGER, UPDATE ON elasticpot.* TO 'elasticpot'@'localhost';
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

```bash
MySQL> CREATE USER IF NOT EXISTS 'elasticpotReadOnly'@'localhost' IDENTIFIED BY 'OTHER PASSWORD HERE' PASSWORD EXPIRE NEVER;
MySQL> GRANT SELECT ON elasticpot.* TO 'elasticpotReadOnly'@'localhost';
```

(Make sure you specify a proper password that you want to use for the user
`elasticpotReadOnly` instead of 'OTHER PASSWORD HERE'.)

Finally, make sure that the user-related changes are committed to the database:

```mysql
MySQL> FLUSH PRIVILEGES;
MySQL> exit
```

Next, load the database schema:

```bash
$ cd /home/elasticpot/elasticpot/
$ mysql -p -u elasticpot elasticpot
MySQL> source ./docs/sql/mysql.sql;
MySQL> exit
```

## Honeypot Configuration

Add the following entries to the file `~/elasticpot/etc/honeypot.cfg`

```honeypot.cfg
[output_mysql]
enabled = true
host = localhost
database = elasticpot
username = elasticpot
password = PASSWORD HERE
port = 3306
# Whether to store geolocation data in the database
geoip = true
# Location of the databases used for geolocation
geoip_citydb = data/GeoLite2-City.mmdb
geoip_asndb = data/GeoLite2-ASN.mmdb
```

Make sure you use the password you specified for the MySQL user `elasticpot`
instead of 'PASSWORD HERE'. Make sure the options `geoip_citydb` and
`geoip_asndb` point to the correct paths of the two MaxMind geolocation
databases.

Since the file `honeypot.cfg` contains in cleartext the password for
the database, it would be a good idea to change its permissions so that only
the user `elasticpot` can access it:

```bash
chmod g-r,g-w,o-r,o-w ~/elasticpot/etc/honeypot.cfg
```

## Restart the honeypot

```bash
./bin/honeypot restart
```
