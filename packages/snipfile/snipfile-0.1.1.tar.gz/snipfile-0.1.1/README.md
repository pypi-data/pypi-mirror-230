# snipfile

snipfile is a python package that aims to provide easy-to-use primitives for transforming binary files.  

It was written when I needed to write a parser for different sections of binary files. In order to not having to calculate tons of relative offsets all the time (and a desire to write more readable code), I decided to implement the Slice class. The other stuff quickly followed.

### Classes + functions

- `class File(f: fileobj)` wraps other file-like objects, e.g. files opened using `open()`, `io.BytesIO()`, etc.)  
  we rely on the following methods and properties to be present: `.read()`, `.seek()`, `.tell()`, `.name`
- `class Slice(f: Filelike, *, offset:int, size:int)` provides a smaller window into a file. seek() and tell() use positions relative to .offset, and read() won't read beyond the Slice's size
- `cutAt(f: Filelike, *positions:int)` takes a File/Slice/... and returns a list of Slices pointing to sections of it (with the positions you provided as boundaries)  
  e.g. cutAt(f, 5) returns [Slice(offset=0, size=5), Slice(offset=5, size=f.size()-5)]
- `split(f: Filelike, delimiter:bytes)` cuts a file whenever it sees the delimiter (similar to `b'hello\nworld\n'.split('\n')`)
- `splitAfter(f: Filelike, delimiter:bytes)` similar to split(), but keeps the delimiter at the end of each Slice
- `join(*parts: Filelike)` returns a JoinedFile object that behaves the same way as a file containing each of the parts in that order would (join() can be seen as the inverse of cutAt() or splitAfter())
- `punchHole(f:Filelike, start:int, size/end:int)` uses cutAt() and join() to remove a section of the file
- `class Filelike` serves as the base class for the others (File, Slice, ...)
...

### Characteristics + design considerations
- snipfile can work with large files. it won't cache data it reads in memory between read() calls;
- there's no real issue with cutting cutting and joining files into large numbers of chunks;  
  e.g. when 1GB file into 1MB chunks, you will end up with with 1000 Slice objects, each pointing at the same underlying File.
  (it should therefore be possible to write a hex editor with proper insert/remove/undo/redo support without using too much RAM)
  - each Slice consists of nothing more than a pointer to a File object, a start and a size.
    It simply implements read(), tell(), seek(), ... in a way that behave like accessing a file that only contained that part of the file.
- snipfile only provides read access; but you can cut and join slices as you wish after which you can call .writeTo()
  to store the modified data back to disk (but don't overwrite the file in-place unless you know what you're doing)
- we generally assume that the wrapped file doesn't change in size; all our file-like classes will be initialized with position and/or size information, which they then rely on
- snipfile relies heavily on `seek()`. it'll call seek on the underlying file before each `read()` (as it assumes someone else may have messed with the file in the meantime)
- snipfile development relies on type hints to limit the potential for coding errors
- note: at this moment, our Filelike classes don't provide a close() method (and also lack `__enter__()` or `__exit__()`). As there could be any number of objects pointing to the same file, we don't make assumptions on what should happen if you e.g. call close() on a Slice (it could be the only object pointing to that file, but there's simply no way to tell)  
  make sure to call f.close() on the original file-like (if applicable)