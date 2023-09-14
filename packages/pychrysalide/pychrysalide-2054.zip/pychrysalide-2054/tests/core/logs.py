
from chrysacase import ChrysalideTestCase
from pychrysalide import core


class TestCoreLogs(ChrysalideTestCase):
    """TestCase for analysis.core.core."""

    def testDefaultLevel(self):
        """Ensure all messages are hidden by default."""

        self.assertEqual(core.get_verbosity(), core.LogMessageType.COUNT)


    def testWrongLevel(self):
        """Verify the type of level when defining new verbosity."""

        with self.assertRaisesRegex(Exception, 'unable to convert the provided argument to LogMessageType'):

            core.set_verbosity('XXX')


    def testWrongMessage(self):
        """Check for unhandled message level."""

        with self.assertRaisesRegex(Exception, 'invalid value for LogMessageType'):

            core.log_message(core.LogMessageType.COUNT, 'Message')
