import unittest

from unittest.mock import Mock

from d64.block import Block


class TestBlock(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.block_start.return_value = 0
        self.image.map = bytes(Block.SECTOR_SIZE)

    def test_track_sector(self):
        block = Block(self.image, 10, 20)
        self.assertEqual(block.track, 10)
        self.assertEqual(block.sector, 20)

    def test_is_final(self):
        block = Block(self.image, None, None)
        self.image.map = b'\x00'
        self.assertTrue(block.is_final)
        self.image.map = b'\x12'
        self.assertFalse(block.is_final)

    def test_data_size(self):
        block = Block(self.image, None, None)
        self.image.map = b'\x00\xff'
        self.assertEqual(block.data_size, 254)
        self.image.map = bytearray(2)
        block.data_size = 42
        self.assertEqual(self.image.map[0], 0)
        self.assertEqual(self.image.map[1], 43)
        with self.assertRaises(ValueError):
            block.data_size = 400

    def test_next_block(self):
        block = Block(self.image, None, None)
        self.image.map = b'\x1a\x17'
        next_block = block.next_block()
        self.assertEqual(next_block.track, 26)
        self.assertEqual(next_block.sector, 23)
        self.image.map = bytearray(2)
        block2 = Block(self.image, 9, 14)
        block.set_next_block(block2)
        self.assertEqual(self.image.map[0], 9)
        self.assertEqual(self.image.map[1], 14)

    def test_data_access(self):
        block = Block(self.image, None, None)
        self.image.map = b'\x00\x10\x11\x12\x13\x14\x15'
        self.assertEqual(block.get(2, 6), b'\x11\x12\x13\x14')

    def test_equal(self):
        blocks = [Block(self.image, 3, 4), Block(self.image, 5, 6)]
        self.assertIn(Block(self.image, 5, 6), blocks)
        self.assertNotIn(Block(self.image, 7, 8), blocks)


if __name__ == '__main__':
    unittest.main()
