#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.types import BasicType


class TestBasicType(ChrysalideTestCase):
    """TestCase for analysis.BasicType."""


    def testBasicTypeConstructor(self):
        """Build some basic types."""

        tp = BasicType(BasicType.BaseType.VOID)

        self.assertEqual(str(tp), 'void')

        self.assertEqual(tp.base, BasicType.BaseType.VOID)

        with self.assertRaisesRegex(TypeError, 'Bad basic type.'):

            tp = BasicType(BasicType.BaseType.INVALID)

        with self.assertRaisesRegex(TypeError, 'invalid value for BaseType'):

            tp = BasicType(0x1234)
