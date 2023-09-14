#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests pour valider la gestion des symboles


from chrysacase import ChrysalideTestCase
from pychrysalide.arch import vmpa, mrange
from pychrysalide.format import BinSymbol


class TestBinarySymbols(ChrysalideTestCase):
    """TestCase for format.BinSymbol."""


    def testSymbolProperties(self):
        """Validate the basic properties of symbols."""

        saddr = vmpa(0x10, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertEqual(symbol.range.length, 0x3)

        symbol.range = mrange(saddr, 0x4)

        self.assertEqual(symbol.range.length, 0x4)

        self.assertEqual(symbol.stype, BinSymbol.SymbolType.ENTRY_POINT)

        symbol.stype = BinSymbol.SymbolType.DATA

        self.assertEqual(symbol.stype, BinSymbol.SymbolType.DATA)

        self.assertEqual(symbol.status, BinSymbol.SymbolStatus.INTERNAL)

        symbol.status = BinSymbol.SymbolStatus.EXPORTED

        self.assertEqual(symbol.status, BinSymbol.SymbolStatus.EXPORTED)

        self.assertEqual(symbol.label, None)

        symbol.label = 'AAA'

        self.assertEqual(symbol.label, 'AAA')

        symbol.label = None

        self.assertEqual(symbol.label, None)


    def testSymbolDefaultStatus(self):
        """Validate the default status for symbols."""

        saddr = vmpa(0x10, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertEqual(symbol.status, BinSymbol.SymbolStatus.INTERNAL)

        self.assertEqual(str(symbol.status), 'SymbolStatus.INTERNAL')


    def testSymbolFlags(self):
        """Play with symbol flags."""

        saddr = vmpa(0x10, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertEqual(symbol.flags, BinSymbol.SymbolFlag.NONE)

        ret = symbol.set_flag(BinSymbol.SymbolFlag.NONE)
        self.assertTrue(ret)

        ret = symbol.has_flag(BinSymbol.SymbolFlag.NONE)
        self.assertFalse(ret)

        ret = symbol.unset_flag(BinSymbol.SymbolFlag.NONE)
        self.assertFalse(ret)

        ret = symbol.set_flag(BinSymbol.SymbolFlag.HAS_NM_PREFIX)
        self.assertTrue(ret)

        ret = symbol.has_flag(BinSymbol.SymbolFlag.HAS_NM_PREFIX)
        self.assertTrue(ret)

        ret = symbol.unset_flag(BinSymbol.SymbolFlag.HAS_NM_PREFIX)
        self.assertTrue(ret)

        ret = symbol.has_flag(BinSymbol.SymbolFlag.HAS_NM_PREFIX)
        self.assertFalse(ret)


    def testSymbolComparison(self):
        """Compare symbols and check the result."""

        saddr = vmpa(0x100, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol0 = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        saddr = vmpa(0x10, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol1 = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        saddr = vmpa(0x100, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x30)
        symbol2 = BinSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertTrue(symbol0 == symbol0)

        self.assertTrue(symbol0 > symbol1)

        self.assertTrue(symbol1 < symbol2)

        self.assertTrue(symbol0 == symbol2)


    def testSymbolSubclassing(self):
        """Verify the symbol subclassing is working."""

        class MySymbol(BinSymbol):
            def _get_label(self):
                return 'AAA'

        saddr = vmpa(0x100, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x3)
        symbol = MySymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertEqual(symbol.label, 'AAA')

        symbol.label = 'BBB'

        self.assertEqual(symbol.label, 'BBB')

        class MyOtherSymbol(BinSymbol):
            pass

        other = MyOtherSymbol(srange, BinSymbol.SymbolType.ENTRY_POINT)

        self.assertEqual(other.label, None)

        other.label = 'CCC'

        self.assertEqual(other.label, 'CCC')
