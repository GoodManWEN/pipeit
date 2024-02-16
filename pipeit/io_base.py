from types import ClassMethodDescriptorType
from typing import Callable, Union, Type, Any
from .base import AbstractSelfModifiedClass, PipeManagerEnd

class AbstractIO(object):

    def __init__(self):
        super(AbstractIO, self).__init__()

    def __call__(self, _iter):
        return RuntimeError("Method not allowed")

    def __iter__(self):
        return RuntimeError("Method not allowed")

    def __ror__(self, other: Any) -> Union[int, Any]:
        raise TypeError("ROR operation not allowed")

    def __or__(self, other: Any) -> Any:
        raise TypeError("OR operation not allowed")


class ReadPseudo:
    """Used as input type check"""
    def __init__(self, file_name: str, encoding: Union[None, str] = None):
        self._file_name = file_name
        self._encoding = encoding


class WritePseudo:
    """Used as input type check"""
    def __init__(self, file_name: str, text: Union[str, bytes], encoding: Union[None, str] = None):
        self._file_name = file_name
        self._text = text
        self._encoding = encoding


def _ast_bitor_detect(code: str) -> str:
    from ast import parse, walk, unparse, Expr, Str, BitOr
    tree = parse(code)
    for node in walk(tree):
        if isinstance(node, BitOr):
            return True
    return False 

    # # The following code is used to remove comments from 'code'
    #     if isinstance(node, Expr) and isinstance(node.value, Str):
    #         node.value.s = ""
    # filtered_code = unparse(tree)
    # return filtered_code


class BaseRead(AbstractIO):

    @classmethod
    def _read_type(cls) -> str:
        raise NotImplementedError()

    def __new__(cls, *args, **kwargs) -> Union[str, bytes, Type['BaseRead']]:
        from inspect import currentframe, getframeinfo
        
        caller_frame = currentframe().f_back
        caller_context = ''.join(getframeinfo(caller_frame).code_context)
        if _ast_bitor_detect(caller_context.strip()):
            return super().__new__(cls)
        else:
            try:
                rp = ReadPseudo(*args, **kwargs)
            except Exception as e:
                raise e
            file_name = rp._file_name
            encoding = None  
            if 'b' not in cls._read_type():
                if rp._encoding is None:
                    encoding = 'utf-8'
                else:
                    encoding = rp._encoding
            else:
                if rp._encoding is not None:
                    raise ValueError("binary mode doesn't take an encoding argument")
            with open(file_name, cls._read_type(), encoding=encoding) as f:
                return f.read()

    def __init__(self, file_name: str, encoding: Union[None, str] = None):
        self.file_name = file_name
        self.encoding = encoding
        self._storage = None
        encoding = None
        if 'b' not in self.__class__._read_type():
            if self.encoding is None:
                encoding = 'utf-8'
            else:
                encoding = self.encoding
        else:
            if self.encoding is not None:
                raise ValueError("binary mode doesn't take an encoding argument")
        with open(file_name, self.__class__._read_type(), encoding=encoding) as f:
            self._storage = f.read()

    def __or__(self, other: Any):
        if isinstance(other, Callable):
            return other(self._storage)
        elif isinstance(other, PipeManagerEnd):
            return self._storage
        return other


class BaseWrite(AbstractIO):

    @classmethod
    def _write_type(cls) -> str:
        raise NotImplementedError()

    def __new__(cls, *args, **kwargs) -> Union[int, Type['BaseWrite']]:
        from inspect import currentframe, getframeinfo

        caller_frame = currentframe().f_back
        caller_context = ''.join(getframeinfo(caller_frame).code_context)
        if _ast_bitor_detect(caller_context.strip()):
            return super().__new__(cls)
        else:
            try:
                wp = WritePseudo(*args, **kwargs)
            except Exception as e:
                raise e
            file_name, text = wp._file_name, wp._text
            encoding = None 
            if 'b' not in cls._write_type():
                if wp._encoding is None:
                    encoding = 'utf-8'
                else:
                    encoding = wp._encoding
            else:
                if wp._encoding is not None:
                    raise ValueError("binary mode doesn't take an encoding argument")
            with open(file_name, cls._write_type(), encoding=encoding) as f:
                return f.write(text)

    def __init__(self, file_name: str, text: Union[str, bytes, None] = None, encoding: Union[None, str] = None):
        self.file_name = file_name
        self.encoding = encoding
        self._storage = None
        if text is not None:
            raise TypeError("Can't pass in text with pipe and specified text at the same time")

    def __ror__(self, other: Any) -> Union[int, Any]:
        if isinstance(other, Union[str, bytes]):
            encoding = None 
            if 'b' not in self.__class__._write_type():
                if self.encoding is None:
                    encoding = 'utf-8'
                else:
                    encoding = self.encoding
            else:
                if self.encoding is not None:
                    raise ValueError("binary mode doesn't take an encoding argument")
            with open(self.file_name, self.__class__._write_type(), encoding=encoding) as f:
                return f.write(other)
        return other