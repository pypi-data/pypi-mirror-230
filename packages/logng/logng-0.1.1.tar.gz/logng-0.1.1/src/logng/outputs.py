from sys import stdout as _stdout
from typing import Any


class __VirtualAttyStdout:
    def isatty(self) -> bool:
        return True

    def __getattr__(self, name: str) -> Any:
        return getattr(_stdout, name)

VirtualAttyStdout = __VirtualAttyStdout()