#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-

import locale

from chrysacase import ChrysalideTestCase
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.plugins.kaitai.parsers import KaitaiStruct


class TestKaitaiStruct(ChrysalideTestCase):
    """TestCase for the KaitaiStruct parsing."""


    @classmethod
    def setUpClass(cls):

        super(TestKaitaiStruct, cls).setUpClass()

        cls.log('Setting locale suitable for floats...')

        cls._old_locale = locale.getlocale(locale.LC_NUMERIC)

        locale.setlocale(locale.LC_NUMERIC, 'C')


    @classmethod
    def tearDownClass(cls):

        super(TestKaitaiStruct, cls).tearDownClass()

        cls.log('Reverting locale...')

        locale.setlocale(locale.LC_NUMERIC, cls._old_locale)



    #################################
    ### 4. Kaitai Struct language
    #################################


    def testKaitaiFixedLength(self):
        """Load fixed-size structures."""

        # Cf. 4.1. Fixed-size structures

        definitions = '''
meta:
  id: mydesc
  title: My Long Title
  endian: be
seq:
  - id: field0
    type: u4
'''

        kstruct = KaitaiStruct(definitions)

        self.assertEqual(kstruct.meta.id, 'mydesc')
        self.assertEqual(kstruct.meta.title, 'My Long Title')

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)
        self.assertEqual(parsed.field0.value, 0x01020304)

        definitions = '''
meta:
  endian: le
seq:
  - id: field0
    type: u4
  - id: field1
    type: u4be
'''

        kstruct = KaitaiStruct(definitions)

        self.assertIsNone(kstruct.meta.id)
        self.assertIsNone(kstruct.meta.title)

        content = MemoryContent(b'\x01\x02\x03\x04\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)
        self.assertEqual(parsed.field0.value, 0x04030201)

        self.assertEqual(parsed.field1.range.length, 4)
        self.assertEqual(parsed.field1.value, 0x01020304)


        definitions = '''
seq:
  - id: field0
    type: u1
  - id: field1
    size: 2
  - id: field2
    size: field0 + 1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04\x05')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 1)
        self.assertEqual(parsed.field0.value, 0x01)

        self.assertEqual(parsed.field1.range.length, 2)
        self.assertEqual(parsed.field1.truncated_bytes, b'\x02\x03')

        self.assertEqual(parsed.field2.range.length, 2)
        self.assertEqual(parsed.field2.truncated_bytes, b'\x04\x05')


    def testDocstrings(self):
        """Handle Kaitai documentation."""

        # Cf. 4.2. Docstrings

        definitions = '''
seq:
  - id: rating
    type: s4
    doc: Rating, can be negative
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x02\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.rating.creator.doc, 'Rating, can be negative')


    def testKaitaiContents(self):
        """Read various forms of fixed content."""

        # Cf. 4.3. Checking for "magic" signatures

        definitions = '''
seq:
  - id: field0
    contents: [ 0, 0x10, '22', "50 ]
'''

        # ValueError: Unable to create Kaitai structure.
        with self.assertRaisesRegex(ValueError, "Unable to create Kaitai structure"):
            kstruct = KaitaiStruct(definitions)
            self.assertIsNotNone(kstruct)


        definitions = '''
seq:
  - id: field0
    contents: [ 0x41, 66, 'CD' ]
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABCD')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)

        self.assertEqual(parsed.field0.value, b'ABCD')


        definitions = '''
seq:
  - id: field0
    contents: ABCD
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABCD')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)


        definitions = '''
seq:
  - id: field0
    contents: "ABCD"
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABCD')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)


        definitions = '''
seq:
  - id: field0
    contents:
      - 0x41
      - "B"
      - CD
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABCD')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.range.length, 4)


    def testVariableLengthStructures(self):
        """Parse variable-length structures."""

        # Cf. 4.4. Variable-length structures

        definitions = '''
seq:
  - id: my_len
    type: u1
  - id: my_str
    type: str
    size: my_len
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x03ABC')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_len.value, 3)

        self.assertEqual(parsed.my_str.value, b'ABC')


        definitions = '''
seq:
  - id: my_len
    type: u1
  - id: my_str
    type: str
    size: my_len * 2
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x03ABCDEF')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_len.value, 3)

        self.assertEqual(parsed.my_str.value, b'ABCDEF')


        definitions = '''
seq:
  - id: field0
    size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x02\x03')

        parsed = kstruct.parse(content)

        self.assertEqual(content, parsed.content)

        self.assertEqual(parsed.range.addr.phys, 0)
        self.assertEqual(parsed.range.length, len(content.data))


    def testDelimitedStructures(self):
        """Parse delimited structures."""

        # Cf. 4.5. Delimited structures

        definitions = '''
seq:
  - id: my_string
    type: str
    terminator: 0
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABC\x00DEF')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_string.value, b'ABC')


        definitions = '''
seq:
  - id: my_string
    type: strz
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABC\x00DEF')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_string.value, b'ABC')


        definitions = '''
seq:
  - id: name
    type: str
    size: 8
    terminator: 0
  - id: guard
    size: 1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'ABC\x00\x00\x00\x00\x00x\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.name.value, b'ABC')

        self.assertEqual(parsed.guard.value, b'x')


    def __passed__testEnums(self):
        """Parse delimited structures."""

        # Cf. 4.6. Enums (named integer constants)

        pass


    def testSubTypes(self):
        """Includes subtypes definitions."""

        # Cf. 4.7. Substructures (subtypes)

        definitions = '''
seq:
  - id: field0
    type: custom_type
  - id: field1
    type: custom_type
  - id: field2
    type: custom_type
types:
  custom_type:
    seq:
      - id: len
        type: u1
      - id: value
        size: len
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\xaa\x02\xbb\xbb\x03\xcc\xcc\xcc')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.len.value, 1)
        self.assertEqual(parsed.field0.value.truncated_bytes, b'\xaa')

        self.assertEqual(parsed.field1.len.value, 2)
        self.assertEqual(parsed.field1.value.truncated_bytes, b'\xbb\xbb')

        self.assertEqual(parsed.field2.len.value, 3)
        self.assertEqual(parsed.field2.value.truncated_bytes, b'\xcc\xcc\xcc')


    def testOtherAttributesAccess(self):
        """Access attributes in other types."""

        # Cf. 4.8. Accessing attributes in other types

        definitions = '''
