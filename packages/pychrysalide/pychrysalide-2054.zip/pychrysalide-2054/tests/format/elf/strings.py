#!/usr/bin/python3
# -*- coding: utf-8 -*-


# S'assure que les chaînes présentes sont bien chargées en tant que telles.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis import LoadedBinary
from pychrysalide.arch import RawInstruction
from pychrysalide.format.elf import ElfFormat
from threading import Event
import os
import sys


class TestElfString(ChrysalideTestCase):
    """TestCase for ELF strings."""

    @classmethod
    def setUpClass(cls):

        super(TestElfString, cls).setUpClass()

        cls.log('Compile binary "strings" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s strings > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestElfString, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testElfStrings(self):
        """Ensure available strings are loaded as strings."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'strings')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsInstance(fmt, ElfFormat)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        expected = {
            'hello_arm_str'        : False,
            'no_command_line_str'  : False,
            'got_command_line_str' : False
        }

        for sym in binary.format.symbols:

            if sym.label in expected.keys():

                ins = binary.processor.find_instr_by_addr(sym.range.addr)

                if type(ins) is RawInstruction:
                    expected[sym.label] = ins.is_string

        for k in expected.keys():
            self.assertTrue(expected[k])
