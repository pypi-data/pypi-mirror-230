import sys
import logging
import datetime
from gunicorn import glogging


class GunicornLogger(glogging.Logger):
    """Custom logger for Gunicorn log messages."""

    # override gunicorn's now() for asctime's format
    def now(self):
            return datetime.datetime.utcnow().isoformat(sep=' ', timespec='milliseconds')

    def setup(self, cfg):
        """Configure Gunicorn application logging configuration."""

        super().setup(cfg)
        self.error_fmt =(
            '{"ts": "%(asctime)s", "loglevel": "%(levelname)s", "message": "%(message)s"}'
        )
        self.access_fmt = (
            '{'
            '"ts": "%(t)s", "host": "%(h)s", "status_line": "%(r)s", "status": "%(s)s"'
            ', "response_len": "%(b)s", "referer": "%(f)s"'
            '}'
        )

        # override gunicorn's 'access_log_format' configuration
        self.cfg.set("access_log_format", self.access_fmt)

        # Override Gunicorn's `error_log` configuration.
        self._set_handler(
            self.error_log, cfg.errorlog, logging.Formatter(
                fmt=self.error_fmt))

class MockGunicornConfig:

    def __init__(self):
        self.loglevel = 'INFO'
        self.capture_output = True
        self.errorlog = '-'
        self.accesslog = None
        self.access_log_format = ''
        self.syslog = None
        self.logconfig_dict = None
        self.logconfig_json = None
        self.logconfig = None

    def set(self, name, value):
        pass
