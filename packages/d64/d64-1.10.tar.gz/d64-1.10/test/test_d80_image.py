import unittest

from d64.d80_image import D80Image


class TestD80ImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D80Image(None)

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 29)
        self.assertEqual(self.image.max_sectors(30), 29)
        self.assertEqual(self.image.max_sectors(50), 27)
        self.assertEqual(self.image.max_sectors(60), 25)
        self.assertEqual(self.image.max_sectors(65), 23)
        self.assertEqual(self.image.max_sectors(77), 23)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(78)

    def test_block_start(self):
        self.assertEqual(self.image.block_start(1, 0), 0)
        self.assertEqual(self.image.block_start(1, 1), 256)
        self.assertEqual(self.image.block_start(1, 20), 5120)
        self.assertEqual(self.image.block_start(2, 0), 7424)
        self.assertEqual(self.image.block_start(60, 16), 428800)

    def test_block_start_bad(self):
        with self.assertRaises(ValueError):
            self.image.block_start(0, 0)
        with self.assertRaises(ValueError):
            self.image.block_start(52, 31)


if __name__ == '__main__':
    unittest.main()
