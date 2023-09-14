#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider la gestion des erreurs relevées.


from chrysacase import ChrysalideTestCase
from pychrysalide.arch import vmpa, mrange
from pychrysalide.format import BinFormat
from pychrysalide.format import BinSymbol
import os
import sys


class SimpleFormat(BinFormat):
    pass


class TestFormatErrors(ChrysalideTestCase):
    """TestCase for format.BinFormat."""


    def create_fake_symbol(self, index):
        saddr = vmpa(index * 0x10, vmpa.VMPA_NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol = BinSymbol(BinSymbol.STP_ENTRY_POINT, srange)
        return symbol


    def testBasicSymbolOperations(self):
        """Deal with the basic operations related to symbols in a binary format."""

        sf = SimpleFormat()

        self.assertTrue(len(list(sf.symbols)) == 0)

        symbols = [ self.create_fake_symbol(i) for i in range(4) ]
        s0, s1, s2, s3 = symbols

        for s in symbols:
            sf.add_symbol(s)

        self.assertTrue(len(list(sf.symbols)) == len(symbols))

        sf.remove_symbol(s2)

        self.assertTrue(list(sf.symbols) == [s0, s1, s3])


    def testBadParamsForAdding(self):
        """Check if bad parameters fail for adding a new symbol."""

        sf = SimpleFormat()

        with self.assertRaises(TypeError):
            sf.add_symbol('s')


    def testWrongRemoval(self):
        """Try to remove a wrong symbol from a format."""

        sf = SimpleFormat()

        s23 = self.create_fake_symbol(23)
        sf.remove_symbol(s23)
