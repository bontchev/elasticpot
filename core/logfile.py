
from sys import stdout
from datetime import datetime

from twisted.python import log, util
from twisted.python.logfile import DailyLogFile


class HoneypotDailyLogFile(DailyLogFile):
    """
    Overload original Twisted with improved date formatting
    """

    def suffix(self, tupledate):
        """
        Return the suffix given a (year, month, day) tuple or unixtime
        """
        try:
            return "{:02d}-{:02d}-{:02d}".format(tupledate[0], tupledate[1], tupledate[2])
        except Exception:
            # try taking a float unixtime
            return '_'.join(map(str, self.toDate(tupledate)))


def myFLOemit(self, eventDict):
    """
    Format the given log event as text and write it to the output file.

    @param eventDict: a log event
    @type eventDict: L{dict} mapping L{str} (native string) to L{object}
    """

    # Custom emit for FileLogObserver
    text = log.textFromEventDict(eventDict)
    if text is None:
        return
    timeStr = self.formatTime(eventDict['time'])
    fmtDict = {
        'text': text.replace('\n', '\n\t')
    }
    msgStr = log._safeFormat('%(text)s\n', fmtDict)
    util.untilConcludes(self.write, timeStr + ' ' + msgStr)
    util.untilConcludes(self.flush)


def myFLOformatTime(self, when):
    """
    Log time in UTC

    By default it's formatted as an ISO8601-like string (ISO8601 date and
    ISO8601 time separated by a space). It can be customized using the
    C{timeFormat} attribute, which will be used as input for the underlying
    L{datetime.datetime.strftime} call.

    @type when: C{int}
    @param when: POSIX (ie, UTC) timestamp.

    @rtype: C{str}
    """
    timeFormatString = self.timeFormat
    if timeFormatString is None:
        timeFormatString = '[%Y-%m-%d %H:%M:%S.%fZ]'
    return datetime.utcfromtimestamp(when).strftime(timeFormatString)


def set_logger(cfg_options):
    log.FileLogObserver.emit = myFLOemit
    log.FileLogObserver.formatTime = myFLOformatTime
    if cfg_options['logfile'] is None:
        log.startLogging(stdout)
    else:
        log.startLogging(HoneypotDailyLogFile.fromFullPath(cfg_options['logfile']), setStdout=False)
