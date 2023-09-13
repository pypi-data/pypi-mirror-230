
import os
import typing
from ._base import Filelike, PositionInfo

class JoinedFiles(Filelike):
    class _RelativeOffset:
        def __init__(self, idx:int, offset:int):
            self.idx = idx
            self.offset = offset

    class PartInfo:
        def __init__(self, idx:int, offset:int, size:int):
            self.idx = idx
            self.offset = offset
            self.size = size

    def __init__(self, parts:'typing.List[Filelike]'):
        super().__init__(moduleName='join')
        self.parts = parts
        self._pos:int = 0
        self._size:int = sum(part.size() for part in parts)
        self._offsets:typing.List[int] = []
        self._currentIndex = 0
        offset = 0
        for part in parts:
            self._offsets.append(offset)
            offset += part.size()

    def _getRelativeOffset(self, offset:int) -> _RelativeOffset:
        # check current part first
        idx = self._currentIndex
        partOffset = self._offsets[idx]
        partSize = self.parts[idx].size()
        if offset >= partOffset and offset < partOffset+partSize:
            return JoinedFiles._RelativeOffset(idx=idx, offset=offset-partOffset)

        # no match -> check other parts
        for i, partOffset in enumerate(self._offsets):
            if partOffset > offset: break
            idx = i

        partOffset = self._offsets[idx]
        partSize = self.parts[idx].size()
        return JoinedFiles._RelativeOffset(idx=idx, offset=offset-partOffset)

    def __repr__(self) -> str:
        return f"JoinedFiles({', '.join([repr(part) for part in self.parts])})"

    def getPositionInfo(self, pos: int) -> PositionInfo:
        info = self._getRelativeOffset(pos)
        part = self.parts[info.idx]
        return part.getPositionInfo(info.offset)

    def read(self, n: int = -1) -> bytes:
        if n < 0: n = self._size - self._pos
        if n <= 0: return b''

        rc = b''
        info = self._getRelativeOffset(self._pos)
        while True:
            f = self.parts[info.idx]
            f.seek(info.offset)
            data = f.read(n - len(rc))
            if not data: break
            rc += data
            self._pos += len(data)
            info = self._getRelativeOffset(self._pos)
            self._currentIndex = info.idx
        return rc

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            self._pos = offset
        elif whence == os.SEEK_CUR:
            self._pos += offset
        elif whence == os.SEEK_END:
            self._pos = self._size + offset
        else: raise ValueError(f"seek(): unsupported whence param: {whence}")

        if self._pos < 0: self._pos = 0
        if self._pos > self._size: self._pos = self._size

        # find the part that matches our position
        idx = 0
        for i, offset in enumerate(self._offsets):
            if self._pos < offset: break
            idx = i
        self._currentIndex = idx

        return self._pos
 
    def size(self) -> int: return self._size
    def tell(self) -> int: return self._pos

def join(*parts: Filelike):
    " combines filelike objects into a seamless whole, i.e. read() calls should not stop at part boundaries "
    return JoinedFiles(list(parts))