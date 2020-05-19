
from json import dump
from copy import deepcopy
from os import makedirs, linesep
from os.path import dirname, basename

from core import output
from core.tools import mkdir
from core.config import CONFIG
from core.logfile import HoneypotDailyLogFile

class Output(output.Output):

    def start(self):
        self.epoch_timestamp = CONFIG.getboolean('output_jsonlog', 'epoch_timestamp', fallback=False)
        fn = CONFIG.get('output_jsonlog', 'logfile')
        dirs = dirname(fn)
        base = basename(fn)
        mkdir(dirs)
        self.outfile = HoneypotDailyLogFile(base, dirs, defaultMode=0o664)

    def stop(self):
        self.outfile.flush()

    def write(self, event):
        if not self.epoch_timestamp:
            # We need 'unixtime' value in some other plugins
            event_dump = deepcopy(event)
            event_dump.pop('unixtime', None)
        else:
            event_dump = event
        dump(event_dump, self.outfile, separators=(',', ':'))
        self.outfile.write(linesep)
        self.outfile.flush()
