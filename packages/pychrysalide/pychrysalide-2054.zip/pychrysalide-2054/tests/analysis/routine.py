#!/usr/bin/python3
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import BinRoutine


class TestBinaryRoutines(ChrysalideTestCase):
    """TestCase for binary routine."""

    def testUnicodeName(self):
        """Ensure Unicode checks are well performed."""

        name = 'ABC'

        r = BinRoutine()

        r.name = name

        self.assertEqual(r.name, name)
