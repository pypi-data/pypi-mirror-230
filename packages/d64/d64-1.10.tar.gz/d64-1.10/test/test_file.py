import unittest

from unittest.mock import Mock

from d64.exceptions import DiskFullError
from d64.file import File

from test.mock_block import MockBlock


class TestFileRead(unittest.TestCase):

    def setUp(self):
        MockBlock.BLOCK_FILL = b'\x00\x01\x02\x03' * 64
        mock_entry = Mock()
        mock_entry.first_block.return_value = MockBlock()
        self.file = File(mock_entry, 'r')
        self.file.block.data_size = 254

    def test_read_small(self):
        data = self.file.read(10)
        self.assertEqual(len(data), 10)
        self.assertEqual(data, b'\x02\x03\x00\x01\x02\x03\x00\x01\x02\x03')
        data = self.file.read(4)
        self.assertEqual(len(data), 4)
        self.assertEqual(data, b'\x00\x01\x02\x03')

    def test_read_past_end(self):
        self.file.block.data_size = 10
        data = self.file.read(20)
        self.assertEqual(len(data), 10)
        self.assertEqual(data, b'\x02\x03\x00\x01\x02\x03\x00\x01\x02\x03')
        data = self.file.read(20)
        self.assertEqual(len(data), 0)

    def test_read_multi_block(self):
        block2 = MockBlock()
        block2._set_data(b'\x10\x11\x12\x13' * 64)
        self.file.block.set_next_block(block2)
        data = self.file.read(303)
        self.assertEqual(len(data), 303)
        expected = b'\x02\x03'+b'\x00\x01\x02\x03'*63+b'\x12\x13'+b'\x10\x11\x12\x13'*11+b'\x10\x11\x12'
        self.assertEqual(data, expected)

    def test_read_boundary(self):
        block2 = MockBlock()
        block2._set_data(b'\x10\x11\x12\x13' * 64)
        self.file.block._set_data(b'\x00\x01\x02\x03' * 64)
        self.file.block.set_next_block(block2)
        data = self.file.read(254)
        self.assertEqual(len(data), 254)
        expected = b'\x02\x03'+b'\x00\x01\x02\x03'*63
        self.assertEqual(data, expected)
        data = self.file.read(49)
        self.assertEqual(len(data), 49)
        expected = b'\x12\x13'+b'\x10\x11\x12\x13'*11+b'\x10\x11\x12'
        self.assertEqual(data, expected)

    def test_read_seek(self):
        _ = self.file.read(9)
        self.file.seek(2)
        data = self.file.read(4)
        self.assertEqual(data, b'\x00\x01\x02\x03')

    def tearDown(self):
        MockBlock.BLOCK_FILL = bytes(64) * 4


class TestFileWrite(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        mock_image.alloc_first_block.return_value = MockBlock(mock_image)
        mock_image.alloc_next_block.return_value = MockBlock(mock_image)
        self.entry = Mock()
        self.entry.size = 0
        self.entry.block = MockBlock(mock_image)
        self.file = File(self.entry, 'w')

    def test_write_small(self):
        self.assertEqual(self.file.write(b'abcdefg\r'), 8)
        self.assertEqual(self.file.block.data[2:10], b'abcdefg\r')
        self.assertEqual(self.file.write(b'tuvwxyz\r'), 8)
        self.assertEqual(self.file.block.data[2:18], b'abcdefg\rtuvwxyz\r')

    def test_write_multi_block(self):
        self.assertEqual(self.file.write(b'\x00\x01\x02\x03' * 70), 280)
        block1 = self.entry.set_first_block.call_args_list[0][0][0]
        self.assertEqual(block1.data[2:], b'\x00\x01\x02\x03'*63+b'\x00\x01')
        block2 = block1.next_block()
        self.assertIsNotNone(block2)
        self.assertEqual(block2.data[2:28], b'\x02\x03'+b'\x00\x01\x02\x03'*6)
        self.assertEqual(self.file.entry.size, 2)

    def test_write_multi_full(self):
        self.file.image.alloc_next_block.return_value = None
        with self.assertRaises(DiskFullError):
            self.file.write(b'\x00\x01\x02\x03' * 70)

    def test_write_empty(self):
        self.file.__exit__(None, None, None)
        self.assertEqual(self.file.block.data_size, 1)
        self.assertEqual(self.file.block.data[2], 0x0d)


if __name__ == '__main__':
    unittest.main()
