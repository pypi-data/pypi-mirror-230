#!/usr/bin/python
# -*- coding: utf-8 -*-


# Eprouve quelques mécanismes de construction côté Python.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent
from pychrysalide.format.elf import ElfFormat


class TestNonExistingBinary(ChrysalideTestCase):
    """TestCase for non existent binary loading."""

    def testNonExistent(self):
        """Try to load a non existent binary without crashing."""

        cnt = FileContent('non_existing_binary')
        self.assertIsNone(cnt)

        with self.assertRaisesRegex(TypeError, 'argument 1 must be pychrysalide.analysis.BinContent, not None'):

            fmt = ElfFormat(cnt)
