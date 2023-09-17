import unittest
from unittest.mock import Mock

from d64.d81_dir_entry import D81DirEntry

from test.mock_block import MockBlock


class TestDirEntryRead(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        mock_image.block_start.return_value = 0
        self.block = MockBlock(mock_image)
        self.block.data = bytearray(32)

    def test_read_file_type_d81(self):
        entry = D81DirEntry(self.block, 0)
        self.block.data[2] = 0x85
        self.assertEqual(entry.file_type, 'CBM')


class TestDirEntryFree(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.max_sectors.return_value = 30
        self.block = MockBlock(self.image)
        self.block.data = bytearray(32)
        self.entry = D81DirEntry(self.block, 0)
        self.entry.file_type = 'CBM'

    def test_free_blocks(self):
        freed = []

        def _free_block(b):
            freed.append((b.track, b.sector))

        self.image.free_block = _free_block
        self.entry.start_ts = (21, 29)
        self.entry.size = 2
        self.entry.free_blocks()
        self.assertIn((21, 29), freed)
        self.assertIn((22, 0), freed)
