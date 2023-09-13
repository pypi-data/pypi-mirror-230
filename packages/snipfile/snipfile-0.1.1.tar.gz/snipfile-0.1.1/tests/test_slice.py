import os

import snipfile

def test_slice():
    # default values (i.e. the full file)
    slice = snipfile.Slice(snipfile.fromBytes(b'hello world'))
    assert slice.read() == b'hello world'
    assert slice.offset == 0
    assert slice.size() == 11

    # offset only
    slice = snipfile.Slice(snipfile.fromBytes(b'hello world'), offset=3)
    assert slice.read() == b'lo world'
    assert slice.offset == 3
    assert slice.size() == 8

    # size only
    slice = snipfile.Slice(snipfile.fromBytes(b'hello world'), size=4)
    assert slice.read() == b'hell'
    assert slice.offset == 0
    assert slice.size() == 4

    # both
    slice = snipfile.Slice(snipfile.fromBytes(b'hello world'), offset=3, size=5)
    assert slice.read() == b'lo wo'
    assert slice.offset == 3
    assert slice.size() == 5

    # negative offset (i.e. last 5 bytes of the file)
    slice = snipfile.Slice(snipfile.fromBytes(b'hello world'), offset=-5)
    assert slice.read() == b'world'
    assert slice.offset == 6
    assert slice.size() == 5

def test_seek():
    slice = snipfile.Slice(snipfile.fromBytes(b'hello, my dear world'), offset=7, size=7) # "my dear"
    assert slice.read() == b'my dear'
    assert slice.read() == b''

    slice.seek(0, os.SEEK_SET)
    assert slice.read(2) == b'my'
    assert slice.read(1) == b' '
    assert slice.read(6) == b'dear'

    slice.seek(-99, os.SEEK_SET)
    assert slice.tell() == 0
    slice.seek(99, os.SEEK_SET)
    assert slice.tell() == 7

    slice.seek(-4, os.SEEK_CUR)
    assert slice.read() == b'dear'
    slice.seek(-99, os.SEEK_CUR)
    assert slice.tell() == 0

    slice.seek(0, os.SEEK_END)
    assert slice.tell() == 7
    slice.seek(4, os.SEEK_END)
    assert slice.tell() == 7
    slice.seek(-4, os.SEEK_END)
    assert slice.read() == b'dear'



def test_split():
    data = b'a;b'
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b';')]
    assert parts == data.split(b';')

    data = b';'
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b';')]
    assert parts == data.split(b';')

    data = b';;'
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b';')]
    assert parts == data.split(b';')

    data = b'hello world, this.is.a test '
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b" ")]
    assert parts == data.split(b' ')

    data = b'bananabread'
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b'an')]
    assert parts == data.split(b'an')

def test_split_long_delimiter():
    # delimiter's longer than the file
    data = b'abc'
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b'thisislongerthanbuff')]
    assert parts == [b'abc']

    data = b''
    parts = [slice.read() for slice in snipfile.split(snipfile.fromBytes(data), b';')]
    assert parts == [b'']

def test_splitAfter():
    data = b'hello\nworld\n'
    parts = [slice.read() for slice in snipfile.splitAfter(snipfile.fromBytes(data), b'\n')]
    assert parts == [b'hello\n', b'world\n']

def test_cut():
    data = b'hello world'
    parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 2,5,6)]
    assert parts == [b'he', b'llo', b' ', b'world']

    parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 2,-2)]
    assert parts == [b'he', b'llo wor', b'ld']

    # we expect to get empty slices in stead of (omitting empty sections)
    parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 6, 10)]
    assert parts == [b'hello ', b'worl', b'd']
    parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 6, 11)]
    assert parts == [b'hello ', b'world', b'']
    parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 6, 6, 11)]
    assert parts == [b'hello ', b'', b'world', b'']

    # providing cuts in the wrong order leads to an Exception
    try:
        parts = [slice.read() for slice in snipfile.cutAt(snipfile.fromBytes(data), 8,6,4,2)]
        assert False, "we expect the code to raise a ValueError if the user provides cut points in the wrong order"
    except ValueError:
        pass

