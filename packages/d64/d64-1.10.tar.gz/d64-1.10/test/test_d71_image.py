import unittest

from d64.d71_image import D71Image


class TestD71ImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D71Image(None)

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 21)
        self.assertEqual(self.image.max_sectors(5), 21)
        self.assertEqual(self.image.max_sectors(20), 19)
        self.assertEqual(self.image.max_sectors(30), 18)
        self.assertEqual(self.image.max_sectors(50), 21)
        self.assertEqual(self.image.max_sectors(55), 19)
        self.assertEqual(self.image.max_sectors(65), 18)
        self.assertEqual(self.image.max_sectors(70), 17)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(71)

    def test_block_start(self):
        self.assertEqual(self.image.block_start(1, 0), 0)
        self.assertEqual(self.image.block_start(1, 1), 256)
        self.assertEqual(self.image.block_start(1, 20), 5120)
        self.assertEqual(self.image.block_start(2, 0), 5376)
        self.assertEqual(self.image.block_start(35, 16), 174592)

    def test_block_start_bad(self):
        with self.assertRaises(ValueError):
            self.image.block_start(0, 0)
        with self.assertRaises(ValueError):
            self.image.block_start(36, 21)


if __name__ == '__main__':
    unittest.main()
