
import os
import snipfile


def test_join():
    hello = snipfile.fromBytes(b"hello\n")
    world = snipfile.fromBytes(b"world\n")

    helloworld = snipfile.join(hello, world)
    assert helloworld.read() == b'hello\nworld\n'
    assert snipfile.join(world, hello, hello, world).read() == b'world\nhello\nhello\nworld\n'

    empty = snipfile.Slice(helloworld, offset=4, size=0)
    assert snipfile.join(hello, empty, world).read() == b'hello\nworld\n'

    assert snipfile.join(*snipfile.splitAfter(helloworld, b'\n')).read() == b'hello\nworld\n'

    assert snipfile.join(empty, empty, world).read() == b'world\n'

def test_join_empty():
    nothingness = snipfile.join()
    assert nothingness.size() == 0
    assert nothingness.read() == b''

    # JoinedFiles will correct seek positions
    assert nothingness.seek(100) == 0
    assert nothingness.seek(1, whence=os.SEEK_CUR) == 0
    assert nothingness.seek(-100, os.SEEK_CUR) == 0
    assert nothingness.seek(100, os.SEEK_END) == 0
    assert nothingness.seek(-100, os.SEEK_END) == 0

    assert nothingness.read() == b''
    assert nothingness.tell() == 0