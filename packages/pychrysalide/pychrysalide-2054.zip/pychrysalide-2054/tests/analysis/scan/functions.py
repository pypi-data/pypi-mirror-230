
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent


class TestRostFunctions(RostTestClass):
    """TestCases for the core functions of ROST."""

    # Core
    # ====

    def testDatasize(self):
        """Handle the size of the provided data."""

        cnt = MemoryContent(b'\x01\x02\x03\x04')

        cases = [
            'datasize == 4',
            'uint16(0) == 0x201 and uint16(datasize - 2) == 0x0403',
        ]

        for c in cases:

            rule = '''
rule test {

   condition:
      %s

}
''' % c

            self.check_rule_success(rule, cnt)


    # Modules
    # =======

    def testConsole(self):
        """Ensure logging always returns true."""

        rule = '''
rule test {

   condition:
      console.log()

}
'''

        self.check_rule_success(rule)


    def testMagic(self):
        """Scan text content with the Magic module."""

        cnt = MemoryContent(b'aaaa')

        cases = [
            [ 'type', 'ASCII text, with no line terminators' ],
            [ 'mime_encoding', 'us-ascii' ],
            [ 'mime_type', 'text/plain' ],
        ]

        for target, expected in cases:

            rule = '''
rule test {

   condition:
      magic.%s() == "%s"

}
''' % (target, expected)

            self.check_rule_success(rule, cnt)


    def testMathOperations(self):
        """Perform math operations with core functions."""

        rule = '''
rule test {

   condition:
      math.to_string(123) == "123"
         and math.to_string(291, 16) == "0x123"
         and math.to_string(-83, 8) == "-0123"
         and math.to_string(123, 2) == "0b1111011"

}
'''

        self.check_rule_success(rule)


    def testStringOperations(self):
        """Perform string operations with core functions."""

        rule = '''
rule test {

   condition:
      string.lower("ABCd") == "abcd" and string.lower("123abc") == "123abc"

}
'''

        self.check_rule_success(rule)

        rule = '''
rule test {

   condition:
      string.upper("abcD") == "ABCD" and string.upper("123ABC") == "123ABC"

}
'''

        self.check_rule_success(rule)

        rule = '''
rule test {

   condition:
      string.to_int("123") == 123
         and string.to_int("123", 16) == 291
         and string.to_int("0x123") == 291
         and string.to_int("-0123") == -83

}
'''

        self.check_rule_success(rule)


    def testTime(self):
        """Check current time."""

        # Cf. https://www.epochconverter.com/

        rule = '''
rule test {

   condition:
      time.make(2023, 8, 5, 22, 8, 41) == 0x64cec869

}
'''

        self.check_rule_success(rule)

        rule = '''
rule test {

   condition:
      time.now() >= 0x64cec874 and time.now() <= time.now()

}
'''

        self.check_rule_success(rule)
