#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests minimalistes pour valider l'intégration des adresses et espaces mémoire
# depuis Python.


from chrysacase import ChrysalideTestCase
from pychrysalide.arch import vmpa


class TestVmpa(ChrysalideTestCase):
    """TestCase for arch.vmpa."""

    def testInit(self):
        """VMPA values are left uninitialized by default."""

        v = vmpa()

        self.assertIsNone(v.phys)
        self.assertIsNone(v.virt)


    def testAdd(self):
        """Verify the commutative property of addition."""

        a = vmpa(0, 0) + 1

        b = 1 + vmpa(0, 0)

        c = vmpa(1, 1)

        self.assertEqual(a, b)
        self.assertEqual(a, c)


    def testCompareWrong(self):
        """Verify unhandled comparisons with VMPA."""

        a = vmpa()

        with self.assertRaisesRegex(Exception, 'Unable to cast object as VMPA.'):

            self.assertLess(a, 'b')


    def testCompareFair(self):
        """Verify right VMPA comparisons."""

        a = vmpa(0)
        b = vmpa()

        self.assertLess(a, b)

        self.assertGreater(b, a)

        a = vmpa()
        b = vmpa()

        self.assertEqual(a, b)
