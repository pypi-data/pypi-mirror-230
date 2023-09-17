import unittest

from unittest.mock import patch

from d64.disk_image import DiskImage


class ImageA:
    def valid_image(filepath):
        return False


class ImageB:
    def valid_image(filepath):
        return filepath == 'TEST'


class TestDiskImage(unittest.TestCase):

    def test_valid_image(self):
        with patch.object(DiskImage, 'all_image_classes', (ImageA, ImageB)):
            self.assertTrue(DiskImage.is_valid_image('TEST'))
            self.assertFalse(DiskImage.is_valid_image('FAIL'))
