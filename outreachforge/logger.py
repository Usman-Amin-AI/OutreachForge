import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        event = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
        }

        if hasattr(record, "extra"):
            event.update(record.extra)

        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)

        return json.dumps(event)


logger = logging.getLogger("outreachforge")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)


def log(event: str, **kwargs) -> None:
    logger.info(event, extra={"extra": kwargs})


def warn(event: str, **kwargs) -> None:
    logger.warning(event, extra={"extra": kwargs})


def error(event: str, **kwargs) -> None:
    logger.error(event, extra={"extra": kwargs})
