
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from chrysacase import ChrysalideTestCase
from pychrysalide.glibext import ConfigParam, GenConfig


class TestConfiguration(ChrysalideTestCase):
    """TestCase for configuration related items.*"""


    def testCfgParamValues(self):
        """Set and unset configuration parameter values."""

        color = Gdk.RGBA()
        color.parse('#3465A4')

        param = ConfigParam('config.color', ConfigParam.ConfigParamType.COLOR, color)

        self.assertEqual(param.value, color)

        param.make_empty()

        void = Gdk.RGBA(red=0, green=0, blue=0, alpha=0)
        self.assertEqual(param.value, void)

        param.value = color

        self.assertEqual(param.value, color)


    def testCfgParamStates(self):
        """Validate all states of an evolving parameter."""

        param = ConfigParam('config.int', ConfigParam.ConfigParamType.INTEGER)

        self.assertEqual(param.state, ConfigParam.ConfigParamState.EMPTY | ConfigParam.ConfigParamState.DEFAULT)

        param.make_empty()

        self.assertEqual(param.state, ConfigParam.ConfigParamState.EMPTY | ConfigParam.ConfigParamState.DEFAULT)

        param = ConfigParam('config.int', ConfigParam.ConfigParamType.INTEGER, 0x123)

        self.assertEqual(param.value, 0x123)

        self.assertEqual(param.state, ConfigParam.ConfigParamState.DEFAULT)

        param.make_empty()

        self.assertEqual(param.state, ConfigParam.ConfigParamState.EMPTY | ConfigParam.ConfigParamState.CHANGED)

        param.value = 0x1

        self.assertEqual(param.state, ConfigParam.ConfigParamState.CHANGED)

        param.reset()

        self.assertEqual(param.state, ConfigParam.ConfigParamState.DEFAULT)


    def testCfgParamDesc(self):
        """Export types and states as strings when needed."""

        param = ConfigParam('config.int', ConfigParam.ConfigParamType.INTEGER)

        self.assertTrue('|' in str(param.state))

        self.assertTrue('.' in str(param.type))


    def testConfiguration(self):
        """Feed and browse a basic configuration."""

        config = GenConfig()
        self.assertIsNotNone(config)
        self.assertIsNone(config.filename)

        for i in range(5):
            param = ConfigParam('config.int.%u' % i, ConfigParam.ConfigParamType.INTEGER, i)
            config.add(param)

        chain = ''

        for p in config.params:
            chain += '%u' % p.value

        self.assertTrue(chain == ''.join([ '%u' % i for i in range(5) ]))

        found = config.search('config.int.3')
        self.assertTrue(found.value == 3)

        found = config.search('config.int.33')
        self.assertIsNone(found)

        for p in config.params:
            p.value *= 10

        chain = ''

        for p in config.params:
            chain += '%u' % p.value

        self.assertTrue(chain == ''.join([ '%u' % (i * 10) for i in range(5) ]))
