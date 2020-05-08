
from time import time
from random import randint
from json import dumps, load

from core import tools

from twisted.python import log
from twisted.web.resource import Resource

try:
    from urllib.parse import unquote
    def decode(x):
        return x.decode()
except ImportError:
    from urlparse import unquote
    def decode(x):
        return x


class Index(Resource):
    isLeaf = True
    page_cache = {
        'aliases.json': '',
        'banner.json': '',
        'cluster.json': '',
        'error.json': '',
        'index1long.json': '',
        'index1short.json': '',
        'index2long.json': '',
        'index2short.json': '',
        'indices.txt': '',
        'nodes.json': '',
        'pluginhead.html': '',
        'search.json': '',
        'stats1.json': '',
        'stats2.json': ''
    }

    def __init__(self, options):
        self.cfg = options

    def render_HEAD(self, request):
        path = unquote(decode(request.uri))
        collapsed_path = tools.resolve_url(path)

        tools.logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

        event = {
            'eventid': 'elasticpot.recon',
            'message': 'Head scan',
            'url': collapsed_path
        }

        self.report_event(request, event)

        return self.send_response(request)

    def render_GET(self, request):
        path = unquote(decode(request.uri))
        collapsed_path = tools.resolve_url(path)
        url_path = list(filter(None, collapsed_path.split('/')))

        tools.logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

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
        elif url_path[0].startswith('_search'):
            # /_search
            # /_search?pretty
            # /_search?source
            return self.fake_search(request)
        elif url_path[0] == '_stats':
            # /_stats
            return self.fake_stats1(request)
        elif url_path[0].startswith('favicon.'):
            # /favicon.ico
            return self.send_response(request)
        elif '_alias' in url_path or '_aliases' in url_path:
            # /%2A/_alias
            # /_aliases
            # /_aliases?pretty
            return self.fake_alias(request)
        elif len(url_path) >= 2:
            if url_path[0] == '_cat' and url_path[1].startswith('indices'):
                # /_cat/indices
                # /_cat/indices?pretty
                # /_cat/indices?v
                # /_cat/indices?format=json&h=index
                # /_cat/indices?bytes=b&format=json
                has_header = 'v' in url_path[1]
                json_formatted = 'format=json' in url_path[1]
                terse = 'h=index' in url_path[1]
                return self.fake_indices(request, has_header, json_formatted, terse)
            elif url_path[0] == '_plugin' and url_path[1].startswith('head'):
                # /_plugin/head
                return self.fake_plugins(request)
            elif url_path[0] == '_cluster':
                if url_path[1].startswith('health'):
                    # /_cluster/health
                    return self.fake_cluster(request)
                elif url_path[1] == 'stats':
                    # /_cluster/stats
                    return self.fake_stats2(request)
                else:
                    return self.fake_error(request, url_path[0])
            else:
                return self.fake_error(request, url_path[0])
        else:
            # /c
            # /stat
            # /nice%20ports,/Trinity.txt.bak
            return self.fake_error(request, url_path[0])

    def render_POST(self, request):
        path = unquote(decode(request.uri))

        tools.logger(request, 'INFO', '{}: {}'.format(decode(request.method), path))

        if request.getHeader('Content-Length'):
            collapsed_path = tools.resolve_url(path)
            content_length = int(request.getHeader('Content-Length'))
            if content_length > 0:
                post_data = request.content.read()
                tools.logger(request, 'INFO', 'POST body: {}'.format(decode(post_data)))
                event = {
                    'eventid': 'elasticpot.attack',
                    'message': 'Exploit',
                    'payload': post_data,
                    'url': path
                }

                self.report_event(request, event)

                if collapsed_path.startswith('/_search'):
                    return self.fake_search(request)

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

    def fake_search(self, request):
        shards = randint(5, 50)
        response = self.get_json('search.json')
        response['took'] = randint(1, 25)
        response['_shards']['total'] = shards
        response['_shards']['successful'] = shards
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
        human_time = tools.get_utc_time(unix_time)
        local_ip = tools.get_local_ip()
        event['timestamp'] = human_time
        event['unixtime'] = unix_time
        event['src_ip'] = request.getClientAddress().host
        event['src_port'] = request.getClientAddress().port
        event['dst_ip'] = local_ip
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
        tools.write_event(event, self.cfg)

    def get_json(self, page):
        if page not in self.page_cache:
            return {}
        if self.page_cache[page] == '':
            with open('responses/{}'.format(page), 'r') as f:
                self.page_cache[page] = load(f)
        return self.page_cache[page]

    # a simple wrapper to cache files from "responses" folder
    def get_page(self, page):
        if page not in self.page_cache:
            return ''
        # if page is not in cache, load it from file
        if self.page_cache[page] == '':
            if page.endswith('.json'):
                self.page_cache[page] = dumps(self.get_json(page), separators=(',', ':'))
            else:
                with open('responses/{}'.format(page), 'r') as f:
                    self.page_cache[page] = f.read()
        return self.page_cache[page]

    # overload base class's send_response() to set appropriate headers and server version
    def send_response(self, request, page=''):
        request.setHeader('Server', 'Apache')
        request.setHeader('Content-Length', str(len(page)))
        request.setHeader('Content-Type', 'application/json; charset=UTF-8')
        request.setHeader('Connection', 'Close')
        return '{}'.format(page).encode('utf-8')
