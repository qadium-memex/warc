from builtins import str
from builtins import range
from builtins import object

from .. import warc

import os.path

from io import StringIO, BytesIO

class TestWARCHeader(object):
    def test_attrs(self):
        h = warc.WARCHeader({
            "WARC-Type": "response",
            "WARC-Record-ID": "<record-1>",
            "WARC-Date": "2000-01-02T03:04:05Z",
            "Content-Length": "10"
        })
        assert h.type == "response"
        assert h.record_id == "<record-1>"
        assert h.date == "2000-01-02T03:04:05Z"
        assert h.content_length == 10

    def test_item_access(self):
        h = warc.WARCHeader({
            "WARC-Type": "response",
            "X-New-Header": "42"
        })
        assert h['WARC-Type'] == "response"
        assert h['WARC-TYPE'] == "response"
        assert h['warc-type'] == "response"

        assert h['X-New-Header'] == "42"
        assert h['x-new-header'] == "42"

    def test_str(self):
        h = warc.WARCHeader({})
        assert str(h) == "WARC/1.0\r\n\r\n"

        h = warc.WARCHeader({
            "WARC-Type": "response"
        })
        assert str(h) == "WARC/1.0\r\n" + "WARC-Type: response\r\n\r\n"

    def test_init_defaults(self):
        # It should initialize all the mandatory headers
        h = warc.WARCHeader({"WARC-Type": "resource"}, defaults=True)
        assert h.type == "resource"
        assert "WARC-Date" in h
        assert "Content-Type" in h
        assert "WARC-Record-ID" in h

    def test_new_content_types(self):
        def f(type):
            return warc.WARCHeader({"WARC-Type": type}, defaults=True)
        assert f("response")["Content-Type"] == "application/http; msgtype=response"
        assert f("request")["Content-Type"] == "application/http; msgtype=request"
        assert f("warcinfo")["Content-Type"] == "application/warc-fields"
        assert f("newtype")["Content-Type"] == "application/octet-stream"

SAMPLE_WARC_RECORD_TEXT = (
    "WARC/1.0\r\n" +
    "Content-Length: 10\r\n" +
    "WARC-Date: 2012-02-10T16:15:52Z\r\n" +
    "Content-Type: application/http; msgtype=response\r\n" +
    "WARC-Type: response\r\n" +
    "WARC-Record-ID: <urn:uuid:80fb9262-5402-11e1-8206-545200690126>\r\n" +
    "WARC-Target-URI: http://example.com/\r\n" +
    "\r\n" +
    "Helloworld" +
    "\r\n\r\n"
)

class TestWARCReader(object):
    def test_read_header1(self):
        f = StringIO(SAMPLE_WARC_RECORD_TEXT)
        h = warc.WARCReader(f).read_record().header
        assert h.date == "2012-02-10T16:15:52Z"
        assert h.record_id == "<urn:uuid:80fb9262-5402-11e1-8206-545200690126>"
        assert h.type == "response"
        assert h.content_length == 10

    def test_empty(self):
        reader = warc.WARCReader(StringIO(""))
        assert reader.read_record() is None

    def test_read_record(self):
        f = StringIO(SAMPLE_WARC_RECORD_TEXT)
        reader = warc.WARCReader(f)
        record = reader.read_record()
        assert "".join(record.payload) == "Helloworld"

    def read_multiple_records(self):
        f = StringIO(SAMPLE_WARC_RECORD_TEXT * 5)
        reader = warc.WARCReader(f)
        for i in range(5):
            rec = reader.read_record()
            assert rec is not None

class TestWarcFile(object):
    def test_read(self):
        f = warc.WARCFile(fileobj=StringIO(SAMPLE_WARC_RECORD_TEXT))
        assert f.read_record() is not None
        assert f.read_record() is None

    def test_write_gz(self):
        """Test writing multiple member gzip file."""
        buffer = StringIO()
        f = warc.WARCFile(fileobj=buffer, mode="w", compress=True)
        for i in range(10):
            record = warc.WARCRecord(payload="hello %d" % i)
            f.write_record(record)

        GZIP_MAGIC_NUMBER = '\037\213'
        assert buffer.getvalue().count(GZIP_MAGIC_NUMBER) == 10

    def test_long_header(self):
        """Test large WARC header with a CRLF across a 1024 byte boundrary"""
        warc_dir = os.path.dirname(warc.__file__)
        file = os.path.join(warc_dir, '../test_data/crlf_at_1k_boundary.warc.gz')
        f = warc.WARCFile(file)
        h = f.read_record().header
        assert h['WARC-Payload-Digest'] == "sha1:M4VJCCJQJKPACSSSBHURM572HSDQHO2P"

if __name__ == '__main__':
    TestWARCReader().test_read_header()
