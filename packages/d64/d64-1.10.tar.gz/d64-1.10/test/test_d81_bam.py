import unittest
from unittest.mock import Mock

from d64.d81_bam import D81BAM

from test.mock_block import MockBlock


class TestBAM(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.MIN_TRACK = 1
        self.image.MAX_TRACK = 80
        self.image.side_a_bam_block = MockBlock()
        self.image.side_b_bam_block = MockBlock()
        self.image.bam = D81BAM(self.image)

    def test_get_entry(self):
        self.image.side_a_bam_block.data[0x1c:0x22] = b'\x17\xc9\x6e\x5b\x6f\x85'
        entry = self.image.bam.get_entry(3)
        self.assertEqual(entry, (23, '1001001101110110110110101111011010100001'))
        self.image.side_b_bam_block.data[0x34:0x3a] = b'\x17\xc9\x6e\x5b\x6f\x85'
        entry = self.image.bam.get_entry(47)
        self.assertEqual(entry, (23, '1001001101110110110110101111011010100001'))

    def test_set_entry(self):
        self.image.bam.set_entry(3, 26, '1101101101110001101010111011101010110111')
        self.assertEqual(self.image.side_a_bam_block.data[0x1c:0x22], b'\x1a\xdb\x8e\xd5]\xed')
        self.image.bam.set_entry(47, 26, '1101101101110001101010111011101010110111')
        self.assertEqual(self.image.side_b_bam_block.data[0x34:0x3a], b'\x1a\xdb\x8e\xd5]\xed')


if __name__ == '__main__':
    unittest.main()
