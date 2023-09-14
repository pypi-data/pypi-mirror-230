#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider la gestion des erreurs relevées.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import LoadedBinary
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.arch import vmpa
from pychrysalide.format import FlatFormat
from pychrysalide.glibext import BinPortion


class TestFlatFormat(ChrysalideTestCase):
    """TestCase for format.FlatFormat."""


    def testSimpleFlatFormatContent(self):
        """Load a simple content for a flat format."""

        data  = b'\x00\x00\x00\xef'

        cnt = MemoryContent(data)

        fmt = FlatFormat(cnt)
        fmt.set_machine('armv7')

        base = vmpa(0, 0)

        p = BinPortion(BinPortion.BPC_CODE, base, cnt.size)
        p.rights = BinPortion.PAC_READ | BinPortion.PAC_EXEC

        fmt.register_user_portion(p)

        binary = LoadedBinary(fmt)

        binary.analyze_and_wait()

        self.assertTrue(list(binary.processor.instrs)[0].keyword == 'svc')
