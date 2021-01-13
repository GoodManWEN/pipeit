import os , sys
sys.path.append(os.getcwd())
import pytest
from pipeit import *

def test_feature():
    a = PIPE | range(10) | (map , lambda x:x + 1) | (map , str) | list | END
    assert a == list(map(str , map(lambda x:x + 1 , range(10))))
    func = lambda x: PIPE | range(x) | (map , lambda x:x + 1) | (map , str) | list | END
    assert func(9) == list(map(str , map(lambda x:x + 1 , range(9))))