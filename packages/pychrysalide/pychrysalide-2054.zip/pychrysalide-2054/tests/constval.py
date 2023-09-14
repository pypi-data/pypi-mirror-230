#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide import PyConstvalObject
from pychrysalide.arch import ArchInstruction
import pickle


class TestConstVal(ChrysalideTestCase):
    """TestCase for PyConstvalObject."""


    def testCreation(self):
        """Validate PyConstvalObject creation from Python."""

        cst = PyConstvalObject(123, 'XXX')

        self.assertEqual(cst, 123)

        self.assertEqual(str(cst), 'XXX')


    def testString(self):
        """Validate the PyConstvalObject implementation."""

        self.assertEqual(ArchInstruction.ILT_JUMP, 1)

        self.assertEqual(str(ArchInstruction.ILT_JUMP), 'ILT_JUMP')


    def testStorage(self):
        """Ensure PyConstvalObject instances are storable."""

        cst = ArchInstruction.ILT_JUMP

        data = pickle.dumps(cst)

        cst = pickle.loads(data)

        self.assertEqual(cst, ArchInstruction.ILT_JUMP)

        self.assertEqual(str(cst), 'ILT_JUMP')
