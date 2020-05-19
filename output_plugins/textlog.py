
from os import makedirs, linesep
from os.path import dirname, basename

from core import output
from core.tools import mkdir
from core.config import CONFIG
from core.logfile import HoneypotDailyLogFile

class Output(output.Output):

    def start(self):
        fn = CONFIG.get('output_textlog', 'logfile')
        dirs = dirname(fn)
        base = basename(fn)
        mkdir(dirs)
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
