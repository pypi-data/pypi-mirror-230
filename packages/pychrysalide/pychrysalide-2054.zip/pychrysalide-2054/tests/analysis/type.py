#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import DataType


class TestDataType(ChrysalideTestCase):
    """TestCase for analysis.DataType."""


    def testTypeSubclassing(self):
        """Verify the data type subclassing is working."""

        class MyType(DataType):

            def __init__(self, num):
                super(MyType, self).__init__()
                self._num = num

            def _to_string(self, include):
                return '%x' % self._num

            def _dup(self):
                return MyType(self._num)

        tp = MyType(0x123)

        self.assertEqual(str(tp), '123')

        tp2 = tp.dup()

        self.assertEqual(str(tp), str(tp2))


    def testTypeDefaultProperties(self):
        """Check for default values of some type properties."""

        class MyPropType(DataType):
            pass

        tp = MyPropType()

        self.assertTrue(tp.handle_namespaces)

        self.assertFalse(tp.is_pointer)

        self.assertFalse(tp.is_reference)

        class MyPropType2(DataType):

            def _handle_namespaces(self):
                return True

            def _is_pointer(self):
                return 123 < 1234

            def _is_reference(self):
                return False

        tp2 = MyPropType2()

        self.assertTrue(tp.handle_namespaces)

        self.assertTrue(tp2.is_pointer)

        self.assertFalse(tp2.is_reference)


    def testTypeNamespaces(self):
        """Test the type namespace property."""

        class MyNSType(DataType):

            def __init__(self, name):
                super(MyNSType, self).__init__()
                self._name = name

            def _to_string(self, include):
                return self._name

        tp = MyNSType('TP')
        ns = MyNSType('NS')

        self.assertIsNone(tp.namespace)

        tp.namespace = (ns, '.')

        self.assertEqual(str(tp), 'NS.TP')

        self.assertEqual(tp.namespace, (ns, '.'))


    def testTypeHash(self):
        """Hash a user-defined type."""

        class MyUserType(DataType):

            def __init__(self, name):
                super(MyUserType, self).__init__()
                self._name = name

            def _hash(self):
                return hash(self._name)

        tp = MyUserType('random')

        self.assertEqual(tp.hash, hash('random') & ((1 << 32) - 1))

        class MyOutOfRangeUserType(DataType):

            hard_coded_hash = -8752470794866657507

            def __init__(self, name):
                super(MyOutOfRangeUserType, self).__init__()
                self._name = name

            def _hash(self):
                return self.hard_coded_hash

        tp = MyOutOfRangeUserType('out-of-range')

        self.assertEqual(tp.hash, MyOutOfRangeUserType.hard_coded_hash & ((1 << 32) - 1))
