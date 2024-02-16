from .io_base import BaseRead, BaseWrite

class Read(BaseRead):

    @classmethod
    def _read_type(cls) -> str:
        return 'r'

class ReadB(BaseRead):

    @classmethod
    def _read_type(cls) -> str:
        return 'rb'

class Write(BaseWrite):

    @classmethod
    def _write_type(cls) -> str:
        return 'w' 

class WriteB(BaseWrite):

    @classmethod
    def _write_type(cls) -> str:
        return 'wb' 

