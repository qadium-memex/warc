from builtins import object
from ..utils import FilePart, CaseInsensitiveDict
from io import StringIO

class TestCaseInsensitiveDict(object):

    def test_all(self):
        d = CaseInsensitiveDict()
        d['Foo'] = 1
        assert d['foo'] == 1
        assert 'foo' in d
        assert 'Foo' in d

        assert 'bar' not in d
        d['BAR'] = 2
        assert 'bar' in d
        assert d['bar'] == 2

        assert sorted(d.keys()) == ["BAR", "Foo"]
        assert sorted(d.items()) == [('BAR', 2), ('Foo', 1)]

class TestFilePart(object):
    def setup_method(self, m):
        # 5 chars in each line
        self.text = "\n".join(["aaaa", "bbbb", "cccc", "dddd", "eeee", "ffff"])

    def test_read(self):
        part = FilePart(StringIO(self.text), 0)
        assert part.read() == ""

        part = FilePart(StringIO(self.text), 5)
        assert part.read() == "aaaa\n"

        part = FilePart(StringIO(self.text), 10)
        assert part.read() == "aaaa\nbbbb\n"

        # try with large data
        part = FilePart(StringIO("a" * 10000), 10)
        assert len(part.read()) == 10

    def test_read_with_size(self):
        part = FilePart(StringIO(self.text), 10)
        assert part.read(3) == "aaa"
        assert part.read(3) == "a\nb"
        assert part.read(3) == "bbb"
        assert part.read(3) == "\n"
        assert part.read(3) == ""

    def test_readline(self):
        part = FilePart(StringIO(self.text), 11)
        assert part.readline() == "aaaa\n"
        assert part.readline() == "bbbb\n"
        assert part.readline() == "c"
        assert part.readline() == ""

    def test_iter(self):
        part = FilePart(StringIO(self.text), 11)
        assert list(part) == ["aaaa\n", "bbbb\n", "c"]
