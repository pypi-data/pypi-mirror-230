#!/usr/bin/python3
# -*- coding: utf-8 -*-


# S'assure du bon fonctionnement des blocs basiques


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis import LoadedBinary
from pychrysalide.arch import ArchInstruction
from pychrysalide.format.elf import ElfFormat
import os
import sys


class TestDisassLoop(ChrysalideTestCase):
    """TestCase for loop detection."""

    @classmethod
    def setUpClass(cls):

        super(TestDisassLoop, cls).setUpClass()

        cls.log('Compile binary "h2" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s h2 > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestDisassLoop, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testLoopOverflow(self):
        """Ensure loop number does't not get overestimated."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'h2')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('main')
        self.assertIsNotNone(sym)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 2)
