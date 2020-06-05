
import MySQLdb

from core import output
from core.config import CONFIG
from core.tools import geolocate

from hashlib import sha256
from geoip2.database import Reader

from twisted.python import log
from twisted.enterprise.adbapi import ConnectionPool


class ReconnectingConnectionPool(ConnectionPool):
    """
    Reconnecting adbapi connection pool for MySQL.
    This class improves on the solution posted at
    http://www.gelens.org/2008/09/12/reinitializing-twisted-connectionpool/
    by checking exceptions by error code and only disconnecting the current
    connection instead of all of them.
    Also see:
    http://twistedmatrix.com/pipermail/twisted-python/2009-July/020007.html
    """

    def _runInteraction(self, interaction, *args, **kw):
        try:
            return ConnectionPool._runInteraction(
                self, interaction, *args, **kw)
        except MySQLdb.OperationalError as e:   # pylint: disable=no-member
            if e.args[0] not in (2003, 2006, 2013):
                raise e
            conn = self.connections.get(self.threadID())
            self.disconnect(conn)
            # Try the interaction again
            return ConnectionPool._runInteraction(
                self, interaction, *args, **kw)


class Output(output.Output):

    def local_log(self, msg):
        if self.debug:
            log.msg(msg)

    def start(self):
        host = CONFIG.get('output_mysql', 'host', fallback='localhost')
        database = CONFIG.get('output_mysql', 'database', fallback='')
        user = CONFIG.get('output_mysql', 'username', fallback='', raw=True)
        password = CONFIG.get('output_mysql', 'password', fallback='', raw=True)
        port = CONFIG.getint('output_mysql', 'port', fallback=3306)

        self.debug = CONFIG.getboolean('output_mysql', 'debug', fallback=False)
        self.geoip = CONFIG.getboolean('output_mysql', 'geoip', fallback=True)

        try:
            self.dbh = ReconnectingConnectionPool(
                'MySQLdb',
                host=host,
                db=database,
                user=user,
                passwd=password,
                port=port,
                charset='utf8',
                use_unicode=True,
                cp_min=1,
                cp_max=1
            )
        except MySQLdb.Error as e:  # pylint: disable=no-member
            self.local_log('MySQL plugin: Error {}: {}'.format(e.args[0], e.args[1]))

        if self.geoip:
            geoipdb_city_path = CONFIG.get('output_mysql', 'geoip_citydb', fallback='')
            geoipdb_asn_path = CONFIG.get('output_mysql', 'geoip_asndb', fallback='')
            try:
                self.reader_city = Reader(geoipdb_city_path)
            except:
                self.local_log('Failed to open City GeoIP database {}'.format(geoipdb_city_path))

            try:
                self.reader_asn = Reader(geoipdb_asn_path)
            except:
                self.local_log('Failed to open ASN GeoIP database {}'.format(geoipdb_asn_path))

    def stop(self):
        if self.geoip:
            if self.reader_city is not None:
                self.reader_city.close()
            if self.reader_asn is not None:
                self.reader_asn.close()

    def write(self, event):
        """
        TODO: Check if the type (date, datetime or timestamp) of columns is appropriate for your needs and timezone
        - MySQL Documentation - The DATE, DATETIME, and TIMESTAMP Types
            (https://dev.mysql.com/doc/refman/5.7/en/datetime.html):
        "MySQL converts TIMESTAMP values from the current time zone to UTC for storage,
        and back from UTC to the current time zone for retrieval.
        (This does not occur for other types such as DATETIME.)"
        """
        self.dbh.runInteraction(self.connect_event, event)

    def simple_query(self, txn, sql, args):
        if self.debug:
            if len(args):
                self.local_log("output_mysql: MySQL query: {} {}".format(sql, repr(args)))
            else:
                self.local_log("output_mysql: MySQL query: {}".format(sql))
        try:
            if len(args):
                txn.execute(sql, args)
            else:
                txn.execute(sql)
            result = txn.fetchall()
        except Exception as e:
            self.local_log('output_mysql: MySQL Error: {}'.format(e))
            result = None
        return result

    def get_id(self, txn, table, column, entry):
        r = self.simple_query(txn, "SELECT `id` FROM `{}` WHERE `{}` = %s".format(table, column), (entry, ))
        if r:
            id = r[0][0]
        else:
            self.simple_query(txn, "INSERT INTO `{}` (`{}`) VALUES (%s)".format(table, column), (entry, ))
            r = self.simple_query(txn, 'SELECT LAST_INSERT_ID()', ())
            if r:
                id = int(r[0][0])
            else:
                id = 0
        return id

    def get_hashed_id(self, txn, table, entry):
        sc = entry.strip()
        shasum = sha256(sc).hexdigest()
        r = self.simple_query(txn, "SELECT `id` FROM `{}` WHERE `inputhash` = %s".format(table), (shasum, ))
        if r:
            id = int(r[0][0])
        else:
            self.simple_query(txn, "INSERT INTO `{}` (`input`, `inputhash`) VALUES (%s, %s)".format(table),
                              (sc.decode('utf-8').encode('unicode_escape'), shasum, ))
            r = self.simple_query(txn, 'SELECT LAST_INSERT_ID()', ())
            if r:
                id = int(r[0][0])
            else:
                id = 0
        return id

    def connect_event(self, txn, event):
        remote_ip = event['src_ip']

        path_id = self.get_id(txn, 'urls', 'path', event['url'])
        message_id = self.get_id(txn, 'messages', 'message', event['message'])
        if 'payload' in event:
            payload_id = self.get_hashed_id(txn, 'payloads', event['payload'])
        else:
            payload_id = 'NULL'
        if 'user_agent' in event:
            agent_id = self.get_id(txn, 'user_agents', 'user_agent', event['user_agent'])
        else:
            agent_id = 'NULL'
        if 'content_type' in event:
            content_id = self.get_id(txn, 'content_types', 'content_type', event['content_type'])
        else:
            content_id = 'NULL'
        if 'accept_language' in event:
            language_id = self.get_id(txn, 'accept_languages', 'accept_language', event['accept_language'])
        else:
            language_id = 'NULL'
        sensor_id = self.get_id(txn, 'sensors', 'name', event['sensor'])

        self.simple_query(txn, """
            INSERT INTO `connections` (
                `timestamp`, `ip`, `remote_port`, `request`, `url`,
                `payload`, `message`, `user_agent`, `content_type`,
                `accept_language`, `local_host`, `local_port`, `sensor`)
            VALUES (FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (event['unixtime'], remote_ip, event['src_port'], event['request'], path_id, payload_id,
            message_id, agent_id, content_id, language_id, event['dst_ip'], event['dst_port'], sensor_id, ))

        if self.geoip:
            country, country_code, city, org, asn_num = geolocate(remote_ip, self.reader_city, self.reader_asn)
            self.simple_query(txn, """
                INSERT INTO `geolocation` (`ip`, `country_name`, `country_iso_code`, `city_name`, `org`, `org_asn`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `country_name` = %s,
                    `country_iso_code` = %s,
                    `city_name` = %s,
                    `org` = %s,
                    `org_asn` = %s
                """,
                (remote_ip, country, country_code, city, org, asn_num, country, country_code, city, org, asn_num, ))
