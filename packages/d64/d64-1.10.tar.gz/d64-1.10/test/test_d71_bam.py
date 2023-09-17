import unittest
from unittest.mock import Mock

from d64.d71_bam import D71BAM

from test.mock_block import MockBlock


class TestBAM(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.MIN_TRACK = 1
        self.image.MAX_TRACK = 70
        self.image.bam_block = MockBlock()
        self.image.extra_bam_block = MockBlock()
        self.image.bam = D71BAM(self.image)

    def test_get_entry(self):
        self.image.bam_block.data[12:16] = b'\x0d\xc9\x6e\x1b'
        entry = self.image.bam.get_entry(3)
        self.assertEqual(entry, (13, '100100110111011011011000'))
        self.image.bam_block.data[0xe8] = 0x0d
        self.image.extra_bam_block.data[33:36] = b'\xc9\x6e\x1b'
        entry = self.image.bam.get_entry(47)
        self.assertEqual(entry, (13, '100100110111011011011000'))

    def test_set_entry(self):
        self.image.bam.set_entry(3, 15, '110111011100111101011000')
        self.assertEqual(self.image.bam_block.data[12:16], b'\x0f\xbb\xf3\x1a')
        self.image.bam.set_entry(47, 15, '110111011100111101011000')
        self.assertEqual(self.image.bam_block.data[0xe8], 0x0f)
        self.assertEqual(self.image.extra_bam_block.data[33:36], b'\xbb\xf3\x1a')


if __name__ == '__main__':
    unittest.main()
