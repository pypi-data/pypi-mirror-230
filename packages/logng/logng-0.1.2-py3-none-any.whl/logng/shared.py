from functools import partial
from typing import Callable, Tuple
from logng.base.enums import LogLevel
from logng.base.intfs import ILogger, TemplateLogger

__shared_logger: ILogger = TemplateLogger()


def set_logger(logger: ILogger) -> ILogger:
    global __shared_logger
    __shared_logger = logger
    return __shared_logger


get_or_default: Callable[[ILogger], ILogger] = (
    lambda default: __shared_logger if __shared_logger is not None else default
)


log: Callable[[LogLevel, *Tuple[str]], None] = lambda level, *msg: __shared_logger.log(
    level, *msg
)
set_log_level: Callable[[LogLevel], None] = lambda level: __shared_logger.set_log_level(
    level
)
info = partial(log, LogLevel.INFO)
warn = partial(log, LogLevel.WARN)
error = partial(log, LogLevel.ERROR)
debug = partial(log, LogLevel.DEBUG)
trace = partial(log, LogLevel.TRACE)
flush = lambda: __shared_logger.flush()
