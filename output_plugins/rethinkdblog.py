
from rethinkdb import r

from core import output
from core.config import CONFIG

from twisted.python import log


class Output(output.Output):

    def start(self):
        host = CONFIG.get('output_rethinkdblog', 'host', fallback='localhost')
        port = CONFIG.getint('output_rethinkdblog', 'port', fallback=28015)
        db = CONFIG.get('output_rethinkdblog', 'db', fallback='elasticpot')
        password = CONFIG.get('output_rethinkdblog', 'password', raw=True)
        self.table = CONFIG.get('output_rethinkdblog', 'table', fallback='events')

        self.connection = r.connect(
            host=host,
            port=port,
            db=db,
            password=password
        )

        try:
            r.db_create(db).run(self.connection)
            r.db(db).table_create(self.table).run(self.connection)
        except r.RqlRuntimeError as err:
            log.msg('output_rethinkdblog: Error: {}'.format(err.message))

    def stop(self):
        self.connection.close()

    def write(self, event):
        try:
            r.table(self.table).insert(event).run(self.connection)
        except r.RqlRuntimeError as err:
            log.msg('output_rethinkdblog: Error: {}'.format(err.message))
