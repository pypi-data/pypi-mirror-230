import unittest

from unittest.mock import patch, Mock

from d64.d81_bam_block import D81BAMBlock

from test.mock_block import MockBlock


class TestD81BAMBlock(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        p = patch.object(D81BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block = D81BAMBlock(mock_image, None, None)

    def test_dos_type(self):
        p = patch.object(D81BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(2, 77)
            self.assertEqual(self.bam_block.dos_type, 77)
            self.bam_block.dos_type = ord('D')
            self.assertEqual(self.bam_block.dos_type, ord('D'))

    def test_verify(self):
        p = patch.object(D81BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(6, 0x80)
            self.assertTrue(self.bam_block.verify)
            self.bam_block.set(6, 0x20)
            self.assertFalse(self.bam_block.verify)
            self.bam_block.verify = True
            self.assertEqual(self.bam_block.get(6), 0xa0)

    def test_header_crc(self):
        p = patch.object(D81BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(6, 0x40)
            self.assertTrue(self.bam_block.check_header_crc)
            self.bam_block.set(6, 0x20)
            self.assertFalse(self.bam_block.check_header_crc)
            self.bam_block.check_header_crc = True
            self.assertEqual(self.bam_block.get(6), 0x60)

    def test_auto_start(self):
        p = patch.object(D81BAMBlock, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.bam_block.set(7, 0x40)
            self.assertTrue(self.bam_block.auto_start)
            self.bam_block.set(7, 0)
            self.assertFalse(self.bam_block.auto_start)
            self.bam_block.auto_start = True
            self.assertEqual(self.bam_block.get(7), 0xff)
