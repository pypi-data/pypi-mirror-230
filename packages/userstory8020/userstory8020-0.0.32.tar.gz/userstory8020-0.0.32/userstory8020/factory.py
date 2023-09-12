import logging


class AppDefaultFormater(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        seperator = " " * (8 - len(record.levelname))
        record.__dict__["levelprefix"] = record.levelname + ":" + seperator
        return super().formatMessage(record)