seq:
  - id: header
    type: main_header
  - id: body
    size: header.body_len
types:
  main_header:
    seq:
      - id: magic
        contents: FMT
      - id: body_len
        type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'FMT\x04\xaa\xbb\xcc\xdd')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.header.magic.raw_bytes, b'FMT')
        self.assertEqual(parsed.header.magic.range.length, 3)

        self.assertEqual(parsed.header.body_len.value, 4)

        self.assertEqual(parsed.body.raw_bytes, b'\xaa\xbb\xcc\xdd')
        self.assertEqual(parsed.body.range.length, 4)


    def testConditionals(self):
        """Read Kaitai values according to previous loaded values."""

        # Cf. 4.9. Conditionals

        definitions = '''
seq:
  - id: field1
    type: u1
  - id: field2
    type: u1
  - id: field3
    type: u1
    if: field1 + field2 > 10
  - id: field4
    type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field1.value, 0x01)
        self.assertEqual(parsed.field2.value, 0x02)
        self.assertFalse(hasattr(parsed, 'field3'))
        self.assertEqual(parsed.field4.value, 0x03)


        definitions = '''
seq:
  - id: field1
    type: u1
  - id: field2
    type: u1
  - id: field3
    type: u1
    if: field1 + field2 > 1
  - id: field4
    type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field1.value, 0x01)
        self.assertEqual(parsed.field2.value, 0x02)
        self.assertTrue(hasattr(parsed, 'field3'))
        self.assertEqual(parsed.field4.value, 0x04)


        definitions = '''
seq:
  - id: field1
    type: u1
  - id: field2
    type: u1
  - id: field3
    type: u1
    if: field1 + field2 == threshold::three
  - id: field4
    type: u1
enums:
  threshold:
    1: one
    2: two
    3: three
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field1.value, 0x01)
        self.assertEqual(parsed.field2.value, 0x02)
        self.assertTrue(hasattr(parsed, 'field3'))
        self.assertEqual(parsed.field4.value, 0x04)


    def testRepeatedReadUntilEOS(self):
        """Read items until the end of the stream."""

        # Cf. 4.10.1. Repeat until end of stream

        definitions = '''
seq:
  - id: field0
    type: u2be
    repeat: eos
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x00\x02\x00\x03\x00\x04\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(len(parsed.field0), len(content.data) / 2)

        for i in range(4):
            self.assertEqual(parsed.field0[i].value, (i + 1) << 8)


    def testRepeatedReadAccordingToCounter(self):
        """Repeat read of items for a nomber of times."""

        # Cf. 4.10.2. Repeat for a number of times

        definitions = '''
seq:
  - id: field0
    type: u1
  - id: field1
    type: u1
    repeat: expr
    repeat-expr: 1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x01')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.value, 0x01)

        self.assertEqual(len(parsed.field1), 1)

        for i in range(1):
            self.assertEqual(parsed.field1[i].value, i + 1)

        definitions = '''
seq:
  - id: field0
    type: u1
  - id: field1
    type: u1
  - id: field2
    type: u2
    repeat: expr
    repeat-expr: field0 + field1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x01\x00\x02\x00\x03\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field0.value, 0x01)
        self.assertEqual(parsed.field1.value, 0x02)

        self.assertEqual(len(parsed.field2), 3)

        for i in range(3):
            self.assertEqual(parsed.field2[i].value, i + 1)


    def testRepeatUntilConditionIsMet(self):
        """Repeat until condition is met."""

        # Cf. 4.10.3. Repeat until condition is met

        definitions = '''
seq:
  - id: numbers
    type: u1
    repeat: until
    repeat-until: _ == 0xff
  - id: extra
    type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\xff\xcc')

        parsed = kstruct.parse(content)

        self.assertEqual(len(parsed.numbers), 3)

        for i in range(2):
            self.assertEqual(parsed.numbers[i].value, i + 1)

        self.assertEqual(parsed.numbers[2].value, 0xff)

        self.assertEqual(parsed.extra.value, 0xcc)

        definitions = '''
seq:
  - id: records
    type: buffer_with_len
    repeat: until
    repeat-until: _.len == 0
types:
  buffer_with_len:
    seq:
      - id: len
        type: u1
      - id: value
        size: len
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x02\xaa\xaa\x01\xbb\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.records[0].len.value, 2)
        self.assertEqual(parsed.records[0].value.raw_bytes, b'\xaa\xaa')

        self.assertEqual(parsed.records[1].len.value, 1)
        self.assertEqual(parsed.records[1].value.raw_bytes, b'\xbb')

        self.assertEqual(parsed.records[2].len.value, 0)
        self.assertEqual(parsed.records[2].value.raw_bytes, b'')


    def testParseTLVImplementation(self):
        """Parse a typical TLV implementation."""

        # Cf. 4.11. Typical TLV implementation (switching types on an expression)

        definitions = '''
seq:
  - id: record
    type: rec_def
    repeat: eos
types:
  rec_def:
    seq:
      - id: rec_type
        type: u1
      - id: len
        type: u1
      - id: body
        size: len
        type:
          switch-on: rec_type
          cases:
            1: rec_type_1
            2: rec_type_2
  rec_type_1:
    seq:
      - id: field1
        type: u1
  rec_type_2:
    seq:
      - id: field2
        type: u2
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x01\xaa\x02\x02\xcc\xbb')

        parsed = kstruct.parse(content)

        self.assertEqual(len(parsed.record), 2)

        self.assertEqual(parsed.record[0].rec_type.value, 1)
        self.assertEqual(parsed.record[0].len.value, 1)
        self.assertEqual(parsed.record[0].body.field1.value, 0xaa)

        self.assertEqual(parsed.record[1].rec_type.value, 2)
        self.assertEqual(parsed.record[1].len.value, 2)
        self.assertEqual(parsed.record[1].body.field2.value, 0xbbcc)


    def testInstanceWithDataBeyondTheSequence(self):
        """Build instances with data beyond the sequence."""

        # Cf. 4.12. Instances: data beyond the sequence

        definitions = '''
