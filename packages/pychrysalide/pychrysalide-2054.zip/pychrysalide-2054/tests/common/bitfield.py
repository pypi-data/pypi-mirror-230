
from chrysacase import ChrysalideTestCase
from pychrysalide.common import BitField


class TestBitFields(ChrysalideTestCase):
    """TestCase for common.BitField*"""

    def testDuplicateBitField(self):
        """Check duplicated bitfield value."""

        bf = BitField(10, 0)

        bf2 = bf.dup()

        self.assertEqual(bf, bf2)

        self.assertEqual(bf.size, bf2.size)

        self.assertEqual(bf.popcount, bf2.popcount)

    def testResizeBitField(self):
        """Resize bitfields."""

        bf_a = BitField(10, 0)

        bf_b = BitField(6, 0)
        bf_b.resize(10)

        self.assertEqual(bf_a, bf_b)

        bf_a = BitField(133, 1)

        bf_b = BitField(64, 1)
        bf_b.resize(133)

        self.assertEqual(bf_a, bf_b)


    def testBitFieldValues(self):
        """Evaluate bitfields basic values."""

        bf_a = BitField(75, 1)

        bf_b = BitField(75, 0)

        self.assertNotEqual(bf_a, bf_b)

        bf_a = BitField(75, 1)

        bf_b = BitField(75, 0)
        bf_b.set_all()

        self.assertEqual(bf_a, bf_b)

        self.assertEqual(bf_a.popcount, bf_b.popcount)

        bf_a = BitField(75, 1)
        bf_a.reset_all()

        bf_b = BitField(75, 0)

        self.assertEqual(bf_a, bf_b)

        self.assertEqual(bf_a.popcount, bf_b.popcount)


    def testBitFieldLogicalOperations(self):
        """Perform logical operations on bitfields."""

        bf_a = BitField(75, 1)

        bf_b = BitField(75, 0)

        self.assertEqual(bf_a.size, bf_b.size)

        bf_f = bf_a & bf_b

        self.assertEqual(bf_f, bf_b)

        self.assertEqual(bf_f.popcount, bf_b.popcount)

        bf_f = bf_a | bf_b

        self.assertEqual(bf_f, bf_a)

        self.assertEqual(bf_f.popcount, bf_a.popcount)


    def testBitFieldLogicalOperationsAt(self):
        """Perform logical operations on bitfields at a given position."""

        bf_a = BitField(75, 0)

        bf_b = BitField(4, 1)
        bf_b.reset(2, 1)

        bf_a.or_at(bf_b, 63)

        self.assertFalse(bf_a.test(62))

        self.assertTrue(bf_a.test(63))
        self.assertTrue(bf_a.test(64))
        self.assertFalse(bf_a.test(65))
        self.assertTrue(bf_a.test(66))

        self.assertFalse(bf_a.test(67))

        bf_a = BitField(75, 0)

        bf_a.or_at(bf_b, 60)

        self.assertFalse(bf_a.test(59))

        self.assertTrue(bf_a.test(60))
        self.assertTrue(bf_a.test(61))
        self.assertFalse(bf_a.test(62))
        self.assertTrue(bf_a.test(63))

        self.assertFalse(bf_a.test(64))


    def testBitFieldSwitch(self):
        """Switch various bits in bitfields."""

        bf_1 = BitField(75, 1)

        bf_0 = BitField(75, 0)

        bf_t = BitField(75, 0)

        for i in range(75):
            bf_t.set(i, 1)

        self.assertEqual(bf_t, bf_1)

        self.assertEqual(bf_t.popcount, bf_1.popcount)

        for i in range(75):
            bf_t.reset(i, 1)

        self.assertEqual(bf_t, bf_0)

        self.assertEqual(bf_t.popcount, bf_0.popcount)


    def testBitFieldBits(self):
        """Test bits in bitfields."""

        bf = BitField(54, 1)

        self.assertTrue(bf.test(0))

        self.assertTrue(bf.test(53))

        self.assertTrue(bf.test_all(0, 54))

        self.assertFalse(bf.test_none(0, 54))

        bf = BitField(54, 0)

        self.assertFalse(bf.test(0))

        self.assertFalse(bf.test(53))

        self.assertFalse(bf.test_all(0, 54))

        self.assertTrue(bf.test_none(0, 54))


    def testBitFieldWithBitField(self):
        """Test bits in bitfields against other bitfields."""

        bf = BitField(32, 0)
        bf.set(8, 16)

        mask = BitField(8, 1)

        self.assertTrue(bf.test_ones_with(8, mask))
        self.assertTrue(bf.test_ones_with(16, mask))
        self.assertFalse(bf.test_ones_with(17, mask))
        self.assertTrue(bf.test_zeros_with(24, mask))

        bf = BitField(256, 0)
        bf.set(60, 8)
        bf.set(126, 10)

        mask = BitField(4, 1)

        self.assertTrue(bf.test_zeros_with(8, mask))
        self.assertTrue(bf.test_zeros_with(122, mask))

        self.assertFalse(bf.test_zeros_with(58, mask))
        self.assertFalse(bf.test_ones_with(58, mask))
        self.assertTrue(bf.test_ones_with(60, mask))
        self.assertFalse(bf.test_zeros_with(63, mask))
        self.assertTrue(bf.test_ones_with(64, mask))
        self.assertFalse(bf.test_zeros_with(65, mask))
        self.assertFalse(bf.test_ones_with(65, mask))

        self.assertFalse(bf.test_zeros_with(125, mask))
        self.assertFalse(bf.test_ones_with(125, mask))
        self.assertTrue(bf.test_ones_with(128, mask))
        self.assertFalse(bf.test_zeros_with(129, mask))
        self.assertTrue(bf.test_ones_with(132, mask))
        self.assertFalse(bf.test_zeros_with(133, mask))
        self.assertFalse(bf.test_ones_with(133, mask))

        self.assertTrue(bf.test_zeros_with(136, mask))


    def testPopCountForBitField(self):
        """Count bits set to 1 in bitfield."""

        bf = BitField(65, 1)

        self.assertEqual(bf.size, 65)

        self.assertEqual(bf.popcount, 65)


    def testBitFieldComparison(self):
        """Check bitfield comparison."""

        bf_a = BitField(9, 0)
        bf_a.set(0, 1)
        bf_a.set(5, 1)

        bf_b = BitField(9, 1)

        self.assertNotEqual(bf_a, bf_b)


    def testRealCase00(self):
        """Test bits in bitfields against other bitfields in a real case (#02)."""

        bf = BitField(128, 0)

        for b in [ 0, 50, 54, 58, 66, 70, 98 ]:
            bf.set(b, 1)

        mask = BitField(128, 0)

        for b in [ 0, 51 ]:
            mask.set(b, 1)

        self.assertFalse(bf.test_zeros_with(0, mask))

        self.assertTrue(bf.test_zeros_with(1, mask))

        bf = BitField(32, 0)

        mask = BitField(32, 0)

        self.assertTrue(bf.test_zeros_with(0, mask))

        for b in [ 0, 8, 9, 10 ]:
            mask.set(b, 1)

        self.assertTrue(bf.test_zeros_with(0, mask))

        bf = BitField(32, 1)

        self.assertFalse(bf.test_zeros_with(0, mask))

        self.assertTrue(bf.test_ones_with(0, mask))


    def testRealCase01(self):
        """Test bits in bitfields against other bitfields in a real case (#01)."""

        bf = BitField(128, 0)

        mask = BitField(128, 0)

        bits = [ 0, 50, 54, 58, 66, 70, 98 ]

        for b in bits:
            mask.set(b, 1)

        bf.or_at(mask, 0)

        self.assertEqual(mask.popcount, len(bits))

        self.assertEqual(mask.popcount, bf.popcount)
