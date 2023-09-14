
from common import RostTestClass


class TestRostSets(RostTestClass):
    """TestCases for sets support in ROST."""

    def testSetsAsBooleans(self):
        """Convert sets to boolean."""

        rule = '''
rule test {

   condition:
      ()

}
'''

        self.check_rule_failure(rule)


        rule = '''
rule test {

   condition:
      (1, )

}
'''

        self.check_rule_success(rule)


        rule = '''
rule test {

   condition:
      ("aaa", true, 123)

}
'''

        self.check_rule_success(rule)


    def testStringAsArray(self):
        """Handle strings as arrays."""

        rule = '''
rule test {

   condition:
      count("aaa")

}
'''

        self.check_rule_success(rule)


        rule = '''
rule test {

   condition:
      count("aaa") == 3

}
'''

        self.check_rule_success(rule)


    def testSetsIntersections(self):
        """Perform sets intersections."""

        rule = '''
rule test {

   condition:
      ("aaa", "bbb") in ("AAA", "BBB", "aaa")

}
'''

        self.check_rule_success(rule)


        rule = '''
rule test {

   condition:
      ("aaa", "bbb") in ("123", )

}
'''

        self.check_rule_failure(rule)













        # TODO :

        # test : intersection(a, a) == a

        # test : "123" in "0123456789"
        # test : "123" in "012987"

