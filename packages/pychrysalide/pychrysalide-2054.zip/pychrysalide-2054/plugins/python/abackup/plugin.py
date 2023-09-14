
# Chrysalide - Outil d'analyse de fichiers binaires
# plugin.py - point d'entrée pour le greffon assurant la gestion des sauvegardes Android
#
# Copyright (C) 2019 Cyrille Bagard
#
#  This file is part of Chrysalide.
#
#  Chrysalide is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  Chrysalide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import io
import tarfile
from pychrysalide import core
from pychrysalide.analysis.contents import EncapsulatedContent
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.plugins import PluginModule
from .backup import AndroidBackup
from .password import PasswordReader


class AndroidBackupPlugin(PluginModule):
    """Open and process Android backup files."""

    _name = 'AndroidBackup'
    _desc = 'Add suppport for the Android backup file format'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( PluginModule.PluginAction.CONTENT_EXPLORER, )


    def _handle_binary_content(self, action, content, wid, status):
        """Process an operation on a binary content."""

        assert(action == PluginModule.PluginAction.CONTENT_EXPLORER)

        try:
            backup = AndroidBackup(content)
        except:
            backup = None

        if backup:

            # Get the backup password, if required

            encrypted = backup.is_encrypted()

            if encrypted:

                if 'password' in content.attributes.keys:

                    password = content.attributes['password']

                else:

                    if core.is_batch_mode():
                        password = PasswordReader.read_password_from_console()
                    else:
                        password = PasswordReader.read_password_from_gui()

                    #content.attributes['password'] = password

                if password:

                    try:
                        backup.get_master_key(password)
                        valid = True
                    except:
                        valid = False

                else:
                    valid = False

            else:

                password = None

            # Extract all the backup content

            if not(encrypted) or valid:

                tar_content = backup.get_content(password)

                tar_stream = io.BytesIO(tar_content)

                explorer = core.get_content_explorer()

                try:

                    tf = tarfile.TarFile(fileobj=tar_stream, mode='r')

                    for ti in tf.getmembers():

                        if not(ti.type == tarfile.REGTYPE):
                            continue

                        fobj = tf.extractfile(ti)

                        data = fobj.read()

                        if len(data):

                            mem_content = MemoryContent(data)
                            encaps_content = EncapsulatedContent(content, ti.name, mem_content)

                            explorer.populate_group(wid, encaps_content)

                except:

                    core.log_message(core.LogMessageType.ERROR, 'The Android backup is corrupted')

            else:

                core.log_message(core.LogMessageType.ERROR, 'Bad Android backup password')
