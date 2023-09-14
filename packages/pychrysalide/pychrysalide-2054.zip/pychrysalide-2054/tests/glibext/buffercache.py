
from chrysacase import ChrysalideTestCase
from gi.repository import GObject
from pychrysalide.analysis.contents import MemoryContent
from pychrysalide.glibext import BufferCache
from pychrysalide.glibext import BufferLine
from pychrysalide.glibext import LineGenerator


class CommentBuilder(GObject.Object, LineGenerator):
    def _count_lines(self):
        return 1
    def _get_flags(self, index, repeat):
        return BufferLine.BufferLineFlags.NONE
    def _print(self, line, index, repeat, content):
        line.append_text(0, '# Comment', BufferLine.RenderingTagType.PRINTABLE)


class TestBufferCache(ChrysalideTestCase):
    """TestCase for glibext.BufferCache*"""

    def testCacheConstructor(self):
        """Build all possible kinds of buffer caches."""

        cache = BufferCache()
        self.assertIsNotNone(cache)
        self.assertIsNone(cache.content)

        cache = BufferCache(None)
        self.assertIsNotNone(cache)
        self.assertIsNone(cache.content)

        cnt = MemoryContent(b'\x00' * 8)

        cache = BufferCache(cnt)
        self.assertIsNotNone(cache)
        self.assertIsNotNone(cache.content)


    def testCacheRendering(self):
        """Check a buffer cache simple content."""

        cache = BufferCache()

        cache.append(CommentBuilder(), BufferLine.BufferLineFlags.NONE)

        cache.append(CommentBuilder())

        self.assertEqual(2, cache.lines_count)
