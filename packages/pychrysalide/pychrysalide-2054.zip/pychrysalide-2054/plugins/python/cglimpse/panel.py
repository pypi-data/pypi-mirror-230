
import os
from gi.repository import Gtk
from pychrysalide import core
from pychrysalide.glibext import ConfigParam
from pychrysalide.gtkext import BuiltNamedWidget
from pychrysalide.gtkext import EasyGtk
from pychrysalide.gui import PanelItem
from pychrysalide.gui.panels import UpdatablePanel


from .distro import ByteDistribution
from .entropy import ShannonEntropy


class CGlimpsePanel(PanelItem, UpdatablePanel):

    _key = 'cglimpse'

    _path = 'Ms'

    _working_group_id = core.setup_tiny_global_work_group()


    @staticmethod
    def setup_config(config):
        """Register the configuration parameters for all the methods."""

        param = ConfigParam('cglimpse.selected', ConfigParam.ConfigParamType.ULONG, 0)
        config.add(param)

        ShannonEntropy.setup_config(config)

        ByteDistribution.setup_config(config)


    def __init__(self):
        """Initialize the GUI panel."""

        directory = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(directory, 'panel.ui')

        widget = BuiltNamedWidget('Content glimpse', 'Binary content glimpse', filename)

        super(CGlimpsePanel, self).__init__(widget)

        self._builder = self.named_widget.builder

        self._builder.connect_signals(self)

        self._start_changed_sid = -1
        self._end_changed_sid = -1

        self._content = None
        self._start = 0
        self._end = 0

        self._config = None
        self._methods = {}
        self._current = None


    def attach_config(self, config):
        """Attach a loaded configuration to the displayed panel."""

        self._config = config

        self._methods['shannon'] = ShannonEntropy(self._builder, config, self._force_update)
        self._methods['distrib'] = ByteDistribution(self._builder, config, self._force_update)

        param = config.search('cglimpse.selected')
        selected = param.value

        combo = self._builder.get_object('method_sel')

        if selected == combo.get_active():
            self._on_method_changed(combo)
        else:
            combo.set_active(selected)


    def _change_content(self, old, new):
        """Get notified about a LoadedContent change."""

        self._content = new.content if new else None

        length = len(self._content.data) if self._content else 1

        self._start = 0
        self._end = length

        scale = self._builder.get_object('start_pos')
        scale.set_range(0, length - 1)
        scale.set_value(0)

        self._start_changed_sid = scale.connect('value-changed', self._on_position_value_changed)

        scale = self._builder.get_object('end_pos')
        scale.set_range(1, length)
        scale.set_value(length)

        self._end_changed_sid = scale.connect('value-changed', self._on_position_value_changed)

        combo = self._builder.get_object('method_sel')
        self._on_method_changed(combo)


    def _setup(self, uid):
        """Prepare an update process for a panel."""

        assert(uid == 0)

        return ( 1, {}, 'Computing data for content glimpse' )


    def _introduce(self, uid, data):
        """Introduce the update process and switch display."""

        assert(uid == 0)

        # Reduce the rendering concurrency between the GTK main loop and this thread
        #self.switch_to_updating_mask()


    def _process(self, uid, status, id, data):
        """Perform the computing of data to render."""

        assert(uid == 0)

        self._current.update(self._content.data, [ self._start, self._end ])

        area = self._builder.get_object('content')
        area.queue_draw()


    def _conclude(self, uid, data):
        """Conclude the update process and display the computed data."""

        assert(uid == 0)

        # Reduce the rendering concurrency between the GTK main loop and this thread
        # self.switch_to_updated_content()


    def _clean_data(self, uid, data):
        """Delete dynamically generated objects for the panel update."""

        # Not really useful here...

        assert(uid == 0)


    def _on_options_toggled(self, button):
        """React on options display/hide order."""

        lbl = self._builder.get_object('options_label')

        common = self._builder.get_object('common_options')

        if button.get_active():

            button.get_parent().child_set_property(button, 'expand', False)
            lbl.set_angle(0)

            common.show()

        else:

            button.get_parent().child_set_property(button, 'expand', True)
            lbl.set_angle(90)

            common.hide()


    def _on_method_changed(self, combo):
        """React on method selection change."""

        tree_iter = combo.get_active_iter()

        if tree_iter:

            model = combo.get_model()
            key = model[tree_iter][1]

            assert(key in self._methods.keys())

            self._current = self._methods[key]
            self._current.switch()

            stack = self._builder.get_object('specific_options')
            stack.set_visible_child_name('%s_page' % key)

            param = self._config.search('cglimpse.selected')
            param.value = combo.get_active()

            self._force_update()


    def _on_position_value_changed(self, scale):
        """React when the data range value changes."""

        start_scale = self._builder.get_object('start_pos')
        self._start = int(start_scale.get_value())

        end_scale = self._builder.get_object('end_pos')
        self._end = int(end_scale.get_value())

        length = len(self._content.data) if self._content else 1

        start_scale.disconnect(self._start_changed_sid)
        end_scale.disconnect(self._end_changed_sid)

        start_scale.set_range(0, self._end - 1)
        end_scale.set_range(self._start + 1, length)

        self._start_changed_sid = start_scale.connect('value-changed', self._on_position_value_changed)
        self._end_changed_sid = end_scale.connect('value-changed', self._on_position_value_changed)

        self._force_update()


    def _force_update(self):
        """Force the update of the rendering."""

        if self._content:

            self.run_update(0)


    def _render_grid(self, widget, cr):
        """Draw a basic empty grid."""

        # Colors

        color = EasyGtk.get_color_from_style('view', True)
        bg_color = [ color.red, color.green, color.blue, color.alpha ]

        color = EasyGtk.get_color_from_style('background', False)
        line_color = [ color.red, color.green, color.blue, color.alpha ]

        # Background

        w = widget.get_allocation().width
        h = widget.get_allocation().height

        cr.set_source_rgba(*bg_color)

        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Area definitions

        x_range, y_range = self._current.setup_rendering()

        margin_left = 0
        margin_bottom = 0

        y_count = int((y_range[2] - y_range[0]) / y_range[1])

        for i in range(y_count + 1):

            text = self._current.format_legend(y_range[0] + i * y_range[1], True)

            (_, _, width, height, _, _) = cr.text_extents(text)

            if width > margin_left:

                margin_left = width
                margin_bottom = height

        bar_padding = 5
        bar_tick = 3
        arrow_size = 4

        graph_left = bar_padding + margin_left + bar_tick * 3
        graph_right = w - 2 * bar_padding

        graph_bottom = h - bar_padding - margin_bottom - bar_tick * 3

        data_left = graph_left + 2 * bar_padding
        data_right = graph_right - 2 * bar_padding

        data_top = 5 * bar_padding
        data_bottom = graph_bottom - 2 * bar_padding

        data_height = data_bottom - data_top
        data_width = data_right - data_left

        data_area = [ data_left, data_top, data_width, data_height ]

        # Grid content #1

        cr.set_source_rgba(*line_color)

        cr.set_line_width(1)

        cr.move_to(graph_left, 2 * bar_padding)
        cr.line_to(graph_left, graph_bottom)
        cr.line_to(graph_right, graph_bottom)

        cr.stroke()

        cr.move_to(graph_right, graph_bottom)
        cr.line_to(graph_right - arrow_size, graph_bottom - arrow_size)
        cr.line_to(graph_right - arrow_size, graph_bottom + arrow_size)

        cr.fill()

        cr.move_to(graph_left, 2 * bar_padding)
        cr.line_to(graph_left - arrow_size, 2 * bar_padding + arrow_size)
        cr.line_to(graph_left + arrow_size, 2 * bar_padding + arrow_size)

        cr.fill()

        cr.set_source_rgba(0, 0, 0, 0.2)

        cr.rectangle(*data_area)
        cr.fill()

        # Grid content #2

        y_count = int((y_range[2] - y_range[0]) / y_range[1])

        for i in range(y_count + 1):

            y = data_bottom - (i * data_height) / y_count

            # Line

            cr.save()

            cr.set_source_rgba(*line_color[:3], line_color[3] * 0.4)
            cr.set_dash([ 2 * bar_tick, 6 * bar_tick ])

            cr.move_to(graph_left + 6 * bar_tick, y)
            cr.line_to(data_right, y)

            cr.stroke()

            cr.restore()

            # Tick

            cr.set_source_rgba(*line_color)

            cr.move_to(graph_left - bar_tick, y)
            cr.line_to(graph_left + bar_tick, y)

            cr.stroke()

            # Text

            text = self._current.format_legend(y_range[0] + i * y_range[1], True)

            _, _, tw, th, _, _ = cr.text_extents(text)

            x = graph_left - 3 * bar_tick - tw

            cr.move_to(x, y + th / 2)
            cr.show_text(text)

        x_count = int((x_range[2] - x_range[0]) / x_range[1])

        for i in range(x_count + 1):

            x = data_left + (i * data_width) / x_count

            # Line

            cr.save()

            cr.set_source_rgba(*line_color[:3], line_color[3] * 0.4)
            cr.set_dash([ 2 * bar_tick, 6 * bar_tick ])

            cr.move_to(x, data_top)
            cr.line_to(x, data_bottom)

            cr.stroke()

            cr.restore()

            # Tick

            cr.set_source_rgba(*line_color)

            cr.move_to(x, graph_bottom - bar_tick)
            cr.line_to(x, graph_bottom + bar_tick)

            cr.stroke()

            # Text

            text = self._current.format_legend(x_range[0] + i * x_range[1], False)

            _, _, tw, th, _, _ = cr.text_extents(text)

            y = graph_bottom + 3 * bar_tick + th

            cr.move_to(x - tw / 2, y)
            cr.show_text(text)

        return data_area


    def _render_content_glimpse(self, widget, cr):
        """Draw the selected content view."""

        data_area = self._render_grid(widget, cr)

        if self._content:
            self._current.render(cr, data_area)
