#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


import pychrysalide
from chrysacase import ChrysalideTestCase
from pychrysalide import arch
from pychrysalide.arch import ImmOperand



class TestImmediate(ChrysalideTestCase):
    """TestCase for arch.ImmOperand."""


    def validateValue(self, value, size, padding, strings):
        """Check all kinds of things with a given immediate operand."""

        display = [
            ImmOperand.IOD_BIN, ImmOperand.IOD_OCT,
            ImmOperand.IOD_DEC,
            ImmOperand.IOD_HEX
        ]

        for d in display:

            op = ImmOperand(size, value)

            self.assertTrue(op.size == size)
            self.assertTrue(op.value == value)

            op.padding = padding
            op.display = d

            string = op.to_string()
            self.assertEqual(string, strings[d])


    def testByteOne(self):
        """Run sanity checks on immediate operand with value 1."""

        strings = {
            ImmOperand.IOD_BIN: 'b1',
            ImmOperand.IOD_OCT: '01',
            ImmOperand.IOD_DEC: '1',
            ImmOperand.IOD_HEX: '0x1'
        }

        self.validateValue(1, arch.MDS_8_BITS_UNSIGNED, False, strings)


    def testByteOnePadded(self):
        """Run sanity checks on immediate operand with padded value 1."""

        strings = {
            ImmOperand.IOD_BIN: 'b00000001',
            ImmOperand.IOD_OCT: '01',
            ImmOperand.IOD_DEC: '1',
            ImmOperand.IOD_HEX: '0x01'
        }

        self.validateValue(1, arch.MDS_8_BITS_UNSIGNED, True, strings)
