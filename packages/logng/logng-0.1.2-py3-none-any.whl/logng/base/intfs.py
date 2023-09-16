from abc import ABC, abstractmethod
from typing import Any

from logng.base.enums import LogLevel


class ILogger(ABC):
    @abstractmethod
    def log(self, level: LogLevel, *msg: Any) -> None:
        ...

    @abstractmethod
    def flush(self):
        ...

    @abstractmethod
    def set_log_level(self, level: LogLevel) -> None:
        ...


class TemplateLogger(ILogger):
    def log(self, level: LogLevel, *msg: Any) -> None:
        return super().log(level, *msg)

    def flush(self):
        return super().flush()

    def set_log_level(self, level: LogLevel) -> None:
        return super().set_log_level(level)