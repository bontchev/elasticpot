
from core import output
from core.config import CONFIG
from core.tools import geolocate

from elasticsearch import Elasticsearch, NotFoundError


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_elastic', 'host', fallback='localhost')
        port = CONFIG.getint('output_elastic', 'port', fallback=9200)
        username = CONFIG.get('output_elastic', 'username', fallback=None)
        password = CONFIG.get('output_elastic', 'password', fallback=None)

        use_ssl = CONFIG.getboolean('output_elastic', 'ssl', fallback=False)

        self.index = CONFIG.get('output_elastic', 'index', fallback='elasticpot')
        self.type = CONFIG.get('output_elastic', 'type', fallback='_doc')
        self.pipeline = CONFIG.get('output_elastic', 'pipeline', fallback='geoip')

        options = {}
        # connect
        if (username is not None) and (password is not None):
            options['http_auth'] = (username, password)
        if use_ssl:
            options['scheme'] = 'https'
            options['use_ssl'] = use_ssl
            options['ssl_show_warn'] = False
            options['verify_certs'] = CONFIG.getboolean('output_elastic', 'verify_certs', fallback=True)
            if options['verify_certs']:
                options['ca_certs'] = CONFIG.get('output_elastic', 'ca_certs')

        # connect
        self.es = Elasticsearch('{}:{}'.format(host, port), **options)

        if not self.es.indices.exists(index=self.index):
            # create index
            self.es.indices.create(index=self.index)

        # ensure geoip pipeline is well set up
        if self.pipeline == 'geoip':
            # create a new feature if it does not exist yet
            self.check_geoip_mapping()
            # ensure the geoip pipeline is setup
            self.check_geoip_pipeline()

    def check_geoip_mapping(self):
        """
        This function ensures that the right mapping is set up
        to convert source ip (src_ip) into geo data.
        """
        if self.es.indices.exists(index=self.index):
            # Add mapping (to add geo field -> for geoip)
            # The new feature is named 'geo'.
            # You can put mappings several times, if it exists the
            # PUT requests will be ignored.
            body = {
                'properties':
                {
                    'geo':
                    {
                        'properties':
                        {
                            'location':
                            {
                                'type': 'geo_point'
                            }
                        }
                    }
                }
            }
            self.es.indices.put_mapping(index=self.index, body=body)

    def check_geoip_pipeline(self):
        """
        This function aims to set at least a geoip pipeline
        to map IP to geo locations
        """
        try:
            # check if the geoip pipeline exists. An error
            # is raised if the pipeline does not exist
            self.es.ingest.get_pipeline(self.pipeline)
        except NotFoundError:
            # geoip pipeline
            body = {
                'description': 'Add geoip info',
                'processors':
                [
                    {
                        'geoip':
                        {
                            'field': 'src_ip',  # input field of the pipeline (source address)
                            'target_field': 'geo',  # output field of the pipeline (geo data)
                            'database_file': 'GeoLite2-City.mmdb',
                        }
                    }
                ]
            }
            self.es.ingest.put_pipeline(id=self.pipeline, body=body)

    def stop(self):
        pass

    def write(self, entry):
        self.es.index(index=self.index, doc_type=self.type, body=entry)
