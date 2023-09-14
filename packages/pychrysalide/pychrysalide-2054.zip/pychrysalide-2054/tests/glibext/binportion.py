
from chrysacase import ChrysalideTestCase
from pychrysalide.arch import vmpa
from pychrysalide.glibext import BinPortion


class TestPathNames(ChrysalideTestCase):
    """TestCase for glibext.BinPortion*"""


    def testPortionProperties(self):
        """Validate various binary portion properties."""

        p = BinPortion(BinPortion.BinaryPortionCode.RAW, 0x102, 10)

        p.desc = 'ABC'
        self.assertEqual(p.desc, 'ABC')

        self.assertEqual(p.range.addr.phys, None)
        self.assertEqual(p.range.addr.virt, 0x102)
        self.assertEqual(p.range.length, 10)

        p.continuation = True
        self.assertTrue(p.continuation)

        p.continuation = False
        self.assertFalse(p.continuation)

        p.rights = BinPortion.PortionAccessRights.ALL
        self.assertEqual(p.rights, BinPortion.PortionAccessRights.READ | BinPortion.PortionAccessRights.WRITE | BinPortion.PortionAccessRights.EXEC)


    def testPortionMethods(self):
        """Validate some binary portion methods."""

        p = BinPortion(BinPortion.BinaryPortionCode.RAW, 0x102, 10)

        self.assertEqual(p.range.length, 10)

        p.limit_range(10)

        self.assertEqual(p.range.length, 10)

        p.limit_range(6)

        self.assertEqual(p.range.length, 6)


    def testPortionComparison(self):
        """Compare different binary portions."""

        p0 = BinPortion(BinPortion.BinaryPortionCode.CODE, 0x102, 10)

        addr = vmpa(vmpa.VmpaSpecialValue.NO_PHYSICAL, 0x102)
        p1 = BinPortion(BinPortion.BinaryPortionCode.CODE, addr, 10)

        self.assertEqual(p0, p1)
