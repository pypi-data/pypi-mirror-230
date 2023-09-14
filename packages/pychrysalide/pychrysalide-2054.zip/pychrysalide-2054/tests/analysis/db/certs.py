#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant la génération de certificats


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.db import certs
import shutil
import subprocess
import tempfile


class TestRestrictedContent(ChrysalideTestCase):
    """TestCase for analysis.db.certs."""

    @classmethod
    def setUpClass(cls):

        super(TestRestrictedContent, cls).setUpClass()

        cls._tmppath = tempfile.mkdtemp()

        cls.log('Using temporary directory "%s"' % cls._tmppath)


    @classmethod
    def tearDownClass(cls):

        super(TestRestrictedContent, cls).tearDownClass()

        cls.log('Delete directory "%s"' % cls._tmppath)

        shutil.rmtree(cls._tmppath)


    def checkOutput(self, cmd, expected):
        """Run a command and check its output."""

        output = ''

        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except:
            pass

        self.assertEqual(output, expected)


    def testMakeCA(self):
        """Check for building a valid CA."""

        identity = {

            'C': 'UK',
            'CN': 'OpenSSL Group'

        }

        ret = certs.build_keys_and_ca(self._tmppath, 'ca', 3650 * 24 * 60 * 60, identity)
        self.assertTrue(ret)

        cmd = 'openssl x509 -in %s/ca-cert.pem -subject -noout' % self._tmppath

        expected = b'subject=C = UK, CN = OpenSSL Group\n'

        self.checkOutput(cmd, expected)

        cmd = 'openssl verify -CApath %s -CAfile %s/ca-cert.pem %s/ca-cert.pem' \
              % (self._tmppath, self._tmppath, self._tmppath)

        expected = bytes('%s/ca-cert.pem: OK\n' % self._tmppath, 'utf-8')

        self.checkOutput(cmd, expected)


    def testMakeCSR(self):
        """Check for requesting a valid signing request."""

        identity = {

            'C': 'UK',
            'CN': 'OpenSSL Group'

        }

        ret = certs.build_keys_and_request(self._tmppath, 'server', identity);
        self.assertTrue(ret)


    def testSignCert(self):
        """Check for properly signing a certificate."""

        ret = certs.sign_cert('%s/server-csr.pem' % self._tmppath, '%s/ca-cert.pem' % self._tmppath, \
                              '%s/ca-key.pem' % self._tmppath, '%s/server-cert.pem' % self._tmppath, \
                              3650 * 24 * 60 * 60)
        self.assertTrue(ret)

        cmd = 'openssl x509 -in %s/server-cert.pem -subject -noout' % self._tmppath

        expected = b'subject=C = UK, CN = OpenSSL Group\n'

        self.checkOutput(cmd, expected)

        cmd = 'openssl verify -CApath %s -CAfile %s/ca-cert.pem %s/server-cert.pem' \
              % (self._tmppath, self._tmppath, self._tmppath)

        expected = bytes('%s/server-cert.pem: OK\n' % self._tmppath, 'utf-8')

        self.checkOutput(cmd, expected)

