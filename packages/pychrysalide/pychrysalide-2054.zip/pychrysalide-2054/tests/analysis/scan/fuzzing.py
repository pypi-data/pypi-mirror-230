
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.analysis.scan import ContentScanner
from pychrysalide.analysis.scan import ScanOptions
from pychrysalide.analysis.scan.patterns.backends import AcismBackend
from pychrysalide.analysis.scan.patterns.backends import BitapBackend


class TestRostFuzzingFixes(RostTestClass):
    """TestCases to remember all the fixes for crashes identified by fuzzing."""

    def testEmptyPatternListWithContent(self):
        """Check no backend is run if there is no pattern to look for."""

        content = MemoryContent(b'\n')

        rule = '''
'''

        backends = [
            AcismBackend, # This one was segfaulting
            BitapBackend,
        ]

        for b in backends:

            options = ScanOptions()
            options.backend_for_data = b

            scanner = ContentScanner(rule)
            ctx = scanner.analyze(options, content)

            self.assertIsNotNone(ctx)


    def testMandatoryCondition(self):
        """Ensure a condition section exists in a rule."""

        rule = '''
rule test {

}
'''

        with self.assertRaisesRegex(ValueError, 'Unable to create content scanner'):

            scanner = ContentScanner(rule)


    def testNonExistingPattern(self):
        """Avoid to count the matches of a non-existing pattern."""

        rule = '''
rule test {

   condition:
      #badid

}
'''

        with self.assertRaisesRegex(ValueError, 'Unable to create content scanner'):

            scanner = ContentScanner(rule)


    def testNamespacesWithoutReductionCode(self):
        """Clean the code for ROST namespaces."""

        rule = '''
rule test {

   condition:
      console

}
'''

        self.check_rule_failure(rule)


    def testCallOnNonCallable(self):
        """Reject calls on non callable expressions softly."""

        rule = '''
rule test {

   condition:
      console.log().log()

}
'''

        self.check_rule_failure(rule)


    def testSelfReferencingRule(self):
        """Reject any rule referencing itself as match condition."""

        rule = '''
rule test {

   condition:
      test

}
'''

        self.check_rule_failure(rule)
