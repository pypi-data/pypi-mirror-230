#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-

from gi.repository import Gtk
from pychrysalide.analysis import LoadedBinary
from pychrysalide.analysis.contents import FileContent

import sys

for arg in sys.argv[1:]:

    fc = FileContent(arg)

    print('  --> file content:', fc)

    binary = LoadedBinary(fc)

    print('  --> loaded binary:', binary)

    if binary is not None:

        def disassembly_is_done(obj, binary):
            Gtk.main_quit()

        binary.connect('disassembly-done', disassembly_is_done, binary)

        binary.analyse()

        # Attente de la réception du signal
        # Cf. http://stackoverflow.com/questions/28873688/python-how-to-block-in-pygtk-while-waiting-for-timeout-add-callback
        Gtk.main()
