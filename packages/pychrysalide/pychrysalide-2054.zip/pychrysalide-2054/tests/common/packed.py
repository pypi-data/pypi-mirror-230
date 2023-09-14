
# Tests pour valider les tampons de données


from chrysacase import ChrysalideTestCase
from pychrysalide.common import PackedBuffer


class TestPackedBuffers(ChrysalideTestCase):
    """TestCase for common.PackedBuffer*"""

    def testPackedBufferConstructor(self):
        """Validate new packed buffers."""

        pbuf = PackedBuffer()
        self.assertIsNotNone(pbuf)


    def testPackedBufferData(self):
        """Play with packed buffer data."""

        pbuf = PackedBuffer()

        data = b'0123456789'

        pbuf.extend(data, False)
        pbuf.extend(data)

        self.assertEqual(pbuf.payload_length, 2 * len(data))

        self.assertFalse(pbuf.more_data)

        pbuf.rewind()

        self.assertTrue(pbuf.more_data)

        got = pbuf.peek(1)
        self.assertEqual(got, b'0')

        got = pbuf.peek(2)
        self.assertEqual(got, b'01')

        pbuf.advance(3)

        got = pbuf.peek(2)
        self.assertEqual(got, b'34')

        pbuf.advance(8)

        got = pbuf.peek(2)
        self.assertEqual(got, b'12')

        pbuf.rewind()

        got = pbuf.extract(4)
        self.assertEqual(got, b'0123')

        got = pbuf.extract(8, True)
        self.assertEqual(got, b'10987654')
