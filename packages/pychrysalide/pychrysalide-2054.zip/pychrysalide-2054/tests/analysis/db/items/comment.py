#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant la manipulation des commentaires


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.db.items import DbComment
from pychrysalide.glibext import BufferLine


class TestDbComment(ChrysalideTestCase):
    """TestCase for analysis.db.items.DbComment."""


    def testCreation(self):
        """Ensure comments are buildable from Python."""

        c0 = DbComment(0, BufferLine.BLF_HAS_CODE, repeatable=True)

        self.assertIsNotNone(c0)

        with self.assertRaises(TypeError):

            c1 = DbComment(0, BufferLine.BLF_HAS_CODE, text=None, before=False)

        c2 = DbComment(0, BufferLine.BLF_HAS_CODE, text='None', before=False)

        self.assertIsNotNone(c2)
