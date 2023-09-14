
from chrysacase import ChrysalideTestCase
from pychrysalide.common import fnv1a


class TestFnv1a(ChrysalideTestCase):
    """TestCase for common FNV-1a hashing features."""

    def testFnv1aSamples(self):
        """Compute some Fnv1a hashs."""

        # Test cases from http://isthe.com/chongo/src/fnv/test_fnv.c

        val = fnv1a('')
        self.assertEqual(val, 0xcbf29ce484222325)

        val = fnv1a('chongo was here!\n')
        self.assertEqual(val, 0x46810940eff5f915)
