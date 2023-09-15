import logging
from typing import Any, Optional

# noinspection PyPep8Naming
class logger:
    level: int
    CRITICAL: int
    ERROR: int
    WARNING: int
    INFO: int
    DEBUG: int
    SUCCESS: int
    VERBOSE: int
    TRACE: int
    @staticmethod
    def trace(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def debug(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def verbose(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def info(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def success(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def warning(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def error(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def critical(msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def log(level: int, msg: Any, *args: list, **kwargs: dict[str]): ...
    @staticmethod
    def set_level(level: int): ...
    @staticmethod
    def set_file(
        filename: Optional[str] = None,
        formatter: logging.Formatter = None,
        mode: str = "a",
        max_bytes: int = 100 * 1024 * 1024,
        backup_count: int = 5,
        encoding: str = "utf-8",
        log_level: Optional[int] = None,
        disable_stderr_logger: bool = False,
    ): ...
    @staticmethod
    def hide_location(): ...
    @staticmethod
    def show_threading(): ...
    @staticmethod
    def hide_threading(): ...
