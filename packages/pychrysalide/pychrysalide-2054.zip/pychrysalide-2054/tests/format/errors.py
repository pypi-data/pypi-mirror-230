#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider la gestion des erreurs relevées.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.arch import vmpa
from pychrysalide.format import BinFormat
from pychrysalide.format.elf import ElfFormat
import os
import sys


class TestFormatErrors(ChrysalideTestCase):
    """TestCase for format.BinFormat errors."""

    @classmethod
    def setUpClass(cls):

        super(TestFormatErrors, cls).setUpClass()

        cls.log('Compile binary "strings" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s%self strings > /dev/null 2>&1' % (dirpath, os.sep))


    @classmethod
    def tearDownClass(cls):

        super(TestFormatErrors, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s%self clean > /dev/null 2>&1' % (dirpath, os.sep))


    def testBasic(self):
        """Perform some sanity tests on format error handling."""

        errlen = 3

        pattern = []

        for i in range(errlen):

            addr = vmpa(vmpa.VMPA_NO_PHYSICAL, 0x100 + i * 0x10)

            pattern.append([BinFormat.BFE_STRUCTURE, addr, 'random desc #%d' % i])

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'elf' + os.sep + 'strings')
        fmt = ElfFormat(cnt)

        for i in range(errlen):

            fmt.add_error(pattern[i][0], pattern[i][1], pattern[i][2])

        self.assertEqual(len(fmt.errors), errlen)
