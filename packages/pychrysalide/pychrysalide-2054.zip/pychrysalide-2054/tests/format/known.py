#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.format import KnownFormat


class TestKnownFormat(ChrysalideTestCase):
    """TestCase for format.KnownFormat."""


    def testKnownFormatConstructor(self):
        """Build Load a simple content for a flat format."""

        with self.assertRaisesRegex(RuntimeError, 'pychrysalide.format.KnownFormat is an abstract class'):
            fmt = KnownFormat()

        class MyKnownFormat(KnownFormat):
            pass

        with self.assertRaisesRegex(TypeError, 'function takes exactly 1 argument .0 given.'):
            fmt = MyKnownFormat()

        class MyKnownFormat2(KnownFormat):
            pass

        with self.assertRaisesRegex(TypeError, 'unable to convert the provided argument to binary content'):
            fmt = MyKnownFormat2(123)

        class MyKnownFormatReady(KnownFormat):
            _key = 'rdy'
            def __init2__(self, cnt):
                super(MyKnownFormatReady, self).__init2__(cnt)

        data  = b'\x00\x00\x00\xef'

        cnt = MemoryContent(data)
        fmt = MyKnownFormatReady(cnt)

        self.assertIsNotNone(fmt)

        self.assertEqual(fmt.key, 'rdy')
