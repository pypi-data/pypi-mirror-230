#!/usr/bin/python3
# -*- coding: utf-8 -*-


# S'assure du bon fonctionnement des blocs basiques


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis import LoadedBinary
from pychrysalide.format.elf import ElfFormat
import os
import sys


class TestARMv7(ChrysalideTestCase):
    """TestCase for ARMv7."""

    @classmethod
    def setUpClass(cls):

        super(TestARMv7, cls).setUpClass()

        cls.log('Compile binary "endofname" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s endofname > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestARMv7, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testBranchLR(self):
        """Ensure some bx instructions are marked as return points."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'endofname')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('endofname')
        self.assertIsNotNone(sym)

        block = list(sym.basic_blocks)[1]

        self.assertEqual(len(block.boundaries[1].destinations), 0)
