#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Licencing Agreement: MalwareTech Public Licence
This software is free to use providing the user yells
"Oh no, the cyberhackers are coming!" prior to each installation.
"""

from os.path import join
from socket import gethostname
from argparse import ArgumentParser

from core.config import CONFIG
from core.protocol import Index
from core.logfile import set_logger
from core.tools import mkdir, import_plugins, stop_plugins, get_public_ip

from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor

__VERSION__ = '1.0.5'
__description__ = 'Elasticsearch Honeypot'
__license__ = 'GPL'
__uri__ = 'https://gitlab.com/bontchev/elasticpot'
__author__ = 'Vesselin Bontchev'
__email__ = 'vbontchev@yahoo.com'


def get_options(cfg_options):
    parser = ArgumentParser(description=__description__)

    parser.add_argument('-v', '--version', action='version', version='%(prog)s version ' + __VERSION__)
    parser.add_argument('-p', '--port', type=int, default=cfg_options['port'],
                        help='Port to listen on (default: {})'.format(cfg_options['port']))
    parser.add_argument('-l', '--logfile', type=str, default=cfg_options['logfile'],
                        help='Log file (default: stdout)')
    parser.add_argument('-r', '--responses', type=str, default=cfg_options['responses_dir'],
                        help='Directory of the response files (default: {})'.format(cfg_options['responses_dir']))
    parser.add_argument('-s', '--sensor', type=str, default=cfg_options['sensor'],
                        help='Sensor name (default: {})'.format(cfg_options['sensor']))

    args = parser.parse_args()
    return args


def mySiteLog(request):
    """
    Empty log formatter to suppress the normal logging of
    the web requests, since we'll be doing our own logging.
    """
    return


def set_options():
    cfg_options = {}

    cfg_options['port'] = CONFIG.getint('honeypot', 'listen_port', fallback=9200)
    log_name = CONFIG.get('honeypot', 'log_filename', fallback='')
    if log_name:
        logdir = CONFIG.get('honeypot', 'log_path', fallback='')
        mkdir(logdir)
        cfg_options['logfile'] = join(logdir, log_name)
    else:
        cfg_options['logfile'] = None
    cfg_options['sensor'] = CONFIG.get('honeypot', 'sensor_name', fallback=gethostname())
    cfg_options['responses_dir'] = CONFIG.get('honeypot', 'responses_dir', fallback='responses')

    args = get_options(cfg_options)

    cfg_options['port'] = args.port
    cfg_options['logfile'] = args.logfile
    cfg_options['sensor'] = args.sensor
    cfg_options['public_ip_url'] = CONFIG.get('honeypot', 'public_ip_url', fallback='https://ident.me')
    cfg_options['public_ip'] = get_public_ip(cfg_options['public_ip_url'])
    cfg_options['cluster_name'] = CONFIG.get('honeypot', 'cluster_name', fallback='elasticsearch')
    cfg_options['host_name'] = CONFIG.get('honeypot', 'host_name', fallback='elk')
    cfg_options['instance_name'] = CONFIG.get('honeypot', 'instance_name', fallback='Green Goblin')
    cfg_options['spoofed_version'] = CONFIG.get('honeypot', 'spoofed_version', fallback='1.4.1')
    cfg_options['build'] = CONFIG.get('honeypot', 'build', fallback='89d3241')
    cfg_options['total_processors'] = CONFIG.getint('honeypot', 'total_processors', fallback='12')
    cfg_options['total_cores'] = CONFIG.getint('honeypot', 'total_cores', fallback='24')
    cfg_options['total_sockets'] = CONFIG.getint('honeypot', 'total_sockets', fallback='48')
    cfg_options['mac_address'] = CONFIG.get('honeypot', 'mac_address', fallback='08:01:c7:3F:15:DD')
    cfg_options['report_public_ip'] = CONFIG.getboolean('honeypot', 'report_public_ip', fallback=False)

    return cfg_options


def main():
    cfg_options = set_options()

    set_logger(cfg_options)

    log.msg(__description__ + ' by ' + __author__)

    cfg_options['output_plugins'] = import_plugins(cfg_options)

    site = Site(Index(cfg_options))
    site.log = mySiteLog
    log.msg('Listening on port {}.'.format(cfg_options['port']))
    reactor.listenTCP(cfg_options['port'], site)    # pylint: disable=no-member
    reactor.run()   # pylint: disable=no-member
    log.msg('Shutdown requested, exiting...')
    stop_plugins(cfg_options)


if __name__ == '__main__':
    main()
