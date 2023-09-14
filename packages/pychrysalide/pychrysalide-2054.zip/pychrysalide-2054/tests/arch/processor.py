#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


import pychrysalide
from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide import arch
from pychrysalide.arch import ArchProcessor
from pychrysalide.arch import ProcContext
from pychrysalide.arch import vmpa
from pychrysalide.format import FlatFormat


class TestProcessor(ChrysalideTestCase):
    """TestCase for arch.ArchProcessor."""


    def testGI(self):
        """Validate the GObject introspection."""

        with self.assertRaises(RuntimeError):
            np = ArchProcessor()


        class NewContext(ProcContext):
            pass

        class NewProcWithCtx(ArchProcessor):

            def __init__(self):

                props = {
                    'endianness':   arch.SRE_LITTLE,
                    'mem_size':     arch.MDS_32_BITS_UNSIGNED,
                    'ins_min_size': arch.MDS_32_BITS_UNSIGNED,
                    'vspace':       False
                }

                super(NewProcWithCtx, self).__init__(**props)

            def _get_context(self):
                return NewContext()

            def _disassemble(self, ctx, content, pos, format):
                return None


        np = NewProcWithCtx()

        data  = b'\x01\x02\x03\x04'
        cnt = MemoryContent(data)
        fmt = FlatFormat(cnt)

        ctx = np.get_context()
        self.assertTrue(type(ctx) == NewContext)

        pos = vmpa(0)

        ins = np.disassemble(ctx, cnt, pos, fmt)

        self.assertIsNone(ins)
