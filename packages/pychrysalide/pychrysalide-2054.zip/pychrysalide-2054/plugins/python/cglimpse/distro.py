
from gi.repository import Gdk
from pychrysalide.glibext import ConfigParam

from .method import GlimpseMethod


class ByteDistribution(GlimpseMethod):


    @staticmethod
    def setup_config(config):
        """Register the configuration parameters for the method."""

        color = Gdk.RGBA()
        color.parse('#3465A4')

        param = ConfigParam('cglimpse.distrib.color', ConfigParam.ConfigParamType.COLOR, color)
        config.add(param)


    def __init__(self, builder, config, update_cb):
        """Prepare a Distrib entropy display."""

        super(ByteDistribution, self).__init__(builder, config, update_cb)

        self._v_legend = 'Quantity'
        self._h_legend = 'Byte values'

        self._x_range = [ 0, 0x20, 0x100 ]
        self._y_range = [ 0, 25, 100 ]

        self._values = {}

        button = builder.get_object('distrib_color')
        button.connect('color-set', self._on_color_set)

        param = config.search('cglimpse.distrib.color')
        color = param.value

        self._color = [ color.red, color.green, color.blue, color.alpha ]
        self._shadow_color = [ color.red * 0.5, color.green * 0.5, color.blue * 0.5, color.alpha ]

        button.set_rgba(param.value)


    def _on_color_set(self, button):
        """React on color chosen for the rendering."""

        color = button.get_rgba()

        self._color = [ color.red, color.green, color.blue, color.alpha ]
        self._shadow_color = [ color.red * 0.5, color.green * 0.5, color.blue * 0.5, color.alpha ]

        param = self._config.search('cglimpse.distrib.color')
        param.value = color

        self._update_cb()


    def format_legend(self, value, vert):
        """Build the label used for a rule."""

        text = str(int(value))

        return text


    def update(self, data, coverage):
        """Compute internal values for the method."""

        max_count = 0

        self._values = {}

        for i in range(256):
            self._values[i] = 0

        for b in data[coverage[0] : coverage[1]]:

            if b in self._values.keys():
                self._values[b] += 1

        for c in self._values.values():
            if c > max_count:
                max_count = c

        self._y_range = [ 0, max_count / 4, max_count ]


    def render(self, cr, area):
        """Draw the bytes distribution for the current binary, if any."""

        max_count = self._y_range[-1]

        last_x = area[0]

        cr.set_source_rgba(*self._shadow_color)
        cr.set_source_rgba(*self._color)
        cr.set_line_width(1)

        for i in range(256):

            x = area[0] + ((i + 1) * area[2]) / 256
            h = (area[3] * self._values[i]) / max_count

            cr.rectangle(last_x, area[1] + area[3] - h, x - last_x, h)
            cr.fill()

            last_x = x
