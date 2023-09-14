
class GlimpseMethod():
    """Abstract class for gimpses."""


    def __init__(self, builder, config, update_cb):
        """Populate the class with its attributes."""

        self._builder = builder
        self._config = config
        self._update_cb = update_cb

        self._v_legend = None
        self._h_legend = None

        self._x_range = None
        self._y_range = None


    def switch(self):
        """Switch the panel labels to the method ones."""

        lbl = self._builder.get_object('v_legend')
        lbl.set_text(self._v_legend)

        lbl = self._builder.get_object('h_legend')
        lbl.set_text(self._h_legend)


    def setup_rendering(self):
        """Provide information useful for drawing the grid."""

        return self._x_range, self._y_range


    def format_legend(self, value, vert):
        """Build the label used for a rule."""

        return str(value)


    def update(self, data, coverage):
        """Compute internal values for the method."""

        pass


    def render(self, cr, area):
        """Draw the bytes distribution for the current binary, if any."""

        pass
