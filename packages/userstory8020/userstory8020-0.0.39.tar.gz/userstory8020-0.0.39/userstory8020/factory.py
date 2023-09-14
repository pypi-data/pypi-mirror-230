import logging
import platform
from os import makedirs, path
from tempfile import gettempdir
from logging.handlers import TimedRotatingFileHandler


class AppDefaultFormater(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        seperator = " " * (8 - len(record.levelname))
        record.__dict__["levelprefix"] = record.levelname + ":" + seperator
        return super().formatMessage(record)


class AppTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self,
                 filename,
                 when,
                 interval=1,
                 backupCount=0,
                 encoding=None,
                 delay=False,
                 utc=False,
                 atTime=None):
        if platform.system() == 'Windows':
            self.__logs_dir = f'{gettempdir()}\\{__package__}\\logs'
            self.__filename = f'{self.__logs_dir}\\{filename}'
        elif platform.system() == 'Linux':
            self.__logs_dir = f'{gettempdir()}/{__package__}/logs'
            self.__filename = f'{self.__logs_dir}/{filename}'

        if not path.exists(self.__logs_dir):
            # if the logs directory is not present
            # then create it.
            makedirs(self.__logs_dir)
        super(AppTimedRotatingFileHandler,
              self).__init__(filename=self.__filename,
                             when=when,
                             interval=interval,
                             backupCount=backupCount,
                             encoding=encoding,
                             delay=delay,
                             utc=utc,
                             atTime=atTime)
