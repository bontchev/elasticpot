
from re import search

from core import output
from core.config import CONFIG

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

from twisted.python import log


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_influx', 'host', fallback='')
        port = CONFIG.getint('output_influx', 'port', fallback=8086)
        ssl = CONFIG.getboolean('output_influx', 'ssl', fallback=False)

        self.client = None
        try:
            self.client = InfluxDBClient(host=host, port=port, ssl=ssl, verify_ssl=ssl)
        except InfluxDBClientError as e:
            log.msg("output_influx: I/O error({}): '{}'".format(e.code, e.message))
            return

        if self.client is None:
            log.msg('output_influx: cannot instantiate client!')
            return

        if (CONFIG.has_option('output_influx', 'username') and
            CONFIG.has_option('output_influx', 'password')):
            username = CONFIG.get('output_influx', 'username')
            password = CONFIG.get('output_influx', 'password', raw=True)
            self.client.switch_user(username, password)

        dbname = CONFIG.get('output_influx', 'database_name', fallback='elasticpot')

        retention_policy_duration_default = '12w'
        retention_policy_name = dbname + '_retention_policy'

        if CONFIG.has_option('output_influx', 'retention_policy_duration'):
            retention_policy_duration = CONFIG.get('output_influx', 'retention_policy_duration')

            match = search(r'^\d+[dhmw]{1}$', retention_policy_duration)
            if not match:
                log.msg(("output_influx: invalid retention policy. Using default '{}'.").format(retention_policy_duration))
                retention_policy_duration = retention_policy_duration_default
        else:
            retention_policy_duration = retention_policy_duration_default

        database_list = self.client.get_list_database()
        dblist = [str(elem['name']) for elem in database_list]

        if dbname not in dblist:
            self.client.create_database(dbname)
            self.client.create_retention_policy(
                retention_policy_name,
                retention_policy_duration,
                1,
                database=dbname,
                default=True
            )
        else:
            retention_policies_list = self.client.get_list_retention_policies(database=dbname)
            rplist = [str(elem['name']) for elem in retention_policies_list]
            if retention_policy_name not in rplist:
                self.client.create_retention_policy(
                    retention_policy_name,
                    retention_policy_duration,
                    1,
                    database=dbname,
                    default=True
                )
            else:
                self.client.alter_retention_policy(
                    retention_policy_name,
                    database=dbname,
                    duration=retention_policy_duration,
                    replication=1,
                    default=True
                )

        self.client.switch_database(dbname)

    def stop(self):
        pass

    def write(self, event):
        if self.client is None:
            log.msg('output_influx: client object is not instantiated')
            return

        eventid = event['eventid']

        # measurement init
        m = {
            'measurement': eventid.replace('.', '_'),
            'tags': {
                'src_ip': event['src_ip']
            },
            'fields': {
                'src_ip': event['src_ip'],
                'src_port': event['src_port'],
                'dst_ip': event['dst_ip'],
                'dst_port': event['dst_port'],
                'request': event['request'],
                'url': event['url'],
                'message': event['message'],
                'sensor': self.sensor
            },
        }
        for key in ['payload', 'user_agent', 'accept_language', 'content_type']:
            if key in event:
                m['fields'].update({key: event[key]})

        result = self.client.write_points([m])

        if not result:
            log.msg("output_influx: error when writing '{}' measurement in the db.".format(eventid))
