#!/usr/bin/python3
# -*- coding: utf-8 -*-


# S'assure du bon fonctionnement des blocs basiques


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis import BinRoutine, LoadedBinary
from pychrysalide.arch import ArchInstruction
from pychrysalide.arch import vmpa
from pychrysalide.format.elf import ElfFormat
from pychrysalide.format import FlatFormat
from pychrysalide.glibext import BinPortion
import os
import sys


class TestBasicBlocks(ChrysalideTestCase):
    """TestCase for basic blocks."""

    @classmethod
    def setUpClass(cls):

        super(TestBasicBlocks, cls).setUpClass()

        cls.log('Compile binary "hello" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s hello > /dev/null 2>&1' % dirpath)

        os.system('make -C %s irreducible > /dev/null 2>&1' % dirpath)

        os.system('make -C %s selfloop > /dev/null 2>&1' % dirpath)

        os.system('make -C %s evalcommand > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestBasicBlocks, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testBlockList(self):
        """Check basic tests for basic block list."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'hello')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('main')
        self.assertIsNotNone(sym)

        found = sym.basic_blocks.find_by_addr(sym.range.addr)
        self.assertIsNotNone(found)

        self.assertEqual(found, list(sym.basic_blocks)[0])

        self.assertEqual(found.index, 0)

        self.assertEqual(found.rank, 0)


    def testIrreducible(self):
        """Validate support for irreducible loops."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'irreducible')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('argstr')
        self.assertIsNotNone(sym)

        found = sym.basic_blocks.find_by_addr(sym.range.addr)
        self.assertIsNotNone(found)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 2)


    def testSelfLoopBlock(self):
        """Validate support for self loop blocks."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'selfloop')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('string_array_len')
        self.assertIsNotNone(sym)

        found = sym.basic_blocks.find_by_addr(sym.range.addr)
        self.assertIsNotNone(found)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 1)


    def testComplexLoopBlock(self):
        """Validate support for complex loop blocks."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'evalcommand')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsNotNone(fmt)

        binary = LoadedBinary(fmt)
        self.assertIsNotNone(binary)

        binary.analyze_and_wait()

        sym = fmt.find_symbol_by_label('evalcommand')
        self.assertIsNotNone(sym)

        found = sym.basic_blocks.find_by_addr(sym.range.addr)
        self.assertIsNotNone(found)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 3)


    def testOtherLoops(self):
        """Check situation with some binary codes old troubles."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        # Malware e8e1bc048ef123a9757a9b27d1bf53c092352a26bdbf9fbdc10109415b5cadac
        # Fonction jinit_color_converter de lib/armeabi/libgame.so

        cnt = FileContent(fullname[:baselen] + 'jinit_color_converter.bin')
        self.assertIsNotNone(cnt)

        fmt = FlatFormat(cnt)

        fmt.set_machine('armv7')

        base = vmpa(0, 0x12a524)

        p = BinPortion(BinPortion.BPC_CODE, base, cnt.size)
        p.rights = BinPortion.PAC_READ | BinPortion.PAC_EXEC

        fmt.register_user_portion(p)

        fmt.register_code_point(base.virt + 1, True)

        sym = BinRoutine()
        sym.range = p.range

        fmt.add_symbol(sym)

        binary = LoadedBinary(fmt)

        status = binary.analyze_and_wait()
        self.assertTrue(status)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 3)

        loop_count = 0

        for ins in binary.processor.instrs:
            for _, dt in ins.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 3)

        # Malware 6e4b64ede44bf4cfb36da04aacc9a22ba73e11be2deac339e275d3bde3b31311
        # Fonction sub_a1bc de lib/armeabi-v7a/liblamelib.so

        cnt = FileContent(fullname[:baselen] + 'sub_a1bc.bin')
        self.assertIsNotNone(cnt)

        fmt = FlatFormat(cnt)

        fmt.set_machine('armv7')

        base = vmpa(0, 0xa1bc)

        p = BinPortion(BinPortion.BPC_CODE, base, cnt.size)
        p.rights = BinPortion.PAC_READ | BinPortion.PAC_EXEC

        fmt.register_user_portion(p)

        fmt.register_code_point(base.virt + 1, True)

        sym = BinRoutine()
        sym.range = p.range

        fmt.add_symbol(sym)

        binary = LoadedBinary(fmt)

        status = binary.analyze_and_wait()
        self.assertTrue(status)

        loop_count = 0

        for blk in sym.basic_blocks:
            for _, dt in blk.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 7)

        loop_count = 0

        for ins in binary.processor.instrs:
            for _, dt in ins.destinations:
                if dt == ArchInstruction.ILT_LOOP:
                    loop_count += 1

        self.assertEqual(loop_count, 7)
