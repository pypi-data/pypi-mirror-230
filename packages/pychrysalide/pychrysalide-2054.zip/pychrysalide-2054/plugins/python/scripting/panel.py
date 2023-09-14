
import os
from gi.repository import Gdk, GdkPixbuf, GLib, GObject
from pychrysalide.gtkext import BuiltNamedWidget
from pychrysalide.gui import core
from pychrysalide.gui import PanelItem



class ScriptPanel(PanelItem):

    _key = 'pyscripting'

    _path = 'MEN'
    _key_bindings = '<Shift>F5'


    def __init__(self):
        """Initialize the GUI panel."""

        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, 'panel.ui')

        widget = BuiltNamedWidget('Python scripts', 'Recently run Python scripts', filename)

        super(ScriptPanel, self).__init__(widget)

        if not('run-requested' in GObject.signal_list_names(ScriptPanel)):

            GObject.signal_new('run-requested', ScriptPanel, GObject.SignalFlags.RUN_FIRST,
                               GObject.TYPE_NONE, (GObject.TYPE_STRING, ))

            GObject.signal_new('ask-for-new-script', ScriptPanel, GObject.SignalFlags.RUN_FIRST,
                               GObject.TYPE_NONE, ())

        self._last_selected = None
        self._manager = None

        builder = self.named_widget.builder

        icon_renderer = builder.get_object('icon_renderer')
        icon_renderer.props.xpad = 8

        builder.connect_signals(self)


    def attach_manager(self, manager):
        """Assign the recent manager to the panel."""

        self._manager = manager

        manager.connect("changed", self._on_recent_list_changed)

        self._on_recent_list_changed(manager)


    def _on_row_activated(self, treeview, path, column):
        """React on a row activation."""

        store = self.named_widget.builder.get_object('store')

        siter = store.get_iter(path)

        self.emit('run-requested', store[siter][3])


    def _on_selection_changed(self, selection):
        """React on tree selection change."""

        model, treeiter = selection.get_selected()

        if treeiter:
            self._last_selected = model[treeiter][3]
        else:
            self._last_selected = None


    def on_key_press_event(self, widget, event):
        """React on a key press inside the tree view."""

        if event.keyval == Gdk.KEY_Delete:

            selection = self.named_widget.builder.get_object('selection')

            model, treeiter = selection.get_selected()

            if treeiter:

                uri = GLib.filename_to_uri(model[treeiter][3])

                self._manager.remove_item(uri)

        elif event.keyval == Gdk.KEY_Insert:

            self.emit('ask-for-new-script')


    def _add_entry(self, filename):
        """Add an entry for a new recent Python script."""

        directory = os.path.dirname(os.path.realpath(__file__))
        icon_filename = os.path.join(directory, 'python-script-icon-16x16.png')

        icon = GdkPixbuf.Pixbuf.new_from_file(icon_filename)
        name = os.path.basename(filename)
        path = os.path.dirname(filename)

        store = self.named_widget.builder.get_object('store')

        store.append([ icon, name, path, filename ])


    def _on_recent_list_changed(self, manager):
        """React on resources manager content change."""

        saved = self._last_selected

        # Register the new item

        builder = self.named_widget.builder

        store = builder.get_object('store')
        store.clear()

        for item in manager.get_items():

            filename = GLib.filename_from_uri(item.get_uri())[0]

            self._add_entry(filename)

        # Restore previous selection

        selection = builder.get_object('selection')

        siter = store.iter_children()

        while siter:

            if store[siter][3] == saved:

                selection.select_iter(siter)
                break

            siter = store.iter_next(siter)
