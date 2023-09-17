import unittest
from unittest.mock import Mock

from d64.d80_d82_bam import D80D82BAM

from test.mock_block import MockBlock


class TestD80BAM(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.MIN_TRACK = 1
        self.image.MAX_TRACK = 77
        bam1 = MockBlock()
        bam1.track_range = (1, 51)
        bam2 = MockBlock()
        bam2.track_range = (51, 78)
        self.image.bam_blocks = [bam1, bam2]
        self.image.bam = D80D82BAM(self.image)

    def test_get_entry(self):
        self.image.bam_blocks[0].data[0x10:0x15] = b'\x12\xc9\xa7\x6e\x1b'
        entry = self.image.bam.get_entry(3)
        self.assertEqual(entry, (18, '10010011111001010111011011011000'))
        self.image.bam_blocks[1].data[0x10:0x15] = b'\x0f\x95\x7c\x30\x3a'
        entry = self.image.bam.get_entry(53)
        self.assertEqual(entry, (15, '10101001001111100000110001011100'))

    def test_set_entry(self):
        self.image.bam.set_entry(3, 15, '10101001001111100000110001011100')
        self.assertEqual(self.image.bam_blocks[0].data[0x10:0x15], b'\x0f\x95\x7c\x30\x3a')
        self.image.bam.set_entry(53, 18, '10010011111001010111011011011000')
        self.assertEqual(self.image.bam_blocks[1].data[0x10:0x15], b'\x12\xc9\xa7\x6e\x1b')


if __name__ == '__main__':
    unittest.main()
