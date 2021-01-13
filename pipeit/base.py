from typing import Callable

class PipeManagerEnd:
    
    def __ror__(self , other):
        return other

class AbstractSelfModifiedClass:
    
    def __init__(self , func):
        self._func = func
        self._storage = None

    def _exec(self):
        return self

    def __call__(self , _iter):
        return self

    def __iter__(self):
        return self._storage

    def __or__(self , other):
        if self._storage is None:
            raise RuntimeError("Empty object is not allowed to be used in chain.")
        if isinstance(other , PipeManagerEnd):
            return self._storage
        elif isinstance(other , AbstractSelfModifiedClass):
            self._storage = other._exec(self._storage)
        elif isinstance(other , tuple):
            raise SyntaxError("Not allowed to mix use different wrapper call.")
        elif isinstance(other , Callable):
            return other(self._storage)
        else:
            self._storage = other
        return self

    def __ror__(self , _iter):
        self._storage = self._exec(_iter)
        return self