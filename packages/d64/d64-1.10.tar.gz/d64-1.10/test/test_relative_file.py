import unittest

from unittest.mock import patch, Mock

from d64.exceptions import DiskFullError, FileIndexError
from d64.relative_file import RelativeFile
from d64.side_sector import SideSector

from test.mock_block import MockBlock


class TestRelFileRead(unittest.TestCase):

    def setUp(self):
        MockBlock.BLOCK_FILL = b'\x00\x01\x02\x03' * 64
        mock_entry = Mock()
        mock_entry.first_block.return_value = MockBlock()
        mock_entry.record_len = 30
        self.file = RelativeFile(mock_entry, 'r')
        self.file.block.data_size = 254

    def test_read_record(self):
        self.assertEqual(len(self.file.read_record()), 30)

    def tearDown(self):
        MockBlock.BLOCK_FILL = bytes(64) * 4


class TestRelFileWrite(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        mock_image.alloc_first_block.return_value = MockBlock(mock_image)
        mock_image.alloc_next_block.side_effect = lambda x, y: MockBlock(mock_image)
        self.entry = Mock()
        self.entry.size = 0
        self.entry.block = MockBlock(mock_image)
        self.file = RelativeFile(self.entry, 'w')
        self.file.image = mock_image

    def test_write_short(self):
        self.entry.record_len = 27
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.assertEqual(self.file.write(b'abcdefg\r'), 27)
            self.assertEqual(self.file.side_sector.number, 0)
            self.assertEqual(self.file.side_sector.record_len, 27)
            self.assertEqual(len(self.file.side_sector.all_side_sectors()), 1)
            self.assertEqual(len(self.file.side_sector.all_data_blocks()), 1)
        self.assertEqual(self.file.block.data_size, 27)
        self.assertEqual(self.file.block.data[2:29], b'abcdefg\r'+b'\x00'*19)
        self.assertEqual(self.entry.size, 2)

    def test_write_long(self):
        self.entry.record_len = 27
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.assertEqual(self.file.write(b'abcdefg'*5), 27*2)
        self.assertEqual(self.file.block.data_size, 27*2)

    def test_write_multi_ss(self):
        self.entry.record_len = 245
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            for _ in range(0, 125):
                self.file.write(b'abcdefg')
            self.assertEqual(len(self.file.side_sector.all_data_blocks()), 1)
        self.assertEqual(self.entry.size, 123)

    def test_write_first_fail(self):
        self.entry.record_len = 27
        self.file.image.alloc_next_block.side_effect = lambda x, y: None
        with self.assertRaises(DiskFullError):
            p = patch.object(SideSector, '__bases__', (MockBlock,))
            with p:
                p.is_local = True
                self.file.get_first_block()
        self.file.image.free_block.assert_called_once()

    def test_write_new_ss_fail(self):
        mock_ss = Mock()
        mock_ss.number = 5
        mock_ss.all_data_blocks.return_value = (None, ) * 120
        self.file.image.alloc_next_block.side_effect = lambda x, y: MockBlock()
        self.file.block = MockBlock()
        self.file.side_sector = mock_ss
        with self.assertRaises(FileIndexError):
            self.file.get_new_block()
        mock_ss.number = 1
        self.file.image.alloc_next_block.side_effect = lambda x, y: None
        with self.assertRaises(DiskFullError):
            self.file.get_new_block()


if __name__ == '__main__':
    unittest.main()
