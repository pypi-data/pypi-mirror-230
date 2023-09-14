
from chrysacase import ChrysalideTestCase
from pychrysalide.common import encode_hex, decode_hex_digit


class TestHexValues(ChrysalideTestCase):
    """TestCase for common hexadecimal features*"""

    def testHexEncoding(self):
        """Convert data to hex string."""

        ref = b'ABC'

        self.assertEqual(encode_hex(ref), ref.hex())

        ref = 'ABC'

        self.assertEqual(encode_hex(ref), bytes(ref, 'ascii').hex())

        ref = 'ABC'

        self.assertEqual(encode_hex(ref, False), bytes(ref, 'ascii').hex().upper())


    def testHexDecoding(self):
        """Convert a hex string to value."""

        self.assertEqual(decode_hex_digit('A'), 0xa)
