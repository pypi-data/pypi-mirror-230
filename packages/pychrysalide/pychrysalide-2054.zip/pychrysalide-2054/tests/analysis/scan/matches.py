
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent


class TestRostMatchs(RostTestClass):
    """TestCases for the ROST pattern matching engine."""

    def testCountMatches(self):
        """Count matches patterns."""

        cnt = MemoryContent(b'aaa aaa bbb aaa')

        rule = '''
rule test {

   strings:
      $a = "aaa"
      $b = "bbb"

   condition:
      #a == 3 and #b < 2

}
'''

        self.check_rule_success(rule, cnt)
