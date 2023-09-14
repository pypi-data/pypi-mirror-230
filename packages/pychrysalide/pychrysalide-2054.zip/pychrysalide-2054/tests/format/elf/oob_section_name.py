#!/usr/bin/python
# -*- coding: utf-8 -*-


# Une section peut avoir un index pour son nom démesurément grand (et invalide).
#
# Si la section des chaînes de caractères est toute aussi grande et invalide,
# l'index invalide reste suffisamment cohérent pour passer les premiers tests
# de extract_name_from_elf_string_section() et conduire ensuite à un plantage
# lors de l'accès concret, au moment de l'appel à strlen().


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.format.elf import ElfFormat
import os
import sys


class TestNonExistingBinary(ChrysalideTestCase):
    """TestCase for corrupted ELF binaries with wrong section names."""

    @classmethod
    def setUpClass(cls):

        super(TestNonExistingBinary, cls).setUpClass()

        cls.log('Compile binary "oob_section_name" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s oob_section_name > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestNonExistingBinary, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testOOBSectionName(self):
        """Avoid crashing when dealing with OutOfBound section names."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'oob_section_name')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsInstance(fmt, ElfFormat)
