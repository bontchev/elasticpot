
from sys import version_info
from os import makedirs, path
from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM

from core.config import CONFIG

from twisted.python import log

try:
    from urllib.request import urlopen
    from urllib.parse import urlsplit, urlunsplit
except ImportError:
    from urllib import urlopen
    from urlparse import urlsplit, urlunsplit


def decode(x):
    if version_info[0] < 3:
        return x
    else:
        return x.decode('utf-8')


def get_utc_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).isoformat() + 'Z'


def get_public_ip(ip_reporter):
    if version_info[0] < 3:
        return urlopen(ip_reporter).read().decode('latin1', errors='replace').encode('utf-8')
    else:
        return urlopen(ip_reporter).read()


def get_local_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def resolve_url(url):
    parts = list(urlsplit(url))
    segments = parts[2].split('/')
    segments = [segment + '/' for segment in segments[:-1]] + [segments[-1]]
    resolved = []
    for segment in segments:
        if segment in ('../', '..'):
            if resolved[1:]:
                resolved.pop()
        elif segment not in ('./', '.'):
            resolved.append(segment)
    parts[2] = ''.join(resolved)
    return urlunsplit(parts)


def logger(request, log_level, msg):
    log.msg('[{}] ({}:{}): {}'.format(log_level, request.getClientAddress().host, request.getClientAddress().port, msg))


def write_event(event, cfg):
    output_plugins = cfg['output_plugins']
    for plugin in output_plugins:
        try:
            plugin.write(event)
        except Exception as e:
            log.err(e)
            continue


def mkdir(dir_path):
    if not dir_path:
        return
    if path.exists(dir_path) and path.isdir(dir_path):
        return
    makedirs(dir_path)


def import_plugins(cfg):
    # Load output modules (inspired by the Cowrie honeypot)
    log.msg('Loading the plugins...')
    output_plugins = []
    general_options = cfg
    for x in CONFIG.sections():
        if not x.startswith('output_'):
            continue
        if CONFIG.getboolean(x, 'enabled') is False:
            continue
        engine = x.split('_')[1]
        try:
            output = __import__('output_plugins.{}'.format(engine),
                                globals(), locals(), ['output'], 0).Output(general_options)
            output_plugins.append(output)
            log.msg('Loaded output engine: {}'.format(engine))
        except ImportError as e:
            log.err('Failed to load output engine: {} due to ImportError: {}'.format(engine, e))
        except Exception as e:
            log.err('Failed to load output engine: {} {}'.format(engine, e))
    return output_plugins


def stop_plugins(cfg):
    log.msg('Stoping the plugins...')
    for plugin in cfg['output_plugins']:
        try:
            plugin.stop()
        except Exception as e:
            log.err(e)
            continue


def geolocate(remote_ip, reader_city, reader_asn):
    try:
        response_city = reader_city.city(remote_ip)
        city = response_city.city.name
        if city is None:
            city = ''
        else:
            city = decode(city.encode('utf-8'))
        country = response_city.country.name
        if country is None:
            country = ''
            country_code = ''
        else:
            country = decode(country.encode('utf-8'))
            country_code = decode(response_city.country.iso_code.encode('utf-8'))
    except Exception as e:
        log.err(e)
        city = ''
        country = ''
        country_code = ''

    try:
        response_asn = reader_asn.asn(remote_ip)
        if response_asn.autonomous_system_organization is None:
            org = ''
        else:
            org = decode(response_asn.autonomous_system_organization.encode('utf-8'))

        if response_asn.autonomous_system_number is not None:
            asn_num = response_asn.autonomous_system_number
        else:
            asn_num = 0
    except Exception as e:
        log.err(e)
        org = ''
        asn_num = 0
    return country, country_code, city, org, asn_num
