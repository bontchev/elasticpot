# Installation guide (on Ubuntu 16.04)

- [Installation guide (on Ubuntu 16.04)](#installation-guide-on-ubuntu-1604)
  - [Step 1: Install the dependencies](#step-1-install-the-dependencies)
  - [Step 2: Open the firewall for port 9200 traffic](#step-2-open-the-firewall-for-port-9200-traffic)
  - [Step 3: Create a user account](#step-3-create-a-user-account)
  - [Step 4: Checkout the code](#step-4-checkout-the-code)
  - [Step 5: Setup Virtual Environment](#step-5-setup-virtual-environment)
  - [Step 6: Create a configuration file](#step-6-create-a-configuration-file)
  - [Step 7: Start the honeypot](#step-7-start-the-honeypot)
  - [Configure additional output plugins (OPTIONAL)](#configure-additional-output-plugins-optional)
  - [Change the default responses (OPTIONAL)](#change-the-default-responses-optional)
  - [Docker usage (OPTIONAL)](#docker-usage-optional)
  - [Command-line options](#command-line-options)
  - [Upgrading the honeypot](#upgrading-the-honeypot)

## Step 1: Install the dependencies

First we install system-wide support for Python virtual environments and other
dependencies. Actual Python packages are installed later.

```bash
sudo apt-get update
sudo apt-get install git python-virtualenv libffi-dev build-essential libpython-dev python2.7-minimal python3.5-minimal python-dev libmysqlclient-dev
```

## Step 2: Open the firewall for port 9200 traffic

If TCP port 9200 is not aleady opened for incoming connections on your firewall
and router, you must open it now.

To open it on the firewall, execute the following command:

```bash
sudo ufw allow 9200/tcp
```

If your honeypot machine is behind a NAT router, you must open the router
for traffic coming over port 9200 too. How exactly this is done depends on
the router model; please consult the instruction manual of the router.

## Step 3: Create a user account

It is strongly recommended to run the honeypot as a dedicated non-root user
(named `elasticpot` in our example), who cannot `sudo`:

```bash
$ sudo adduser --disabled-password elasticpot
Adding user 'elasticpot' ...
Adding new group 'elasticpot' (1002) ...
Adding new user 'elasticpot' (1002) with group 'elasticpot' ...
Changing the user information for elasticpot
Enter the new value, or press ENTER for the default
Full Name []:
Room Number []:
Work Phone []:
Home Phone []:
Other []:
Is the information correct? [Y/n]

$ sudo su - elasticpot
```

## Step 4: Checkout the code

```bash
$ git clone https://gitlab.com/bontchev/elasticpot.git
Cloning into 'elasticpot'...
remote: Enumerating objects: 116, done.
remote: Counting objects: 100% (116/116), done.
remote: Compressing objects: 100% (62/62), done.
remote: Total 116 (delta 56), reused 90 (delta 45), pack-reused 0
Receiving objects: 100% (116/116), 61.36 KiB | 1.75 MiB/s, done.
Resolving deltas: 100% (56/56), done.

$ cd elasticpot
```

## Step 5: Setup Virtual Environment

Next you need to create your virtual environment:

```bash
$ pwd
/home/elasticpot/elasticpot
$ virtualenv elasticpot-env
New python executable in ./elasticpot-env/bin/python
Installing setuptools, pip, wheel...done.
```

Activate the virtual environment and install the necessary dependencies

```bash
$ source elasticpot-env/bin/activate
(elasticpot-env) $ pip install --upgrade pip
(elasticpot-env) $ pip install --upgrade -r requirements.txt
```

## Step 6: Create a configuration file

The configuration for the honeypot is stored in `etc/honeypot.cfg.base` and
`etc/honeypot.cfg`. Both files are read on startup but the entries from
`etc/honeypot.cfg` take precedence. The `.base` file contains the default
settings and can be overwritten by upgrades, while `honeypot.cfg` will not be
touched. To run with a standard configuration, there is no need to change
anything.

For instance, in order to enable JSON logging, create `etc/honeypot.cfg` and
put in it only the following:

```honeypot.cfg
[output_jsonlog]
enabled = true
logfile = log/elasticpot.json
epoch_timestamp = true
```

For more information about how to configure additional output plugins (from
the available ones), please consult the appropriate `README.md` file in the
subdirectory corresponding to the plugin inside the `docs` directory.

## Step 7: Start the honeypot

Make a copy of the file `honeypot-launch.cfg.base`:

```bash
$ pwd
/home/elasticpot/elasticpot
$ cd etc
$ cp honeypot-launch.cfg.base honeypot-launch.cfg
$ cd ..
```

Before starting the honeypot, make sure that you have specified correctly
where it should look for the virtual environment. This documentation suggests
that you create it in `/home/elasticpot/elasticpot/elasticpot-env/`. If you
have indeed created it there, there is no need to change anything. If, however,
you have created it elsewhere, you have to edit the file
`/home/elasticpot/elasticpot/etc/honeypot-launch.cfg` and change the setting
of the variable `HONEYPOT_VIRTUAL_ENV` to point to the directory where your
virtual environment is.

Now you can launch the honeypot:

```bash
$ pwd
/home/elasticpot/elasticpot
$ ./bin/honeypot start
Starting the honeypot ...
The honeypot was started successfully.
```

## Configure additional output plugins (OPTIONAL)

The honeypot automatically outputs event data as text to the file
`log/honeypot.log`. Additional output plugins can be configured to record the
data other ways. Supported output plugins include:

- JSON
- MySQL

More plugins are likely to be added in the future.

See `docs/[Output Plugin]/README.md` for details.

## Change the default responses (OPTIONAL)

By default, the honeypot sends as responses to the various queries that it
emulates the contents of the files in the `responses` directory. However,
this can be used to fingerprint the honeypot, so the user is *strongly*
encouraged to change their contents.

In other to prevent future updates of the honeypot from overwriting the
changes of these files made by the user, one should store the custom
responses in a separate directory and specify this directory either
in the `responses_dir=` directive of the `etc/honeypot.cfg` file or
via the `-r` command-line option.

The meaning of these response files is as follows:

File | Send as a response to the query
--- | ---
`aliases.json` | Anything containing `alias`
`banner.json` | `/`
`cluster.json` | Anythinig starting with `/_cluster/health`
`error.json` | Any unrecognized query
`index1long.json`, `index2long.json` | A `/_cat/indices` query that doesn't contain the parameter `h=index`
`index1short.json`, `index2short.json` | A `/_cat/indices` query that contains the parameter `h=index`
`indices.txt` | A `/_cat/indices` query that doesn't contain the parameter `format=json`
`nodes.json` | Anything starting with `/_nodes`
`pluginhead.html` | `/_plugin/head`
`search.json` | Anything starting with `/_search`
`stats1.json` | Anything starting with `/_stats`
`stats2.json` | `/_cluster/stats`

It is advisable to leave the file `banner.json` unchanged, because it
identifies the simulated Elasticsearch server as being an old version, which
is vulnerable to remote code execution, thus enticing the attackers to attempt
to exploit it.

Similarly, there is normally no need to modify the file `error.json`.

The honeypot currently emulates an Elasticsearch database with 2 indices
(`index1*.json` and `index2*.json`). Their contents and names can be changed
via the response files but their number cannot be. It is advisable that the
contents of the files `aliases.json` and `indices.txt` reflects the names
of these two indices, if they are modified by the user (the latter is
advisable, in order to avoid fingerprinting).

## Docker usage (OPTIONAL)

First, from a user who can `sudo` (i.e., not from the user `elasticpot`) make
sure that `docker` is installed and that the user `elasticpot` is a member of
the `docker` group:

```bash
sudo apt-get install docker.io
sudo usermod -a -G docker elasticpot
```

**WARNING!** A user who belongs to the `docker` group has root user
privileges, which negates the advantages of creating the `elasticpot` user as a
restricted user in the first place. If a user is not a member of the `docker`
group, the only way for them to use Docker is via `sudo` - which a restricted
user like `elasticpot` cannot do. Since this increases the
[attack surface](https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface),
we advise against using the honeypot with Docker. One alternative is to look
into other containerization systems that do not require privileged user access
in order to operate - e.g., [Podman](https://podman.io/).

Then switch to the user `elasticpot`, build the Docker image, and run it:

```bash
sudo su - elasticpot
docker build -t elasticpot .
docker run -d -p 9200:9200/tcp -u $(id -u):$(id -g) -v $(HOME}/elasticpot:/elasticpot -w /elasticpot elasticpot
```

## Command-line options

elasticpot supports the following command-line options:

```options
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -p PORT, --port PORT  Port to listen on (default: 9200)
  -l LOGFILE, --logfile LOGFILE
                        Log file (default: stdout)
  -r RESPONSES, --responses RESPONSES
                        Directory of the response files (default: responses)
  -s SENSOR, --sensor SENSOR
                        Sensor name (default: computer-name)
```

The settings specified via command-line options take precedence over the
corresponding settings in the `.cfg` files.

## Upgrading the honeypot

Updating is an easy process. First stop your honeypot. Then fetch any
available updates from the repository. As a final step upgrade your Python
dependencies and restart the honeypot:

```bash
./bin/honeypot stop
git pull
pip install --upgrade -r requirements.txt
./bin/honeypot start
```
