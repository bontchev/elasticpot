
from core import output
from core.config import CONFIG
from core.tools import geolocate

from pymongo import MongoClient
from geoip2.database import Reader

from twisted.python import log

class Output(output.Output):

    def insert_one(self, collection, event):
        try:
            return collection.insert_one(event).inserted_id
        except Exception as e:
            log.msg('output_mongodb: Error: {}'.format(e))
            return None

    def start(self):
        host = CONFIG.get('output_mongodb', 'host', fallback='localhost')
        port = CONFIG.getint('output_mongodb', 'port', fallback=27017)
        username = CONFIG.get('output_mongodb', 'username', fallback='', raw=True)
        password = CONFIG.get('output_mongodb', 'password', fallback='', raw=True)
        db_name = CONFIG.get('output_mongodb', 'database', fallback='elasticpot')
        db_addr = CONFIG.get('output_mongodb', 'connection_string')
        db_addr = db_addr.format(username, password, host, port, db_name)

        self.geoip = CONFIG.getboolean('output_mongodb', 'geoip', fallback=True)

        try:
            self.mongo_client = MongoClient(db_addr)
            self.mongo_db = self.mongo_client[db_name]
            # Define Collections
            self.col_connections = self.mongo_db['connections']
            if self.geoip:
                self.col_geolocation = self.mongo_db['geolocation']
        except Exception as e:
            log.msg('output_mongodb: Error: {}'.format(e))

        if self.geoip:
            geoipdb_city_path = CONFIG.get('output_mongodb', 'geoip_citydb', fallback='data/GeoLite2-City.mmdb')
            geoipdb_asn_path = CONFIG.get('output_mongodb', 'geoip_asndb', fallback='data/GeoLite2-ASN.mmdb')
            try:
                self.reader_city = Reader(geoipdb_city_path)
            except:
                log.msg('Failed to open City GeoIP database {}'.format(geoipdb_city_path))

            try:
                self.reader_asn = Reader(geoipdb_asn_path)
            except:
                log.msg('Failed to open ASN GeoIP database {}'.format(geoipdb_asn_path))

    def stop(self):
        self.mongo_client.close()
        if self.geoip:
            if self.reader_city is not None:
                self.reader_city.close()
            if self.reader_asn is not None:
                self.reader_asn.close()

    def write(self, event):
        self.insert_one(self.col_connections, event)
        if self.geoip:
            remote_ip = event['src_ip']
            if not self.col_geolocation.find_one({'ip': remote_ip}):
                country, country_code, city, org, asn_num = geolocate(remote_ip, self.reader_city, self.reader_asn)
                geo_entry = {
                    'ip': remote_ip,
                    'country': country,
                    'country_code': country_code,
                    'city': city,
                    'org': org,
                    'asn': asn_num
                }
                self.insert_one(self.col_geolocation, geo_entry)
