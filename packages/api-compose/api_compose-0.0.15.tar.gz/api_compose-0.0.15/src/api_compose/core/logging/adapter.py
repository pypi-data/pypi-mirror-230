import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from lxml import etree
from lxml.etree import _Element
from pydantic import BaseModel as _BaseModel

from api_compose.core.events.base import BaseEvent
from api_compose.core.events.default import DefaultEvent
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.core.utils import _modify_json_encoder  # noqa - modify json.dump behaviour


class LoggerAdapter():
    IS_INITIALISED = False

    def __init__(
            self,
            name,
            log_file_path: Path,
            overwrite: bool = True,
            logging_level=logging.DEBUG
    ):
        self.name = name
        self.log_file_path = log_file_path
        self.logging_level = logging_level

        if overwrite:
            self._delete_log_file()

        self._logger = self._get_logger()
        self.__class__.IS_INITIALISED = True

    def _get_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        logger.setLevel(self.logging_level)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(StreamFormatter())
        stream_handler.addFilter(EventFilter())
        logger.addHandler(stream_handler)

        logger.propagate = False

        if self.log_file_path and not self.log_file_path.is_dir():
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setFormatter(FileJsonFormatter())
            file_handler.addFilter(EventFilter())
            logger.addHandler(file_handler)

        return logger

    def _delete_log_file(self):
        if self.log_file_path and self.log_file_path.is_file() and not self.__class__.IS_INITIALISED:
            self.log_file_path.unlink()

    def debug(self, message: str, event: Optional[BaseEvent] = None):
        self.log(logging.DEBUG, message, event)

    def info(self, message: str, event: Optional[BaseEvent] = None):
        self.log(logging.INFO, message, event)

    def warning(self, message: str, event: Optional[BaseEvent] = None):
        self.log(logging.WARNING, message, event)

    def error(self, message: str, event: Optional[BaseEvent] = None):
        self.log(logging.ERROR, message, event)

    def critical(self, message: str, event: Optional[BaseEvent] = None):
        self.log(logging.CRITICAL, message, event)

    def log(self, level, message, event: Optional[BaseEvent] = None):
        if event is None:
            self._logger.log(level=level, msg=message, extra=DefaultEvent().model_dump())
        else:
            self._logger.log(level=level, msg=message, extra=event.model_dump())


class EventFilter(logging.Filter):
    def filter(self, record):
        logging_event_filters = GlobalSettingsModelSingleton.get().logging.event_filters
        if len(logging_event_filters) == 0:
            # Do nothing
            return True
        else:
            # Filter allow for events in the filter
            return record.event in logging_event_filters


class SimpleNamespaceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleNamespace):
            return vars(obj)
        if isinstance(obj, _BaseModel):
            return obj.model_dump_json()
        if isinstance(obj, type):
            return str(type)
        if isinstance(obj, _Element):
            return etree.tostring(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)


class FileJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        log_dict = {
            "event": getattr(record, 'event', None),
            "message": record.getMessage(),
            "logger": record.name,
            "level": record.levelname,
            "timestamp": self.formatTime(record),
            "data": getattr(record, 'data', None)
        }
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_dict, cls=SimpleNamespaceEncoder)


class StreamFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.msg = f"[{getattr(record, 'event')}] : {record.levelname} - {record.msg}"
        return super().format(record)
