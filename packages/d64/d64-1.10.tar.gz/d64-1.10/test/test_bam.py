import unittest

from d64.d64_bam import D64BAM
from d64.d64_image import D64Image
from d64.exceptions import ConsistencyError

from test.mock_block import MockBlock


class TestBAM(unittest.TestCase):

    def setUp(self):
        self.dir_data = b'\x12\x01A\x00\x15\xff\xff\x1f\x15\xff\xff\x1f\x15\xff\xff\x1f\x15\xff\xff\x1f\x15' \
                        b'\xff\xff\x1f\x15\xff\xff\x1f\x15\xff\xff\x1f\x04\x80\x02\n\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0el\xfb\x07\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01' \
                        b'\x00\x02\x00\x12\xff\xff\x03\x12\xff\xff\x03\x12\xff\xff\x03\x12\xff\xff\x03\x11\xff' \
                        b'\xff\x01\x11\xff\xff\x01\x11\xff\xff\x01\x11\xff\xff\x01\x11\xff\xff\x01GAMES TAPE\xa0' \
                        b'\xa0\xa0\xa0\xa0\xa0\xa0\xa0GT\xa02A\xa0\xa0\xa0\xa0\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.image = D64Image(None)
        self.image.bam_block = MockBlock()

    def test_get_entry(self):
        self.image.bam_block.data = self.dir_data
        entry = self.image.bam.get_entry(1)
        self.assertEqual(entry, (21, '111111111111111111111000'))

    def test_is_alloc_true(self):
        self.image.bam_block.data = self.dir_data
        self.assertTrue(self.image.bam.is_allocated(8, 3))

    def test_is_alloc_false(self):
        self.image.bam_block.data = self.dir_data
        self.assertFalse(self.image.bam.is_allocated(8, 7))

    def test_total_free(self):
        self.image.bam_block.data = self.dir_data
        self.assertEqual(self.image.bam.total_free(), 309)

    def test_check(self):
        self.image.bam_block.data = self.dir_data
        self.image.bam.check()

    def test_set_entry(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        track = 1
        self.image.bam.set_entry(track, 15, '110111011100111101011000')
        entry_start = self.image.bam.BAM_OFFSET+(track-1)*self.image.bam.BAM_ENTRY_SIZE
        self.assertEqual(self.image.bam_block.data[entry_start], 15)
        self.assertEqual(self.image.bam_block.data[entry_start+1:entry_start+4], b'\xbb\xf3\x1a')

    def test_set_allocated(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        track = 8
        self.image.bam.set_allocated(track, 7)
        entry = self.image.bam.get_entry(track)
        self.assertEqual(entry, (3, '000000000100000001010000'))

    def test_set_allocated_invalid(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        with self.assertRaises(ValueError):
            self.image.bam.set_allocated(8, 3)

    def test_set_free(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        track = 8
        self.image.bam.set_free(track, 2)
        entry = self.image.bam.get_entry(track)
        self.assertEqual(entry, (5, '001000010100000001010000'))

    def test_set_free_invalid(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        with self.assertRaises(ValueError):
            self.image.bam.set_free(8, 7)

    def test_check_bad(self):
        self.image.bam_block.data = bytearray(self.dir_data)
        self.image.bam.set_entry(1, 14, '110111011100111101011000')
        with self.assertRaises(ConsistencyError):
            self.image.bam.check()


class TestBAMStatic(unittest.TestCase):

    def test_free_from_zero(self):
        free_bits = '001000010100000001010000'
        self.assertEqual(D64BAM.free_from(free_bits, 0), 2)

    def test_free_from_wrap(self):
        free_bits = '001000010100000000000000'
        self.assertEqual(D64BAM.free_from(free_bits, 11), 2)

    def test_free_from_bad(self):
        free_bits = '000000000000000000000000'
        with self.assertRaises(ConsistencyError):
            D64BAM.free_from(free_bits, 0)


if __name__ == '__main__':
    unittest.main()
