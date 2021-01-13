from functools import partial
from typing import Callable
from .base import AbstractSelfModifiedClass , PipeManagerEnd

class PipeManager:

    def __init__(self):
        self._storage = None

    def __or__(self , other):
        if isinstance(other , PipeManagerEnd):
            ret = self._storage
            self._storage = None
            return ret
        elif isinstance(other , AbstractSelfModifiedClass):
            self._storage = other._exec(self._storage)
        elif isinstance(other , tuple):
            self._storage = partial(*other)(self._storage)
        elif isinstance(other , Callable):
            self._storage = other(self._storage)
        else:
            self._storage = other
        return self

PIPE = PipeManager()
END = PipeManagerEnd()