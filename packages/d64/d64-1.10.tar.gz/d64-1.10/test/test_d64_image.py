import unittest

from d64.d64_image import D64Image, D64_40TrackImage

from test.mock_block import MockBlock


class TestD64ImageRead(unittest.TestCase):

    def setUp(self):
        self.image = D64Image(None)
        self.image.bam_block = MockBlock()

    def test_read_dos_version(self):
        self.image.bam_block.data[0xa5] = 0x32
        self.assertEqual(self.image.dos_version, ord('2'))

    def test_read_name(self):
        self.image.bam_block.data[0x90:0xa0] = b'GAMES TAPE\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0'
        self.assertEqual(self.image.name, b'GAMES TAPE')

    def test_read_id(self):
        self.image.bam_block.data[0xa2:0xa4] = b'GT'
        self.assertEqual(self.image.id, b'GT')

    def test_dos_type(self):
        self.image.bam_block.data[2] = 0x41
        self.assertEqual(self.image.dos_type, ord('A'))


class TestD64ImageWrite(unittest.TestCase):

    def setUp(self):
        self.image = D64Image(None)
        self.image.bam_block = MockBlock()

    def test_write_dos_version(self):
        self.image.dos_version = 0x64
        self.assertEqual(self.image.dos_version, 0x64)

    def test_write_name(self):
        self.image.name = b'EXAMPLE'
        self.assertEqual(self.image.name, b'EXAMPLE')
        self.image.name = b'SHORT'
        self.assertEqual(self.image.bam_block.data[0x90:0x96], b'SHORT\xa0')
        self.image.name = b'VERY LONG EXAMPLE'
        self.assertEqual(self.image.name, b'VERY LONG EXAMPL')
        self.assertNotEqual(self.image.bam_block.data[0xa0], 0x45)

    def test_write_id(self):
        self.image.id = b'EX'
        self.assertEqual(self.image.id, b'EX')
        with self.assertRaises(ValueError):
            self.image.id = b'LONG'

    def test_write_dos_type(self):
        self.image.dos_type = 0x77
        self.assertEqual(self.image.dos_type, 0x77)
        self.assertEqual(self.image.bam_block.data[2], 0x77)
        self.assertEqual(self.image.bam_block.data[0xa6], 0x77)


class TestD64ImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D64Image(None)
        self.image.bam_block = MockBlock()

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 21)
        self.assertEqual(self.image.max_sectors(5), 21)
        self.assertEqual(self.image.max_sectors(10), 21)
        self.assertEqual(self.image.max_sectors(15), 21)
        self.assertEqual(self.image.max_sectors(20), 19)
        self.assertEqual(self.image.max_sectors(25), 18)
        self.assertEqual(self.image.max_sectors(30), 18)
        self.assertEqual(self.image.max_sectors(35), 17)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(36)

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
            self.image.block_start(1, 21)


class TestD64_40TrackImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D64_40TrackImage(None)
        self.image.bam_block = MockBlock()

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 21)
        self.assertEqual(self.image.max_sectors(35), 17)
        self.assertEqual(self.image.max_sectors(36), 17)
        self.assertEqual(self.image.max_sectors(39), 17)
        self.assertEqual(self.image.max_sectors(40), 17)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(41)

    def test_block_start(self):
        self.assertEqual(self.image.block_start(1, 0), 0)
        self.assertEqual(self.image.block_start(35, 16), 174592)
        self.assertEqual(self.image.block_start(36, 1), 175104)
        self.assertEqual(self.image.block_start(40, 16), 196352)


if __name__ == '__main__':
    unittest.main()
