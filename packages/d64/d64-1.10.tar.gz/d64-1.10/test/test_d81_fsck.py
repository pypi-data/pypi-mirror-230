import unittest

from contextlib import suppress
from pathlib import Path

import d64.scripts.d64_fsck

from d64.d81_image import D81Image

import binary


class TestD81_fsck(unittest.TestCase):

    def setUp(self):
        self.base_path = Path(__file__).parent / 'data' / 'test.d81'
        self.test_path = Path('/tmp/test_bad.d81')
        self.base_bin = binary.load_binary(self.base_path)
        d64.scripts.d64_fsck.QUIET = True
        d64.scripts.d64_fsck.FIX = True
        d64.scripts.d64_fsck.YES = True

    def tearDown(self):
        with suppress(FileNotFoundError):
            self.test_path.unlink()

    def test_clean(self):
        d64.scripts.d64_fsck.FIX = False
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.base_path), 0)

    def test_bad_dir_link(self):
        patch = [{'at': 399361, 'from': b'\x03', 'to': b'\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D81Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.header_block.next_block().sector, 3)
        finally:
            image.close()

    def test_bad_bam_size(self):
        patch = [{'at': 399873, 'from': b'\xff', 'to': b'\x88'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D81Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.side_b_bam_block.data_size, 0xfe)
        finally:
            image.close()

    def test_bam_40_02_not_alloc(self):
        patch = [{'at': 399866, 'from': b'$\xf0', 'to': b'%\xf4'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D81Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(40), (36, '0000111111111111111111111111111111111111'))
        finally:
            image.close()

    def test_partition_not_alloc(self):
        patch = [{'at': 399632, 'from': b'(\xff\xff\xff\xff\xff'*29, 'to': b'\x00'*168+b'\x01\x04\x00\x00\x00\x00'},
                 {'at': 400130, 'from': b'\x00\x00', 'to': b'\x85\x01'},
                 {'at': 400133, 'from': b'\x00'*16, 'to': b'PARTITION\xa0\xa0\xa0\xa0\xa0\xa0\xa0'},
                 {'at': 400158, 'from': b'\x00\x00', 'to': b'\x88\x04'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D81Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(29), (0, '0000000000000000000000000000000000000000'))
        finally:
            image.close()


if __name__ == '__main__':
    unittest.main()
