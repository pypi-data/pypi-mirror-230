# import json

import datetime
import inspect
import json
import logging
from typing import Any, Dict  # , Tuple, Union

from hypergo.utility import Utility

CALLER_DEPTH: int = 10


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        stack_item = inspect.stack()[CALLER_DEPTH]
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "name": f"{stack_item.filename}:{stack_item.lineno} {stack_item.function}",
            "level": record.levelname,
            "message": record.msg,
        }
        return json.dumps(log_data)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("hypergo")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    #file_handler = logging.FileHandler(
    #    Utility.create_folders_for_file(
    #        f"./.hypergo_storage/logs/app_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
    #    )
    #)
    #file_handler.setFormatter(JSONFormatter())
    #logger.addHandler(file_handler)

    return logger


my_logger = get_logger()


class Logger:
    @staticmethod
    def warning(*args: Any, **kwargs: Any) -> None:
        my_logger.warning(args)

    @staticmethod
    def debug(*args: Any, **kwargs: Any) -> None:
        my_logger.debug(args)

    @staticmethod
    def info(*args: Any, **kwargs: Any) -> None:
        my_logger.info(args)

    @staticmethod
    def error(*args: Any, **kwargs: Any) -> None:
        my_logger.error(args)

    @staticmethod
    def critical(*args: Any, **kwargs: Any) -> None:
        my_logger.critical(args)
