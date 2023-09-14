
# Chrysalide - Outil d'analyse de fichiers binaires
# password.py - lecture des mots de passe pour une sauvegarde chiffrée
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


from pychrysalide.gui import core
from gi.repository import GLib, Gtk
from threading import Event


class PasswordReader():
    """Features for getting a backup password."""


    @staticmethod
    def read_password_from_console():
        """Get the backup console from the console."""

        password = input('Enter the password of the backup: ')

        return password


    @staticmethod
    def _show_password_box(mutex, ref):

        dlgbox = Gtk.MessageDialog(parent = core.get_editor_window(),
                                   flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                   type = Gtk.MessageType.QUESTION,
                                   buttons = Gtk.ButtonsType.OK_CANCEL,
                                   message_format = 'The backup file is password protected. Please enter it here:')

        dlgbox.set_title('Android backup password')

        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_invisible_char("*")
        entry.set_size_request(250, 0)

        area = dlgbox.get_content_area()
        area.pack_end(entry, False, False, 0)

        dlgbox.show_all()
        response = dlgbox.run()

        if response == Gtk.ResponseType.OK:
            ref['password'] = entry.get_text()

        dlgbox.destroy()

        mutex.set()


    @staticmethod
    def read_password_from_gui():
        """Get the backup console from a dialog box."""

        evt = Event()
        ref = {}

        GLib.idle_add(PasswordReader._show_password_box, evt, ref)

        evt.wait()

        return ref['password'] if 'password' in ref.keys() else None
