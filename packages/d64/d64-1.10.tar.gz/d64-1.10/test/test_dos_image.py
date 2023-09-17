import unittest

from unittest.mock import patch, Mock

from d64.dos_image import DOSImage

from test.mock_bam import MockBAM
from test.mock_block import MockBlock


class TestDOSImageAlloc(unittest.TestCase):

    def setUp(self):
        self.image = DOSImage(None)
        self.image.DIR_TRACK = 18
        self.image.DIR_SECTOR = 1
        self.image.MAX_TRACK = 35
        self.image.TRACK_SECTOR_MAX = ((21, (1, 35)), )
        self.image.bam = MockBAM(self.image.TRACK_SECTOR_MAX)

    def test_alloc_first_below(self):
        self.image.bam.fill_entry(17)
        block = self.image.alloc_first_block()
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 0)
        block = self.image.alloc_first_block()
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 1)

    def test_alloc_first_above(self):
        self.image.bam.clear_entry(17)
        self.image.bam.fill_entry(19)
        block = self.image.alloc_first_block()
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 19)
        self.assertEqual(block.sector, 0)
        block = self.image.alloc_first_block()
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 19)
        self.assertEqual(block.sector, 1)

    def test_alloc_first_full(self):
        for t in range(1, 36):
            self.image.bam.clear_entry(t)
        self.image.bam.fill_entry(18)
        self.assertIsNone(self.image.alloc_first_block())

    def test_alloc_next_interleave(self):
        self.image.bam.fill_entry(17)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 10)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 11)
        block = self.image._alloc_next_block(17, 16, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 4)
        block = self.image._alloc_next_block(17, 11, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 17)
        self.assertEqual(block.sector, 0)

    def test_alloc_diff_track(self):
        self.image.bam.clear_entry(17)
        self.image.bam.fill_entry(16)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 16)
        self.assertEqual(block.sector, 10)

    def test_alloc_above(self):
        for t in range(1, 18):
            self.image.bam.clear_entry(t)
        self.image.bam.fill_entry(19)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 19)
        self.assertEqual(block.sector, 10)

    def test_alloc_dir(self):
        for t in range(1, 36):
            self.image.bam.clear_entry(t)
        self.image.bam.fill_entry(18)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNotNone(block)
        self.assertEqual(block.track, 18)
        self.assertEqual(block.sector, 10)

    def test_alloc_full(self):
        for t in range(1, 36):
            self.image.bam.clear_entry(t)
        block = self.image._alloc_next_block(17, 0, 10)
        self.assertIsNone(block)


class MockImage(DOSImage):
    DIR_TRACK = 18
    DIR_SECTOR = 1
    DIR_INTERLEAVE = 3

    def __init__(self, filename):
        super().__init__(filename)
        self._alloc_first_block_return = []
        self._alloc_next_block_return = []
        self.bam = Mock()
        self._free_called_for = []

    def alloc_first_block(self):
        if self._alloc_first_block_return:
            return self._alloc_first_block_return.pop(0)
        return None

    def alloc_next_block(self, _, __, directory=False):
        if self._alloc_next_block_return:
            return self._alloc_next_block_return.pop(0)
        return None

    def free_block(self, block):
        self._free_called_for.append(block)


class TestDirEntry(unittest.TestCase):
    def setUp(self):
        self.free_dir_entry = bytes(64)
        self.in_use_dir_entry = b'\x00\xff\x82\x0A\x14\x46\x49\x47\x48\x54\x45\x52\x20\x52\x41\x49' \
                                b'\x44\xA0\xA0\xA0\xA0\x00\x00\x00\x00\x00\x00\x00\x00\x00\xE7\x01'

    def test_deleted_entry_exists(self):
        image = MockImage(None)
        MockBlock.BLOCK_FILL = self.free_dir_entry * 8
        with patch('d64.dos_image.Block', new=MockBlock):
            entry = image.get_free_entry()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.block.track, 18)
        self.assertEqual(entry.block.sector, 1)

    def test_from_new_block(self):
        image = MockImage(None)
        MockBlock.BLOCK_FILL = self.in_use_dir_entry * 8
        image._alloc_next_block_return = [MockBlock(image, 18, 4)]
        with patch('d64.dos_image.Block', new=MockBlock):
            entry = image.get_free_entry()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.block.track, 18)
        self.assertEqual(entry.block.sector, 4)

    def test_no_free_next(self):
        image = MockImage(None)
        MockBlock.BLOCK_FILL = self.in_use_dir_entry * 8
        image._alloc_next_block_return = []
        with patch('d64.dos_image.Block', new=MockBlock):
            entry = image.get_free_entry()
        self.assertIsNone(entry)

    def tearDown(self):
        MockBlock.BLOCK_FILL = bytes(64) * 4


class TestChains(unittest.TestCase):

    def test_clone_chain(self):
        image = MockImage(None)
        image._alloc_next_block_return = [MockBlock(image, 20, 2), MockBlock(image, 20, 7), MockBlock(image, 20, 11)]
        MockBlock.BLOCK_FILL = b'\x99\x88\x77\x66\x55\x44\x33\x22' * 64
        block1 = MockBlock()
        block2 = MockBlock()
        block3 = MockBlock()
        block3.data_size = 176
        block2.set_next_block(block3)
        block1.set_next_block(block2)
        new_block1 = image.clone_chain(block1)
        self.assertIsNotNone(new_block1)
        self.assertEqual(new_block1.sector, 2)
        self.assertIsNotNone(new_block1.next_block())
        self.assertEqual(new_block1.next_block().sector, 7)
        self.assertIsNotNone(new_block1.next_block().next_block())
        self.assertEqual(new_block1.next_block().next_block().sector, 11)
        self.assertTrue(new_block1.next_block().next_block().is_final)

    def tearDown(self):
        MockBlock.BLOCK_FILL = bytes(64) * 4


class TestValidImage(unittest.TestCase):

    def test_valid_image(self):
        class TestImage(DOSImage):
            IMAGE_SIZES = (1234, )

        mock_stat = Mock()
        mock_stat.st_size = 1234
        mock_path = Mock()
        mock_path.stat.return_value = mock_stat
        self.assertTrue(TestImage.valid_image(mock_path))
        mock_stat.st_size = 4321
        self.assertFalse(TestImage.valid_image(mock_path))


if __name__ == '__main__':
    unittest.main()
