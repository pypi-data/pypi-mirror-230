
import math
from gi.repository import Gdk
from pychrysalide.glibext import ConfigParam

from .method import GlimpseMethod


class ShannonEntropy(GlimpseMethod):


    @staticmethod
    def setup_config(config):
        """Register the configuration parameters for the method."""

        color = Gdk.RGBA()
        color.parse('#3465A4')

        param = ConfigParam('cglimpse.shannon.color', ConfigParam.ConfigParamType.COLOR, color)
        config.add(param)

        param = ConfigParam('cglimpse.shannon.step', ConfigParam.ConfigParamType.ULONG, 0x80)
        config.add(param)


    def __init__(self, builder, config, update_cb):
        """Prepare a Shannon entropy display."""

        super(ShannonEntropy, self).__init__(builder, config, update_cb)

        self._v_legend = 'Entropy'
        self._h_legend = 'Byte offsets'

        self._x_range = [ 0, 1024, 10240 ]
        self._y_range = [ 0.0, 0.25, 1.0 ]

        self._coverage = None
        self._values = []

        button = builder.get_object('shannon_color')
        button.connect('color-set', self._on_color_set)

        param = config.search('cglimpse.shannon.color')
        color = param.value

        self._color = [ color.red, color.green, color.blue, color.alpha ]
        self._shadow_color = [ color.red * 0.5, color.green * 0.5, color.blue * 0.5, color.alpha ]

        button.set_rgba(param.value)

        scale = builder.get_object('shannon_step')
        scale.connect('format-value', self._on_scale_format_value)
        scale.connect('value-changed', self._on_scale_value_changed)

        param = config.search('cglimpse.shannon.step')
        step = param.value

        self._step = step

        scale.set_value(step)


    def _on_color_set(self, button):
        """React on color chosen for the rendering."""

        color = button.get_rgba()

        self._color = [ color.red, color.green, color.blue, color.alpha ]
        self._shadow_color = [ color.red * 0.5, color.green * 0.5, color.blue * 0.5, color.alpha ]

        param = self._config.search('cglimpse.shannon.color')
        param.value = color

        self._update_cb()


    def _on_scale_value_changed(self, scale):
        """React when the range value changes."""

        step = int(scale.get_value())

        self._step = step

        param = self._config.search('cglimpse.shannon.step')
        param.value = step

        self._update_cb()


    def _on_scale_format_value(self, scale, value):
        """Change how the scale value is displayed."""

        return '0x%x' % int(value)


    def format_legend(self, value, vert):
        """Build the label used for a rule."""

        if vert:
            text = str(value)

        else:

            multi = 1

            scale = [ ' kb', ' Mb', ' Gb', ' Tb' ]
            suffix = ''

            remaining = value

            for i in range(len(scale)):

                if remaining < 1024:
                    break

                multi *= 1024

                remaining /= 1024
                suffix = scale[i]

            if value % multi == 0:
                text = '%u%s' % (remaining, suffix)
            else:
                text = '%.1f%s' % (value / multi, suffix)

        return text


    def update(self, data, coverage):
        """Compute internal values for the method."""

        self._coverage = coverage

        size = self._coverage[1] - self._coverage[0]

        step = math.ceil(size / 10)

        self._x_range = [ coverage[0], step, coverage[0] + 10 * step ]

        self._values = []

        for i in range(self._x_range[0], self._x_range[2], self._step):

            counter = [ 0 for i in range(256) ]

            start = i
            end = i + self._step

            if end > self._coverage[1]:
                end = self._coverage[1]

            for b in data[start : end]:
                counter[b] += 1

            ent = 0.0

            for c in counter:
                if c > 0:
                    freq = c / (end - start)
                    ent += freq * math.log(freq, 256)

            self._values.append(-ent)


    def render(self, cr, area):
        """Draw the bytes distribution for the current binary, if any."""

        size = self._coverage[1] - self._coverage[0]

        step = math.ceil(size / 10)

        start = self._coverage[0]
        last_x = area[0]

        last_y = area[1] + area[3] - (area[3] * self._values[0])
        cr.move_to(last_x, last_y + 2)

        for i in range(self._x_range[0], self._x_range[2], self._step):

            end = i + self._step

            if end > self._coverage[1]:
                end = self._coverage[1]

            x = area[0] + ((end - start) * area[2]) / (10 * step)
            y = area[1] + area[3] - (area[3] * self._values[int((i - self._x_range[0]) / self._step)])

            if last_y != y:
                cr.line_to(last_x, y + 2)
                last_y = y

            cr.line_to(x, y + 2)

            last_x = x

        cr.set_source_rgba(*self._shadow_color)
        cr.set_line_width(4)
        cr.stroke()

        last_x = area[0]

        last_y = area[1] + area[3] - (area[3] * self._values[0])
        cr.move_to(last_x, last_y)

        for i in range(self._x_range[0], self._x_range[2], self._step):

            end = i + self._step

            if end > self._coverage[1]:
                end = self._coverage[1]

            x = area[0] + ((end - start) * area[2]) / (10 * step)
            y = area[1] + area[3] - (area[3] * self._values[int((i - self._x_range[0]) / self._step)])

            if last_y != y:
                cr.line_to(last_x, y)
                last_y = y

            cr.line_to(x, y)

            last_x = x

        cr.set_source_rgba(*self._color)
        cr.set_line_width(2)
        cr.stroke()
