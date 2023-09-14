
from pychrysalide.gui import core
from pychrysalide.plugins import PluginModule

from .panel import ConvPanel


class LiveConverter(PluginModule):
    """Convert raw values into interpreted values."""

    _name = 'LiveConverter'
    _desc = 'Convert raw values into interprered values'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( )


    def __init__(self):
        """Initialize the plugin for Chrysalide."""

        super(LiveConverter, self).__init__()

        core.register_panel(ConvPanel)
