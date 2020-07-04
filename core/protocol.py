
from os import sep
from time import time
from random import randint
from json import dumps, load

from core.tools import decode, get_local_ip, get_utc_time, logger, resolve_url, write_event

from twisted.python import log
from twisted.web.resource import Resource

try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote


class Index(Resource):
    isLeaf = True
    page_cache = {
        'aliases.json': '',
        'banner.json': '',
        'cluster.json': '',
        'clusterstore.json': '',
        'error.json': '',
        'index1long.json': '',
        'index1short.json': '',
        'index2long.json': '',
        'index2short.json': '',
        'indices.txt': '',
        'nodes.json': '',
        'nodes2.json': '',
        'nodes2.txt': '',
        'mapping.json': '',
        'pluginhead.html': '',
        'search.json': '',
        'search2.json': '',
        'settings.json': '',
        'stats1.json': '',
        'stats2.json': '',
        'store.json': ''
    }

    def __init__(self, options):
        self.cfg = options

    def render_HEAD(self, request):
        path = unquote(decode(request.uri))
        collapsed_path = resolve_url(path)

        logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

        event = {
            'eventid': 'elasticpot.recon',
            'message': 'Head scan',
            'url': collapsed_path
        }

        self.report_event(request, event)

        return self.send_response(request)

    def render_GET(self, request):
        path = unquote(decode(request.uri))
        collapsed_path = resolve_url(path)
        url_path = list(filter(None, collapsed_path.split('/')))

        logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

        event = {
            'eventid': 'elasticpot.recon',
            'message': 'Scan',
            'url': collapsed_path
        }

        self.report_event(request, event)

        if len(url_path) == 0:
            # /
            return self.fake_banner(request)
        elif url_path[0].startswith('_nodes'):
            # /_nodes
            # /_nodes/stats
            return self.fake_nodes(request)
            # Not handled:
            # /_nodes/_local
        elif url_path[0].startswith('_search'):
            # /_search
            # /_search?pretty
            # /_search?source
            return self.fake_search(request)
        elif url_path[0] == '_stats':
            # /_stats
            # /_stats/
            # /_stats/indexing
            return self.fake_stats1(request)
        elif url_path[0] == '_mapping':
            # /_mapping
            return self.fake_mapping(request)
        elif url_path[0].startswith('favicon.'):
            # /favicon.ico
            return self.send_response(request)
        elif 'alias' in collapsed_path:
            # /%2A/_alias
            # /_aliases
            # /_aliases?pretty
            # /_aliases?pretty=true
            # /_cat/aliases?format=json&h=alias
            return self.fake_alias(request)
        elif url_path[-1].startswith('_settings'):
            # /*/_settings
            return self.fake_settings(request)
            # Not handled (should return settings.json too):
            # /*
        elif len(url_path) >= 2:
            if url_path[0] == '_cat':
                if url_path[1].startswith('indices'):
                    # /_cat/indices
                    # /_cat/indices?pretty
                    # /_cat/indices?v
                    # /_cat/indices?format=json
                    # /_cat/indices?format=json&h=index
                    # /_cat/indices?format=text&v=true
                    # /_cat/indices?bytes=b&format=json
                    # /_cat/indices/1cf0aa9d61f185b59f643939f862c01f89b21360?bytes=b
                    # /_cat/indices/db18744ea5570fa9bf868df44fecd4b58332ff24?bytes=b
                    has_header = 'v' in url_path[1]
                    json_formatted = 'format=json' in url_path[1]
                    terse = 'h=index' in url_path[1]
                    return self.fake_indices(request, has_header, json_formatted, terse)
                elif url_path[1].startswith('nodes'):
                    # /_cat/nodes
                    # /_cat/nodes?format=json
                    # /_cat/nodes?h=name,id,i,po,v,m,u,dt,du,r,gto
                    json_formatted = 'format=json' in url_path[1]
                    return self.fake_nodes2(request, json_formatted)
                else:
                    return self.fake_error(request, url_path[0])
            elif url_path[-1] == 'store' or url_path[-2] == 'store':
                # /_all/_stats/store
                # /_stats/store
                # /_stats/store/?pretty&human&level=cluster
                cluster = 'level=cluster' in collapsed_path
                pretty = 'pretty' in collapsed_path
                return self.fake_store(request, cluster, pretty)
            elif url_path[0] == '_plugin' and url_path[1].startswith('head'):
                # /_plugin/head
                return self.fake_plugins(request)
            elif url_path[-1].startswith('_search'):
                # /1cf0aa9d61f185b59f643939f862c01f89b21360/_search?pretty=true&q=*:*
                # /1cf0aa9d61f185b59f643939f862c01f89b21360/_search?size=5000
                # /db18744ea5570fa9bf868df44fecd4b58332ff24/_search?pretty=true&q=*:*
                # /db18744ea5570fa9bf868df44fecd4b58332ff24/_search?size=5000
                json_formatted = 'pretty' in url_path[-1]
                index = url_path[0]
                return self.fake_search2(request, index, json_formatted)
            elif url_path[0] == '_cluster':
                if url_path[1].startswith('health'):
                    # /_cluster/health
                    return self.fake_cluster(request)
                elif url_path[1] == 'stats':
                    # /_cluster/stats
                    return self.fake_stats2(request)
                # Not handled:
                # /_cluster/state
                else:
                    return self.fake_error(request, url_path[0])
            else:
                return self.fake_error(request, url_path[0])
            #  Not handled:
            # /evox/about
            # /stalker_portal/c/
            # /streaming/clients_live.php
            # /streaming/QxAvEzlK.php
            # /streaming/uo6jIDnf.php
            #  These should return
            #  {"error": "Incorrect HTTP method for uri [{path}] and method [GET], allowed: [POST]","status": 405}
        else:
            # /api.php
            # /client_area/
            # /HNAP1
            # /index/_search?pretty=true&q=*:*
            # /login.php
            # /Nmap/folder/check1592730162
            # /nmaplowercheck1592730162
            # /NmapUpperCheck1592730162
            # /nice%20ports,/Trinity.txt.bak
            # /robots.txt
            # /sitemap.xml
            # /stalker_portal/c/version.js
            # /stat
            # /streaming
            # /system_api.php
            # /4e5e5d7364f443e28fbf0d3ae744a59a
            # /?c=4e5e5d7364f443e28fbf0d3ae744a59a
            return self.fake_error(request, url_path[0])
            #  Not handled:
            # /c
            #  This should return:
            #  {"error":{"root_cause":[{"type":"illegal_argument_exception","reason":"request [/] contains unrecognized parameter: [c]"}],
            #  "type":"illegal_argument_exception","reason":"request [/] contains unrecognized parameter: [c]"},"status":400}

    def render_POST(self, request):
        path = unquote(decode(request.uri))

        logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

        if request.getHeader('Content-Length'):
            collapsed_path = resolve_url(path)
            content_length = int(request.getHeader('Content-Length'))
            if content_length > 0:
                post_data = decode(request.content.read())
                logger(request, 'INFO', 'POST body: {}'.format(post_data))
                event = {
                    'eventid': 'elasticpot.attack',
                    'message': 'Exploit',
                    'payload': post_data,
                    'url': path
                }

                self.report_event(request, event)

                # /_search
                # /_search?pretty
                # /_search?source
                # /1cf0aa9d61f185b59f643939f862c01f89b21360/_search
                # /db18744ea5570fa9bf868df44fecd4b58332ff24/_search
                if '/_search' in collapsed_path:
                    return self.fake_search(request)

        # Not handled:
        # /website/blog/
        # /info/info
        # /_sql?format=json
        # /sdk
        # send empty response as we're now done
        return self.send_response(request)

    def fake_banner(self, request):
        response = self.get_json('banner.json')
        response['name'] = self.cfg['instance_name']
        response['cluster_name'] = self.cfg['cluster_name']
        response['version']['number'] = self.cfg['spoofed_version']
        page = dumps(response, indent=2, separators=(',', ' : '))
        return self.send_response(request, page)

    def fake_indices(self, request, has_header, json_formatted, terse):
        if json_formatted:
            if terse:
                index1 = self.get_page('index1short.json')
                index2 = self.get_page('index2short.json')
            else:
                index1 = self.get_page('index1long.json')
                index2 = self.get_page('index2long.json')
            page = '[{},{}]'.format(index1, index2)
        else:
            page = self.get_page('indices.txt')
            if has_header:
                header = 'health status index                                    uuid                   pri rep docs.count docs.deleted store.size pri.store.size'
                page = header + '\n' + page
        return self.send_response(request, page)

    def fake_cluster(self, request):
        response = self.get_json('cluster.json')
        response['cluser_name'] = self.cfg['cluster_name']
        page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_alias(self, request):
        page = self.get_page('aliases.json')
        return self.send_response(request, page)

    def fake_nodes(self, request):
        public_ip = decode(self.cfg['public_ip'])
        node_name = 'x1JG6g9PRHy6ClCOO2-C4g'
        response = self.get_json('nodes.json')
        response['cluster_name'] = self.cfg['cluster_name']
        response['nodes'][node_name]['name'] = self.cfg['instance_name']
        response['nodes'][node_name]['transport_address'] = 'inet[/{}:9300]'.format(public_ip)
        response['nodes'][node_name]['host'] = self.cfg['host_name']
        response['nodes'][node_name]['ip'] = public_ip
        response['nodes'][node_name]['version'] = self.cfg['spoofed_version']
        response['nodes'][node_name]['build'] = self.cfg['build']
        response['nodes'][node_name]['http_address'] = 'inet[/{}:9200]'.format(public_ip)
        response['nodes'][node_name]['os']['available_processors'] = self.cfg['total_processors']
        response['nodes'][node_name]['os']['cpu']['total_cores'] = self.cfg['total_cores']
        response['nodes'][node_name]['os']['cpu']['total_sockets'] = self.cfg['total_sockets']
        response['nodes'][node_name]['process']['id'] = randint(100, 40000)
        response['nodes'][node_name]['network']['primary_interface']['address'] = public_ip
        response['nodes'][node_name]['network']['primary_interface']['mac_address'] = self.cfg['mac_address']
        response['nodes'][node_name]['transport']['publish_address'] = 'inet[/{}:9200]'.format(public_ip)
        response['nodes'][node_name]['http']['publish_address'] = 'inet[/{}:9200]'.format(public_ip)
        page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_nodes2(self, request, json_formatted):
        public_ip = decode(self.cfg['public_ip'])
        if json_formatted:
            response = self.get_json('nodes2.json')
            response['ip'] = public_ip
            page = '[{}]'.format(dumps(response, separators=(',', ':')))
        else:
            page = '{} {}'.format(public_ip, self.get_page('nodes2.txt'))
        return self.send_response(request, page)

    def fake_search(self, request):
        shards = randint(5, 50)
        response = self.get_json('search.json')
        response['took'] = randint(1, 25)
        response['_shards']['total'] = shards
        response['_shards']['successful'] = shards
        page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_search2(self, request, index, json_formatted):
        response = self.get_json('search2.json')
        response['hits']['hits'][0]['_index'] = index
        if json_formatted:
            page = dumps(response, indent=2, separators=(',', ' : '))
        else:
            page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_plugins(self, request):
        page = self.get_page('pluginhead.html')
        return self.send_response(request, page)

    def fake_stats1(self, request):
        page = self.get_page('stats1.json')
        return self.send_response(request, page)

    def fake_stats2(self, request):
        response = self.get_json('stats2.json')
        response['cluster_name'] = self.cfg['cluster_name']
        response['nodes']['os']['allocated_processors'] = self.cfg['total_processors']
        response['nodes']['os']['available_processors'] = self.cfg['total_processors']
        response['timestamp'] = int(time())
        page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_mapping(self, request):
        page = self.get_page('mapping.json')
        return self.send_response(request, page)

    def fake_settings(self, request):
        page = self.get_page('settings.json')
        return self.send_response(request, page)

    def fake_store(self, request, cluster, pretty):
        if cluster:
            response = self.get_json('clusterstore.json')
        else:
            response = self.get_json('store.json')
        if pretty:
            page = dumps(response, indent=2, separators=(',', ' : '))
        else:
            page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def fake_error(self, request, index):
        response = self.get_json('error.json')
        response['error']['root_cause'][0]['reason'] = 'no such index [{}]'.format(index)
        response['error']['root_cause'][0]['resource.id'] = index
        response['error']['root_cause'][0]['index'] = index
        response['error']['reason'] = 'no such index [{}]'.format(index)
        response['error']['resource.id'] = index
        response['error']['index'] = index
        page = dumps(response, separators=(',', ':'))
        return self.send_response(request, page)

    def report_event(self, request, event):
        unix_time = time()
        human_time = get_utc_time(unix_time)
        local_ip = get_local_ip()
        event['timestamp'] = human_time
        event['unixtime'] = unix_time
        event['src_ip'] = request.getClientAddress().host
        event['src_port'] = request.getClientAddress().port
        event['dst_port'] = self.cfg['port']
        event['sensor'] = self.cfg['sensor']
        event['request'] = decode(request.method)
        user_agent = request.getHeader('User-Agent')
        if user_agent:
            event['user_agent'] = user_agent
        content_type = request.getHeader('Content-Type')
        if content_type:
            event['content_type'] = content_type
        accept_language = request.getHeader('Accept-Language')
        if accept_language:
            event['accept_language'] = accept_language
        event['dst_ip'] = self.cfg['public_ip'] if self.cfg['report_public_ip'] else local_ip
        write_event(event, self.cfg)

    def get_json(self, page):
        if page not in self.page_cache:
            log.msg('Missing JSON file: "{}".'.format(page))
            return {}
        if self.page_cache[page] == '':
            with open('{}{}{}'.format(self.cfg['responses_dir'], sep, page), 'r') as f:
                self.page_cache[page] = load(f)
        return self.page_cache[page]

    # a simple wrapper to cache files from "responses" folder
    def get_page(self, page):
        if page not in self.page_cache:
            log.msg('Missing file: "{}".'.format(page))
            if page.lower().endswith('.json'):
                return '{}'
            else:
                return ''
        # if page is not in cache, load it from file
        if self.page_cache[page] == '':
            if page.lower().endswith('.json'):
                self.page_cache[page] = dumps(self.get_json(page), separators=(',', ':'))
            else:
                with open('{}{}{}'.format(self.cfg['responses_dir'], sep, page), 'r') as f:
                    self.page_cache[page] = f.read()
        return self.page_cache[page]

    # overload base class's send_response() to set appropriate headers and server version
    def send_response(self, request, page=''):
        request.setHeader('Server', 'Apache')
        request.setHeader('Content-Length', str(len(page)))
        request.setHeader('Content-Type', 'application/json; charset=UTF-8')
        request.setHeader('Connection', 'Close')
        return '{}'.format(page).encode('utf-8')
