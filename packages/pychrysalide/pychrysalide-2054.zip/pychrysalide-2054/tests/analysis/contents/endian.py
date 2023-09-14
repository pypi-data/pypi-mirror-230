#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider le boutisme des accès mémoire.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinContent
from pychrysalide.analysis.contents import FileContent, RestrictedContent
from pychrysalide.arch import vmpa
import tempfile


class TestEndianness(ChrysalideTestCase):
    """TestCase for analysis.BinContent."""

    @classmethod
    def setUpClass(cls):

        super(TestEndianness, cls).setUpClass()

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

        super(TestEndianness, cls).tearDownClass()

        cls.log('Delete file "%s"' % cls._out.name)

        cls._out.close()


    def testMiddleEndianness(self):
        """Test some old endianness."""

        fcnt = FileContent(self._out.name)

        # 16 bits

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u16(start, BinContent.SourceEndian.LITTLE_WORD)
        self.assertEqual(val, 0x1516)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u16(start, BinContent.SourceEndian.BIG_WORD)
        self.assertEqual(val, 0x1615)

        # 32 bits

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u32(start, BinContent.SourceEndian.LITTLE_WORD)
        self.assertEqual(val, 0x17181516)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u32(start, BinContent.SourceEndian.BIG_WORD)
        self.assertEqual(val, 0x16151817)

        # 64 bits

        start = vmpa(0, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u64(start, BinContent.SourceEndian.LITTLE_WORD)
        self.assertEqual(val, 0x0708050603040102)

        start = vmpa(0, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u64(start, BinContent.SourceEndian.BIG_WORD)
        self.assertEqual(val, 0x0201040306050807)


    def testEndianness(self):
        """Test usual endianness."""

        fcnt = FileContent(self._out.name)

        # 16 bits

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u16(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x1615)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u16(start, BinContent.SourceEndian.BIG)
        self.assertEqual(val, 0x1516)

        # 32 bits

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u32(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x18171615)

        start = vmpa(12, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u32(start, BinContent.SourceEndian.BIG)
        self.assertEqual(val, 0x15161718)

        # 64 bits

        start = vmpa(0, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u64(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x0807060504030201)

        start = vmpa(0, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = fcnt.read_u64(start, BinContent.SourceEndian.BIG)
        self.assertEqual(val, 0x0102030405060708)
