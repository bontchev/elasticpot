
from json import dumps
from redis import StrictRedis

from core import output
from core.config import CONFIG


SEND_METHODS = {
    'lpush': lambda redis_client, key, message: redis_client.lpush(key, message),
    'rpush': lambda redis_client, key, message: redis_client.rpush(key, message),
    'publish': lambda redis_client, key, message: redis_client.publish(key, message),
}


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_redisdb', 'host')
        port = CONFIG.get('output_redisdb', 'port')
        db = CONFIG.get('output_redisdb', 'db', fallback='0')
        password = CONFIG.get('output_redisdb', 'password', fallback=None, raw=True)

        self.redis = StrictRedis(host=host, port=port, db=db, password=password)

        self.keyname = CONFIG.get('output_redisdb', 'keyname')

        method = CONFIG.get('output_redisdb', 'send_method', fallback='lpush')
        try:
            self.send_method = SEND_METHODS[method]
        except KeyError:
            self.send_method = SEND_METHODS['lpush']

    def stop(self):
        pass

    def write(self, event):
        self.send_method(self.redis, self.keyname, dumps(event))
