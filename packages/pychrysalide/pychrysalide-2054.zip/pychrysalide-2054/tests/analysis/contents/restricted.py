#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider l'intégration des contenus restreints
# depuis Python.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinContent
from pychrysalide.analysis.contents import FileContent, RestrictedContent
from pychrysalide.arch import vmpa, mrange
import tempfile


class TestRestrictedContent(ChrysalideTestCase):
    """TestCase for analysis.contents.RestrictedContent."""

    @classmethod
    def setUpClass(cls):

        super(TestRestrictedContent, cls).setUpClass()

        cls._out = tempfile.NamedTemporaryFile()

        cls._out.write(b'\x01\x02\x03\x04')
        cls._out.write(b'\x05\x06\x07\x08')
        cls._out.write(b'\x11\x12\x13\x14')
        cls._out.write(b'\x15\x16\x17\x18')
        cls._out.write(b'\x21\x22\x23\x24')
        cls._out.write(b'\x25\x26\x27\x28')
        cls._out.write(b'\x31\x32\x33\x34')
        cls._out.write(b'\x35\x36\x37\x38')

        cls._out.flush()

        cls.log('Using temporary file "%s"' % cls._out.name)


    @classmethod
    def tearDownClass(cls):

        super(TestRestrictedContent, cls).tearDownClass()

        cls.log('Delete file "%s"' % cls._out.name)

        cls._out.close()


    def testReadAccess(self):
        """Check valid accesses to restricted content."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 12) # 0x15 ... 0x28

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        val = rcnt.read_u8(start)
        self.assertEqual(val, 0x15)

        val = rcnt.read_u8(start)
        self.assertEqual(val, 0x16)

        val = rcnt.read_u16(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x1817)

        val = rcnt.read_u32(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x24232221)


    def testReadRawAccess(self):
        """Check valid raw accesses to restricted content."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 12) # 0x15 ... 0x28

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        val = rcnt.read_raw(start, 1)
        self.assertEqual(val, b'\x15')

        val = rcnt.read_raw(start, 1)
        self.assertEqual(val, b'\x16')

        val = rcnt.read_raw(start, 2)
        self.assertEqual(val, b'\x17\x18')

        val = rcnt.read_raw(start, 4)
        self.assertEqual(val, b'\x21\x22\x23\x24')


    def testBorderLineAccess(self):
        """Check valid border line accesses to restricted content."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 12) # 0x15 ... 0x28

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u8(start)
        self.assertEqual(val, 0x15)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u16(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x1615)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u32(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x18171615)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u64(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x2423222118171615)

        start = vmpa(23, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u8(start)
        self.assertEqual(val, 0x28)

        start = vmpa(22, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u16(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x2827)

        start = vmpa(20, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u32(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x28272625)

        start = vmpa(16, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_u64(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x2827262524232221)


    def testBorderLineRawAccess(self):
        """Check valid border line raw accesses to restricted content."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 12) # 0x15 ... 0x28

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 1)
        self.assertEqual(val, b'\x15')

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 2)
        self.assertEqual(val, b'\x15\x16')

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 4)
        self.assertEqual(val, b'\x15\x16\x17\x18')

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 8)
        self.assertEqual(val, b'\x15\x16\x17\x18\x21\x22\x23\x24')

        start = vmpa(23, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 1)
        self.assertEqual(val, b'\x28')

        start = vmpa(22, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 2)
        self.assertEqual(val, b'\x27\x28')

        start = vmpa(20, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 4)
        self.assertEqual(val, b'\x25\x26\x27\x28')

        start = vmpa(16, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        val = rcnt.read_raw(start, 8)
        self.assertEqual(val, b'\x21\x22\x23\x24\x25\x26\x27\x28')


    def testWrongAccess(self):
        """Check invalid accesses to restricted content."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 12) # 0x15 ... 0x28

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        with self.assertRaisesRegex(Exception, 'Invalid read access.'):

            start = vmpa(1, vmpa.VmpaSpecialValue.NO_VIRTUAL)
            val = rcnt.read_u8(start)

        with self.assertRaisesRegex(Exception, 'Invalid read access.'):

            start = vmpa(11, vmpa.VmpaSpecialValue.NO_VIRTUAL)
            val = rcnt.read_u16(start, BinContent.SourceEndian.LITTLE)

        with self.assertRaisesRegex(Exception, 'Invalid read access.'):

            start = vmpa(23, vmpa.VmpaSpecialValue.NO_VIRTUAL)
            val = rcnt.read_u16(start, BinContent.SourceEndian.LITTLE)


    def testDescription(self):
        """Ensure restriction range is described."""

        fcnt = FileContent(self._out.name)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 1)

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        self.assertTrue(rcnt.describe().endswith(' [0xc:0xd]'))
