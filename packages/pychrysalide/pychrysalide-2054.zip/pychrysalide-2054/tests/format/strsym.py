
from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinContent
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.arch import vmpa, mrange
from pychrysalide.format import FlatFormat, StrSymbol


class TestBinarySymbols(ChrysalideTestCase):
    """TestCase for format.StrSymbol."""

    def testStringSymbolConstructors(self):
        """Build string symbols."""

        data = b'ABCD1234'

        cnt = MemoryContent(data)
        fmt = FlatFormat(cnt, 'xxx', BinContent.SourceEndian.LITTLE)

        saddr = vmpa(0x0, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        srange = mrange(saddr, 0x5)

        symbol = StrSymbol(StrSymbol.StringEncodingType.GUESS, fmt, srange)

        self.assertEqual(symbol.raw, b'ABCD1')
        self.assertEqual(symbol.utf8, 'ABCD1')
        self.assertEqual(symbol.encoding, StrSymbol.StringEncodingType.ASCII)

        symbol = StrSymbol(StrSymbol.StringEncodingType.GUESS, string='abcdef', addr=saddr)

        self.assertEqual(symbol.raw, b'abcdef')
        self.assertEqual(symbol.utf8, 'abcdef')
        self.assertEqual(symbol.encoding, StrSymbol.StringEncodingType.ASCII)
