from typing import Callable
from .base import AbstractSelfModifiedClass

class Filter(AbstractSelfModifiedClass):

    def _exec(self , _iter):
        return filter(self._func , _iter)

class Map(AbstractSelfModifiedClass):

    def _exec(self , _iter):
        return map(self._func , _iter)