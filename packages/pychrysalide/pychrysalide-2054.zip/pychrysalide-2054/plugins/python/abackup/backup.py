
# Chrysalide - Outil d'analyse de fichiers binaires
# backup.py - gestionnaire du format de fichier des sauvegardes Android
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


try:
    from Crypto.Cipher import AES
except:
    AES = None

import hashlib
import io
import pychrysalide
from pychrysalide.analysis.contents import FileContent
from pychrysalide.arch import vmpa
import zlib


PBKDF2_KEY_SIZE = 32


class AndroidBackup():
    """Reader for Android backups."""


    def _read_lines(self, pos, lcount):
        """Read lcount lines from a given pos in a binary content."""

        count = 0

        buf = ''

        while count < lcount:

            got = chr(self._content.read_u8(pos))

            buf += got

            if got == '\n':
                count += 1

            if pos.phys == self._content.size:
                break

        return buf


    def __init__(self, content):
        """Create an Android backup reader from a binary content."""

        # Refs from https://android.googlesource.com/platform/frameworks/base.git/+/refs/heads/master/ :

        #  - versions : services/backup/java/com/android/server/backup/BackupManagerService.java#184
        #  - content : services/backup/java/com/android/server/backup/fullbackup/PerformAdbBackupTask.java#335

        self._content = content

        pos = vmpa(0, vmpa.VMPA_NO_VIRTUAL)

        # Read the global file header

        self._header = self._read_lines(pos, 4)

        lines = self._header.split('\n')

        if len(lines) != 5 or lines[0] != 'ANDROID BACKUP':
            raise ValueError('Invalid header')

        self._version = lines[1]

        if not(lines[2] in ['0', '1']):
            raise ValueError('Content should be compressed or uncompressed')

        self._compressed = (lines[2] == '1')

        if not(lines[3] in ['none', 'AES-256']):
               raise ValueError('Encryption not supported!')

        self._encrypted = (lines[3] == 'AES-256')

        # Read the encryption header

        if not(self._encrypted):

            self._enc_header = None

            self._user_password_salt = None
            self._master_key_checksum_salt = None
            self._pbkdf2_rounds_numer = None
            self._user_key_iv = None
            self._master_key_blob = None

        else:

            self._enc_header = self._read_lines(pos, 5)

            lines = self._enc_header.split('\n')

            if len(lines) != 6:
                raise ValueError('Invalid encryption header')

            self._user_password_salt = bytes.fromhex(lines[0])
            self._master_key_checksum_salt = bytes.fromhex(lines[1])
            self._pbkdf2_rounds_numer = int(lines[2])
            self._user_key_iv = bytes.fromhex(lines[3])
            self._master_key_blob = bytes.fromhex(lines[4])

        self._backup_start = pos.phys


    def is_encrypted(self):
        """Tell if the backup is encrypted."""

        return self._encrypted


    def _convert_master_key(self, input_bytes):
        """Convert a master key into an UTF-8 byte array."""

        output = []

        for byte in input_bytes:

            if byte < ord(b'\x80'):
                output.append(byte)
            else:
                output.append(ord('\xef') | (byte >> 12))
                output.append(ord('\xbc') | ((byte >> 6) & ord('\x3f')))
                output.append(ord('\x80') | (byte & ord('\x3f')))

        return bytes(output)


    def get_master_key(self, password):
        """Get a verified master key and its IV for the backup encryption."""

        if AES is None:
            raise OSError('No AES support')

        key = hashlib.pbkdf2_hmac('sha1', password.encode('utf-8'),
                                  self._user_password_salt,
                                  self._pbkdf2_rounds_numer, PBKDF2_KEY_SIZE)

        alg = AES.new(key, AES.MODE_CBC, self._user_key_iv)

        master_key = alg.decrypt(self._master_key_blob)

        blob = io.BytesIO(master_key)

        master_iv_length = ord(blob.read(1))
        master_iv = blob.read(master_iv_length)
        master_key_length = ord(blob.read(1))
        master_key = blob.read(master_key_length)
        master_key_checksum_length = ord(blob.read(1))
        master_key_checksum = blob.read(master_key_checksum_length)

        checksum = hashlib.pbkdf2_hmac('sha1', self._convert_master_key(master_key),
                                       self._master_key_checksum_salt,
                                       self._pbkdf2_rounds_numer, PBKDF2_KEY_SIZE)

        if not master_key_checksum == checksum:
            raise ValueError('Invalid decryption password')

        return master_key, master_iv


    def get_content(self, password=None):
        """Extract the backup content as a simple tarball content."""

        data = self._content.data[self._backup_start:]

        if self._encrypted:

            assert(password)

            # Cf. https://f-o.org.uk/2017/decrypting-android-backups-with-python.html

            master_key, master_iv = self.get_master_key(password)

            alg = AES.new(master_key, AES.MODE_CBC, master_iv)

            data = alg.decrypt(data)

        if self._compressed:

            d = zlib.decompressobj()
            extracted = d.decompress(data)

        else:

            extracted = data

        return extracted