instances:
  some_integer:
    pos: 0x4
    type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04\x05\x06\x07\x08')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.some_integer.value, 5)


        definitions = '''
seq:
  - id: file_offset
    type: u1
  - id: file_size
    type: u1
instances:
  body:
    pos: file_offset
    size: file_size
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x04\x02\x90\x90ABCD')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.file_offset.value, 4)

        self.assertEqual(parsed.file_size.value, 2)

        self.assertEqual(parsed.body.value, b'AB')


    def testValueInstances(self):
        """Build value instances"""

        # Cf. 4.13. Value instances

        definitions = '''
seq:
  - id: length
    type: u1
  - id: extra
    type: u1
instances:
  length_extended:
    value: length * 3 + extra
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.length.value, 1)

        self.assertEqual(parsed.extra.value, 2)

        self.assertEqual(parsed.length_extended.value, 5)


    def testBitSizedIntegers(self):
        """Read bit-sized integers."""

        # Cf. 4.14. Bit-sized integers

        definitions = '''
seq:
  - id: packed_1
    type: u1
instances:
  version:
    value: (packed_1 & 0b11110000) >> 4
  len_header:
    value:  packed_1 & 0b00001111
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x9a')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.packed_1.value, 0x9a)

        self.assertEqual(parsed.version.value, 0x9)

        self.assertEqual(parsed.len_header.value, 0xa)


    def __passed__testBitSizedIntegersBigEndian(self):
        """Read bit-sized integers."""

        # Cf. 4.14.1. Big-endian order

        pass


    def __passed__testBitSizedIntegersLittleEndian(self):
        """Read bit-sized integers."""

        # Cf. 4.14.2. Little-endian order

        pass


    def __passed__testBitSizedIntegersSpecifiedEndianness(self):
        """Read bit-sized integers with specified bit endianness."""

        # Cf. 4.14.3. Specifying bit endianness

        pass



    #################################
    ### 5. Streams and substreams
    #################################


    def testTotalSizeLimit(self):
        """Limit total size of structure."""

        # Cf. 5.1. Limiting total size of structure

        definitions = '''
seq:
  - id: body_len
    type: u1
  - id: random
    size: 2
  - id: comment
    size: body_len - 2
  - id: extra
    type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x05\x01\x02---\xbb')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.body_len.value, 0x05)

        self.assertEqual(parsed.random.raw_bytes, b'\x01\x02')

        self.assertEqual(parsed.comment.raw_bytes, b'---')

        self.assertEqual(parsed.extra.raw_bytes, b'\xbb')


        definitions = '''
seq:
  - id: body_len
    type: u1
  - id: body
    type: record_body
    size: body_len
  - id: extra
    type: u1
types:
  record_body:
    seq:
      - id: random
        size: 2
      - id: comment
        size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x05\x01\x02---\xbb')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.body_len.value, 0x05)

        self.assertEqual(parsed.body.random.raw_bytes, b'\x01\x02')

        self.assertEqual(parsed.body.comment.raw_bytes, b'---')

        self.assertEqual(parsed.extra.raw_bytes, b'\xbb')


    def testRepeatSizeLimit(self):
        """Repeating until total size reaches limit."""

        # Cf. 5.2. Repeating until total size reaches limit

        content = MemoryContent(b'\x03\x00\x01\x02\xbb')

        definitions = '''
seq:
  - id: total_len
    type: u1
  - id: files
    type: file_entries
    size: total_len
  - id: extra
    type: u1
types:
  file_entries:
    seq:
      - id: entries
        type: entry
        repeat: eos
  entry:
    seq:
      - id: index
        type: u1
'''

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.total_len.value, 3)

        self.assertEqual(len(parsed.files.entries), 3)

        for i in range(3):
            self.assertEqual(parsed.files.entries[i].index.value, i)

        self.assertEqual(parsed.extra.value, 0xbb)


    def testRelativePositioning(self):
        """Parse with relative positioning."""

        # Cf. 5.3. Relative positioning

        content = MemoryContent(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\0xe\x0f')

        definitions = '''
seq:
  - id: some_header
    size: 4
  - id: body
    type: block
    size: 12
types:
  block:
    seq:
      - id: foo
        type: u1
    instances:
      some_bytes_in_the_middle:
        pos: 4
        size: 4
'''

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.some_header.value, b'\x00\x01\x02\x03')
        self.assertEqual(parsed.body.foo.value, 0x04)

        self.assertEqual(parsed.body.some_bytes_in_the_middle.value, b'\x08\x09\x0a\x0b')


    def testAbsolutePositioning(self):
        """Read from absolute position."""

        # Cf. 5.4. Absolute positioning

        content = MemoryContent(b'\x06\x03\x00\x00\x00\x00\x01\x02\x03\xbb')

        definitions = '''
seq:
  - id: items
    size: 10
    type: entry
    repeat: eos
types:
  entry:
    seq:
      - id: ofs_body
        type: u1
      - id: len_body
        type: u1
    instances:
      body:
        io: _root._io
        pos: ofs_body
        size: len_body
