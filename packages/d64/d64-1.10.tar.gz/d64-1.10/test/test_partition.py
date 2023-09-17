import unittest

from unittest.mock import Mock

from d64.partition import Partition

from test.mock_block import MockBlock


class TestCreatePartition(unittest.TestCase):

    def setUp(self):
        self.entry = Mock()
        self.image = Mock()
        self.image.get_free_entry.return_value = self.entry
        self.part = Partition(self.image, name=b'test')

    def test_create(self):
        start_block = MockBlock(self.image, 1, 0)
        self.entry.partition_blocks.return_value = iter([start_block])
        self.part.create(start_block, 1)
        self.assertEqual(self.entry.name, b'test')
        self.image.bam.set_allocated.assert_called_once()

    def test_create_bad_block(self):
        start_block = MockBlock(self.image, 1, 0)

        def part_blocks():
            yield start_block
            raise ValueError("mocked bad sector")

        self.entry.partition_blocks = part_blocks
        with self.assertRaises(ValueError):
            self.part.create(start_block, 2)
        self.image.free_block.assert_called_once()
        self.entry.reset.assert_called_once()
        self.assertIsNone(self.part.entry)

    def test_create_exists(self):
        mock_entry = Mock()
        mock_entry.name.return_value = b'test'
        part = Partition(None, entry=mock_entry)
        with self.assertRaises(FileExistsError):
            part.create(None, None)
