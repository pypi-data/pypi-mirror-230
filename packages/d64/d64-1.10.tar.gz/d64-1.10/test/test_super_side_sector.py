import unittest

from unittest.mock import patch

from d64.side_sector import SideSector
from d64.super_side_sector import SuperSideSector

from test.mock_block import MockBlock


class TestSuperSideSector(unittest.TestCase):

    def setUp(self):
        p = patch.object(SuperSideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.super_side = SuperSideSector(None, None, None)

    def test_clear_side_sectors(self):
        p1 = patch.object(SuperSideSector, '__bases__', (MockBlock,))
        with p1:
            p1.is_local = True
            p2 = patch.object(SideSector, '__bases__', (MockBlock,))
            with p2:
                p2.is_local = True
                self.super_side.data[3:0xff] = b'\xee\x22' * 126
                self.super_side.clear_side_sectors()
                self.assertEqual(len(self.super_side.all_side_sectors()), 0)
                self.assertEqual(self.super_side.super_id, 0xfe)

    def test_add_side_sector(self):
        mock_side = MockBlock(None, 30, 7)
        p1 = patch.object(SuperSideSector, '__bases__', (MockBlock,))
        with p1:
            p1.is_local = True
            p2 = patch.object(SideSector, '__bases__', (MockBlock,))
            with p2:
                p2.is_local = True
                self.super_side.add_side_sector(mock_side)
                self.assertEqual(len(self.super_side.all_side_sectors()), 1)

    def test_side_sector(self):
        mock_side = MockBlock(None, 30, 7)
        p1 = patch.object(SuperSideSector, '__bases__', (MockBlock,))
        with p1:
            p1.is_local = True
            p2 = patch.object(SideSector, '__bases__', (MockBlock,))
            with p2:
                p2.is_local = True
                self.super_side.set_side_sector(4, mock_side)
                self.assertEqual(self.super_side.side_sector(4).track, 30)
                with self.assertRaises(ValueError):
                    self.super_side.side_sector(130)
                with self.assertRaises(ValueError):
                    self.super_side.set_side_sector(130, mock_side)
