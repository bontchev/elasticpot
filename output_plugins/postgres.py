
import psycopg2

from core import output
from core.config import CONFIG
from core.tools import geolocate

from hashlib import sha256
from geoip2.database import Reader

from twisted.python import log


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_postgres', 'host', fallback='localhost')
        port = CONFIG.getint('output_postgres', 'port', fallback=5432)
        username = CONFIG.get('output_postgres', 'username', fallback='elasticpot')
        password = CONFIG.get('output_postgres', 'password')
        database = CONFIG.get('output_postgres', 'database', fallback='elasticpot')
        self.debug = CONFIG.getboolean('output_postgres', 'debug', fallback=False)
        self.geoip = CONFIG.getboolean('output_postgres', 'geoip', fallback=True)

        try:
            self.conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=host,
                port=port
            )
        except Exception as e:
            log.msg(e)

        self.cur = self.conn.cursor()

        if self.geoip:
            geoipdb_city_path = CONFIG.get('output_postgres', 'geoip_citydb', fallback='data/GeoLite2-City.mmdb')
            geoipdb_asn_path = CONFIG.get('output_postgres', 'geoip_asndb', fallback='data/GeoLite2-ASN.mmdb')

            try:
                self.reader_city = Reader(geoipdb_city_path)
            except:
                log.msg('Failed to open City GeoIP database {}'.format(geoipdb_city_path))

            try:
                self.reader_asn = Reader(geoipdb_asn_path)
            except:
                log.msg('Failed to open ASN GeoIP database {}'.format(geoipdb_asn_path))

    def stop(self):
        self.cur.close()
        self.conn.close()
        if self.geoip:
            if self.reader_city is not None:
                self.reader_city.close()
            if self.reader_asn is not None:
                self.reader_asn.close()

    def write(self, event):
        self.connect_event(event)

    def simple_query(self, sql, args, returns_value=True):
        if self.debug:
            log.msg('output_postgres: postgres query: {} {}'.format(sql, repr(args)))
        result = None
        try:
            self.cur.execute(sql, args)
            if returns_value:
                result = self.cur.fetchone()
        except Exception as e:
            log.msg('output_postgres: postgres Error: {}'.format(e))
        return result

    def get_id(self, table, column, entry):
        r = self.simple_query("SELECT id FROM {} WHERE {} = %s".format(table, column), (entry, ))
        if r:
            id = int(r[0])
        else:
            r = self.simple_query("INSERT INTO {} ({}) VALUES (%s) RETURNING id".format(table, column), (entry, ))
            if r:
                id = int(r[0])
            else:
                id = 0
        return id

    def get_hashed_id(self, table, entry):
        sc = entry.strip()
        shasum = sha256(sc).hexdigest()
        r = self.simple_query("SELECT id FROM {} WHERE inputhash = %s".format(table), (shasum, ))
        if r:
            id = int(r[0])
        else:
            r = self.simple_query("INSERT INTO {} (input, inputhash) VALUES (%s, %s) RETURNING id".format(table),
                                  (sc.decode('utf-8').encode('unicode_escape'), shasum, ))
            if r:
                id = int(r[0])
            else:
                id = 0
        return id

    def connect_event(self, event):
        remote_ip = event['src_ip']

        path_id = self.get_id('urls', 'path', event['url'])
        message_id = self.get_id('messages', 'message', event['message'])
        if 'payload' in event:
            payload_id = self.get_hashed_id('payloads', event['payload'])
        else:
            payload_id = 0
        if 'user_agent' in event:
            agent_id = self.get_id('user_agents', 'user_agent', event['user_agent'])
        else:
            agent_id = 0
        if 'content_type' in event:
            content_id = self.get_id('content_types', 'content_type', event['content_type'])
        else:
            content_id = 0
        if 'accept_language' in event:
            language_id = self.get_id('accept_languages', 'accept_language', event['accept_language'])
        else:
            language_id = 0
        sensor_id = self.get_id('sensors', 'name', event['sensor'])

        self.simple_query("""
            INSERT INTO connections (
                time_stamp, ip, remote_port, request, url,
                payload, message, user_agent, content_type,
                accept_language, local_host, local_port, sensor)
            VALUES (to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (event['unixtime'], remote_ip, event['src_port'], event['request'], path_id, payload_id,
            message_id, agent_id, content_id, language_id, event['dst_ip'], event['dst_port'], sensor_id, ), False)

        if self.geoip:
            country, country_code, city, org, asn_num = geolocate(remote_ip, self.reader_city, self.reader_asn)
            self.simple_query("""
                INSERT INTO geolocation (ip, country_name, country_iso_code, city_name, org, org_asn)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (ip) DO UPDATE SET
                    country_name = %s,
                    country_iso_code = %s,
                    city_name = %s,
                    org = %s,
                    org_asn = %s
                """,
                (remote_ip, country, country_code, city, org, asn_num, country, country_code, city, org, asn_num, ), False)
        self.conn.commit()
