import unittest

from contextlib import suppress
from pathlib import Path

import d64.scripts.d64_fsck

from d64.d71_image import D71Image

import binary


class TestD71_fsck(unittest.TestCase):

    def setUp(self):
        self.base_path = Path(__file__).parent / 'data' / 'test.d71'
        self.test_path = Path('/tmp/test_bad.d71')
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

    def test_bam_53_00_not_alloc(self):
        patch = [{'at': 91630, 'from': b'\x00', 'to': b'\x01'}, {'at': 266291, 'from': b'\x00', 'to': b'\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D71Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(53), (0, '000000000000000000000000'))
        finally:
            image.close()


if __name__ == '__main__':
    unittest.main()
