import io
import os
import typing

from ._base import Filelike, PositionInfo

if hasattr(typing, 'Protocol'):
    class _PythonFile(typing.Protocol):
        def read(self, n:int) -> bytes: ...
        def seek(self, __offset:int, __whence:int=os.SEEK_SET) -> int: ...
        def tell(self) -> int: ...



class File(Filelike):
    " thin wrapper around python file-like objects "
    def __init__(self, fileobj:typing.Union['_PythonFile', str], *, size:typing.Optional[int]=None):
        " wraps a python low-level file like object  "
        super().__init__(moduleName='file')
        if isinstance(fileobj, str):
            fileobj = open(fileobj, 'rb')
        if size is None:
            size = fileobj.seek(0, os.SEEK_END)
            fileobj.seek(0)
        self._size = size
        self.f = fileobj
        #self.name = fileobj.name

    def getPositionInfo(self, pos: int) -> PositionInfo:
        name:typing.Optional[str] = None
        if hasattr(self.f, 'name'): name = getattr(self.f, 'name')
        return PositionInfo(file=self, name=name, pos=pos)

    def read(self, n:int=-1) -> bytes: return self.f.read(n)
    def seek(self, offset: int, whence:int=os.SEEK_SET) -> int:
        return self.f.seek(offset, whence)
    def size(self) -> int: return self._size
    def tell(self) -> int: return self.f.tell()

def fromBytes(data:bytes) -> File:
    " syntactic sugar for `File(io.BytesIO(data))` "
    return File(io.BytesIO(data))