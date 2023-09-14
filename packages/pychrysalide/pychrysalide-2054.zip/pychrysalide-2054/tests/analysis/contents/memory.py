#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider l'intégration des contenus résidant
# en mémoire depuis Python.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinContent
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.arch import vmpa, mrange


class TestMemoryContent(ChrysalideTestCase):
    """TestCase for analysis.contents.MemoryContent."""

    def testSimpleAccess(self):
        """Check valid accesses to memory content."""

        data  = b'\x01\x02\x03\x04'
        data += b'\x05\x06\x07\x08'
        data += b'\x11\x12\x13\x00'
        data += b'\x15\x16\x17\x18'
        data += b'\x21\x22\x23\x24'
        data += b'\x25\x26\x27\x28'
        data += b'\x31\x32\x00\x34'
        data += b'\x35\x36\x37\x38'

        cnt = MemoryContent(data)

        start = vmpa(4, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = cnt.read_u8(start)
        self.assertEqual(val, 0x05)

        val = cnt.read_u8(start)
        self.assertEqual(val, 0x06)

        start = vmpa(14, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = cnt.read_u16(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x1817)

        start = vmpa(10, vmpa.VmpaSpecialValue.NO_VIRTUAL)

        val = cnt.read_u32(start, BinContent.SourceEndian.LITTLE)
        self.assertEqual(val, 0x16150013)


    def testWrongAccess(self):
        """Check invalid accesses to memory content."""

        data = b'\x35'

        cnt = MemoryContent(data)

        with self.assertRaisesRegex(Exception, 'Invalid read access.'):

            start = vmpa(1, vmpa.VmpaSpecialValue.NO_VIRTUAL)
            val = cnt.read_u8(start)

        with self.assertRaisesRegex(Exception, 'Invalid read access.'):

            start = vmpa(0, vmpa.VmpaSpecialValue.NO_VIRTUAL)
            val = cnt.read_u16(start, BinContent.SourceEndian.LITTLE)
