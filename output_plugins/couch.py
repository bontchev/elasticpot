
from core import output
from core.config import CONFIG
from core.tools import geolocate

from couchdb import Server
from geoip2.database import Reader

from twisted.python import log

class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_couch', 'host', fallback='localhost')
        port = CONFIG.getint('output_couch', 'port', fallback=5984)
        username = CONFIG.get('output_couch', 'username', fallback='elasticpot', raw=True)
        password = CONFIG.get('output_couch', 'password', fallback='', raw=True)
        db_name = CONFIG.get('output_couch', 'database', fallback='elasticpot')

        try:
            couchserver = Server('http://{}:{}@{}:{}'.format(username, password, host, port))

            if db_name in couchserver:
                self.couch_db = couchserver[db_name]
            else:
                self.couch_db = couchserver.create(db_name)
        except Exception as e:
            log.err('output_couch: Error: {}'.format(e))

        self.geoip = CONFIG.getboolean('output_couch', 'geoip', fallback=True)

        if self.geoip:
            geoipdb_city_path = CONFIG.get('output_couch', 'geoip_citydb', fallback='data/GeoLite2-City.mmdb')
            geoipdb_asn_path = CONFIG.get('output_couch', 'geoip_asndb', fallback='data/GeoLite2-ASN.mmdb')
            try:
                self.reader_city = Reader(geoipdb_city_path)
            except:
                log.err('Failed to open City GeoIP database {}'.format(geoipdb_city_path))

            try:
                self.reader_asn = Reader(geoipdb_asn_path)
            except:
                log.err('Failed to open ASN GeoIP database {}'.format(geoipdb_asn_path))

    def stop(self):
        if self.geoip:
            if self.reader_city is not None:
                self.reader_city.close()
            if self.reader_asn is not None:
                self.reader_asn.close()

    def write(self, event):
        if self.geoip:
            country, country_code, city, org, asn_num = geolocate(event['src_ip'], self.reader_city, self.reader_asn)
            event['country'] = country
            event['country_code'] = country_code
            event['city'] = city
            event['org'] = org
            event['asn'] = asn_num

        try:
            self.couch_db.save(event)
        except Exception as e:
            log.err('output_couch: Error: {}'.format(e))
