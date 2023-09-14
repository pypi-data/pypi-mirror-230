#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.types import ClassEnumType


class TestClassEnumType(ChrysalideTestCase):
    """TestCase for analysis.ClassEnumType."""


    def testClassEnumTypeConstructor(self):
        """Build some class/enum types."""

        tp = ClassEnumType(ClassEnumType.ClassEnumKind.STRUCT)

        self.assertEqual(str(tp), '')

        tp = ClassEnumType(ClassEnumType.ClassEnumKind.STRUCT, 'XXX')

        self.assertEqual(str(tp), 'XXX')

        with self.assertRaisesRegex(TypeError, 'Bad class/enum kind.'):

            tp = ClassEnumType(ClassEnumType.ClassEnumKind.COUNT)

        with self.assertRaisesRegex(TypeError, 'invalid value for ClassEnumKind'):

            tp = ClassEnumType(0x1234)
