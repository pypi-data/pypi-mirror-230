
from gi.repository import GLib, Gtk
import os

from pychrysalide import core
from pychrysalide.gui import core as gcore
from pychrysalide.gui import MenuBar
from pychrysalide.gtkext import EasyGtk
from pychrysalide.plugins import PluginModule

from .panel import ScriptPanel


class ScriptingEngine(PluginModule):
    """Extend the GUI to run external Python scripts."""

    _name = 'ScriptingEngine'
    _desc = 'Run external Python scripts on demand'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( PluginModule.PluginAction.PLUGIN_LOADED, PluginModule.PluginAction.PANEL_CREATION )

    _manager = None


    def __init__(self):
        """Initialize the plugin for Chrysalide."""

        super(ScriptingEngine, self).__init__()

        # Scripts panel

        gcore.register_panel(ScriptPanel)

        # Insert the new menu item into 'File' submenu

        builder = gcore.get_editor_builder()

        if builder:

            file_menu = builder.get_object('file').get_submenu()
            sep_item = builder.get_object('file_sep_1')
            save_item = builder.get_object('file_save_project')

            index = EasyGtk.find_contained_child_index(file_menu, save_item)

            if index == -1:
                raise RuntimeError('file menu not found')

            prev = EasyGtk.get_nth_contained_child(file_menu, index - 1)

            if sep_item == prev:

                sep = Gtk.SeparatorMenuItem()
                sep.show()

                file_menu.insert(sep, index)

            item = Gtk.MenuItem(label='Run Python script...')
            item.connect("activate", self._on_file_run_script_activate)
            item.show()

            file_menu.insert(item, index)


    def _manage(self, action):
        """Ack the full loading of all plugins."""

        if action == PluginModule.PluginAction.PLUGIN_LOADED:

            xbel = self.build_config_filename('recents.xbel', True)

            ScriptingEngine._manager = Gtk.RecentManager(filename=xbel)

        return True


    def _on_panel_creation(self, action, item):
        """Get notified of a new panel creation."""

        if type(item) == ScriptPanel:

            item.attach_manager(ScriptingEngine._manager)

            item.connect('run-requested', self._on_run_requested)
            item.connect('ask-for-new-script', lambda x: self._on_file_run_script_activate(None))


    def _on_file_run_script_activate(self, widget):
        """Look for a new script to run."""

        dialog = Gtk.FileChooserDialog(title='Please choose a Python script to execute',
                                       transient_for=gcore.get_editor_window(),
                                       action=Gtk.FileChooserAction.OPEN)

        dialog.add_buttons(Gtk.STOCK_CANCEL,
                           Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OPEN,
                           Gtk.ResponseType.OK)

        ffilter = Gtk.FileFilter()
        ffilter.set_name('Python files')
        ffilter.add_mime_type('text/x-python')
        dialog.add_filter(ffilter)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        else:
            filename = None

        dialog.destroy()

        if filename:
            self._run_script_file(filename)


    def _run_script_file(self, filename):
        """Run a given script file."""

        self.log_message(core.LogMessageType.INFO, 'Execute the script file \'%s\'' % filename)

        uri = GLib.filename_to_uri(filename)

        recent_data = Gtk.RecentData()
        recent_data.app_name = 'Chrysalide Python plugin'
        recent_data.app_exec = 'chrysalide'
        recent_data.display_name = os.path.basename(filename)
        recent_data.description = 'Python script run inside Chrysalide'
        recent_data.mime_type = 'text/x-python'

        ScriptingEngine._manager.add_full(uri, recent_data)

        try:
            with open(filename, 'r') as fd:
                content = fd.read()

            code = compile(content, '<string>', 'exec')

            eval(code)

        except Exception as e:
            self.log_message(core.LogMessageType.EXT_ERROR, 'Error while running the script: %s' % str(e))


    def _on_run_requested(self, panel, filename):
        """Run a script file from the recents panel."""

        self._run_script_file(filename)
