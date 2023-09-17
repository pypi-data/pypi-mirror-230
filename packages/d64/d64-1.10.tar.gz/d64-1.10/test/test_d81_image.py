import unittest

from d64.d81_image import D81Image

from test.mock_block import MockBlock


class TestD81ImageRead(unittest.TestCase):

    def setUp(self):
        self.image = D81Image(None)
        self.image.header_block = MockBlock()

    def test_read_dos_version(self):
        self.image.header_block.data[0x19] = 0x33
        self.assertEqual(self.image.dos_version, ord('3'))

    def test_read_name(self):
        self.image.header_block.data[4:0x14] = b'GAMES TAPE\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0'
        self.assertEqual(self.image.name, b'GAMES TAPE')

    def test_read_id(self):
        self.image.header_block.data[0x16:0x18] = b'GT'
        self.assertEqual(self.image.id, b'GT')

    def test_dos_type(self):
        self.image.header_block.data[2] = 0x44
        self.assertEqual(self.image.dos_type, ord('D'))


class TestD81ImageWrite(unittest.TestCase):

    def setUp(self):
        self.image = D81Image(None)
        self.image.header_block = MockBlock()
        self.image.side_a_bam_block = MockBlock()
        self.image.side_b_bam_block = MockBlock()

    def test_write_dos_version(self):
        self.image.dos_version = 0x64
        self.assertEqual(self.image.dos_version, 0x64)

    def test_write_name(self):
        self.image.name = b'EXAMPLE'
        self.assertEqual(self.image.name, b'EXAMPLE')
        self.image.name = b'SHORT'
        self.assertEqual(self.image.header_block.data[4:10], b'SHORT\xa0')
        self.image.name = b'VERY LONG EXAMPLE'
        self.assertEqual(self.image.name, b'VERY LONG EXAMPL')
        self.assertNotEqual(self.image.header_block.data[20], 0x45)

    def test_write_id(self):
        self.image.id = b'EX'
        self.assertEqual(self.image.id, b'EX')
        self.assertEqual(self.image.header_block.data[0x16:0x18], b'EX')
        self.assertEqual(self.image.side_a_bam_block.id, b'EX')
        self.assertEqual(self.image.side_b_bam_block.id, b'EX')
        with self.assertRaises(ValueError):
            self.image.id = b'LONG'

    def test_write_dos_type(self):
        self.image.dos_type = 0x77
        self.assertEqual(self.image.dos_type, 0x77)
        self.assertEqual(self.image.header_block.data[2], 0x77)
        self.assertEqual(self.image.header_block.data[0x1a], 0x77)
        self.assertEqual(self.image.side_a_bam_block.dos_type, 0x77)
        self.assertEqual(self.image.side_b_bam_block.dos_type, 0x77)


class TestD81ImageBlocks(unittest.TestCase):

    def setUp(self):
        self.image = D81Image(None)
        self.image.header_block = MockBlock()

    def test_max_sectors(self):
        self.assertEqual(self.image.max_sectors(1), 40)
        self.assertEqual(self.image.max_sectors(5), 40)
        self.assertEqual(self.image.max_sectors(20), 40)
        self.assertEqual(self.image.max_sectors(70), 40)
        self.assertEqual(self.image.max_sectors(80), 40)

    def test_max_sectors_bad(self):
        with self.assertRaises(ValueError):
            self.image.max_sectors(0)
        with self.assertRaises(ValueError):
            self.image.max_sectors(91)

    def test_block_start(self):
        self.assertEqual(self.image.block_start(1, 0), 0)
        self.assertEqual(self.image.block_start(1, 1), 256)
        self.assertEqual(self.image.block_start(1, 20), 5120)
        self.assertEqual(self.image.block_start(2, 0), 10240)
        self.assertEqual(self.image.block_start(45, 27), 457472)

    def test_block_start_bad(self):
        with self.assertRaises(ValueError):
            self.image.block_start(0, 0)
        with self.assertRaises(ValueError):
            self.image.block_start(36, 47)


if __name__ == '__main__':
    unittest.main()