'''

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.items[0].ofs_body.value, 6)
        self.assertEqual(parsed.items[0].len_body.value, 3)

        self.assertEqual(parsed.items[0].body.value, b'\x01\x02\x03')


    def testSubstreamChoice(self):
        """Choose a substream."""

        # Cf. 5.5. Choosing a substream

        content = MemoryContent(b'\xaa\xaa\xaa\xaa\x01\x02\x03\x04\x05\x06\x07\x08\x02\x03')

        definitions = '''
seq:
  - id: global_header
    size: 4
  - id: block_one
    type: big_container
    size: 8
  - id: block_two
    type: smaller_container
    size: 2
types:
  big_container:
    seq:
      - id: some_header
        size: 8
  smaller_container:
    seq:
      - id: ofs_in_big
        type: u1
      - id: len_in_big
        type: u1
    instances:
      something_in_big:
        io: _root.block_one._io
        pos: ofs_in_big
        size: len_in_big
'''

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.block_two.ofs_in_big.value, 2)
        self.assertEqual(parsed.block_two.len_in_big.value, 3)

        self.assertEqual(parsed.block_two.something_in_big.value, b'\x03\x04\x05')


    def __passed__testContentPreProcessing(self):
        """Process content before parsing."""

        # Cf. 5.6. Processing: dealing with compressed, obfuscated and encrypted data

        pass



    ##############################
    ### 6. Expression language
    ##############################


    def testBasicDataTypes(self):
        """Handle basic data types."""

        # Cf. 6.1. Basic data types

        definitions = '''
seq:
  - id: field1
    type: u1
  - id: field2
    type: u2
  - id: field4
    type: u4
  - id: field8
    type: u8
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x02\x04\x04\x04\x04\x08\x08\x08\x08\x08\x08\x08\x08')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field1.range.length, 1)
        self.assertEqual(parsed.field2.range.length, 2)
        self.assertEqual(parsed.field4.range.length, 4)
        self.assertEqual(parsed.field8.range.length, 8)

        definitions = '''
seq:
  - id: field1
    type: u1
  - id: field4
    type: u4le
  - id: field4bis
    type: u4be
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04\x05\x02\x03\x04\x05')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field1.value, 0x01)
        self.assertEqual(parsed.field4.value, 0x05040302)
        self.assertEqual(parsed.field4bis.value, 0x02030405)


        definitions = '''
instances:
  number1:
    value: 0xdead_cafe
  number2:
    value: 0xdead_cafe_dead_cafe
  number3:
    value: 12_345_678
  number4:
    value: 0b10100011
  number5:
    value: 0b1010_0011_1010_0011
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.number1.value, 0xdeadcafe)

        self.assertEqual(parsed.number2.value, 0xdeadcafedeadcafe)

        self.assertEqual(parsed.number3.value, 12345678)

        self.assertEqual(parsed.number4.value, 0b10100011)

        self.assertEqual(parsed.number5.value, 0b1010001110100011)


        definitions = '''
seq:
  - id: op0
    type: u1
instances:
  result:
    value: 0xdeadcafe + op0
  result2:
    value: 0XdeadCAFE + op0
'''

        content = MemoryContent(b'\x00')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result.value, 0xdeadcafe)

        self.assertEqual(parsed.result2.value, 0xdeadcafe)


        definitions = '''
instances:
  bytes1:
    value: []
  bytes2:
    value: [ ]
  bytes3:
    value: [ 0x90 ]
  bytes4:
    value: [foo, 0, A, 0xa, 42]
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.bytes1.value, b'')

        self.assertEqual(parsed.bytes2.value, b'')

        self.assertEqual(parsed.bytes3.value, b'\x90')

        self.assertEqual(parsed.bytes4.value, b'\x66\x6f\x6f\x00\x41\x0a\x2a')


        definitions = '''
instances:
  escaped:
    value: '[ "\\a\\b\\t\\n\\v\\f", "\\0", 0, " \\r\\e\\\"\\123" ]'
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.escaped.value, b'\x07\x08\x09\x0a\x0b\x0c\x00\x00 \x0d\x1b\x22\x53')


        definitions_0 = r'''
instances:
  escaped:
    value: "[ \"\\a\\b\\t\\n\\v\\f\", \"\\0\", 0, \"\\r\\e\\\"'\\123\" ]"
'''

        definitions_1 = r'''
instances:
  escaped:
    value: [ "\\a\\b\\t\\n\\v\\f", "\\0", 0, "\\r\\e\\\"'\\123" ]
'''

        definitions_2 = '''
instances:
  escaped:
    value: [ "\\\\a\\\\b\\\\t\\\\n\\\\v\\\\f", "\\\\0", 0, "\\\\r\\\\e\\\\\\"'\\\\123" ]
'''

        for d in [ definitions_0, definitions_1, definitions_2 ]:

            content = MemoryContent(b'')

            kstruct = KaitaiStruct(d)

            parsed = kstruct.parse(content)

            self.assertEqual(parsed.escaped.value, b'\x07\x08\x09\x0a\x0b\x0c\x00\x00\x0d\x1b\x22\x27\x53')


    def __passed__testUserDefinedTypes(self):
        """Create user-defined types."""

        # Cf. 6.2.1. User-defined types

        pass


    def testArrays(self):
        """Create various arrays."""

        # Cf. 6.2.2. Arrays

        definitions = '''
instances:
  result_0:
    value: "[]"
  result_1:
    value: "[CAFE, 0, BABE]"
  result_2:
    value: "[CAFE, 0, BABE] == 'CAFE' + [ 0x00 ] + 'BABE'"
  result_3:
    value: "[CAFE, 0, BABE] == [ 0x43, 0x41, 0x46, 0x45, 0x00, 0x42, 0x41, 0x42, 0x45 ]"
  result_4:
    value: "[foo, 0, A, 0xa, 42] == [ 0x66, 0x6f, 0x6f, 0x00, 0x41, 0x0a, 0x2a ]"
  result_5:
    value: "[1, 0x55, '▒,3', 3] == [ 0x01, 0x55, 0xe2, 0x96, 0x92, 0x2c, 0x33, 0x03 ]"
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, b'')

        self.assertEqual(parsed.result_1.value, b'CAFE\x00BABE')


        definitions = '''
