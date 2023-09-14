
from chrysacase import ChrysalideTestCase
from pychrysalide.common import itoa


class TestItoa(ChrysalideTestCase):
    """TestCase for calls to the itoa() implementation."""

    def testItoaCallss(self):
        """Convert some integer values into strings."""

        val = itoa(123, 10)
        self.assertEqual(val, '123')

        val = itoa(-123, 10)
        self.assertEqual(val, '-123')

        val = itoa(0, 10)
        self.assertEqual(val, '0')

        val = itoa(0, 2)
        self.assertEqual(val, '0')

        val = itoa(127, 2)
        self.assertEqual(val, '1111111')

        val = itoa(101, 2)
        self.assertEqual(val, '1100101')
