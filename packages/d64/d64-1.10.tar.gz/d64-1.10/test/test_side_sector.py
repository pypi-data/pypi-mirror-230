import unittest

from unittest.mock import patch

from d64.side_sector import SideSector

from test.mock_block import MockBlock


class TestSideSectorRead(unittest.TestCase):

    def setUp(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side = SideSector(None, None, None)

    def test_read_number(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[2] = 4
            self.assertEqual(self.side.number, 4)

    def test_read_rec_len(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[3] = 190
            self.assertEqual(self.side.record_len, 190)

    def test_read_all_ss(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[4:0x10] = b'\x05\x11\x05\x07\x05\x09'+b'\x00'*6
            all_ss = self.side.all_side_sectors()
            self.assertEqual(len(all_ss), 3)
            self.assertEqual(all_ss[1], (5, 7))

    def test_read_all_data(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[0x10:0x100] = b'\x18\x13\x18\x08'+b'\x00'*238
            with patch('d64.side_sector.Block', new=MockBlock):
                all_data = self.side.all_data_blocks()
            self.assertEqual(len(all_data), 2)


class TestSideSectorWrite(unittest.TestCase):

    def setUp(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side = SideSector(None, None, None)

    def test_write_number(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.number = 3
            self.assertEqual(self.side.number, 3)
            with self.assertRaises(ValueError):
                self.side.number = 11

    def test_write_rec_len(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.record_len = 125
            self.assertEqual(self.side.record_len, 125)

    def test_write_clear_side_sectors(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[4:0x10] = b'\xee\x22' * 6
            self.side.clear_side_sectors()
            self.assertEqual(len(self.side.all_side_sectors()), 0)

    def test_write_clear_data_blocks(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[0x10:0x100] = b'\x55\xcc' * 120
            self.side.clear_data_blocks()
            self.assertEqual(len(self.side.all_data_blocks()), 0)
            self.assertEqual(self.side.data_size, 14)

    def test_write_add_side_sector(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[4:0x10] = b'\x22\x11' * 3 + bytes(6)
            new_ss = SideSector(None, 5, 11)
            new_ss.number = 3
            self.side.add_side_sector(new_ss)
            self.assertEqual(len(self.side.all_side_sectors()), 4)
            self.assertIn((5, 11), self.side.all_side_sectors())

    def test_write_add_data_block(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.clear_data_blocks()
            self.side.add_data_block(MockBlock(None, 8, 5))
            self.assertEqual(len(self.side.all_data_blocks()), 1)
            self.assertIn((8, 5), self.side.all_data_blocks())
            self.assertEqual(self.side.data_size, 16)
            self.side.add_data_block(MockBlock(None, 9, 1))
            self.assertEqual(len(self.side.all_data_blocks()), 2)
            self.assertIn((9, 1), self.side.all_data_blocks())
            self.assertEqual(self.side.data_size, 18)

    def test_write_set_ss(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[4:0x10] = b'\x22\x11' * 6
            self.side.set_peers([(5, 11), (5, 1)])
            self.assertEqual(len(self.side.all_side_sectors()), 2)

    def test_write_set_data(self):
        p = patch.object(SideSector, '__bases__', (MockBlock,))
        with p:
            p.is_local = True
            self.side.data[0x10:0x100] = b'\x66\x55' * 120
            new_data = [MockBlock(None, 14, 1), MockBlock(None, 14, 7), MockBlock(None, 14, 2)]
            self.side.set_data_blocks(new_data)
            self.assertEqual(len(self.side.all_data_blocks()), 3)
