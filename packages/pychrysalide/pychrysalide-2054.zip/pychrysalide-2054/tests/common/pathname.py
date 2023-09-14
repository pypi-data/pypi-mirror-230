
from chrysacase import ChrysalideTestCase
from pychrysalide.common import build_relative_filename, build_absolute_filename


class TestPathnames(ChrysalideTestCase):
    """TestCase for common pathname features."""

    @classmethod
    def setUpClass(cls):

        super(TestPathnames, cls).setUpClass()

        cls._tests = [
            {
                'ref'      : '/a/b/d',
                'target'   : '/a/b/e/f',
                'relative' : 'e/f'
            },
            {
                'ref'      : '/a/b/c/d',
                'target'   : '/a/b/f',
                'relative' : '../f'
            },
            {
                'ref'      : '/a/b/c/d',
                'target'   : '/a/b/c/e',
                'relative' : 'e'
            },
            {
                'ref'      : '/a/bb/c/d',
                'target'   : '/a/b/e/f',
                'relative' : '../../b/e/f'
            },
            {
                'ref'      : '/a/b/c/d',
                'target'   : '/a/bb/e/f',
                'relative' : '../../bb/e/f'
            },
            {
                'ref'      : '/a/b/c/d',
                'target'   : '/f',
                'relative' : '../../../f'
            },
            {
                'ref'      : '/z/b/c/d',
                'target'   : '/a/b/e/f',
                'relative' : '../../../a/b/e/f'
            },
            {
                'ref'      : '/a/bbb/c/d',
                'target'   : '/a/bbc/e/f',
                'relative' : '../../bbc/e/f'
            }
        ]


    def testBuildingRelative(self):
        """Build valid relative paths."""

        for tst in self._tests:

            got = build_relative_filename(tst['ref'], tst['target'])

            self.assertEqual(got, tst['relative'])


    def testBuildingAbsolute(self):
        """Build valid absolute paths."""

        for tst in self._tests:

            got = build_absolute_filename(tst['ref'], tst['relative'])

            self.assertEqual(got, tst['target'])


    def testBuildingWrongAbsolute(self):
        """Build invalid absolute paths."""

        with self.assertRaisesRegex(Exception, 'Relative path is too deep.'):

            got = build_absolute_filename('/a/b', '../../c')


    def testPathnameSamples(self):
        """Play with some path samples."""

        filename = build_absolute_filename('/tmp/deep', '../myfile')
        self.assertEqual(filename, '/myfile')

        filename = build_absolute_filename('/tmp/deep/', '../myfile')
        self.assertEqual(filename, '/tmp/myfile')

        filename = build_relative_filename('/tmp/deep', '/myfile')
        self.assertEqual(filename, '../myfile')
