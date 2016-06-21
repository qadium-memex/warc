"""
warc.utils
~~~~~~~~~~

This file is part of warc

:copyright: (c) 2012 Internet Archive
"""
from builtins import str, object, dict
from past.builtins import basestring

import collections


class CaseInsensitiveDict(collections.MutableMapping):
    """Almost like a dictionary, but keys are case-insensitive.

        >>> d = CaseInsensitiveDict(foo=1, Bar=2)
        >>> d['foo']
        1
        >>> d['bar']
        2
        >>> d['Foo'] = 11
        >>> d['FOO']
        11
        >>> d.keys()
        ["foo", "bar"]
    """
    def __init__(self, data=None, **kwargs):
        self._store = collections.OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, keyval[1])
            for (lowerkey, keyval)
            in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))

class FilePart(object):
    """File interface over a part of file.

    Takes a file and length to read from the file and returns a file-object
    over that part of the file.
    """
    def __init__(self, fileobj, length):
        self.fileobj = fileobj
        self.length = length
        self.offset = 0
        self.buf = ""

    def read(self, size=-1):
        if size == -1:
            return self._read(self.length)
        else:
            return self._read(size)

    def _read(self, size):
        if len(self.buf) >= size:
            content = self.buf[:size]
            self.buf = self.buf[size:]
        else:
            size = min(size, self.length - self.offset - len(self.buf))
            content = self.buf + self.fileobj.read(size)
            self.buf = ""
        self.offset += len(content)
        return content

    def _unread(self, content):
        self.buf = content + self.buf
        self.offset -= len(content)

    def readline(self):
        chunks = []
        chunk = self._read(1024)
        while chunk and "\n" not in chunk:
            chunks.append(chunk)
            chunk = self._read(1024)

        if "\n" in chunk:
            index = chunk.index("\n")
            self._unread(chunk[index+1:])
            chunk = chunk[:index+1]
        chunks.append(chunk)
        return "".join(chunks)

    def __iter__(self):
        line = self.readline()
        while line:
            yield line
            line = self.readline()
