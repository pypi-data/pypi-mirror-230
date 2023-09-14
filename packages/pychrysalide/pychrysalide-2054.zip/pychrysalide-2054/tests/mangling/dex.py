#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant le décodage des types et des routines pour le format Dex


from chrysacase import ChrysalideTestCase
from pychrysalide.mangling import DexDemangler


class TestDexMangling(ChrysalideTestCase):
    """TestCase for pychrysalide.mangling.DexDemangler."""

    def check_demangling(self, got, expected):
        """Check a given demangling result."""

        self.assertTrue(str(got) == expected)


    def testDexTypeMangling(self):
        """Check Dex type demangling."""

        demangler = DexDemangler()

        demangled = demangler.decode_type('V')
        self.check_demangling(demangled, 'void')

        demangled = demangler.decode_type('[I')
        self.check_demangling(demangled, 'int []')

        demangled = demangler.decode_type('[[I')
        self.check_demangling(demangled, 'int [][]')

        demangled = demangler.decode_type('Ltoto;')
        self.check_demangling(demangled, 'toto')

        demangled = demangler.decode_type('Ltiti/toto/tata;')
        self.check_demangling(demangled, 'titi.toto.tata')


    def testDexBadTypeMangling(self):
        """Check Dex malformed type mangling."""

        demangler = DexDemangler()

        demangled = demangler.decode_type('Ltiti/toto/tata/;')
        self.assertIsNone(demangled)


    def testDexRoutineMangling(self):
        """Check Dex routine demangling."""

        demangler = DexDemangler()

        demangled = demangler.decode_routine('I')
        self.check_demangling(demangled, 'int ()')


    def testDexBadRoutineMangling(self):
        """Check Dex malformed routine mangling."""

        demangler = DexDemangler()

        demangled = demangler.decode_routine('IX')
        self.assertIsNone(demangled)
