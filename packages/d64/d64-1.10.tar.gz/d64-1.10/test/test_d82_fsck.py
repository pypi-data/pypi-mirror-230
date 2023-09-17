import unittest

from contextlib import suppress
from pathlib import Path

import d64.scripts.d64_fsck

from d64.d82_image import D82Image

import binary


class TestD82_fsck(unittest.TestCase):

    def setUp(self):
        self.base_path = Path(__file__).parent / 'data' / 'test.d82'
        self.test_path = Path('/tmp/test_bad.d82')
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

    def test_bam_38_03_bad_link(self):
        patch = [{'at': 275457, 'from': b'\x06', 'to': b'\x11'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D82Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam_blocks[1].next_block().sector, 6)
        finally:
            image.close()

    def test_bam_38_03_bad_range(self):
        patch = [{'at': 275461, 'from': b'e', 'to': b'T'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D82Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam_blocks[1].track_range, (51, 100))
        finally:
            image.close()

    def test_bam_38_03_not_alloc(self):
        patch = [{'at': 274884, 'from': b'\x1b\xfc', 'to': b'\x1c\xfe'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D82Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(38), (25, '01101101101111111111111111111000'))
        finally:
            image.close()


if __name__ == '__main__':
    unittest.main()
