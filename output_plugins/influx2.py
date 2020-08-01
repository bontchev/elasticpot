
from datetime import datetime

from core import output
from core.config import CONFIG

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from twisted.python import log


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_influx2', 'host')
        token = CONFIG.get('output_influx2', 'token', raw=True)

        self.client = None
        try:
            self.client = InfluxDBClient(url=host, token=token)
        except Exception as e:
            log.msg("output_influx2: I/O error: '{}'".format(e))
            return

        if self.client is None:
            log.msg('output_influx2: cannot instantiate client!')
            return

        self.org = CONFIG.get('output_influx2', 'org')
        self.bucket = CONFIG.get('output_influx2', 'bucket', fallback='elasticpot')
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def stop(self):
        pass

    def write(self, event):
        m = Point(event['eventid'].replace('.', '_'))\
            .tag('src_ip', event['src_ip'])\
            .time(datetime.utcfromtimestamp(event['unixtime']), WritePrecision.NS)

        fields = [
            'src_port',
            'dst_ip',
            'dst_port',
            'request',
            'url',
            'message',
            'sensor',
            'payload',
            'user_agent',
            'accept_language',
            'content_type'
        ]

        for key in fields:
            if key in event:
                m.field(key, event[key])

        self.write_api.write(bucket=self.bucket, org=self.org, record=m)
