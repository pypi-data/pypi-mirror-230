#!/usr/bin/python3
# -*- coding: utf-8 -*-


# S'assure du bon fonctionnement des blocs basiques


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis import StudyProject
from pychrysalide.core import wait_for_all_global_works
import os
import sys


class TestProjectFeatures(ChrysalideTestCase):
    """TestCase for projects."""

    @classmethod
    def setUpClass(cls):

        super(TestProjectFeatures, cls).setUpClass()

        cls.log('Compile binary "hm" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s hm > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestProjectFeatures, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testDisassemblyCache(self):
        """Check disassembly cache availability for loaded binaries."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'hm')
        self.assertIsNotNone(cnt)

        prj = StudyProject()
        prj.discover(cnt, True)

        wait_for_all_global_works()

        self.assertTrue(len(prj.contents) == 1)

        binary = prj.contents[0]

        self.assertIsNotNone(binary)
        self.assertIsNotNone(binary.disassembled_cache)

        cnt = FileContent(fullname[:baselen] + 'hm')
        self.assertIsNotNone(cnt)

        prj = StudyProject()
        prj.discover(cnt)

        wait_for_all_global_works()

        self.assertTrue(len(prj.contents) == 1)

        binary = prj.contents[0]

        self.assertIsNotNone(binary)
        self.assertIsNone(binary.disassembled_cache)
