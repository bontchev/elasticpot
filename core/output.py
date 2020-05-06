
from socket import gethostname

from core.config import CONFIG


class Output(object):
    """
    Abstract base class intended to be inherited by output plugins.
    """

    def __init__(self, general_options):

        self.cfg = general_options

        if not 'sensor' in self.cfg:
            self.sensor = CONFIG.get('honeypot', 'sensor_name', fallback=gethostname())
        else:
            self.sensor = self.cfg['sensor']

        self.start()

    def start(self):
        """
        Abstract method to initialize output plugin
        """
        pass

    def stop(self):
        """
        Abstract method to shut down output plugin
        """
        pass

    def write(self, event):
        """
        Handle a general event within the output plugin
        """
        pass
