
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent


class TestRostScanningBinary(RostTestClass):
    """TestCases for the bytes section syntax (binary)."""

    def testLonelyPatterns(self):
        """Evaluate the most simple patterns."""

        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { 41 }

   condition:
      #a == 1 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { 62 }

   condition:
      #a == 1 and @a[0] == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { 66 }

   condition:
      #a == 1 and @a[0] == 5

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ?1 }

   condition:
      #a == 1 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ?2 }

   condition:
      #a == 1 and @a[0] == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ?6 }

   condition:
      #a == 1 and @a[0] == 5

}
'''

        self.check_rule_success(rule, content=cnt)


    def testLonelyPatternsNot(self):
        """Evaluate the most simple patterns (not version)."""

        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~41 }

   condition:
      #a == 5 and @a[0] == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~62 }

   condition:
      #a == 5 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~66 }

   condition:
      #a == 5 and @a[4] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~?1 }

   condition:
      #a == 5 and @a[0] == 1

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~?2 }

   condition:
      #a == 5 and @a[0] == 0

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'Abcdef')

        rule = '''
rule test {

   strings:
      $a = { ~?6 }

   condition:
      #a == 5 and @a[4] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


    def testSimpleHexPattern(self):
        """Test a simple hex pattern."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 41 62 63 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 2d 41 62 63 }

   condition:
      #a == 1 and @a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


    def testSimpleMaskedHexPattern(self):
        """Test a simple masked hex pattern."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?1 6? ?3 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


    def testHexPatternWithPlainAndMasked(self):
        """Test hex patterns with plain and masked bytes."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 41 6? ?3 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 4? 62 ?3 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 4? ?2 63 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 4? ?2 ?3 }

   condition:
      #a == 1 and @a[0] == 4

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 2d 4? ?2 63 }

   condition:
      #a == 1 and @a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 2d 4? 62 ?3 2d }

   condition:
      #a == 1 and @a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 2? 41 6? 63 ?d }

   condition:
      #a == 1 and @a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


    def testHexPatternWithPlainAndHoles(self):
        """Test hex patterns with plain bytes and holes."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 33 ?? 41 ?? 63 ?? 34 }

   condition:
      #a == 1 and @a[0] == 2

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? 33 ?? 41 ?? 63 ?? 34 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? 33 [1-5] 63 ?? 34 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { [3-4] 41 ?? 63 ?? 34 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? 33 ?? 41 ?? 63 [3-] }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


    def testHexPatternWithMaskedAndHoles(self):
        """Test hex patterns with masked bytes and holes."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?3 ?? 4? ?? 6? ?? ?4 }

   condition:
      #a == 1 and @a[0] == 2

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? ?3 ?? 4? ?? 6? ?? ?4 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? ?3 [1-5] ?3 ?? ?4 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { [3-4] ?1 ?? ?3 ?? ?4 ?? }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ?? 3? ?? 4? ?? 6? [3-] }

   condition:
      #a == 1 and @a[0] == 1 and !a[0] == 9

}
'''

        self.check_rule_success(rule, content=cnt)


    def testPipedPlainHexPatterns(self):
        """Look for several patterns at once with piped definition."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 41 62 ( 63 | 64 | 65 ) }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ( 41 | f2 | f3 ) 62 63 }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 41 ( 61 | 62 | 63 ) 63 }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ( 41 62 63 | 42 62 63 | 43 62 63 ) }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


    def testPipedMaskedHexPatterns(self):
        """Look for several patterns at once with piped definition."""

        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 4? 6? ( ?3 | ?4 | ?5 ) }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ( ?1 | ?2 | ?3 ) 6? 6? }

   condition:
      console.log("COUNTER: ", #a) and #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { 4? ( ?1 | ?2 | ?3 ) 6? }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)


        cnt = MemoryContent(b'123-Abc-456')

        rule = '''
rule test {

   strings:
      $a = { ( 4? ?2 ?3 | 4? 6? 6? | ?3 6? ?3 ) }

   condition:
      #a == 1 and @a[0] == 4 and !a[0] == 3

}
'''

        self.check_rule_success(rule, content=cnt)
