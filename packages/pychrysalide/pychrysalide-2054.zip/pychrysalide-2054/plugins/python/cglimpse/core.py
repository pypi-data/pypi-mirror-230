
from pychrysalide.glibext import ConfigParam
from pychrysalide.gui import core
from pychrysalide.plugins import PluginModule

from .panel import CGlimpsePanel


class ContentGlimpse(PluginModule):
    """Convert raw values into interpreted values."""

    _name = 'ContentGlimpse'
    _desc = 'Display some glimpses of binary contents'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( PluginModule.PluginAction.PLUGIN_LOADED, PluginModule.PluginAction.PANEL_CREATION, )


    def __init__(self):
        """Initialize the plugin for Chrysalide."""

        super(ContentGlimpse, self).__init__()

        core.register_panel(CGlimpsePanel)


    def _manage(self, action):
        """React to several steps of the plugin life."""

        CGlimpsePanel.setup_config(self.config)

        return True


    def _on_panel_creation(self, action, item):
        """Get notified of a new panel creation."""

        if type(item) == CGlimpsePanel:

            item.attach_config(self.config)
