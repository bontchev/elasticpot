
import psycopg2

from core import output
from core.config import CONFIG
from core.tools import geolocate

from hashlib import sha256
from geoip2.database import Reader

from twisted.python import log


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_postgres', 'host')
        port = CONFIG.getint('output_postgres', 'port', fallback=5432)
        username = CONFIG.get('output_postgres', 'username')
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

        self.curr = conn.cursor()

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
        cur.close()
        conn.close()
        if self.geoip:
            if self.reader_city is not None:
                self.reader_city.close()
            if self.reader_asn is not None:
                self.reader_asn.close()

    def write(self, event):
        self.connect_event(event)

    def simple_query(self, sql, args):
        if self.debug:
            if len(args):
                log.msg('output_postgres: postgres query: {} {}'.format(sql, repr(args)))
            else:
                log.msg('output_postgres: postgres query: {}'.format(sql))
        try:
            if len(args):
                self.cur.execute(sql, args)
            else:
                self.cur.execute(sql)
            result = self.cur.fetchmany()
        except Exception as e:
            log.msg('output_postgres: postgres Error: {}'.format(e))
            result = None
        return result

    def get_id(self, table, column, entry):
        r = self.simple_query("SELECT id FROM {} WHERE {} = %s".format(table, column), (entry, ))
        if r:
            id = r[0][0]
        else:
            self.simple_query("INSERT INTO {} ({}) VALUES (%s)".format(table, column), (entry, ))
            r = self.simple_query('SELECT LAST_INSERT_ROWID()', ())
            if r:
                id = int(r[0][0])
            else:
                id = 0
        return id

    def get_hashed_id(self, table, entry):
        sc = entry.strip()
        shasum = sha256(sc).hexdigest()
        r = self.simple_query("SELECT id FROM {} WHERE inputhash = %s".format(table), (shasum, ))
        if r:
            id = int(r[0][0])
        else:
            self.simple_query("INSERT INTO {} (input, inputhash) VALUES (%s, %s)".format(table),
                              (sc.decode('utf-8').encode('unicode_escape'), shasum, ))
            r = self.simple_query('SELECT LAST_INSERT_ROWID()', ())
            if r:
                id = int(r[0][0])
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
            payload_id = 'NULL'
        if 'user_agent' in event:
            agent_id = self.get_id('user_agents', 'user_agent', event['user_agent'])
        else:
            agent_id = 'NULL'
        if 'content_type' in event:
            content_id = self.get_id('content_types', 'content_type', event['content_type'])
        else:
            content_id = 'NULL'
        if 'accept_language' in event:
            language_id = self.get_id('accept_languages', 'accept_language', event['accept_language'])
        else:
            language_id = 'NULL'
        sensor_id = self.get_id('sensors', 'name', event['sensor'])

        self.simple_query("""
            INSERT INTO connections (
                timestamp, ip, remote_port, request, url,
                payload, message, user_agent, content_type,
                accept_language, local_host, local_port, sensor)
            VALUES (DATETIME(%s, 'unixepoch', 'localtime'), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (event['unixtime'], remote_ip, event['src_port'], event['request'], path_id, payload_id,
            message_id, agent_id, content_id, language_id, event['dst_ip'], event['dst_port'], sensor_id, ))

        if self.geoip:
            country, country_code, city, org, asn_num = geolocate(remote_ip, self.reader_city, self.reader_asn)
            result = self.simple_query("""
                INSERT INTO geolocation (ip, country_name, country_iso_code, city_name, org, org_asn)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (remote_ip, country, country_code, city, org, asn_num, ))
            if result is None:
                self.simple_query("""
                    UPDATE geolocation SET
                        country_name = %s,
                        country_iso_code = %s,
                        city_name = %s,
                        org = %s,
                        org_asn = %s
                    WHERE ip = %s
                    """,
                    (country, country_code, city, org, asn_num, remote_ip, ))
