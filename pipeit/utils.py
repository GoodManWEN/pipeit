from functools import partial
from typing import Callable

class _pipe_end:
    ...

class _pipe_start:

    def __init__(self):
        self._storage = None

    def __or__(self , other):
        if isinstance(other , _pipe_end):
            ret = self._storage
            self._storage = None
            return ret
        elif isinstance(other , tuple):
            self._storage = partial(*other)(self._storage)
        elif isinstance(other , Callable):
            self._storage = other(self._storage)
        else:
            self._storage = other
        return self

PIPE = _pipe_start()
END = _pipe_end()