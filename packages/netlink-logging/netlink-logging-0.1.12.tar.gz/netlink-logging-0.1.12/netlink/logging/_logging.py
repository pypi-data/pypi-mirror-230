# noinspection PyPackageRequirements
import __main__
import logging
import pathlib
import sys
import time
from types import MethodType

import logzero

from logzero import logger, ForegroundColors
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG

from netlink.core import Config

logging.Formatter.converter = time.gmtime

SUCCESS = 25
VERBOSE = 15
TRACE = 5

config = Config()

DEFAULT_LEVEL = config.logging.level
DEFAULT_MESSAGE_FORMAT = config.logging.message_format
DEFAULT_FILE_FORMAT = config.logging.file_format
DEFAULT_DATE_FORMAT = config.logging.date_format
DEFAULT_FILE_SIZE = config.logging.file_size
DEFAULT_BACKUP_COUNT = config.logging.file_generations

DEFAULT_COLORS = {
    CRITICAL: ForegroundColors.RED,
    ERROR: ForegroundColors.RED,
    WARNING: ForegroundColors.YELLOW,
    SUCCESS: ForegroundColors.GREEN,
    INFO: ForegroundColors.GREEN,
    VERBOSE: ForegroundColors.BLUE,
    DEBUG: ForegroundColors.CYAN,
    TRACE: ForegroundColors.MAGENTA,
}


def add_logging_level(name: str, level: int) -> None:
    """Add a new logging level

    :param str name: Level name
    :param int level: Level severity
    """

    def _f(self, message, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kwargs)

    logging.addLevelName(level, name.upper())
    setattr(logging.Logger, name.lower(), _f)


add_logging_level("success", SUCCESS)
add_logging_level("verbose", VERBOSE)
add_logging_level("trace", TRACE)

logzero.loglevel(DEFAULT_LEVEL)
logzero.formatter(logzero.LogFormatter(fmt=DEFAULT_MESSAGE_FORMAT, datefmt=DEFAULT_DATE_FORMAT, colors=DEFAULT_COLORS))
try:
    path = pathlib.Path(__main__.__file__)
except AttributeError:
    path = pathlib.Path('<input>')
if path.stem == '__main__':
    path = path.parent


def _default_file():
    logzero.logfile(
        filename="_input_.log" if path.stem == "<input>" else path.with_suffix(".log"),
        formatter=logzero.LogFormatter(fmt=DEFAULT_FILE_FORMAT, datefmt=DEFAULT_DATE_FORMAT),
        maxBytes=DEFAULT_FILE_SIZE,
        backupCount=DEFAULT_BACKUP_COUNT,
        encoding="utf-8",
        loglevel=DEFAULT_LEVEL,
    )


_default_file()


def _set_file(
    self,
    filename=None,
    formatter=None,
    mode="a",
    max_bytes=DEFAULT_FILE_SIZE,
    backup_count=DEFAULT_BACKUP_COUNT,    encoding="utf-8",
    log_level=None,
    disable_stderr_logger=False,
):
    if filename is not None:
        formatter = formatter or logzero.LogFormatter(fmt=DEFAULT_FILE_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
        log_level = log_level or self.level
    logzero.logfile(
        filename=filename,
        formatter=formatter,
        mode=mode,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding,
        loglevel=log_level,
        disableStderrLogger=disable_stderr_logger,
    )


def _enable_file(
    self,
    value: bool = True,
):
    if value:
        _default_file()
    else:
        logzero.logfile(None)


def _disable_file(self):
    _enable_file(False)


def _hide_location(self):
    for i in self.handlers:
        i.formatter._fmt = i.formatter._fmt.replace('%(module)s', '').replace('%(lineno)d', '').replace(':]', ']').replace(' ]', ']')


def _show_threading(self):
    for i in self.handlers:
        if '%(threadName)s' not in i.formatter._fmt:
            i.formatter._fmt = i.formatter._fmt.replace('%(asctime)s', '%(asctime)s %(threadName)s')


def _hide_threading(self):
    for i in self.handlers:
        i.formatter._fmt = i.formatter._fmt.replace(' %(threadName)s', '')


logger.set_file = MethodType(_set_file, logger)
logger.enable_file = MethodType(_enable_file, logger)
logger.disable_file = MethodType(_disable_file, logger)
logger.hide_location = MethodType(_hide_location, logger)
logger.show_threading = MethodType(_show_threading, logger)
logger.hide_threading = MethodType(_hide_threading, logger)
setattr(logger, "set_level", lambda level: logzero.loglevel(level))

logger.CRITICAL = CRITICAL
logger.ERROR    = ERROR
logger.WARNING  = WARNING
logger.INFO     = INFO
logger.DEBUG    = DEBUG
logger.SUCCESS  = SUCCESS
logger.VERBOSE  = VERBOSE
logger.TRACE    = TRACE

sys.excepthook = lambda e, v, tb: logger.critical(f"Uncaught Exception ➔ {e.__name__}: {v}", exc_info=(e, v, tb))
