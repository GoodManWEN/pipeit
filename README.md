# pipeit
[![fury](https://badge.fury.io/py/pipeit.svg)](https://badge.fury.io/py/pipeit)
[![licence](https://img.shields.io/github/license/GoodManWEN/pipeit)](https://github.com/GoodManWEN/pipeit/blob/master/LICENSE)
[![pyversions](https://img.shields.io/pypi/pyversions/pipeit.svg)](https://pypi.org/project/pipeit/)
[![Publish](https://github.com/GoodManWEN/pipeit/workflows/Publish/badge.svg)](https://github.com/GoodManWEN/pipeit/actions?query=workflow:Publish)
[![Build](https://github.com/GoodManWEN/pipeit/workflows/Build/badge.svg)](https://github.com/GoodManWEN/pipeit/actions?query=workflow:Build)

This is a super simple wrapper , let's use python functional programming like Unix pipe!

Inspired by [abersheeran/only-pipe](https://github.com/abersheeran/only-pipe) , [czheo/syntax_sugar_python](https://github.com/czheo/syntax_sugar_python) , [pipetools](https://pypi.org/project/pipetools/)

## Install

    pip install pipeit

## Usage
- Statements start with `PIPE` and end with `END` , which are the only two object in the namespace.
- So feel free to use `from pipeit import *`.
- Convert filter into tuple , e.g. `map(lambda x:x + 1) => (map , lambda x:x + 1)`

## Example

Some description.
```Python
from pipit import PIPE , END

data = PIPE | range(10) | (map , lambda x:x + 1) | (map , str) | list | END
print(data)
func = lambda x: PIPE | range(x) | (map , lambda x:x + 1) | (map , str) | list | END
print(func(10))
```
