
from chrysacase import ChrysalideTestCase
import pychrysalide
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.analysis.db import certs
from pychrysalide.analysis.db import AdminClient, AnalystClient
from pychrysalide.analysis.db import HubServer
import os
import shutil
import sys
import tempfile
import threading


class TestDbConnection(ChrysalideTestCase):
    """TestCase for analysis.db."""

    @classmethod
    def setUpClass(cls):

        super(TestDbConnection, cls).setUpClass()

        cls.log('Compile binary "strings" if needed...')

        fullname = sys.modules[cls.__module__].__file__
        dirpath = os.path.dirname(fullname)

        cls._bin_path = os.path.realpath(dirpath + '/../../format/elf/')

        os.system('make -C %s strings > /dev/null 2>&1' % cls._bin_path)

        cls._tmp_path = tempfile.mkdtemp()

        cls._server_path = '%s/.chrysalide/servers/localhost-9999/' % cls._tmp_path
        os.makedirs(cls._server_path)

        cls._server_authorized_path = '%s/authorized/' % cls._server_path
        os.makedirs(cls._server_authorized_path)

        cls._client_path = '%s/.chrysalide/clients/' % cls._tmp_path
        os.makedirs(cls._client_path)

        cls._client_cert_path = '%s/localhost-9999/' % cls._client_path
        os.makedirs(cls._client_cert_path)

        cls.log('Using temporary directory "%s"' % cls._tmp_path)


    @classmethod
    def tearDownClass(cls):

        super(TestDbConnection, cls).tearDownClass()

        cls.log('Delete built binaries...')

        os.system('make -C %s clean > /dev/null 2>&1' % cls._bin_path)

        ## os.system('ls -laihR %s' % cls._tmp_path)

        cls.log('Delete directory "%s"' % cls._tmp_path)

        shutil.rmtree(cls._tmp_path)


    def testServerListening(self):
        """List binaries available from server."""


        from pychrysalide import core
        core.set_verbosity(0)



        identity = {

            'C': 'FR',
            'CN': 'Test authority'

        }

        ret = certs.build_keys_and_ca(self._server_path, 'ca', 3650 * 24 * 60 * 60, identity)
        self.assertTrue(ret)

        identity = {

            'C': 'FR',
            'CN': 'Test server'

        }

        ret = certs.build_keys_and_request(self._server_path, 'server', identity);
        self.assertTrue(ret)


        ret = certs.sign_cert('%s/server-csr.pem' % self._server_path, '%s/ca-cert.pem' % self._server_path, \
                              '%s/ca-key.pem' % self._server_path, '%s/server-cert.pem' % self._server_path, \
                              3650 * 24 * 60 * 60)
        self.assertTrue(ret)

        identity = {

            'C': 'FR',
            'CN': 'Test admin'

        }

        ret = certs.build_keys_and_request(self._client_path, 'client', identity);
        self.assertTrue(ret)

        ret = certs.sign_cert('%s/client-csr.pem' % self._client_path, '%s/ca-cert.pem' % self._server_path, \
                              '%s/ca-key.pem' % self._server_path, '%s/client-cert.pem' % self._client_cert_path, \
                              3650 * 24 * 60 * 60)
        self.assertTrue(ret)

        shutil.copy('%s/ca-cert.pem' % self._server_path,
                    '%s/ca-cert.pem' % self._client_cert_path)

        shutil.copy('%s/client-cert.pem' % self._client_cert_path,
                    '%s/client-cert.pem' % self._server_authorized_path)


        os.environ['XDG_CONFIG_HOME'] = self._tmp_path
        os.environ['HOME'] = self._tmp_path

        server = HubServer('localhost', '9999')

        #print(server)

        ret = server.start()

        #print(ret)




        # admin = AdminClient()

        # ret = admin.start('localhost', '9999')
        # self.assertTrue(ret)

        # def _on_existing_binaries_updated(adm, evt):
        #     evt.set()

        # event = threading.Event()

        # admin.connect('existing-binaries-updated', _on_existing_binaries_updated, event)

        # ret = admin.request_existing_binaries()
        # self.assertTrue(ret)

        # event.wait()

        # self.assertEqual(len(admin.existing_binaries), 0)



        cnt = MemoryContent(b'A' * 400 * 1024)



        analyst = AnalystClient(cnt.checksum, "elf", [])



        def _on_server_status_changed(analyst, hint, evt):
            print(hint)
            evt.set()


        event = threading.Event()

        analyst.connect('server-status-changed', _on_server_status_changed, event)



        ret = analyst.start('localhost', '9999')
        self.assertTrue(ret)


        event.wait()

        event.clear()

        ret = analyst.send_content(cnt)
        self.assertTrue(ret)


        event.wait()
