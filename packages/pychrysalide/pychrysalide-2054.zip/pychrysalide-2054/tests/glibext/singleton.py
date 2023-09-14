
from chrysacase import ChrysalideTestCase
from gi.repository import GObject
from pychrysalide.glibext import SingletonCandidate, SingletonFactory


class TestSingleton(ChrysalideTestCase):
    """Test cases for pychrysalide.glibext.SingletonFactory."""


    def testSingletonCreation(self):
        """Create singleton objects."""

        with self.assertRaisesRegex(NotImplementedError, 'SingletonCandidate can not be constructed'):

            sc = SingletonCandidate()

        class NewSingletonImplem(GObject.Object, SingletonCandidate):
            pass

        nsi = NewSingletonImplem()

        self.assertIsNotNone(nsi)


    def testFactoryCreation(self):
        """Create singleton factories."""

        sf = SingletonFactory()

        self.assertIsNotNone(sf)

        class MyFactory(SingletonFactory):
            pass

        msf = MyFactory()

        self.assertIsNotNone(msf)


    def testSingletonMethods(self):
        """Test the singleton methods."""

        class IntegerCacheImplem(GObject.Object, SingletonCandidate):

            def __init__(self, val):
                super().__init__()
                self._val = val

            def _list_inner_instances(self):
                return ()

            def __hash__(self):
                return hash('common-key')

            def __eq__(self, other):
                return self._val == other._val

        val_0 = IntegerCacheImplem(0)
        val_0_bis = IntegerCacheImplem(0)
        val_1 = IntegerCacheImplem(1)

        self.assertEqual(hash(val_0), hash(val_0_bis))
        self.assertEqual(hash(val_0), hash(val_1))

        self.assertEqual(val_0.hash(), val_0_bis.hash())
        self.assertEqual(val_0.hash(), val_1.hash())

        self.assertTrue(val_0 == val_0_bis)
        self.assertFalse(val_0 == val_1)


    def testSingletonFootprint(self):
        """Check for singleton memory footprint."""

        sf = SingletonFactory()


        class IntegerCacheImplem(GObject.Object, SingletonCandidate):

            def __init__(self, val):
                super().__init__()
                self._val = val

            def _list_inner_instances(self):
                return ()

            def __hash__(self):
                return hash('common-key')

            def __eq__(self, other):
                return self._val == other._val

            def _set_read_only(self):
                pass

        val_0 = IntegerCacheImplem(0)
        val_0_bis = IntegerCacheImplem(0)
        val_1 = IntegerCacheImplem(1)

        obj = sf.get_instance(val_0)

        self.assertTrue(obj is val_0)

        obj = sf.get_instance(val_0_bis)

        self.assertTrue(obj is val_0)

        obj = sf.get_instance(val_1)

        self.assertTrue(obj is val_1)

        self.assertEqual(len(obj.inner_instances), 0)


        class MasterCacheImplem(GObject.Object, SingletonCandidate):

            def __init__(self, children):
                super().__init__()
                self._children = children

            def _list_inner_instances(self):
                return self._children

            def _update_inner_instances(self, instances):
                self._children = instances

            def __hash__(self):
                return hash('master-key')

            def __eq__(self, other):
                return False

            def _set_read_only(self):
                pass

        master = MasterCacheImplem(( val_0_bis, val_1 ))

        obj = sf.get_instance(master)

        self.assertTrue(obj.inner_instances[0] is val_0)

        self.assertTrue(obj.inner_instances[1] is val_1)
