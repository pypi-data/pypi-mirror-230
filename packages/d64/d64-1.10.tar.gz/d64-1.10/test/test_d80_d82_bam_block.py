import unittest

from unittest.mock import patch, Mock

from d64.d80_d82_bam_block import D80D82BAMBlock

from test.mock_block import MockBlock


class TestD80D82BAMBlock(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        p = patch.object(D80D82BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block = D80D82BAMBlock(mock_image, None, None)

    def test_dos_type(self):
        p = patch.object(D80D82BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(2, 77)
            self.assertEqual(self.bam_block.dos_type, 77)
            self.bam_block.dos_type = ord('C')
            self.assertEqual(self.bam_block.dos_type, ord('C'))

    def test_track_range(self):
        p = patch.object(D80D82BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(4, b'\x10\x20')
            self.assertEqual(self.bam_block.track_range, (16, 31))
            self.bam_block.track_range = (21, 26)
            self.assertEqual(self.bam_block.get(4, 6), b'\x15\x1b')
