#!/usr/bin/python
# -*- coding: utf-8 -*-

from pychrysalide import core
from pychrysalide.analysis.contents import EncapsulatedContent
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.plugins import PluginModule
import io
import zipfile


class ApkFiles(PluginModule):
    """Open and process APK files."""

    _name = 'ApkFiles'
    _desc = 'Add suppport for the APK file format'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( PluginModule.PluginAction.CONTENT_EXPLORER, )


    def _handle_binary_content(self, action, content, wid, status):
        """Process an operation on a binary content."""

        assert(action == PluginModule.PluginAction.CONTENT_EXPLORER)

        pseudo_file = io.BytesIO(content.data)

        if zipfile.is_zipfile(pseudo_file):

            # Handle bad ZIP files such as:
            # c9ad0ec284fd988b294b28cb577bc0a28b1f7d129a14f2228f6548c6f7ed3d55

            # Traceback (most recent call last):
            #  File "... plugins/python/apkfiles/apkfiles.py", line 41, in handle_binary_content
            #    zf = zipfile.ZipFile(pseudo_file)
            #  File "/usr/lib/python3.5/zipfile.py", line 1026, in __init__
            #    self._RealGetContents()
            #  File "/usr/lib/python3.5/zipfile.py", line 1114, in _RealGetContents
            #    fp.seek(self.start_dir, 0)
            # ValueError: negative seek value -104578300

            try:
                zf = zipfile.ZipFile(pseudo_file)
            except:
                zf = None

            if not(zf is None) \
               and zf.namelist().count('classes.dex') > 0 \
               and zf.namelist().count('AndroidManifest.xml') > 0:

                explorer = core.get_content_explorer()

                for name in zf.namelist():

                    # Handle bad ZIP files such as:
                    # 6e432c34d88e65fcd5967cc7cd2f0f4922dfc17ecc6e7acdfe0b1baf94c0851b

                    # Traceback (most recent call last):
                    #  File "... plugins/python/apkfiles/apkfiles.py", line 64, in handle_binary_content
                    #    f = zf.open(name, 'r')
                    #  File "/usr/lib/python3.5/zipfile.py", line 1268, in open
                    #    raise BadZipFile("Bad magic number for file header")
                    # zipfile.BadZipFile: Bad magic number for file header

                    try:
                        with zf.open(name, 'r') as f:
                            data = f.read()
                    except:
                        data = ''

                    # Skip directories and empty entries
                    if len(data) == 0:
                        continue

                    mem_content = MemoryContent(data)
                    encaps_content = EncapsulatedContent(content, name, mem_content)

                    explorer.populate_group(wid, encaps_content)
