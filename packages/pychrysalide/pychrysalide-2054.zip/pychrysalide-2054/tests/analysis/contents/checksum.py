#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant le bon calcul d'empreintes.


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import FileContent, RestrictedContent
from pychrysalide.arch import vmpa, mrange
import hashlib
import tempfile


class TestRestrictedContent(ChrysalideTestCase):
    """TestCase for analysis.contents.RestrictedContent."""

    @classmethod
    def setUpClass(cls):

        super(TestRestrictedContent, cls).setUpClass()

        cls._out = tempfile.NamedTemporaryFile()

        cls._out.write(b'AAAABBBBCCCCDDDD')

        cls._out.flush()

        cls.log('Using temporary file "%s"' % cls._out.name)


    @classmethod
    def tearDownClass(cls):

        super(TestRestrictedContent, cls).tearDownClass()

        cls.log('Delete file "%s"' % cls._out.name)

        cls._out.close()


    def testFullChecksum(self):
        """Check checksum of full content."""

        fcnt = FileContent(self._out.name)
        self.assertIsNotNone(fcnt)

        expected = hashlib.sha256(b'AAAABBBBCCCCDDDD').hexdigest()

        self.assertEqual(fcnt.checksum, expected)


    def testPartialChecksum(self):
        """Check checksum of restricted content."""

        fcnt = FileContent(self._out.name)
        self.assertIsNotNone(fcnt)

        start = vmpa(4, vmpa.VmpaSpecialValue.NO_VIRTUAL)
        covered = mrange(start, 4) # 'BBBB'

        rcnt = RestrictedContent(fcnt, covered)
        self.assertIsNotNone(rcnt)

        expected = hashlib.sha256(b'BBBB').hexdigest()

        self.assertEqual(rcnt.checksum, expected)
