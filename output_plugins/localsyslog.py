
import syslog

from core import output
from core.config import CONFIG

from twisted.python.syslog import SyslogObserver


def formatCef(logentry):
    """
    Take logentry and turn into CEF string
    """
    # Jan 18 11:07:53 host CEF:Version|Device Vendor|Device Product|
    # Device Version|Signature ID|Name|Severity|[Extension]
    cefVendor = 'Elasticpot'
    cefProduct = 'Elasticpot'
    cefVersion = '1.0'
    cefSignature = logentry['eventid']
    cefName = logentry['eventid']
    cefSeverity = '5'

    cefExtensions = {
        'deviceExternalId': logentry['sensor'],
        'msg': logentry['message'],
        'src': logentry['src_ip'],
        'spt': logentry['src_port'],
        'dpt': logentry['dst_port'],
        'dst': logentry['dst_ip'],
        'req': logentry['request'],
        'url': logentry['url'],
        'proto': 'tcp'
    }

    cefList = []
    for key in list(cefExtensions.keys()):
        value = str(cefExtensions[key])
        cefList.append('{}={}'.format(key, value))

    cefExtension = ' '.join(cefList)

    cefString = 'CEF:0|' + \
                cefVendor + '|' + \
                cefProduct + '|' + \
                cefVersion + '|' + \
                cefSignature + '|' + \
                cefName + '|' + \
                cefSeverity + '|' + \
                cefExtension

    return cefString


class Output(output.Output):

    def start(self):
        self.format = CONFIG.get('output_localsyslog', 'format', fallback='text')
        facilityString = CONFIG.get('output_localsyslog', 'facility', fallback='USER')
        facility = vars(syslog)['LOG_' + facilityString]
        self.syslog = twisted.python.syslog.SyslogObserver(prefix='elasticpot', facility=facility)

    def stop(self):
        pass

    def write(self, event):
        if 'isError' not in event:
            event['isError'] = False

        if self.format == 'cef':
            self.syslog.emit({
                'message': formatCef(event),
                'isError': False,
                'system': 'elasticpot'
            })
        else:
            # message appears with additional spaces if message key is defined
            event['message'] = [event['message']]
            self.syslog.emit(event)
