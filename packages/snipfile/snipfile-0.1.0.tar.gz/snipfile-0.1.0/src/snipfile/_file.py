import io
import os
import typing

from ._base import Filelike

class File(Filelike):
    " thin wrapper around python file-like objects "
    def __init__(self, fileobj:typing.Union[typing.BinaryIO, str]):
        super().__init__(moduleName='file')
        if isinstance(fileobj, str):
            fileobj = open(fileobj, 'rb')
        self._size = fileobj.seek(0, os.SEEK_END)
        fileobj.seek(0)
        self.f = fileobj
        #self.name = fileobj.name

    def getPositionInfo(self, pos: int) -> typing.Tuple[str,int]:
        return self.f.name, pos

    def read(self, n:int=-1) -> bytes: return self.f.read(n)
    def seek(self, offset: int, whence:int=os.SEEK_SET) -> int:
        return self.f.seek(offset, whence)
    def size(self) -> int: return self._size
    def tell(self) -> int: return self.f.tell()

def fromBytes(data:bytes) -> File:
    " syntactic sugar for `File(io.BytesIO(data))` "
    return File(io.BytesIO(data))