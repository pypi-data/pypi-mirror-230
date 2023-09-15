from enum import Enum


class LogLevel(Enum):
    DEBUG = 3
    TRACE = 4
    INFO = 5
    WARN = 6
    ERROR = 7


NEED_WRAP = True
NONEED_WRAP = False


class LogBlock(Enum):
    TIME = (0, NEED_WRAP)
    TARGET = (1, NEED_WRAP)
    LEVEL = (2, NEED_WRAP)
    MSG = (3, NONEED_WRAP)
    LEVEL_COLOR = (4, NONEED_WRAP)
    RESET_COLOR = (5, NONEED_WRAP)
