
import snipfile


def test_punchHole():
    f = snipfile.fromBytes(b'hello world')
    assert snipfile.punchHole(f, start=5, size=1).read() == b'helloworld'