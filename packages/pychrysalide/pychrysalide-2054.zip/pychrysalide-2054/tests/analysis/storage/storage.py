
from chrysacase import ChrysalideTestCase
from pychrysalide import core
from pychrysalide.analysis.contents import FileContent
from pychrysalide.analysis.storage import ObjectStorage
from pychrysalide.common import PackedBuffer
import os
import shutil
import tempfile


class TestObjectStorage(ChrysalideTestCase):
    """TestCase for analysis.storage."""

    @classmethod
    def setUpClass(cls):

        super(TestObjectStorage, cls).setUpClass()

        cls._tmp_path = tempfile.mkdtemp()

        config = core.get_main_configuration()
        param = config.search(core.MainParameterKeys.TMPDIR)

        cls._old_tmpdir = param.value
        param.value = cls._tmp_path

        cls.log('Using temporary directory "%s"' % cls._tmp_path)


    @classmethod
    def tearDownClass(cls):

        super(TestObjectStorage, cls).tearDownClass()

        config = core.get_main_configuration()
        param = config.search(core.MainParameterKeys.TMPDIR)

        param.value = cls._old_tmpdir

        # import os
        # os.system('ls -laihR %s' % cls._tmp_path)

        cls.log('Delete directory "%s"' % cls._tmp_path)

        shutil.rmtree(cls._tmp_path)


    def testFileContentStorage(self):
        """Store and load file binary content."""

        storage = ObjectStorage('my-storage-hash')
        self.assertIsNotNone(storage)

        filename = os.path.join(self._tmp_path, 'test.bin')

        with open(filename, 'wb') as fd:
            fd.write(b'ABC')

        cnt = FileContent(filename)
        self.assertIsNotNone(cnt)

        ret = storage.store_object('contents', cnt)
        self.assertEqual(ret, 0)

        pbuf = PackedBuffer()

        ret = storage.store(pbuf)
        self.assertTrue(ret)

        self.assertTrue(pbuf.payload_length > 0)

        pbuf.rewind()

        storage2 = ObjectStorage.load(pbuf)
        self.assertIsNotNone(storage2)

        cnt2 = storage2.load_object('contents', 0)
        self.assertIsNotNone(cnt2)

        self.assertEqual(cnt.data, cnt2.data)