seq:
  - id: indexes
    type: u1
    repeat: eos
instances:
  table:
    value: "[ [ 1, 2, 3 ], [ 4, 5, 6 ], [ 7, 8, 9 ] ]"
  ref:
    value: indexes
  result_0:
    value: table
  result_1:
    value: ref
  result_2:
    value: table[indexes[0]][indexes[1] - 1]
  result_3:
    value: table[indexes[0]][ref[1]]
'''

        content = MemoryContent(b'\x01\x02\x03\x04')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value.value, b'\x01\x02\x03\x04\x05\x06\x07\x08\x09')

        self.assertEqual(type(parsed.result_1).__name__, 'RecordValue')            # result_1
        self.assertEqual(type(parsed.result_1.value).__name__, 'RecordValue')      # result_1.ref
        self.assertEqual(type(parsed.result_1.value.value).__name__, 'RecordList') # result_1.ref.table

        self.assertEqual(parsed.result_1.value.value[3].value, 0x04)

        self.assertEqual(parsed.result_2.value, 5)

        self.assertEqual(parsed.result_3.value, 6)


    def testArithmeticOperators(self):
        """Compute with arithmetic operators."""

        # Cf. 6.3.1. Arithmetic operators

        definitions = '''
seq:
  - id: op0
    type: u1
  - id: op1
    type: u1
instances:
  result_0:
    value: op0 + op1 * 3
  result_1:
    value: (2 + op0) * op1
  result_2:
    value: 7 * 2.0
  result_3:
    value: 7 / 2.0
  result_4:
    value: -5 % 3
  result_5:
    value: 4 % 3
  result_6:
    value: 6 - 3 - -4.0
'''

        content = MemoryContent(b'\x02\x03\x04\x05')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, 11)

        self.assertEqual(parsed.result_1.value, 12)

        self.assertEqual(parsed.result_2.value, 14.0)

        self.assertEqual(parsed.result_3.value, 3.5)

        self.assertEqual(parsed.result_4.value, 1)

        self.assertEqual(parsed.result_5.value, 1)

        self.assertEqual(parsed.result_6.value, 7.0)


        definitions = '''
seq:
  - id: base
    size: 3
instances:
  result_0:
    value: "'xXx ' + base + ' -- %< --'"
'''

        content = MemoryContent(b'ABC')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, b'xXx ABC -- %< --')


        definitions = '''
seq:
  - id: nums
    type: u1
    repeat: eos
instances:
  computed:
    value: nums[0] + nums[3]
  computed2:
    value: nums[0] * nums.size + nums[3]
  computed3:
    value: nums[0] * nums[nums.size - 1]
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x03\x04')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.computed.value, 5)

        self.assertEqual(parsed.computed2.value, 8)

        self.assertEqual(parsed.computed3.value, 4)


    def testRelationalOperators(self):
        """Compute with relational operators."""

        # Cf. 6.3.2. Relational operators

        definitions = '''
seq:
  - id: op0
    type: u1
  - id: op1
    type: u1
  - id: op2
    size: 3
instances:
  result0:
    value: op0 == op1
  result1:
    value: op0 != op1
  result2:
    value: op2 == 'ABC'
  result3:
    value: op2 < 'ABCD'
  result4:
    value: (op0 + 1) >= op1
  result5:
    value: "(op0 + 1) == 'ABC'.length"
'''

        content = MemoryContent(b'\x02\x03ABCD')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertFalse(parsed.result0.value)

        self.assertTrue(parsed.result1.value)

        self.assertTrue(parsed.result2.value)

        self.assertTrue(parsed.result3.value)

        self.assertTrue(parsed.result4.value)

        self.assertTrue(parsed.result5.value)


    def testBitwiseOperators(self):
        """Compute with bitwise operators."""

        # Cf. 6.3.3. Bitwise operators

        definitions = '''
seq:
  - id: op0
    type: u1
  - id: op1
    type: u1
  - id: op2
    type: u1
instances:
  result_0:
    value: op0 & op1
  result_1:
    value: op1 << op0 >> 1
  result_2:
    value: (op2 | 0x80) >> 1
'''

        content = MemoryContent(b'\x02\x07\x01')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, 0x2)

        self.assertEqual(parsed.result_1.value, 14)

        self.assertEqual(parsed.result_2.value, 0x40)


    def testLogicalOperators(self):
        """Compute with logical boolean operators."""

        # Cf. 6.3.4. Logical (boolean) operators

        definitions = '''
seq:
  - id: op0
    type: u1
  - id: op1
    type: u1
instances:
  result_0:
    value: (op0 > 0) and not false
  result_1:
    value: op0 == 1 or op1 == 2
'''

        content = MemoryContent(b'\x01\x02')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertTrue(parsed.result_0.value)

        self.assertTrue(parsed.result_1.value)


    def testTernaryOperator(self):
        """Offer challenges to the ternary operator."""

        # Cf. 6.3.5. Ternary (if-then-else) operator

        definitions = '''
seq:
  - id: op0
    type: u1
  - id: op1
    type: u1
  - id: op2
    type: u1
instances:
  result_0:
    value: 'op0 == 0x80 ? op1 + 1 : op1 * op2'
  result_1:
    value: 'op0 < 0x80 ? op1 + 1 : op1 * op2'
  result_1:
    value: 'op0 < 0x80 ? op1 + 1 : op1 * op2'
  result_2:
    value: '(op0 + 0x10) >= 0x90 ? true : 123'
  result_3:
    value: '(op0 + 0x10) >= 0x90 and false ? true : 123'
'''

        content = MemoryContent(b'\x80\x03\x04')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, 4)

        self.assertEqual(parsed.result_1.value, 12)

        self.assertTrue(parsed.result_2.value)

        self.assertEqual(parsed.result_3.value, 123)


    def testIntegersMethods(self):
        """Run methods from integers."""

        # Cf. 6.4.1. Integers

        definitions = '''
instances:
  bytes1:
    value: 123.to_s == "123" and -123.to_s == '-123'
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertTrue(parsed.bytes1.value)


    def testFloatsMethods(self):
        """Run methods from floating numbers."""

        # Cf. 6.4.2. Floating point numbers

        definitions = '''
