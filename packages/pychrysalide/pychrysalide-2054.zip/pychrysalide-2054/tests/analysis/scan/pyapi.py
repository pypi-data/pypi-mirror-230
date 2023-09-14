
import binascii

from chrysacase import ChrysalideTestCase
from gi._constants import TYPE_INVALID
from pychrysalide.analysis.scan import ScanExpression
from pychrysalide.analysis.scan import ScanOptions
from pychrysalide.analysis.scan import find_token_modifiers_for_name
from pychrysalide.glibext import ComparableItem


class TestRostPythonAPI(ChrysalideTestCase):
    """TestCase for the ROST Python API."""

    def testEmptyOptions(self):
        """Check default scan options."""

        ops = ScanOptions()

        self.assertEqual(ops.backend_for_data, TYPE_INVALID)


    def testDirectInstancesOfExpression(self):
        """Reject direct instances of ROST expressions."""

        with self.assertRaisesRegex(RuntimeError, 'pychrysalide.analysis.scan.ScanExpression is an abstract class'):

            e = ScanExpression()


    def testBooleanComparison(self):
        """Compare custom scan expressions."""

        class StrLenExpr(ScanExpression):

            def __init__(self, value):
                super().__init__(ScanExpression.ExprValueType.STRING)
                self._value = value

            def _cmp_rich(self, other, op):

                if op == ComparableItem.RichCmpOperation.EQ:
                    return len(self._value) == len(other._value)


        e0 = StrLenExpr('00000000000')

        e1 = StrLenExpr('00000000000')

        e2 = StrLenExpr('000000000000000000000000000')

        self.assertTrue(e0 == e1)

        # !?
        # Python teste e0 != e1 (non implémenté), puis e1 != e0 (pareil) et en déduit une différence !
        # self.assertFalse(e0 != e1)

        self.assertFalse(e0 == e2)

        # TypeError: '<' not supported between instances of 'StrLenExpr' and 'StrLenExpr'
        with self.assertRaisesRegex(TypeError, '\'<\' not supported between instances'):
            self.assertTrue(e0 < e1)


    def testBytePatternModifiers(self):
        """Validate the bytes produced by modifiers."""

        mod = find_token_modifiers_for_name('plain')
        self.assertIsNotNone(mod)

        source = b'ABC'
        transformed = mod.transform(source)

        self.assertEqual(source, transformed[0])

        mod = find_token_modifiers_for_name('hex')
        self.assertIsNotNone(mod)

        source = b'ABC'
        transformed = mod.transform(source)

        self.assertEqual(binascii.hexlify(source), transformed[0])

        mod = find_token_modifiers_for_name('rev')
        self.assertIsNotNone(mod)

        source = b'ABC'
        transformed = mod.transform(source)

        self.assertEqual(source[::-1], transformed[0])
