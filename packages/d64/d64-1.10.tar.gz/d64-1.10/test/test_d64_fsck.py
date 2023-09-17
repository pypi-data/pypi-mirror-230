import unittest

from contextlib import suppress
from pathlib import Path

import d64.scripts.d64_fsck

from d64.block import Block
from d64.d64_image import D64Image
from d64.side_sector import SideSector

import binary


class TestD64_fsck(unittest.TestCase):

    def setUp(self):
        self.base_path = Path(__file__).parent / 'data' / 'test.d64'
        self.test_path = Path('/tmp/test_bad.d64')
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

    def test_dos_version(self):
        patch = [{'at': 91557, 'from': b'2', 'to': b'7'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.dos_version, ord('2'))
        finally:
            image.close()

    def test_dos_format(self):
        patch = [{'at': 91558, 'from': b'A', 'to': b'C'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.dos_type, ord('A'))
        finally:
            image.close()

    def test_dir_link(self):
        patch = [{'at': 91392, 'from': b'\x12', 'to': b'\x00'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(repr(image.bam_block), '<Block 18:0 (18:1)>')
        finally:
            image.close()

    def test_bam_entry_diff(self):
        patch = [{'at': 91416, 'from': b'\x15', 'to': b'\x16'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(6), (21, '111111111111111111111000'))
        finally:
            image.close()

    def test_bam_18_00_not_alloc(self):
        patch = [{'at': 91464, 'from': b'\x0el', 'to': b'\x0fm'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(18), (14, '001101101101111111100000'))
        finally:
            image.close()

    def test_dir_18_01_not_alloc(self):
        patch = [{'at': 91464, 'from': b'\x0el', 'to': b'\x0fn'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(18), (14, '001101101101111111100000'))
        finally:
            image.close()

    def test_dir_loop(self):
        patch = [{'at': 93185, 'from': b'\n', 'to': b'\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(len([e for e in image.iterdir()]), 24)
        finally:
            image.close()

    def test_dir_bad_link(self):
        patch = [{'at': 93185, 'from': b'\n', 'to': b'\xc7'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(len([e for e in image.iterdir()]), 24)
        finally:
            image.close()

    def test_dir_end_len(self):
        patch = [{'at': 93953, 'from': b'\xff', 'to': b'\x87'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(Block(image, 18, 10).data_size, 0xfe)
        finally:
            image.close()

    def test_ent_bad_type(self):
        patch = [{'at': 92482, 'from': b'\x82', 'to': b'\x87'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.path(b'SMALL10').entry.file_type, 'PRG')
        finally:
            image.close()

    def test_ent_no_1st(self):
        patch = [{'at': 92483, 'from': b'\x11\x0d', 'to': b'\x00\x00'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)

    def test_ent_bad_1st(self):
        patch = [{'at': 92483, 'from': b'\x11', 'to': b'I'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertFalse(image.path(b'SMALL10').exists())
        finally:
            image.close()

    def test_file_replacement(self):
        patch = [{'at': 91650, 'from': b'\x81', 'to': b'!'},
                 {'at': 91676, 'from': b'\x00\x00', 'to': b'\x11\x01'},
                 {'at': 91682, 'from': b'\x81\x11\x01', 'to': b'\x00\x00\x00'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.path(b'SMALL1').size_bytes, 1000)
        finally:
            image.close()

    def test_file_unclosed(self):
        patch = [{'at': 92482, 'from': b'\x82', 'to': b'\x02'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertTrue(image.path(b'SMALL10').entry.closed)
        finally:
            image.close()

    def test_file_unalloc(self):
        patch = [{'at': 91468, 'from': b'\x00\x00', 'to': b'\x01 '}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(19), (0, '000000000000000000000000'))
        finally:
            image.close()

    def test_file_loop_1st(self):
        patch = [{'at': 93284, 'from': b'\x04', 'to': b'\x02'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertNotEqual(image.path(b'LARGE4').entry.first_block, image.path(b'LARGE5').entry.first_block)
        finally:
            image.close()

    def test_file_bad_link(self):
        patch = [{'at': 84481, 'from': b'\x06', 'to': b'`'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.path(b'LARGE10').size_blocks, 2)
        finally:
            image.close()

    def test_file_loop(self):
        patch = [{'at': 84481, 'from': b'\x06', 'to': b'\x05'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.path(b'LARGE10').size_blocks, 2)
        finally:
            image.close()

    def test_file_xlink(self):
        patch = [{'at': 99841, 'from': b'\x05', 'to': b'\x03'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertNotEqual(Block(image, 19, 14).next_block(), Block(image, 19, 3))
            self.assertEqual(image.path(b'LARGE10').size_blocks, 4)
        finally:
            image.close()

    def test_file_bad_len(self):
        patch = [{'at': 87553, 'from': b'e', 'to': b'\x00'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.path(b'SMALL5').size_bytes, 254)
        finally:
            image.close()

    def test_ss_bad_index(self):
        patch = [{'at': 137986, 'from': b'\x01', 'to': b'\x05'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(side_sector.next_block().number, 1)
        finally:
            image.close()

    def test_ss_bad_rec_len(self):
        patch = [{'at': 137987, 'from': b'\xc8', 'to': b'\x8c'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(side_sector.next_block().record_len, 200)
        finally:
            image.close()

    def test_ss_unalloc(self):
        patch = [{'at': 91500, 'from': b'\x00', 'to': b'\x01'}, {'at': 91502, 'from': b'\x00', 'to': b' '}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            self.assertEqual(image.bam.get_entry(27), (0, '000000000000000000000000'))
        finally:
            image.close()

    def test_ss_peer_ss(self):
        patch = [{'at': 137988, 'from': b'\x14', 'to': b'w'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(side_sector.next_block().all_side_sectors(), [(20, 18), (27, 13), (34, 14)])
        finally:
            image.close()

    def test_ss_data_link(self):
        patch = [{'at': 138122, 'from': b'\x1e', 'to': b'-'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(side_sector.next_block().all_data_blocks()[61], (30, 6))
        finally:
            image.close()

    def test_rel_bad_1st_ss(self):
        patch = [{'at': 94198, 'from': b'\x12', 'to': b'\x97'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
            self.assertEqual(side_sector.record_len, 200)
        finally:
            image.close()

    def test_rel_xlink_1st_ss(self):
        patch = [{'at': 94197, 'from': b'\x14\x12', 'to': b'\x12\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
            self.assertEqual(side_sector.record_len, 200)
        finally:
            image.close()

    def test_rel_bad_ss(self):
        patch = [{'at': 137985, 'from': b'\x0e', 'to': b'\x9a'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
            self.assertEqual(side_sector.record_len, 200)
        finally:
            image.close()

    def test_rel_loop_ss(self):
        patch = [{'at': 137984, 'from': b'"\x0e', 'to': b'\x14\x12'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
            self.assertEqual(side_sector.record_len, 200)
        finally:
            image.close()

    def test_rel_xlink_ss(self):
        patch = [{'at': 137984, 'from': b'"\x0e', 'to': b'\x12\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
            self.assertEqual(side_sector.record_len, 200)
        finally:
            image.close()

    def test_rel_too_many_ss(self):
        patch = [{'at': 75520, 'from': b'\x00\x00', 'to': b'\x0f\x02'}, {'at': 75776, 'from': b'\x00\x00', 'to': b'\x0f\x03'},
                 {'at': 76032, 'from': b'\x00\x00', 'to': b'\x0f\x04'}, {'at': 91452, 'from': b'\x0f\xbe', 'to': b'\x0b\xa0'},
                 {'at': 169728, 'from': b'\x00W', 'to': b'\x0f\x01'}]
        binary.patch(self.base_bin, patch, self.test_path)
        self.assertEqual(d64.scripts.d64_fsck.check_image(self.test_path), 0)
        image = D64Image(self.test_path)
        try:
            image.open('rb')
            side_sector = SideSector(image, *image.path(b'DATABASE').entry.side_sector_ts)
            self.assertEqual(len(side_sector.all_side_sectors()), 3)
        finally:
            image.close()


if __name__ == '__main__':
    unittest.main()
