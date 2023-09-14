
from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.analysis.scan import ContentScanner
from pychrysalide.analysis.scan import ScanOptions
from pychrysalide.analysis.scan.patterns.backends import AcismBackend


class RostTestClass(ChrysalideTestCase):
    """TestCase for analysis.scan.ScanExpression."""

    @classmethod
    def setUpClass(cls):

        super(RostTestClass, cls).setUpClass()

        cls._options = ScanOptions()
        cls._options.backend_for_data = AcismBackend

        cls._empty_content = MemoryContent(b'')


    def _validate_rule_result(self, rule, content, expected):
        """Check for scan success or failure."""

        scanner = ContentScanner(rule)
        ctx = scanner.analyze(self._options, content)

        self.assertIsNotNone(ctx)

        if expected:
            self.assertTrue(ctx.has_match_for_rule('test'))
        else:
            self.assertFalse(ctx.has_match_for_rule('test'))


    def check_rule_success(self, rule, content = None):
        """Check for scan success."""

        if content is None:
            content = self._empty_content

        self._validate_rule_result(rule, content, True)


    def check_rule_failure(self, rule, content = None):
        """Check for scan failure."""

        if content is None:
            content = self._empty_content

        self._validate_rule_result(rule, content, False)
