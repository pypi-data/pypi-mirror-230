#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant le décodage des types et des routines pour le format Java


from chrysacase import ChrysalideTestCase
from pychrysalide.mangling import JavaDemangler


class TestJavaMangling(ChrysalideTestCase):
    """TestCase for pychrysalide.mangling.JavaDemangler."""

    def testJavaSpecMangling(self):
        """Check Java demangling samples from specifications."""

        demangler = JavaDemangler()

        demangled = demangler.decode_type('I')
        self.assertEqual(str(demangled), 'int')

        demangled = demangler.decode_type('Ljava/lang/Object;')
        self.assertEqual(str(demangled), 'java.lang.Object')

        demangled = demangler.decode_type('[[[D')
        self.assertEqual(str(demangled), 'double [][][]')

        demangled = demangler.decode_routine('(IDLjava/lang/Thread;)Ljava/lang/Object;')
        self.assertEqual(str(demangled), 'java.lang.Object (int, double, java.lang.Thread)')
