
from json import dumps

from core import output
from core.config import CONFIG

from hpfeeds.twisted import ClientSessionService

from twisted.internet import endpoints, reactor, ssl

class Output(output.Output):

    def start(self):
        self.channel = CONFIG.get('output_hpfeed', 'channel', fallback='elasticpot')

        if CONFIG.has_option('output_hpfeed', 'endpoint'):
            endpoint = CONFIG.get('output_hpfeed', 'endpoint')
        else:
            server = CONFIG.get('output_hpfeed', 'server')
            port = CONFIG.getint('output_hpfeed', 'port')

            if CONFIG.has_option('output_hpfeed', 'tlscert'):
                with open(CONFIG.get('output_hpfeed', 'tlscert')) as fp:
                    authority = ssl.Certificate.loadPEM(fp.read())
                options = ssl.optionsForClientTLS(server, authority)
                endpoint = endpoints.SSL4ClientEndpoint(reactor, server, port, options)
            else:
                endpoint = endpoints.HostnameEndpoint(reactor, server, port)

        ident = CONFIG.get('output_hpfeed', 'identifier', raw=True)
        secret = CONFIG.get('output_hpfeed', 'secret', raw=True)

        self.client = ClientSessionService(endpoint, ident, secret)
        self.client.startService()

    def stop(self):
        self.client.stopService()

    def write(self, event):
        self.client.publish(self.channel, dumps(event).encode('utf-8'))
