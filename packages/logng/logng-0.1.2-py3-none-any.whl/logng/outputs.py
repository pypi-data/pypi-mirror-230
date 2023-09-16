from io import TextIOWrapper
from sys import stdout as _stdout
from typing import Any


class __VirtualAttyStdout:
    def isatty(self) -> bool:
        return True

    def __getattr__(self, name: str) -> Any:
        return getattr(_stdout, name)


VirtualAttyStdout = __VirtualAttyStdout()


class FileOutput:
    __outputio: TextIOWrapper

    def __init__(self, path: str, mode="w") -> None:
        self.__outputio = open(path, mode=mode)

    def isatty(self) -> bool:
        return False

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__outputio, name)
