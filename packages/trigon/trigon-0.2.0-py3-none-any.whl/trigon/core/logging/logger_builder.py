import logging
import sys
from itertools import chain
from typing import TYPE_CHECKING, Any, Dict, Type

from loguru import _defaults

from trigon.core.logging.handlers import InterceptHandler

if TYPE_CHECKING:
    from trigon.core.middleware import Middleware


def default_formatter(record):
    return (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] "
        "[<level>{level}</level>] "
        "[<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>] "
        "<level>{message}</level>\n"
        "{exception}"
    )


class LoggerBuilder:
    def __init__(self) -> None:
        self.override_tags: list[str] = []
        self.middleware_type: Type[Middleware] | None = None
        self.handlers: list[Dict[str, Any]] = []

    def override(self, *modules: str, level: int = logging.DEBUG):
        logging.basicConfig(handlers=[InterceptHandler()], level=level)

        for logger_name in chain(("",), modules):
            mod_logger = logging.getLogger(logger_name)
            mod_logger.handlers = [InterceptHandler(level=level)]
            mod_logger.propagate = False

        return self

    def add_file_handler(
        self,
        sink: str,
        format=default_formatter,
        retention="7 days",
        compression="zip",
        rotation="500 MB",
    ):
        self.handlers.append(
            {
                "sink": sink,
                "format": format,
                "colorize": False,
                "retention": retention,
                "compression": compression,
                "rotation": rotation,
            },
        )

        return self

    def add_console_handler(
        self,
        error=False,
        format=default_formatter,
    ):
        sink, filter = None, None

        if error:
            sink = sys.stderr

            def filter(record):
                return record["level"].no >= _defaults.LOGURU_WARNING_NO

        else:
            sink = sys.stdout

            def filter(record):
                return record["level"].no < _defaults.LOGURU_WARNING_NO

        self.handlers.append(
            {
                "sink": sink,
                "format": format,
                "filter": filter,
            },
        )

        return self
