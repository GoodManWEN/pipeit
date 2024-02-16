import os, sys
sys.path.append(os.getcwd())
import pytest
from pipeit import Read, Write, ReadB, WriteB, Map
import json

def test_write_empty_text():
    try:
        Write('test.txt', )
    except TypeError as e:
        err_msg = str(e)
        assert 'missing' in err_msg and 'required' in err_msg and 'text' in err_msg

    try:
        WriteB('test.txt', )
    except TypeError as e:
        err_msg = str(e)
        assert 'missing' in err_msg and 'required' in err_msg and 'text' in err_msg

def test_write_wrong_type():
    err_msg = ''
    try:
        Write('test.txt', b'abc123')
    except TypeError as e:
        err_msg = str(e)
    assert 'write() argument must be str, not bytes' in err_msg 

    err_msg = ''
    try:
        WriteB('test.txt', 'abc123')
    except TypeError as e:
        err_msg = str(e)
    assert "a bytes-like object is required, not 'str'" in err_msg 

    try:
        Write('test.txt', 'abc123_你好世界')
    except Exception as e:
        no_raise = False
    else:
        no_raise = True 
    assert no_raise

    try:
        WriteB('test.txt', 'abc123_你好世界'.encode('utf-8'))
    except Exception as e:
        no_raise = False
    else:
        no_raise = True 
    assert no_raise

    err_msg = ''
    try:
        WriteB('test.txt') | 'abc123'
    except TypeError as e:
        err_msg = str(e)
    assert "OR operation not allowed" in err_msg 

    
def test_write_encoding():
    try:
        Write('test.txt', 'abc123_你好世界', encoding='utf-8')
    except Exception as e:
        no_raise = False
    else:
        no_raise = True 
    finally:
        assert no_raise
        with open('test.txt', 'r', encoding='utf-8') as f:
            assert f.read() == 'abc123_你好世界'
    
    try:
        Write('test.txt', 'abc123_你好世界', encoding='gbk')
    except Exception as e:
        no_raise = False
    else:
        no_raise = True 
    finally:
        assert no_raise
        no_raise = True
        try:
            with open('test.txt', 'r', encoding='utf-8') as f:
                assert f.read() == 'abc123_你好世界'
        except UnicodeDecodeError as e:
            no_raise = False
        assert not no_raise

        try:
            with open('test.txt', 'r', encoding='gbk') as f:
                assert f.read() == 'abc123_你好世界'
        except UnicodeDecodeError as e:
            no_raise = False
        else:
            no_raise = True
        assert no_raise

    # default encoding
    Write('test.txt', 'abc123_你好世界')
    no_raise = True
    try:
        with open('test.txt', 'r', encoding='utf-8') as f:
            assert f.read() == 'abc123_你好世界'
    except Exception as e:
        no_raise = False
    assert no_raise


def test_write_pipe():

    'abc123_你好世界' | Write('test.txt')

    with open('test.txt', 'r', encoding='utf-8') as f:
        assert f.read() == 'abc123_你好世界'

    'abc123_你好世界' | Write('test.txt', encoding="gbk")

    no_raise = True
    try:
        with open('test.txt', 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError as e:
        no_raise = False
    assert not no_raise

    with open('test.txt', 'r', encoding='gbk') as f:
        assert f.read() == 'abc123_你好世界'

    raise_msg = ''
    try:
        'abc123_你好世界' | Write('test.txt', name="jack")
    except TypeError as e:
        raise_msg = str(e)
    assert 'unexpected' in raise_msg 

    raise_msg = ''
    try:
        'abc123_你好世界' | Write('test.txt', text="jack")
    except TypeError as e:
        raise_msg = str(e)
    assert 'same' in raise_msg 


    no_raise = True
    try:
        Write('test.txt', "") | "123"
    except TypeError as e:
        no_raise = False
    assert not no_raise

def test_read():

    Write('test.txt', 'abc123_飍雥叒刕叒')

    text = Read('test.txt')
    assert text == 'abc123_飍雥叒刕叒'

    no_raise = True
    try:
        text = Read('test.txt', encoding='gbk')
    except UnicodeDecodeError as e:
        no_raise = False 
    assert not no_raise

    b = ReadB('test.txt')
    assert isinstance(b, bytes)
    assert b == b'abc123_\xe9\xa3\x8d\xe9\x9b\xa5\xe5\x8f\x92\xe5\x88\x95\xe5\x8f\x92'
    f = lambda x: x  
    b = ReadB('test.txt') | f 
    assert isinstance(b, bytes)
    assert b == b'abc123_\xe9\xa3\x8d\xe9\x9b\xa5\xe5\x8f\x92\xe5\x88\x95\xe5\x8f\x92'


    err_msg = ''
    try:
        _ = ReadB('test.txt', encoding='utf-8') # helo
    except ValueError as e:
        err_msg = str(e) 
    assert "binary" in err_msg 

    err_msg = ''
    try:
        f = lambda x:None
        ReadB('test.txt', encoding='utf-8') | f
    except ValueError as e:
        err_msg = str(e)
    assert "binary" in err_msg 

    obj = list(range(10)) | Map(str) | list 
    json.dumps(obj) | Write('test.txt')
    l_obj = Read('test.txt') | json.loads 
    assert isinstance(l_obj, list)
    assert sum(l_obj | Map(int)) == 45
    assert isinstance(ReadB('test.txt'), bytes)


    err_msg = ''
    try:
        'abc123' | Read("test.txt")
    except TypeError as e:
        err_msg = str(e)
    assert "OR operation not allowed" in err_msg 


# test_write_empty_text()
# test_write_wrong_type()
# test_write_encoding()
# test_write_pipe()
# test_read()
