
from common import RostTestClass


class TestRostGrammar(RostTestClass):
    """TestCases for the ROST grammar."""

    def testRelationalExpressions(self):
        """Build expressions with relational comparisons."""

        cases = [

            # Regular
            [ '-1', '<=', '2', True ],
            [ '-1', '<=', '2', True ],
            [ '"aaa"', '==', '"aaa"', True ],
            [ '"aaa"', '<', '"aaaa"', True ],
            [ '""', '<', '"aaaa"', True ],

            # Cast
            [ 'false', '==', '0', True ],
            [ 'false', '==', '1', False ],
            [ 'true', '!=', '0', True ],
            [ '1', '==', 'true', True ],
            [ 'false', '==', '()', True ],
            [ 'true', '==', '(0,)', True ],

        ]

        for op1, kwd, op2, expected in cases:

            rule = '''
rule test {

   condition:
      %s %s %s

}
''' % (op1, kwd, op2)

            if expected:
                self.check_rule_success(rule)
            else:
                self.check_rule_failure(rule)


    def testLogicalOperations(self):
        """Evaluate some logical operations."""

        cases = [
            [ 'true and false', False ],
            [ 'false or false', False ],
            [ 'true and true or false', True ],
            [ 'false or true and false', False ],
            [ '1 or false', True ],
        ]

        for cond, expected in cases:

            rule = '''
rule test {

   condition:
      %s

}
''' % (cond)

            if expected:
                self.check_rule_success(rule)
            else:
                self.check_rule_failure(rule)


    def testArithmeticOperations(self):
        """Evaluate some arithmetic operations."""

        cases = [

            # Clever
            '1 + 2 == 3',
            '10 + -3 == 7',
            '-3 + 10 == 7',
            '-10 - 1 < 0',
            '-10 - 1 == -11',
            '(-10 - 1) == -11',
            '(-1 - -10) == 9',
            '-2 * -3 == 6',
            '-2 * 3 == -6',

            # Legacy
            '1 + 4 * 3 + 2 == 15',
            '(1 + 4) * 3 + 2 == 17',
            '1 + 4 * (3 + 2) == 21',
            '(1 + 4) * (3 + 2) == 25',

        ]

        for c in cases:

            rule = '''
rule test {

   condition:
      %s

}
''' % (c)

            self.check_rule_success(rule)


    def testBasicStringsOperations(self):
        """Build expressions with basic strings operations."""

        cases = [

            # Clever
            [ '123---456', 'contains', '---', True ],
            [ '123---456', 'contains', 'xxx', False ],
            [ '---123---456', 'startswith', '---', True ],
            [ '---123---456', 'startswith', 'xxx', False ],
            [ '123---456---', 'endswith', '---', True ],
            [ '123---456---', 'endswith', 'xxx', False ],
            [ 'AAA---BBB', 'icontains', 'aaa', True ],
            [ 'AAA---BBB', 'icontains', 'xxx', False ],
            [ 'AAA---BBB', 'istartswith', 'aAa', True ],
            [ 'AAA---BBB', 'istartswith', 'xxx', False ],
            [ 'AAA---BBB', 'iendswith', 'bBb', True ],
            [ 'AAA---BBB', 'iendswith', 'xxx', False ],
            [ 'AzertY', 'iequals', 'AZERTY', True ],
            [ 'AzertY', 'iequals', 'AZERTY-', False ],

            # Legacy
            [ '123\t456', 'contains', '\t', True ],
            [ '123-456', 'startswith', '1', True ],
            [ '123-456', 'startswith', '1234', False ],
            [ '123-456', 'endswith', '6', True ],
            [ '123-456', 'endswith', '3456', False ],

        ]

        for op1, kwd, op2, expected in cases:

            rule = '''
rule test {

   condition:
      "%s" %s "%s"

}
''' % (op1, kwd, op2)

            if expected:
                self.check_rule_success(rule)
            else:
                self.check_rule_failure(rule)


    def testSizeUnits(self):
        """Evaluate size units."""

        cases = [
            '1KB == 1024',
            '2MB == 2 * 1024 * 1024',
            '4Kb == (4 * 1024)',
            '1KB <= 1024 and 1024 < 1MB',
        ]

        for c in cases:

            rule = '''
rule test {

   condition:
      %s

}
''' % (c)

            self.check_rule_success(rule)






# TODO : test     <haystack> matches <regex>