instances:
  result_0:
    value: 2.32.to_i == 2 and -7.0.to_i == -7
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertTrue(parsed.result_0.value)


    def XXXtestByteArraysAndStringsMethods(self):
        """Run methods from byte arrays and strings."""

        # Cf. 6.4.3. Byte arrays
        #     6.4.4. Strings

        definitions = '''
instances:
  result_1:
    value: '[].length == 0'
  result_2:
    value: "'edcba'.reverse == 'XXabcdeXX'.substring(2, 6)"
  result_3:
    value: "'123'.to_i == 123 and '-123'.to_i == -123"
  result_4:
    value: "[ 0x50, 0x72, 0x65, 0x73, 0x65, 0x6e, 0x74, 0x61, 0x63, 0x69, 0xc3, 0xb3, 0x6e, 0x2e, 0x73, 0x78, 0x69 ].to_s('utf-8')"
  result_5:
    value: "'1010'.to_i(2) == 10 and 'cc'.to_i(16) == 204"
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertTrue(parsed.result_1.value)

        self.assertTrue(parsed.result_2.value)

        self.assertTrue(parsed.result_3.value)

        # Cf. https://docs.gtk.org/glib/character-set.html
        #     https://developer-old.gnome.org/glib/stable/glib-Character-Set-Conversion.html#g-convert
        self.assertEqual(parsed.result_4.value.decode('utf-8'), 'Presentación.sxi')

        self.assertTrue(parsed.result_5.value)


    def __passed__testEnumsMethods(self):
        """Run methods from booleans."""

        # Cf. 6.4.5. Enums

        pass


    def testBooleansMethods(self):
        """Run methods from booleans."""

        # Cf. 6.4.6. Booleans

        definitions = '''
instances:
  result_0:
    value: true.to_i == 1
  result_1:
    value: (1 == 2).to_i == 0
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertTrue(parsed.result_0.value)

        self.assertTrue(parsed.result_1.value)


    def testUserDefinedTypes(self):
        """Retrieve user-defined types."""

        # Cf. 6.4.7. User-defined types

        definitions = '''
instances:
  result_0:
    value: _root
'''

        content = MemoryContent(b'')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.result_0.value, parsed)


    def __passed__testArraysMethods(self):
        """Run methods from arrays."""

        # Cf. 6.4.8. Array types

        pass


    def __passed__testStreamsMethods(self):
        """Run methods from streams."""

        # Cf. 6.4.9. Streams

        pass



    ##############################
    ### 7. Advanced techniques
    ##############################


    def testSwitchOverStrings(self):
        """Switch over strings."""

        # Cf. 7.1.1. Switching over strings

        definitions = '''
seq:
  - id: rec_type
    type: strz
  - id: body
    type:
      switch-on: rec_type
      cases:
        '"KETCHUP"': rec_type_1
        '"MUSTARD"': rec_type_2
        '"GUACAMOLE"': rec_type_3
types:
  rec_type_1:
    instances:
      direct:
        value: 1
  rec_type_2:
    instances:
      direct:
        value: 2
  rec_type_3:
    instances:
      direct:
        value: 3
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'GUACAMOLE\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.rec_type.value, b'GUACAMOLE')

        self.assertEqual(parsed.body.direct.value, 3)


    def testSwitchOverEnums(self):
        """Switch over enumerations."""

        # Cf. 7.1.2. Switching over enums

        definitions = '''
seq:
  - id: rec_type
    type: u1
    enum: media
  - id: body
    type:
      switch-on: rec_type
      cases:
        'media::cdrom': rec_type_1
        'media::dvdrom': rec_type_2
        'media::cassette': rec_type_3
types:
  rec_type_1:
    instances:
      direct:
        value: 1
  rec_type_2:
    instances:
      direct:
        value: 2
  rec_type_3:
    instances:
      direct:
        value: 3
enums:
  media:
    1: cdrom
    2: dvdrom
    3: cassette
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.rec_type.value, 1)

        self.assertEqual(parsed.body.direct.value, 1)


    def testFourCC(self):
        """Recognize four character code."""

        # Cf. 7.1.3. FourCC

        definitions = '''
seq:
  - id: fourcc
    type: u4le
    enum: pixel_formats
  - id: len
    type: u1
  - id: body
    size: len
    type:
      switch-on: fourcc
      cases:
        'pixel_formats::rgb2': block_rgb2
        'pixel_formats::rle4': block_rle4
        'pixel_formats::rle8': block_rle8
types:
  block_rgb2:
    instances:
      direct:
        value: 2
  block_rle4:
    instances:
      direct:
        value: 4
  block_rle8:
    instances:
      direct:
        value: 8
enums:
  pixel_formats:
    0x32424752: rgb2
    0x34454C52: rle4
    0x38454C52: rle8
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'RLE4\x05ABCDE')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.fourcc.value, 0x34454C52)

        self.assertEqual(parsed.len.value, 0x5)

        self.assertEqual(parsed.body.direct.value, 4)


    def testNothing(self):
        """Do nothing."""

        # Cf. 7.2. Do nothing

        definitions = '''
seq:
  - id: field_0
    size: 1
  - id: field_1
    type: dummy_1
  - id: field_2
    type: dummy_2
  - id: field_3
    type: dummy_3
  - id: field_4
    type: dummy_4
  - id: field_5
    size: 1
