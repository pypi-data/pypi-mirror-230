
from common import RostTestClass


class TestRostBooleans(RostTestClass):
    """TestCases for booleans and ROST."""

    def testFinalCondition(self):
        """Validate the final condition."""

        rule = '''
rule test {

   condition:
      false

}
'''

        self.check_rule_failure(rule)


        rule = '''
rule test {

   condition:
      true

}
'''

        self.check_rule_success(rule)


    def testBasicBooleanOperations(self):
        """Evaluate basic boolean operations."""

        rule = '''
rule test {

   condition:
      true and false

}
'''

        self.check_rule_failure(rule)


        rule = '''
rule test {

   condition:
      true or false

}
'''

        self.check_rule_success(rule)


    def testImplicitCast(self):
        """Imply implicit casts to booleans."""

        rule = '''
rule test {

   condition:
      true and 0

}
'''

        self.check_rule_failure(rule)


        rule = '''
rule test {

   condition:
      1 or false

}
'''

        self.check_rule_success(rule)


        rule = '''
rule test {

   condition:
      1 or ()

}
'''

        self.check_rule_success(rule)
