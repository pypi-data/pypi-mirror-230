#!/usr/bin/python
# -*- coding: utf-8 -*-


# Il arrive que les segments englobent partiellement des sections.
#
# Cela peut être problématique si une section contient une chaîne de taille
# n qui se retrouve à cheval sur deux zones (la section des chaînes découpée
# en deux par exemple).
#
# Au moment d'associer l'instruction chargée à la zone de départ, cette
# dernière n'est pas assez grande car elle ne représente pas la section
# en entier.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import LoadedBinary
from pychrysalide.analysis.contents import FileContent
from pychrysalide.format.elf import ElfFormat
from threading import Event
import os
import sys


class TestOverlappingAreas(ChrysalideTestCase):
    """TestCase for BSS segment overlapping string section."""

    @classmethod
    def setUpClass(cls):

        super(TestOverlappingAreas, cls).setUpClass()

        cls.log('Compile binary "overlapping_areas" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s overlapping_areas > /dev/null 2>&1' % dirpath)


    @classmethod
    def tearDownClass(cls):

        super(TestOverlappingAreas, cls).tearDownClass()

        cls.log('Delete built binaries...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        os.system('make -C %s clean > /dev/null 2>&1' % dirpath)


    def testOOBSectionName(self):
        """Avoid crashing because of overlapping binary areas."""

        fullname = sys.modules[self.__class__.__module__].__file__
        filename = os.path.basename(fullname)

        baselen = len(fullname) - len(filename)

        cnt = FileContent(fullname[:baselen] + 'overlapping_areas')
        self.assertIsNotNone(cnt)

        fmt = ElfFormat(cnt)
        self.assertIsInstance(fmt, ElfFormat)

        binary = LoadedBinary(fmt)

        binary.analyze_and_wait()
