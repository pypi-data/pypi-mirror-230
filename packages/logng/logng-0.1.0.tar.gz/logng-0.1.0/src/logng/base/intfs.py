from abc import ABC, abstractmethod

from logng.base.enums import LogLevel


class ILogger(ABC):
    @abstractmethod
    def log(self, level: LogLevel, *msg: str) -> None:
        ...

    @abstractmethod
    def flush(self):
        ...

    @abstractmethod
    def set_log_level(self, level: LogLevel) -> None:
        ...
