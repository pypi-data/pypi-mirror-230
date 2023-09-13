import typing
from . import _base
from . import _join
from . import _slice

@typing.overload
def punchHole(f: _base.Filelike, *, start:int, size:int) -> _base.Filelike: ...
@typing.overload
def punchHole(f: _base.Filelike, *, start:int, end:int) -> _base.Filelike: ...


def punchHole(f: _base.Filelike, *, start:int, size:typing.Optional[int]=None, end:typing.Optional[int]=None) -> _base.Filelike:
    """ take out a section of f (by combining cutAt() and join())
you can specify the hole either by its start and size or by a start+end position.

- will raise ValueError if start<0, size<0 or end<start
- if you provide both or neither of end and size, we'll also raise a ValueError
- if you attempt to punch an empty hole (i.e. size=0 or start==end), f will be returned unmodified"""
    if end is None:
        if size is None: 
            raise ValueError("please provide a size or end to snipfile.punchHole()")
        end = start+size
    elif size is not None:
        raise ValueError("snipfile.punchHole() only accepts one of size/end")

    size = end-start
    if size < 0: raise ValueError("punchHole(): got hole of negative hole size")
    if start < 0: raise ValueError(f"punchHole() got negative start={repr(start)}")
    if size == 0: return f #shortcut

    before, hole_, after = _slice.cutAt(f, start, end)
    assert hole_.size() == size
    return _join.join(before, after)