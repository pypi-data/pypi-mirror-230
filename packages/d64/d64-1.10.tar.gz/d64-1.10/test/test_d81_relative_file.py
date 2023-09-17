import unittest

from unittest.mock import patch, Mock

from d64.d81_relative_file import D81RelativeFile
from d64.side_sector import SideSector
from d64.super_side_sector import SuperSideSector

from test.mock_block import MockBlock


class TestD81RelFile(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        mock_image.alloc_first_block.return_value = MockBlock(mock_image)
        mock_image.alloc_next_block.side_effect = lambda x, y: MockBlock(mock_image)
        self.entry = Mock()
        self.entry.size = 0
        self.entry.block = MockBlock(mock_image)
        self.file = D81RelativeFile(self.entry, 'w')
        self.file.image = mock_image

    def test_write_short(self):
        self.entry.record_len = 27
        p1 = patch.object(SideSector, '__bases__', (MockBlock,))
        with p1:
            p1.is_local = True
            p2 = patch.object(SuperSideSector, '__bases__', (MockBlock,))
            with p2:
                p2.is_local = True
                self.assertEqual(self.file.write(b'abcdefg\r'), 27)
                self.assertEqual(self.file.side_sector.number, 0)
                self.assertEqual(self.file.side_sector.record_len, 27)
                self.assertEqual(len(self.file.side_sector.all_side_sectors()), 1)
                self.assertEqual(len(self.file.side_sector.all_data_blocks()), 1)
        self.assertEqual(self.file.block.data_size, 27)
        self.assertEqual(self.file.block.data[2:29], b'abcdefg\r'+b'\x00'*19)
        self.assertEqual(self.entry.size, 3)
