from functools import partial
from logng.base.enums import LogLevel
from logng.base.intfs import ILogger

__shared_logger: ILogger = None


def set_logger(logger: ILogger) -> ILogger:
    global __shared_logger
    __shared_logger = logger
    return __shared_logger


def get_or_default(default: ILogger) -> ILogger:
    return __shared_logger if __shared_logger is not None else default


def log(level: LogLevel, *msg: str) -> None:
    return __shared_logger.log(level, *msg)


def set_log_level(level: LogLevel) -> None:
    __shared_logger.set_log_level(level)


info = partial(log, LogLevel.INFO)
warn = partial(log, LogLevel.WARN)
error = partial(log, LogLevel.ERROR)
debug = partial(log, LogLevel.DEBUG)
trace = partial(log, LogLevel.TRACE)
