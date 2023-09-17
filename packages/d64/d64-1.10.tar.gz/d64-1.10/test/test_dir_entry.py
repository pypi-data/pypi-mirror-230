import unittest
from unittest.mock import patch, Mock

from d64.dir_entry import DirEntry

from test.mock_block import MockBlock


class TestDirEntryRead(unittest.TestCase):

    def setUp(self):
        mock_image = Mock()
        mock_image.block_start.return_value = 0
        self.block = MockBlock(mock_image)
        self.block.data = bytearray(32)
        self.entry = DirEntry(self.block, 0)

    def test_read_file_type(self):
        self.block.data[2] = 0x80
        self.assertEqual(self.entry.file_type, 'DEL')
        self.assertFalse(self.entry.protected)
        self.assertFalse(self.entry.replacement)
        self.assertTrue(self.entry.closed)
        self.block.data[2] = 0x81
        self.assertEqual(self.entry.file_type, 'SEQ')
        self.block.data[2] = 0x82
        self.assertEqual(self.entry.file_type, 'PRG')
        self.block.data[2] = 0x03
        self.assertEqual(self.entry.file_type, 'USR')
        self.assertFalse(self.entry.closed)
        self.block.data[2] = 0xc4
        self.assertEqual(self.entry.file_type, 'REL')
        self.assertTrue(self.entry.protected)
        self.block.data[2] = 0x85
        self.assertEqual(self.entry.file_type, '???')
        self.block.data[2] = 0x22
        self.assertEqual(self.entry.file_type, 'PRG')
        self.assertTrue(self.entry.replacement)

    def test_read_start_ts(self):
        self.block.data[3:4] = b'\x0a\x14'
        self.assertEqual(self.entry.start_ts, (10, 20))
        first_block = self.entry.first_block()
        self.assertEqual(first_block.track, 10)
        self.assertEqual(first_block.sector, 20)

    def test_read_replacement_ts(self):
        self.block.data[0x1c:0x1e] = b'\x11\x07'
        self.assertEqual(self.entry.replacement_ts, (17, 7))

    def test_read_name(self):
        self.block.data[5:0x16] = b'\x46\x49\x47\x48\x54\x45\x52\x20\x52\x41\x49\x44\xA0\xA0\xA0\xA0'
        self.assertEqual(self.entry.name, b'FIGHTER RAID')

    def test_read_ss_ts(self):
        self.block.data[0x15:0x17] = b'\x0b\x0c'
        self.assertEqual(self.entry.side_sector_ts, (11, 12))

    def test_read_rec_len(self):
        self.block.data[0x17] = 0x50
        self.assertEqual(self.entry.record_len, 80)

    def test_read_size(self):
        self.block.data[0x1e:0x20] = b'\xe7\x01'
        self.assertEqual(self.entry.size, 487)


class TestDirEntryWrite(unittest.TestCase):

    def setUp(self):
        self.block = MockBlock()
        self.block.data = bytearray(32)
        self.entry = DirEntry(self.block, 0)

    def test_write_file_type(self):
        self.block.data[2] = 0x80
        self.entry.file_type = 'prg'
        self.assertEqual(self.block.data[2], 0x82)
        self.entry.file_type = 0xc3
        self.assertEqual(self.block.data[2], 0xc3)

    def test_write_set_first_block(self):
        self.entry.start_ts = (21, 11)
        mock_block = MockBlock(None, 32, 7)
        self.entry.set_first_block(mock_block)
        self.assertEqual(self.block.data[3:5], b'\x20\x07')

    def test_write_reset_entry(self):
        self.entry.size = 14
        self.start_ts = (7, 16)
        self.side_sector_ts = (31, 6)
        self.entry.reset()
        self.assertEqual(self.entry.size, 0)
        self.assertEqual(self.entry.start_ts, (0, 0))
        self.assertEqual(self.entry.side_sector_ts, (0, 0))

    def test_write_protected(self):
        self.block.data[2] = 0x82
        self.entry.protected = True
        self.assertEqual(self.block.data[2], 0xc2)

    def test_write_closed(self):
        self.block.data[2] = 0xc2
        self.entry.closed = False
        self.assertEqual(self.block.data[2], 0x42)

    def test_write_replacement(self):
        self.block.data[2] = 0x22
        self.entry.replacement = False
        self.assertEqual(self.block.data[2], 0x02)

    def test_write_start_ts(self):
        self.entry.start_ts = (21, 11)
        self.assertEqual(self.block.data[3:5], b'\x15\x0b')

    def test_write_replacement_ts(self):
        self.entry.replacement_ts = (8, 14)
        self.assertEqual(self.block.data[0x1c:0x1e], b'\x08\x0e')

    def test_write_name(self):
        self.block.data[5:21] = b'\xa0' * 16
        self.entry.name = b'LONG NAME'
        self.assertEqual(self.block.data[5:21], b'LONG NAME\xa0\xa0\xa0\xa0\xa0\xa0\xa0')
        self.entry.name = b'SHORT'
        self.assertEqual(self.block.data[5:21], b'SHORT\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0')
        self.block.data[21] = 0x99
        self.entry.name = b'VERY VERY VERY LONG NAME'
        self.assertEqual(self.block.data[5:22], b'VERY VERY VERY L\x99')

    def test_write_ss_ts(self):
        self.entry.side_sector_ts = (11, 12)
        self.assertEqual(self.block.data[0x15:0x17], b'\x0b\x0c')

    def test_write_rec_len(self):
        self.entry.record_len = 130
        self.assertEqual(self.block.data[0x17], 0x82)

    def test_write_size(self):
        self.entry.size = 1234
        self.assertEqual(self.block.data[0x1e:0x20], b'\xd2\x04')


class TestDirEntryFree(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.image.block_start.return_value = 0
        self.block = MockBlock(self.image)
        self.block.data = bytearray(32)
        self.entry = DirEntry(self.block, 0)

    def test_free_blocks(self):
        self.entry.start_ts = (21, 11)
        with patch('d64.dir_entry.Block', new=MockBlock):
            self.entry.free_blocks()
        self.image.free_block.assert_called_once()

    def test_free_blocks_ss(self):
        freed = []

        def _free_block(b):
            freed.append((b.track, b.sector))

        self.image.free_block = _free_block
        self.entry.file_type = 'REL'
        self.entry.start_ts = (21, 11)
        self.entry.side_sector_ts = (11, 12)
        with patch('d64.dir_entry.Block', new=MockBlock):
            self.entry.free_blocks()
        self.assertIn((21, 11), freed)
        self.assertIn((11, 12), freed)
