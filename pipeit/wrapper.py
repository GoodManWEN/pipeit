from typing import Callable
from functools import reduce
from .base import AbstractSelfModifiedClass

class Filter(AbstractSelfModifiedClass):

    def _exec(self , _iter):
        return filter(self._func , _iter)

class Map(AbstractSelfModifiedClass):

    def _exec(self , _iter):
        return map(self._func , _iter)

class Reduce(AbstractSelfModifiedClass):

    def _exec(self , _iter):
        return reduce(self._func , _iter)

    def __ror__(self , _iter):
        return self._exec(_iter)