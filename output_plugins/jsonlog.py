
from json import dump
from errno import EEXIST
from copy import deepcopy
from os import sep, makedirs, linesep
from os.path import dirname, basename, exists

from core import output
from core.config import CONFIG
from core.logfile import HoneypotDailyLogFile

class Output(output.Output):

    def start(self):
        self.epoch_timestamp = CONFIG.getboolean('output_jsonlog', 'epoch_timestamp', fallback=False)
        fn = CONFIG.get('output_jsonlog', 'logfile')
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
        if not self.epoch_timestamp:
            # We need 'unixtime' value in some other plugins
            event_dump = deepcopy(event)
            event_dump.pop('unixtime', None)
        else:
            event_dump = event
        dump(event_dump, self.outfile, separators=(',', ':'))
        self.outfile.write(linesep)
        self.outfile.flush()
