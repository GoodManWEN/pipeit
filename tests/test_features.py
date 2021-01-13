import os , sys
sys.path.append(os.getcwd())
import pytest
from pipeit import *

def test_basic():
    a = PIPE | range(10) | (map , lambda x:x + 1) | (map , str) | list | END
    assert a == list(map(str , map(lambda x:x + 1 , range(10))))

def test_use_in_function1():
    func = lambda x: PIPE | range(x) | (map , lambda x:x + 1) | (map , str) | list | END
    assert func(9) == list(map(str , map(lambda x:x + 1 , range(9))))

def test_mix_use():
    # Mix use obj & tuple
    a = PIPE | range(10) | Filter(lambda x:x > 5) | (map , lambda x:x-1) | list | END
    assert a == list(range(5,9))
    a = PIPE | range(10) | (map , lambda x:x-1) | Filter(lambda x:x > 5) | list | END
    assert a == list(range(6,9))

def test_mix_use2():
    flag = True
    try:
        # with wrapper on the right , unexpected error
        a = (map , lambda x:x-1) | Filter(lambda x:x > 5) | list
        flag = False
    except Exception as exc:
        ...
    assert flag


    flag = True
    try:
        # with wrapper on the left , detected error
        a = Filter(lambda x:x > 5) | (map , lambda x:x-1) | list
        flag = False
    except Exception as exc:
        assert isinstance(exc , RuntimeError)
    assert flag

def test_use_in_function2():
    func = lambda x: PIPE | range(x) | (map , lambda x:x-1) | Filter(lambda x:x > 5) | list | END
    assert func(15) == list(range(6,14))

def test_without_pipe_manager():
    a = range(10) | Map(lambda x:x+1) | Filter(lambda x:x<6) | Map(str) | list 
    assert a == list(map(str , range(1,6)))

def test_exec_order(): 
    flag = True
    try:
        a = range(10) | Map(str) | Filter(lambda x:x < 6) | list 
        flag = False
    except Exception as exc:
        assert isinstance(exc , TypeError)
    assert flag

def test_no_input():
    flag = True
    try:
        a = Map(lambda x:x+1) | Filter(lambda x:x<6) 
        flag = False
    except Exception as exc:
        assert isinstance(exc , RuntimeError)
    assert flag
    
def test_type():
    a = range(10) | Filter(lambda x:x<6)
    assert isinstance(a , Filter)

    a = range(10) | Map(lambda x:x<6)
    assert isinstance(a , Map)

    a = range(10) | Filter(lambda x:x<6) | END
    assert isinstance(a , filter)

    a = range(10) | Filter(lambda x:x<6) | set
    assert isinstance(a , set)

def test_iteration():
    a = range(10) | Filter(lambda x:x<6)
    a = list(a)
    assert a == list(range(0,6))

    a = []
    for i in range(10) | Filter(lambda x:x<6):
        a.append(i)
    assert a == list(range(0,6))

def test_use_in_function3():
    func = lambda x:range(x) | Filter(lambda x:x<6) | list
    assert func(3) == list(range(0,3))
    assert func(9) == list(range(0,6))

def test_misc1():
    a = [[1,2,3],[4,5,6],[7,8,9]] | Map(lambda x:x[2]) | list   
    assert a == [3,6,9]

def test_reduce():
    assert ([1,2,3,4,5] | Reduce(lambda x , y : x + y)) == 15