types:
  # One can use empty JSON object syntax to avoid specifying any of
  # `seq`, `instances`, etc, sections.
  dummy_1: {}
  # One can use explicit doc to note that there's nothing there.
  dummy_2:
    doc: This type is intentionally left blank.
  # One can use empty `seq` or `instances` or `types` section, any
  # other empty sections, or any combination of thereof.
  dummy_3:
    seq: []
    instances: {}
    types: {}
  # One can use a very explicit notion of the fact that we want to parse 0 bytes.
  dummy_4:
    seq:
      - id: no_value
        size: 0
'''

        content = MemoryContent(b'az')

        kstruct = KaitaiStruct(definitions)

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.field_0.value, b'a')

        self.assertEqual(type(parsed.field_1).__name__, 'RecordEmpty')
        self.assertEqual(parsed.field_1.range.length, 0)

        self.assertEqual(type(parsed.field_2).__name__, 'RecordEmpty')
        self.assertEqual(parsed.field_2.range.length, 0)

        self.assertEqual(type(parsed.field_3).__name__, 'RecordEmpty')
        self.assertEqual(parsed.field_3.range.length, 0)

        self.assertEqual(type(parsed.field_4.no_value).__name__, 'RecordEmpty')
        self.assertEqual(parsed.field_4.no_value.range.length, 0)

        self.assertEqual(parsed.field_5.value, b'z')


    def testConsumeIncludeTerminators(self):
        """Consume and/or include terminators."""

        # Cf. 7.3.1. Terminator: consume or include?

        definitions = '''
seq:
  - id: str1
    type: str
    terminator: 0x2e # `.`
  - id: str2
    type: str
    terminator: 0x2e # `.`
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'foo.bar.')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.str1.value, b'foo')

        self.assertEqual(parsed.str2.value, b'bar')


        definitions = '''
seq:
  - id: str1
    type: str
    terminator: 0x2e # `.`
    include: true
  - id: str2
    type: str
    terminator: 0x2e # `.`
    eos-error: false
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'foo.bar')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.str1.value, b'foo.')

        self.assertEqual(parsed.str2.value, b'bar')


        definitions = '''
seq:
  - id: str1
    type: str
    terminator: 0x2e # `.`
    consume: false
  - id: the_rest
    type: str
    size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'foo.bar.')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.str1.value, b'foo')

        self.assertEqual(parsed.the_rest.value, b'.bar.')


        definitions = '''
seq:
  - id: str1
    type: str
    terminator: .
  - id: the_rest
    type: str
    size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'foo.bar.')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.str1.value, b'foo')

        self.assertEqual(parsed.the_rest.value, b'bar.')


        definitions = '''
seq:
  - id: str1
    type: str
    terminator: xxx.
  - id: the_rest
    type: str
    size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'fooxxx.bar.')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.str1.value, b'foo')

        self.assertEqual(parsed.the_rest.value, b'bar.')


    def testIgnoreErrorsInDelimitedStructures(self):
        """Ignore errors in delimited structures."""

        # Cf. 7.3.2. Ignoring errors in delimited structures

        definitions = '''
seq:
  - id: my_string
    type: str
    terminator: 0
    eos-error: false
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x61\x62\x63\x00\x64\x65\x66')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_string.value, b'abc')


        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x61\x62\x63\x00')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_string.value, b'abc')


        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x61\x62\x63')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.my_string.value, b'abc')


    def __passed__testImportTypesFromOtherFiles(self):
        """Import types from other files."""

        # Cf. 7.4. Importing types from other files

        pass


    def __passed__testPlugExternalCodeForOpaqueTypes(self):
        """Plug external code for opaque types."""

        # Cf. 7.5. Opaque types: plugging in external code

        pass


    def __passed__testCustomProcessingRoutines(self):
        """Handle custom processing routines."""

        # Cf. 7.6. Custom processing routines

        pass


    def __passed__testParentTypeEnforcing(self):
        """Enforce parent type."""

        # Cf. 7.7. Enforcing parent type

        pass


    def testTypecasting(self):
        """Ensure there is no need for typecasting."""

        # Cf. 7.8. Typecasting

        definitions = '''
seq:
  - id: num_sections
    type: u1
  - id: sections
    type: section
    repeat: expr
    repeat-expr: num_sections
types:
  section:
    seq:
      - id: sect_type
        type: u1
      - id: body
        type:
          switch-on: sect_type
          cases:
            1: sect_header
            2: sect_color_data
  sect_header:
    seq:
      - id: width
        type: u1
      - id: height
        type: u1
  sect_color_data:
    seq:
      - id: rgb
        size: 3
instances:
  check_0:
    value: sections[0].body.width * sections[0].body.height
  check_1:
    value: sections[1].body.rgb
  check_2:
    value: sections[2].body.width * sections[2].body.height
  check_3:
    value: sections[3].body.rgb
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x04\x01\x02\x04\x02ABC\x01\x03\x05\x02UVW')

        parsed = kstruct.parse(content)

        # Vérifications externes

        self.assertEqual(parsed.num_sections.value, 4)

        self.assertEqual(len(parsed.sections), 4)

        self.assertEqual(parsed.sections[0].body.width.value + parsed.sections[0].body.height.value, 6)

        self.assertEqual(parsed.sections[1].body.rgb.value, b'ABC')

        self.assertEqual(parsed.sections[2].body.width.value + parsed.sections[2].body.height.value, 8)

        self.assertEqual(parsed.sections[3].body.rgb.value, b'UVW')

        # Vérifications internes

        self.assertEqual(parsed.check_0.value, 8)

        self.assertEqual(parsed.check_1.value.value, b'ABC')

        self.assertEqual(parsed.check_2.value, 15)

        self.assertEqual(parsed.check_3.value.value, b'UVW')



    ##########################
    ### 8. Common pitfalls
    ##########################


    def testReadTypeWithSubstream(self):
        """Read user-type with substream."""

        # Cf. 8.1. Specifying size creates a substream

        definitions = '''
seq:
  - id: header
    size: 4
  - id: block
    type: block
    size: 4 # <= important size designation, creates a substream
instances:
  byte_3:
    pos: 3
    type: u1
types:
  block:
    instances:
      byte_3:
        pos: 3
        type: u1
      byte_3_alt:
        io: _root._io # <= thanks to this, always points to a byte in main stream
        pos: 3
        type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x00\x01\x02\x03\x04\x05\x06\x07')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.header.value, b'\x00\x01\x02\x03')

        self.assertEqual(parsed.byte_3.value, 0x03)

        self.assertEqual(parsed.block.byte_3.value, 0x07)

        self.assertEqual(parsed.block.byte_3_alt.value, 0x03)


        definitions = '''
