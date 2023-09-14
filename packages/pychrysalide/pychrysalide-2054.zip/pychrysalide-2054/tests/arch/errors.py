#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider la gestion des erreurs relevées.


from chrysacase import ChrysalideTestCase
from pychrysalide import arch
from pychrysalide.arch import vmpa
from pychrysalide.arch import ArchProcessor


class TestArchErrors(ChrysalideTestCase):
    """TestCase for arch.ArchProcessor errors."""

    def testBasic(self):
        """Perform some sanity tests on architecture error handling."""

        errlen = 3

        pattern = []

        for i in range(errlen):

            addr = vmpa(vmpa.VMPA_NO_PHYSICAL, 0x100 + i * 0x10)

            pattern.append([ArchProcessor.APE_LABEL, addr, 'random desc #%d' % i])


        class NewProc(ArchProcessor):

            def __init__(self):

                props = {
                    'endianness':   arch.SRE_LITTLE,
                    'mem_size':     arch.MDS_32_BITS_UNSIGNED,
                    'ins_min_size': arch.MDS_32_BITS_UNSIGNED,
                    'vspace':       False
                }

                super(NewProc, self).__init__(**props)


        proc = NewProc()

        for i in range(errlen):

            proc.add_error(pattern[i][0], pattern[i][1], pattern[i][2])

        self.assertEqual(len(proc.errors), errlen)
