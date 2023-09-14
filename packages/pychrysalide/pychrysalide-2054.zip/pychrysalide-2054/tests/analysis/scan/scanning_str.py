
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent


class TestRostScanningStrings(RostTestClass):
    """TestCases for the bytes section syntax (strings)."""

    def testSimpleStringPattern(self):
        """Test a simple string pattern."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = "Abc"

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


    def testEscapedStringPattern(self):
        """Test escaped string patterns."""

        cnt = MemoryContent(b'\a\b\t\n\v\f\r' + bytes([ 0x1b ]) + b'"\\\xff')

        rule = r'''
rule test {

   strings:
      $a = "\a\b\t\n\v\f\r\e\"\\\xff"

   condition:
      #a == 1 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'\a\b\t\n--123--\v\f\r' + bytes([ 0x1b ]) + b'"\\\xff')

        rule = r'''
rule test {

   strings:
      $a = "\a\b\t\n--123--\v\f\r\e\"\\\xff"

   condition:
      #a == 1 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


    def testStringModifiers(self):
        """Check string modifiers output."""

        cnt = MemoryContent(b'--414243--')

        rule = '''
rule test {

   strings:
      $a = "ABC" hex

   condition:
      #a == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'--ABC--')

        rule = '''
rule test {

   strings:
      $a = "ABC" plain

   condition:
      #a == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'--CBA--')

        rule = '''
rule test {

   strings:
      $a = "ABC" rev

   condition:
      #a == 1

}
'''


    def testStringPatternFullword(self):
        """Test a fullword string pattern."""

        cnt = MemoryContent(b'ABCDEF 123 ')

        rule = '''
rule test {

   strings:
      $a = "DEF" fullword
      $b = "123" fullword

   condition:
      #a == 0 and #b == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'DEF 123 ')

        rule = '''
rule test {

   strings:
      $a = "DEF" fullword
      $b = "123" fullword

   condition:
      #a == 1 and #b == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'\tDEF 123 ')

        rule = '''
rule test {

   strings:
      $a = "DEF" fullword
      $b = "123" fullword

   condition:
      #a == 1 and #b == 1

}
'''

        self.check_rule_success(rule, content=cnt)


    def testStringPatternCase(self):
        """Test a string pattern with case care."""

        cnt = MemoryContent(b'abc123-Abc123Def456GHI...z0z1z2z3z4z5z6z7z8z9')

        rule = '''
rule test {

   strings:
      $a = "Abc" nocase
      $b = "ABC123DEF456GHI" nocase
      $z = "z0z1z2z3z4z5z6z7z8z9" nocase

   condition:
      #a == 2 and #b == 1 and #z == 1

}
'''

        self.check_rule_success(rule, content=cnt)
