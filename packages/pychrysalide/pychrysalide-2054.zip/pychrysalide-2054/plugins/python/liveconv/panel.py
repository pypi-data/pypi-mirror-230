
import os
from gi.repository import Gtk
from pychrysalide.analysis import LoadedBinary
from pychrysalide.gtkext import BuiltNamedWidget
from pychrysalide.gui import core
from pychrysalide.gui import PanelItem

from .converters import *


class ConvPanel(PanelItem):

    _key = 'liveconv'

    _path = 'MES'


    def __init__(self):
        """Initialize the GUI panel."""

        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, 'panel.ui')

        widget = BuiltNamedWidget('Converter', 'Data live converter', filename)

        super(ConvPanel, self).__init__(widget)

        self._conversions = {

            'int8':   lambda c, a, o: data_to_number(c, a, o, 'b'),
            'uint8':  lambda c, a, o: data_to_number(c, a, o, 'B'),
            'int16':  lambda c, a, o: data_to_number(c, a, o, 'h'),
            'uint16': lambda c, a, o: data_to_number(c, a, o, 'H'),
            'int32':  lambda c, a, o: data_to_number(c, a, o, 'l'),
            'uint32': lambda c, a, o: data_to_number(c, a, o, 'L'),
            'int64':  lambda c, a, o: data_to_number(c, a, o, 'q'),
            'uint64': lambda c, a, o: data_to_number(c, a, o, 'Q'),
            'half_float': lambda c, a, o: data_to_number(c, a, o, 'e'),
            'float':  lambda c, a, o: data_to_number(c, a, o, 'f'),
            'double': lambda c, a, o: data_to_number(c, a, o, 'd'),

            'time':     lambda c, a, o: data_to_time(c, a, o, 'L'),
            'time64':   lambda c, a, o: data_to_time(c, a, o, 'Q'),
            'filetime': data_to_filetime,
            'dostime':  data_to_dos_time,
            'dosdate':  data_to_dos_date,

            'char':  data_to_char,
            'ansi':  data_to_ansi,
            'utf8':  data_to_utf8,
            'utf16': data_to_utf16,

        }

        builder = self.named_widget.builder

        for kind, func in self._conversions.items():

            label = builder.get_object('%s_value' % kind)
            label.set_text('-')

        self._order = '@'


    def _track_cursor(self, source, cursor):
        """Track moves from the current cursor."""

        loaded = core.get_current_content()
        assert(loaded)

        builder = self.named_widget.builder

        for kind, func in self._conversions.items():

            label = builder.get_object('%s_value' % kind)

            try:
                addr = cursor.retrieve()
                label.set_text(func(loaded.content, addr, self._order))

            except Exception as e:
                label.set_text('-')
