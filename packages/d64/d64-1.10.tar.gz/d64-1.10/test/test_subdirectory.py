import unittest

from unittest.mock import Mock

from d64.subdirectory import Subdirectory

from test.mock_bam import MockBAM
from test.mock_block import MockBlock


class TestSubdirectory(unittest.TestCase):

    def test_subdirectory(self):
        mock_image = Mock()
        mock_entry = Mock()
        mock_entry.size = 120
        start_block = MockBlock(mock_image, 10, 0)
        mock_entry.first_block.return_value = start_block
        subdir = Subdirectory(mock_image, mock_entry)
        self.assertEqual(subdir.MIN_TRACK, 10)
        self.assertEqual(subdir.DIR_TRACK, 10)
        self.assertEqual(subdir.MAX_TRACK, 12)

        subdir.bam = MockBAM(((10, (1, 12)),))
        block = subdir.alloc_first_block()
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 11)
        self.assertEqual(block.sector, 0)