seq:
  - id: header
    size: 4
  - id: block
    type: block
instances:
  byte_3:
    pos: 3
    type: u1
types:
  block:
    instances:
      byte_3:
        pos: 3
        type: u1
      byte_3_alt:
        io: _root._io # <= thanks to this, always points to a byte in main stream
        pos: 3
        type: u1
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x00\x01\x02\x03\x04\x05\x06\x07')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.header.value, b'\x00\x01\x02\x03')

        self.assertEqual(parsed.byte_3.value, 0x03)

        self.assertEqual(parsed.block.byte_3.value, 0x03)

        self.assertEqual(parsed.block.byte_3_alt.value, 0x03)


    def testReadTypeWithoutSubstream(self):
        """Read user-type without substream."""

        # Cf. 8.2. Not specifying size does not create a substream

        definitions = '''
seq:
  - id: header
    size: 2
  - id: block_as_type1
    type: type1
    size: 2 # <= important, creates a substream
types:
  type1:
    seq:
      - id: val1
        size: 2
  type2:
    seq:
      - id: val2
        size: 2
instances:
  block_as_type2:
    io: block_as_type1._io
    pos: 0
    type: type2
  internal_check:
    value: block_as_type2._io == _root._io
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'aabb')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.header.value, b'aa')

        self.assertEqual(parsed.block_as_type1.val1.value, b'bb')

        self.assertEqual(parsed.block_as_type2.val2.value, b'bb')

        self.assertFalse(parsed.internal_check.value)


        definitions = '''
seq:
  - id: header
    size: 2
  - id: block_as_type1
    type: type1
types:
  type1:
    seq:
      - id: val1
        size: 2
  type2:
    seq:
      - id: val2
        size: 2
instances:
  block_as_type2:
    io: block_as_type1._io
    pos: 0
    type: type2
  internal_check:
    value: block_as_type2._io == _root._io
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'aabb')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.header.value, b'aa')

        self.assertEqual(parsed.block_as_type1.val1.value, b'bb')

        self.assertEqual(parsed.block_as_type2.val2.value, b'aa')

        self.assertTrue(parsed.internal_check.value)


    def __passed__testSizedProcess(self):
        """Provide a sized data to processing."""

        # Cf. 8.3. Applying process without a size

        pass


    def __passed__testRelatedKeys(self):
        """Check refering keys and their related YAML nodes."""

        # Cf. 8.4. Keys relating to the whole array and to each element in repeated attributes

        pass



    #######################
    ### x. Extra checks
    #######################


    def testMssingField(self):
        """Raise error on missing field."""

        definitions = '''
seq:
  - id: field0
    size-eos: true
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\x01\x02\x02\x03')

        parsed = kstruct.parse(content)
        self.assertIsNotNone(parsed)

        self.assertEqual(parsed.field0.creator.raw_id, 'field0')

        self.assertEqual(parsed.field0.value, b'\x01\x02\x02\x03')

        # AttributeError: 'pychrysalide.plugins.kaitai.records.RecordList' object has no attribute 'xxxx'
        with self.assertRaisesRegex(AttributeError, "object has no attribute 'xxxx'"):
            print(parsed.xxxx)


    def testLEB128Values(self):
        """Read some Little Endian Base 128 values."""

        definitions = '''
seq:
  - id: groups
    type: group
    repeat: until
    repeat-until: not _.has_next
types:
  group:
    -webide-representation: '{value}'
    doc: |
      One byte group, clearly divided into 7-bit "value" chunk and 1-bit "continuation" flag.
    seq:
      - id: b
        type: u1
    instances:
      has_next:
        value: (b & 0b1000_0000) != 0
        doc: If true, then we have more bytes to read
      value:
        value: b & 0b0111_1111
        doc: The 7-bit (base128) numeric value chunk of this group
instances:
  len:
    value: groups.size
  value:
    value: >-
      groups[0].value
      + (len >= 2 ? (groups[1].value << 7) : 0)
      + (len >= 3 ? (groups[2].value << 14) : 0)
      + (len >= 4 ? (groups[3].value << 21) : 0)
      + (len >= 5 ? (groups[4].value << 28) : 0)
      + (len >= 6 ? (groups[5].value << 35) : 0)
      + (len >= 7 ? (groups[6].value << 42) : 0)
      + (len >= 8 ? (groups[7].value << 49) : 0)
    doc: Resulting unsigned value as normal integer
  sign_bit:
    value: '1 << (7 * len - 1)'
  value_signed:
    value: '(value ^ sign_bit) - sign_bit'
    doc-ref: https://graphics.stanford.edu/~seander/bithacks.html#VariableSignExtend
'''

        kstruct = KaitaiStruct(definitions)

        content = MemoryContent(b'\xe5\x8e\x26')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.len.value, 3)

        self.assertEqual(parsed.value.value, parsed.value_signed.value)

        self.assertEqual(parsed.value.value, 624485)


        content = MemoryContent(b'\xc0\xbb\x78')

        parsed = kstruct.parse(content)

        self.assertEqual(parsed.len.value, 3)

        self.assertNotEqual(parsed.value.value, parsed.value_signed.value)

        self.assertEqual(parsed.value_signed.value, -123456)
