from functools import partialmethod
from types import FrameType
from logng.base.enums import LogBlock, LogLevel
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, List, TextIO, Tuple
from colorama import Fore, Style
from time import strftime, localtime
import sys, inspect

from logng.base.intfs import ILogger


if TYPE_CHECKING:

    class _CallLog:
        def __call__(self, *msg: Any) -> None:
            return msg


@dataclass
class LogConfig:
    """
    each property of this cls has a default, just modify as your requirement
    """

    stdouts: Tuple[TextIO] = (sys.stdout,)
    maxcount: int = None
    timeformat: str = "%D %T"
    level_color: Callable[[LogLevel], str] = (
        lambda level: Fore.LIGHTGREEN_EX
        if level == LogLevel.INFO
        else Fore.LIGHTYELLOW_EX
        if level == LogLevel.WARN
        else Fore.LIGHTRED_EX
        if level == LogLevel.ERROR
        else Fore.LIGHTMAGENTA_EX
        if level == LogLevel.TRACE
        else Fore.LIGHTCYAN_EX
    )
    loglevel: LogLevel = LogLevel.INFO
    logblocks: Tuple[LogBlock] = (
        LogBlock.LEVEL_COLOR,
        LogBlock.TIME,
        LogBlock.LEVEL,
        LogBlock.TARGET,
        " ",
        LogBlock.MSG,
        LogBlock.RESET_COLOR,
        "\n",
    )
    logblockwrap: Tuple[str, str] = (
        "[",
        "]",
    )
    locate_back: int = 0


current_logger = None


class Logger(ILogger):
    config: LogConfig
    isatty: List[bool]

    def __init__(self, config: LogConfig = LogConfig()) -> None:
        """
        the more complex config, the lower the output speed, just enable what's u need
        """
        super().__init__()
        self.config = config
        self.isatty = [std.isatty() for std in self.config.stdouts]
        global current_logger
        current_logger = self

    def log(self, level: LogLevel, *msg: Any) -> None:
        if level.value < self.config.loglevel.value:
            return
        for index, std in enumerate(self.config.stdouts):
            for lb in self.config.logblocks:
                if isinstance(lb, str):
                    std.write(lb)
                elif not lb.value[1]:
                    std.write(
                        (
                            " ".join(map(str, msg))
                            if lb == LogBlock.MSG
                            else self.config.level_color(level)
                            if self.isatty[index] and lb == LogBlock.LEVEL_COLOR
                            else Style.RESET_ALL
                            if self.isatty[index] and lb == LogBlock.RESET_COLOR
                            else ""
                        )
                    )
                else:
                    std.write(
                        self.config.logblockwrap[0]
                        + (
                            strftime(self.config.timeformat, localtime())
                            if lb == LogBlock.TIME
                            else level.name
                            if lb == LogBlock.LEVEL
                            else inspect.getmodule(self.__locate_stack()).__name__
                            if lb == LogBlock.TARGET
                            else ""
                        )
                        + self.config.logblockwrap[1]
                    )
        return super().log(level, *msg)

    def __locate_stack(self) -> FrameType:
        sk = inspect.stack()[1][0]
        for _ in range(self.config.locate_back + 1):
            sk = sk.f_back
        return sk

    def flush(self):
        # TODO don't know how to process yet
        return super().flush()

    info: "_CallLog" = partialmethod(log, LogLevel.INFO)
    warn: "_CallLog" = partialmethod(log, LogLevel.WARN)
    error: "_CallLog" = partialmethod(log, LogLevel.ERROR)
    trace: "_CallLog" = partialmethod(log, LogLevel.TRACE)
    debug: "_CallLog" = partialmethod(log, LogLevel.DEBUG)

    def set_log_level(self, level: LogLevel) -> None:
        self.config.loglevel = level
        return super().set_log_level(level)


def get_or_create_logger(config: LogConfig = LogConfig()) -> Logger:
    return current_logger if current_logger is not None else Logger(config)
