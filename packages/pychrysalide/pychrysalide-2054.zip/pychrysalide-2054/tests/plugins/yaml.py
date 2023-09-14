#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.plugins import yaml


class TestYamlSupport(ChrysalideTestCase):
    """TestCase for the YAML support."""


    def testParseSimpleYamlContent(self):
        """Parse basic YAML content."""

        definitions = '''
a: av
b: bv
c: cv
'''

        root = yaml.parse_from_text(definitions)

        self.assertFalse(root.is_sequence)

        self.assertEqual(root.nodes[0].key, 'a')
        self.assertEqual(root.nodes[1].key, 'b')
        self.assertEqual(root.nodes[2].key, 'c')

        self.assertEqual(root.nodes[0].value, 'av')
        self.assertEqual(root.nodes[1].value, 'bv')
        self.assertEqual(root.nodes[2].value, 'cv')

        definitions = '''
- a: av
- b: bv
- c: cv
'''

        root = yaml.parse_from_text(definitions)

        self.assertTrue(root.is_sequence)

        self.assertEqual(root.nodes[0].nodes[0].key, 'a')
        self.assertEqual(root.nodes[1].nodes[0].key, 'b')
        self.assertEqual(root.nodes[2].nodes[0].key, 'c')

        self.assertEqual(root.nodes[0].nodes[0].value, 'av')
        self.assertEqual(root.nodes[1].nodes[0].value, 'bv')
        self.assertEqual(root.nodes[2].nodes[0].value, 'cv')


    def testSearchYamlNodes(self):
        """Search YAML nodes related to paths."""

        definitions = '''
root:
  a: v0
  b: v1
  c: v2
  sub:
    aa: v00
    bb: v01
    cc:
      - i: w
      - j: x
      - k: c
  d: v3
'''

        root = yaml.parse_from_text(definitions)

        found = root.find_first_by_path('/root/a')

        self.assertEqual(found.value, 'v0')

        found = root.find_first_by_path('/root/sub')

        self.assertEqual(found.value, None)

        found = root.find_first_by_path('/root/sub/cc')

        self.assertEqual(found.value, None)

        found = root.find_first_by_path('/root/sub/cc/j')

        self.assertEqual(found.value, 'x')

        found = root.find_first_by_path('/root/d')

        self.assertEqual(found.value, 'v3')


        definitions = '''
root:
  - a: av
    aa: aav
    ab: abv
  - b: bv
    ba: bav
    bb: bbv
'''

        root = yaml.parse_from_text(definitions)

        found = root.find_first_by_path('/root/ba')

        self.assertEqual(found.value, 'bav')

        found = root.find_first_by_path('/root/b')

        self.assertEqual(found.value, 'bv')

        found = root.find_first_by_path('/root/')

        self.assertTrue(found.is_sequence)
        self.assertFalse(found.nodes[0].is_sequence)
        self.assertEqual(found.nodes[0].nodes[0].value, 'av')


    def testComplexYamlContent(self):
        """Process more complex YAML content."""

        definitions = '''
root:
  a: 'v0'
  b: 'v1 ? 1 : 2'
  c: v2 # final comment
  d: "'xx::xx'"
'''

        root = yaml.parse_from_text(definitions)

        found = root.find_first_by_path('/root/a')

        self.assertEqual(found.value, 'v0')

        found = root.find_first_by_path('/root/b')

        self.assertEqual(found.value, 'v1 ? 1 : 2')

        found = root.find_first_by_path('/root/c')

        self.assertEqual(found.value, 'v2')

        found = root.find_first_by_path('/root/d')

        self.assertEqual(found.value, "'xx::xx'")


    def testArrayAsSeq(self):
        """Handle array as YAML block sequence."""

        definitions = '''
root:
  a: [ a, 'b', 0xcc, "\td\n\\"'" ]
'''

        root = yaml.parse_from_text(definitions)

        found = root.find_first_by_path('/root/a')

        self.assertIsNone(found.value)

        self.assertEqual(len(found.children.nodes), 4)

        self.assertEqual(found.children.nodes[0].key, 'a')

        self.assertEqual(found.children.nodes[1].key, 'b')

        self.assertEqual(found.children.nodes[2].key, '0xcc')

        self.assertEqual(found.children.nodes[3].key, "\td \"'")

        self.assertEqual(found.aggregate_value(), '[ a, \'b\', 0xcc, "	d \"\'" ]')
