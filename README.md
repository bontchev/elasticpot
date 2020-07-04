# ElasticPot: an Elasticsearch Honeypot

This is a honeypot simulating a vulnerable Elasticsearch server opened to the
Internet. It uses ideas from various other honeypots, like
[ADBHoneypot](https://gitlab.com/bontchev/adbhoneypot) (for output plugin
support), [Citrix Honeypot](https://gitlab.com/bontchev/CitrixHoneypot) (for
general structure), [Elastichoney](https://github.com/jordan-wright/elastichoney),
(for a general example of an Elasticsearch honeypot).
[ElasticpotPY](https://github.com/schmalle/ElasticpotPY) (for the idea to use
scripted responses stored in files), and
[Delilah](https://github.com/SecurityTW/delilah) (for additional ideas on what
to emulate).

## Prerequisites

- a working MySQL server (only if you use the MySQL output plugin)

## Usage

Check the [installation document](docs/INSTALL.md) for more information how to
properly install, configure, and run the honeypot.
