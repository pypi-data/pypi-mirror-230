import unittest

from d64.d82_image import D82Image


class TestD82ImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D82Image(None)

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 29)
        self.assertEqual(self.image.max_sectors(50), 27)
        self.assertEqual(self.image.max_sectors(60), 25)
        self.assertEqual(self.image.max_sectors(77), 23)
        self.assertEqual(self.image.max_sectors(134), 25)
        self.assertEqual(self.image.max_sectors(154), 23)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(155)

    def test_block_start(self):
        self.assertEqual(self.image.block_start(1, 0), 0)
        self.assertEqual(self.image.block_start(1, 1), 256)
        self.assertEqual(self.image.block_start(78, 0), 533248)
        self.assertEqual(self.image.block_start(139, 12), 973824)

    def test_block_start_bad(self):
        with self.assertRaises(ValueError):
            self.image.block_start(0, 0)
        with self.assertRaises(ValueError):
            self.image.block_start(123, 31)


if __name__ == '__main__':
    unittest.main()
