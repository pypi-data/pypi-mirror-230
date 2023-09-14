
from common import RostTestClass
from pychrysalide.analysis.contents import MemoryContent


class TestRostExamples(RostTestClass):
    """TestCases for the examples provides in the ROST documentation."""

    def testComments(self):
        """Ensure comments do not bother rule definitions."""

        rule = '''
/*
    Multi-line header...
*/

rule test {    // comment

   /*
    * Some context
    */

   condition:  /* List of condition(s) */
      true     // Dummy condition

}
'''

        self.check_rule_success(rule)


    def testArithmeticPrecedence(self):
        """Take care of arithmetic operators precedence."""

        rule = '''
rule test {  // MulFirst

   condition:
      1 + 4 * (3 + 2) == 21
      and
      (1 + 4) * (3 + 2) == 25

}
'''

        self.check_rule_success(rule)


    def testUintCast(self):
        """Process nested integer values from binary content."""

        cnt = MemoryContent(b'\x4d\x5a\x00\x00' + b'\x50\x45\x00\x00' + 52 * b'\x00' + b'\x04\x00\x00\x00')

        rule = '''
rule test {  // IsPE

    condition:

        // MZ signature at offset 0 and ...

        uint16(0) == 0x5a4d and

        // ... PE signature at offset stored in the MZ header at offset 0x3c

        uint32(uint32(0x3c)) == 0x00004550

}
'''

        self.check_rule_success(rule, cnt)
