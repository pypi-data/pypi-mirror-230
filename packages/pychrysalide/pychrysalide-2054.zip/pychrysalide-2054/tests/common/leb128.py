
from chrysacase import ChrysalideTestCase
from pychrysalide.common import pack_uleb128, unpack_uleb128, pack_leb128, unpack_leb128
from pychrysalide.common import PackedBuffer


class TestLEB128Values(ChrysalideTestCase):
    """TestCase for common LEB128 features*"""

    def testUnsignedLeb128Encoding(self):
        """Pack and unpack unsigned LEB128 values."""

        cases = {
            624485: b'\xe5\x8e\x26',
            127: b'\x7f',
            128: b'\x80\x01',
        }

        for value, encoding in cases.items():

            pbuf = PackedBuffer()

            status = pack_uleb128(value, pbuf)
            self.assertTrue(status)

            self.assertEqual(pbuf.payload_length, len(encoding))

            pbuf.rewind()

            got = pbuf.extract(len(encoding))

            self.assertEqual(got, encoding)

            self.assertFalse(pbuf.more_data)

        for value, encoding in cases.items():

            pbuf = PackedBuffer()
            pbuf.extend(encoding, False)

            pbuf.rewind()

            got = unpack_uleb128(pbuf)
            self.assertIsNotNone(got)

            self.assertEqual(got, value)


    def testSignedLeb128Encoding(self):
        """Pack and unpack signed LEB128 values."""

        cases = {
            -123456: b'\xc0\xbb\x78',
            -42: b'\x56',
            -9001: b'\xd7\xb9\x7f',
        }

        for value, encoding in cases.items():

            pbuf = PackedBuffer()

            status = pack_leb128(value, pbuf)
            self.assertTrue(status)

            self.assertEqual(pbuf.payload_length, len(encoding))

            pbuf.rewind()

            got = pbuf.extract(len(encoding))

            self.assertEqual(got, encoding)

            self.assertFalse(pbuf.more_data)

        for value, encoding in cases.items():

            pbuf = PackedBuffer()
            pbuf.extend(encoding, False)

            pbuf.rewind()

            got = unpack_leb128(pbuf)
            self.assertIsNotNone(got)

            self.assertEqual(got, value)


    def testTooBigLeb128Encodings(self):
        """Prevent overflow for LEB128 values."""

        pbuf = PackedBuffer()
        pbuf.extend(b'\x80' * 10 + b'\x7f', False)

        pbuf.rewind()

        got = unpack_uleb128(pbuf)

        self.assertIsNone(got)

        pbuf = PackedBuffer()
        pbuf.extend(b'\x80' * 10 + b'\x7f', False)

        pbuf.rewind()

        got = unpack_leb128(pbuf)

        self.assertIsNone(got)

