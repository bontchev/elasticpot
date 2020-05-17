
from errno import EEXIST
from os import sep, makedirs, linesep
from os.path import dirname, basename, exists

from core import output
from core.config import CONFIG
from core.logfile import HoneypotDailyLogFile

class Output(output.Output):

    def start(self):
        fn = CONFIG.get('output_textlog', 'logfile')
        dirs = dirname(fn)
        base = basename(fn)
        if not exists(dirs) and sep in fn:
            try:
                makedirs(dirs)
            except OSError as exc:
                if exc.errno != EEXIST:
                    raise
        self.outfile = HoneypotDailyLogFile(base, dirs, defaultMode=0o664)

    def stop(self):
        self.outfile.flush()

    def write(self, event):
        self.outfile.write('[{}] '.format(event['timestamp']))
        self.outfile.write('[{}] '.format(event['sensor']))
        self.outfile.write('{} '.format(event['request']))
        self.outfile.write('{} '.format(event['url']))
        self.outfile.write('from {}:{} '.format(event['src_ip'], event['dst_port']))
        self.outfile.write('({})'.format(event['message']))
        if 'payload' in event:
            self.outfile.write('{}\tpayload: {} '.format(linesep, event['payload']))
        self.outfile.write(linesep)
        self.outfile.flush()
