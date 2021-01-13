# pipeit
[![fury](https://badge.fury.io/py/pipeit.svg)](https://badge.fury.io/py/pipeit)
[![licence](https://img.shields.io/github/license/GoodManWEN/pipeit)](https://github.com/GoodManWEN/pipeit/blob/master/LICENSE)
[![pyversions](https://img.shields.io/pypi/pyversions/pipeit.svg)](https://pypi.org/project/pipeit/)
[![Publish](https://github.com/GoodManWEN/pipeit/workflows/Publish/badge.svg)](https://github.com/GoodManWEN/pipeit/actions?query=workflow:Publish)
[![Build](https://github.com/GoodManWEN/pipeit/workflows/Build/badge.svg)](https://github.com/GoodManWEN/pipeit/actions?query=workflow:Build)

Some description.

## Feature
- Some feature.

## Install

    pip install pipeit

## Usage
Some description.

## Example

Some description.
```Python
from pipit import PIPE , END

data = PIPE | range(10) | (map , lambda x:x + 1) | (map , str) | list | END
print(data)
```

A test of new branch
