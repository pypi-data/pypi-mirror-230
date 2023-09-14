#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


import pychrysalide
from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinContent
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.arch import vmpa
from pychrysalide.arch.instructions import RawInstruction


class TestRawInstruction(ChrysalideTestCase):
    """TestCase for arch.instructions.RawInstruction."""

    def testConstructors(self):
        """Build some raw instructions to check their constructors."""

        instr = RawInstruction(vmpa(0), BinContent.MemoryDataSize._32_BITS_UNSIGNED, value=123)
        self.assertIsNotNone(instr)

        data  = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        cnt = MemoryContent(data)

        instr = RawInstruction(vmpa(0), BinContent.MemoryDataSize._32_BITS_UNSIGNED,
                               content=cnt, count=2, endian=BinContent.SourceEndian.LITTLE)
        self.assertIsNotNone(instr)

        with self.assertRaisesRegex(Exception, 'Unable to build the object with the given parameters.'):

            instr = RawInstruction(vmpa(0), BinContent.MemoryDataSize._32_BITS_UNSIGNED,
                                   content=cnt, count=3, endian=BinContent.SourceEndian.LITTLE)
