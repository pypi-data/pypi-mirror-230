import argparse
import math
import sys

from collections import defaultdict
from pathlib import Path

from d64 import DiskImage, DiskFullError
from d64.d71_image import D71Image
from d64.d80_image import D80Image
from d64.d81_image import D81Image
from d64.d82_image import D82Image
from d64.block import Block
from d64.d80_d82_bam_block import D80D82BAMBlock
from d64.d81_bam_block import D81BAMBlock
from d64.side_sector import SideSector
from d64.super_side_sector import SuperSideSector


IMAGES = []
IMAGE = None
FIX = False
YES = False
VERBOSE = False
QUIET = False

USED_BLOCKS = defaultdict(set)


class CheckAborted(KeyboardInterrupt):
    pass


class SideSectorRebuildRequired(Exception):
    pass


class SuperSideSectorRebuildRequired(Exception):
    pass


def is_allocated(block):
    """Return `True` if block is marked as used in the BAM."""
    return IMAGE.bam.is_allocated(block.track, block.sector)


def remember_used(block):
    """Note block usage for later reconciliation."""
    global USED_BLOCKS

    USED_BLOCKS[block.track].add(block.sector)


def valid_link(block, links_to):
    ts = block.get(0, 2)
    try:
        linked_block = Block(IMAGE, *ts)
        if linked_block == links_to:
            return 'good', links_to
        return 'wrong', linked_block
    except ValueError:
        return 'invalid', ts


def fix_error(text, fixer=None, **kwargs):
    """Report, and optionally repair, an error."""
    print("ERROR: "+text)
    if FIX and fixer:
        if YES:
            return fixer(**kwargs)
        response = input("Fix? ")
        if response.lower() in ('q', 'quit'):
            raise CheckAborted
        if response.lower() in ('y', 'yes'):
            return fixer(**kwargs)
    return 1


def check_header():
    """Check various DOS fields and report disk name & id."""
    errors = 0

    if not QUIET:
        print("\nChecking DOS header...")
    if IMAGE.dos_version != IMAGE.DOS_VERSION:
        msg = "Unknown DOS version, "+chr(IMAGE.dos_version)
        errors += fix_error(msg, fix_dos_version)
    elif VERBOSE:
        print("DOS version: "+chr(IMAGE.dos_version))

    if IMAGE.dos_type != IMAGE.DOS_FORMAT:
        msg = "Invalid DOS format, ${:02x}".format(IMAGE.dos_type)
        errors += fix_error(msg, fix_dos_types)
    elif VERBOSE:
        print("DOS format: "+chr(IMAGE.dos_type))

    block = Block(IMAGE, IMAGE.DIR_TRACK, 0)
    if isinstance(IMAGE, D80Image) or isinstance(IMAGE, D82Image):
        next_block = Block(IMAGE, IMAGE.BAM_TRACK, IMAGE.BAM_SECTORS[0])
        txt = 'BAM'
    else:
        next_block = Block(IMAGE, IMAGE.DIR_TRACK, IMAGE.DIR_SECTOR)
        txt = 'directory'

    link_state, val = valid_link(block, next_block)
    if link_state == 'invalid':
        msg = "Invalid link to {} block, {:d}:{:d}".format(txt, *val)
        errors += fix_error(msg, fix_link, block=block, link_to=next_block)
    elif link_state == 'wrong':
        msg = "Invalid link to {} block, {!s}".format(txt, val)
        errors += fix_error(msg, fix_link, block=block, link_to=next_block)
    elif VERBOSE:
        print("Link to {} block OK, {!s}".format(txt, val))

    if not is_allocated(block):
        msg = "Block {!s} not allocated".format(block)
        errors += fix_error(msg, fix_unalloc_block, block=block)
    elif VERBOSE:
        print("Block {!s} allocated".format(block))
    remember_used(block)

    if not QUIET:
        print("Disk name: {}   Disk id: {}".format(IMAGE.name.decode(), IMAGE.id.decode()))
    if errors == 0 and not QUIET:
        print("OK")

    return errors


def check_bam():
    """Check Block Availability Map."""
    errors = 0

    if not QUIET:
        print("\nChecking Block Availability Map...")
    for track in range(IMAGE.MIN_TRACK, IMAGE.MAX_TRACK+1):
        total, bits = IMAGE.bam.get_entry(track)
        counted = bits.count('1')
        if total != counted:
            msg = "Mismatch in track {:d} total and bits, {:d} & {:d} ({})".format(track, total, counted, bits)
            errors += fix_error(msg, fix_bam_entry, track=track)
        if VERBOSE:
            print("Track: {:2d}   Free blocks: {:2d}   Free bits: {}".format(track, total, bits))

    bam_blocks = []
    bam_chain = []
    if isinstance(IMAGE, D71Image):
        # all of track 53 should be marked as allocated
        bam_blocks = [Block(IMAGE, IMAGE.EXTRA_BAM_TRACK, s) for s in range(IMAGE.max_sectors(IMAGE.EXTRA_BAM_TRACK))]
    elif isinstance(IMAGE, D80Image) or isinstance(IMAGE, D82Image):
        # BAM blocks should be marked as allocated
        bam_blocks = [D80D82BAMBlock(IMAGE, IMAGE.BAM_TRACK, s) for s in IMAGE.BAM_SECTORS]
        bam_chain = bam_blocks+[Block(IMAGE, IMAGE.DIR_TRACK, IMAGE.DIR_SECTOR)]
    elif isinstance(IMAGE, D81Image):
        # BAM blocks 1 and 2 should be marked as allocated
        bam_blocks = [D81BAMBlock(IMAGE, IMAGE.DIR_TRACK, 1), D81BAMBlock(IMAGE, IMAGE.DIR_TRACK, 2)]
        bam_chain = bam_blocks.copy()

    while len(bam_chain) >= 2:
        block = bam_chain[0]
        if isinstance(block, D80D82BAMBlock):
            track_range = block.track_range
            expected_track_range = IMAGE.BAM_TRACK_RANGES[len(bam_blocks)+1-len(bam_chain)]
            if track_range != expected_track_range:
                msg = "Block {!s}, invalid track range, {:d}-{:d}".format(block, *track_range)
                errors += fix_error(msg, fix_track_range, block=block, track_range=expected_track_range)
            elif VERBOSE:
                print("Block {!s}, track range {:d}-{:d}".format(block, *track_range))
            if block.dos_type != IMAGE.DOS_FORMAT:
                msg = "Block {!s}, invalid DOS format, ${:02x}".format(block, block.dos_type)
                errors += fix_error(msg, fix_bam_dos_type, block=block)
            elif VERBOSE:
                print("Block {!s}, DOS format, {}".format(block, chr(block.dos_type)))
        link_state, val = valid_link(block, bam_chain[1])
        if link_state == 'invalid':
            msg = "Block {!s}, invalid link to block, {:d}:{:d}".format(block, *val)
            errors += fix_error(msg, fix_link, block=block, link_to=bam_chain[1])
        elif link_state == 'wrong':
            msg = "Block {!s}, invalid link to block, {!s}".format(block, val)
            errors += fix_error(msg, fix_link, block=block, link_to=bam_chain[1])
        elif VERBOSE:
            print("Block {!s}, link to block OK, {!s}".format(block, val))
        bam_chain.pop(0)
    if isinstance(IMAGE, D81Image):
        for block in bam_blocks:
            if block.id != IMAGE.id:
                msg = "Block {!s}, disk id mismatch, {} & {}".format(block, block.id, IMAGE.id)
                errors += fix_error(msg, fix_bam_id, block=block)
            elif VERBOSE:
                print("Block {!s}, disk id {}".format(block, block.id))
            if block.dos_type != IMAGE.DOS_FORMAT:
                msg = "Block {!s}, Invalid DOS format, ${:02x}".format(block, block.dos_type)
                errors += fix_error(msg, fix_bam_dos_types, block=block)
            elif VERBOSE:
                print("Block {!s}, DOS format: {}".format(block, chr(block.dos_type)))
            if VERBOSE:
                print("Block {!s}, verify {}".format(block, 'on' if block.verify else 'off'))
                print("Block {!s}, check header CRC {}".format(block, 'on' if block.check_header_crc else 'off'))
                print("Block {!s}, auto start {}".format(block, 'on' if block.auto_start else 'off'))
        msg = None
        if not bam_blocks[-1].is_final:
            msg = "Final BAM block links to another block"
        else:
            try:
                bam_size = bam_blocks[-1].data_size
                if bam_size != 0xfe:
                    msg = "Final BAM block has invalid data size, {:d}".format(bam_size)
            except ValueError:
                msg = "Final BAM block has invalid data size"
        if msg is not None:
            errors += fix_error(msg, fix_data_size, block=bam_blocks[-1], size=0xfe)

    for block in bam_blocks:
        if not is_allocated(block):
            msg = "Block {!s} not allocated".format(block)
            errors += fix_error(msg, fix_unalloc_block, block=block)
        elif VERBOSE:
            print("Block {!s} allocated".format(block))
        remember_used(block)

    if errors == 0 and not QUIET:
        print("OK")

    return errors


def check_dir_links():
    """Check the chain of blocks in the directory."""
    errors = 0
    block = Block(IMAGE, IMAGE.DIR_TRACK, IMAGE.DIR_SECTOR)

    while True:
        if not is_allocated(block):
            msg = "Block {!s} not allocated".format(block)
            errors += fix_error(msg, fix_unalloc_block, block=block)
        elif VERBOSE:
            print("Block {!s} allocated".format(block))
        remember_used(block)
        if block.is_final:
            if block.data_size != 0xfe:
                msg = "Block {!s} has invalid data size, {:d}".format(block, block.data_size)
                errors += fix_error(msg, fix_data_size, block=block, size=0xfe)
            elif VERBOSE:
                print("Block {!s} checked".format(block))
            # end of chain
            break
        if VERBOSE:
            print("Block {!s} checked".format(block))
        try:
            next_block = block.next_block()
            if next_block.sector in USED_BLOCKS[next_block.track]:
                msg = "Block {!s} links to previous directory block {!s}".format(block, next_block)
                # truncate directory chain
                errors += fix_error(msg, fix_data_size, block=block, size=0xfe)
                break
            block = next_block
        except ValueError:
            ts = block.get(0, 2)
            msg = "Block {!s} has invalid link, {:d}:{:d}".format(block, *ts)
            # truncate directory chain
            errors += fix_error(msg, fix_data_size, block=block, size=0xfe)
            break

    return errors


def check_directory():
    """Check directory integrity."""

    if not QUIET:
        print("\nChecking directory...")
    # first check the integrity of the linked directory blocks
    errors = check_dir_links()

    # next check the basic integrity of each directory entry
    for entry, path in enumerate(IMAGE.iterdir(), 1):
        raw_ftype = path.entry._file_type()
        if raw_ftype & 7 > path.entry.max_file_type():
            msg = "Entry {:2d}, invalid file type, ${:02x}".format(entry, raw_ftype)
            errors += fix_error(msg, fix_ftype, entry=path.entry, ftype='PRG')
        elif VERBOSE:
            print("Entry {:2d} has valid file type, ${:02x} ({})".format(entry, raw_ftype, path.entry.file_type))

        try:
            first_block = path.entry.first_block()
            if VERBOSE:
                print("Entry {:2d}, link to first block OK, {!s}".format(entry, first_block))
        except ValueError:
            # invalid track/sector
            ts = path.entry.start_ts
            msg = "Entry {:2d}, invalid link to first data block, {:d}:{:d}".format(entry, *ts)
            # missing file contents, delete the entry
            errors += fix_error(msg, fix_ftype, entry=path.entry, ftype=0)

        ss_track, ss_sector = path.entry.side_sector_ts
        if path.entry.file_type == 'REL':
            if path.entry.record_len == 0:
                msg = "Entry {:2d}, invalid relative file record length, {:d}".format(entry, path.entry.record_len)
                # missing relative file info, delete the entry
                errors += fix_error(msg, fix_ftype, entry=path.entry, ftype=0)
            elif VERBOSE:
                print("Entry {:2d}, relative file record length {:d}".format(entry, path.entry.record_len))
        elif path.entry.record_len or ss_track or ss_sector:
            msg = "Entry {:2d}, spurious relative file data, {:d}:{:d} {:d}".format(entry, ss_track, ss_sector, path.entry.record_len)
            errors += fix_error(msg, fix_rel_data, entry=path.entry)

    if errors == 0 and not QUIET:
        print("OK")

    return errors


def check_super_side_sector(path, file_blocks):
    """Check the integrity of super side sector & side sectors of a relative file (1581)."""
    errors = 0
    sector_count = 0

    data_stride = SideSector.MAX_SIDE_SECTORS*SideSector.MAX_DATA_LINKS
    if VERBOSE:
        print("Checking side sectors of relative file {!s}".format(path.name))
    try:
        try:
            super_side_sector = SuperSideSector(IMAGE, *path.entry.side_sector_ts)
        except ValueError:
            msg = "File {!s}, invalid link to super side sector, {:d}:{:d}".format(path.name, *path.entry.side_sector_ts)
            raise SuperSideSectorRebuildRequired(msg)

        if super_side_sector.sector in USED_BLOCKS[super_side_sector.track]:
            # block already in use
            msg = "File {!s}, super side sector {!s} is in use".format(path.name, super_side_sector)
            raise SuperSideSectorRebuildRequired(msg)

        if not is_allocated(super_side_sector):
            msg = "File {!s}, super side sector {!s} not allocated".format(path.name, super_side_sector)
            errors += fix_error(msg, fix_unalloc_block, block=super_side_sector)
        elif VERBOSE:
            print("File {!s}, super side sector {!s} allocated".format(path.name, super_side_sector))
        remember_used(super_side_sector)
        sector_count += 1
        super_id = super_side_sector.super_id
        if super_id != SuperSideSector.SUPER_ID:
            msg = "File {!s}, invalid super side sector marker, ${:02x}".format(path.name, super_id)
            errors += fix_error(msg, fix_super_id, super_side_sector=super_side_sector)
        ss_groups = super_side_sector.all_side_sectors()
        from_data = math.ceil(len(file_blocks)/data_stride)
        if len(ss_groups) != from_data:
            msg = "File {!s}, mismatch in side sector group length, {:d} & {:d}".format(path.name, len(ss_groups), from_data)
            raise SuperSideSectorRebuildRequired(msg)

        # check the links to the first side sector of each group
        for ssg_ts in ss_groups:
            try:
                ssg = SideSector(IMAGE, *ssg_ts)
            except ValueError:
                ssg = None
            if ssg is None:
                msg = "File {!s}, invalid side sector group, {:d}:{:d}".format(path.name, *ssg_ts)
                raise SuperSideSectorRebuildRequired(msg)

        if VERBOSE:
            print("File {!s}, {:d} side sector groups".format(path.name, len(ss_groups)))
        for i in range(0, len(ss_groups)):
            try:
                ssg = super_side_sector.side_sector(i)
                ssg_link = None if i+1 == len(ss_groups) else super_side_sector.side_sector(i+1)
                file_slice = file_blocks[i*data_stride:(i+1)*data_stride]
                ss_errors, ss_sector_count = check_side_sector_group(path, ssg, ssg_link, file_slice)
                errors += ss_errors
                sector_count += ss_sector_count
            except SideSectorRebuildRequired as exc:
                ret = fix_error(str(exc), fix_rebuild_ss_group, file_blocks=file_blocks, record_len=path.entry.record_len, next_ssg=ssg_link)
                if isinstance(ret, int):
                    return errors+ret, sector_count
                super_side_sector.set_side_sector(i, ret)
                if i == 0:
                    super_side_sector.set_next_block(ret)

        first_ss = super_side_sector.side_sector(0)
        link_state, val = valid_link(super_side_sector, first_ss)
        if link_state == 'invalid':
            msg = "File {!s}, invalid link to first side sector group {:d}:{:d}".format(path.name, *val)
            errors += fix_error(msg, fix_link, block=super_side_sector, link_to=first_ss)
        elif link_state == 'wrong':
            msg = "File {!s}, invalid link to first side sector group {!s}".format(path.name, val)
            errors += fix_error(msg, fix_link, block=super_side_sector, link_to=first_ss)
        elif VERBOSE:
            print("Link to first side sector group OK, {!s}".format(val))

    except SuperSideSectorRebuildRequired as exc:
        print(str(exc))
        raise NotImplementedError("rebuild super side sector")

    return errors, sector_count


def check_side_sector_group(path, side_sector, next_group, file_blocks):
    """Check the integrity of a side sector group."""
    errors = 0
    sector_count = 0

    ss_from_links = []
    for i in range(SideSector.MAX_SIDE_SECTORS):
        if side_sector.sector in USED_BLOCKS[side_sector.track]:
            # block already in use
            msg = "File {!s}, side sector {!s} is in use".format(path.name, side_sector)
            raise SideSectorRebuildRequired(msg)

        if not is_allocated(side_sector):
            msg = "File {!s}, side sector {!s} not allocated".format(path.name, side_sector)
            errors += fix_error(msg, fix_unalloc_block, block=side_sector)
        elif VERBOSE:
            print("File {!s}, side sector {!s} allocated".format(path.name, side_sector))
        if side_sector.is_final:
            remember_used(side_sector)
            ss_from_links.append(side_sector)
            break
        try:
            next_side_sector = side_sector.next_block()
        except ValueError:
            ts = side_sector.get(0, 2)
            msg = "File {!s}, side sector {!s} invalid link to side sector, {:d}:{:d}".format(path.name, side_sector, *ts)
            raise SideSectorRebuildRequired(msg)
        if side_sector in ss_from_links:
            msg = "File {!s}, side sector {!s} links to previous side sector {!s}".format(path.name, side_sector, next_side_sector)
            raise SideSectorRebuildRequired(msg)
        if side_sector.sector in USED_BLOCKS[side_sector.track]:
            msg = "File {!s}, side sector {!s} is in use".format(path.name, side_sector)
            raise SideSectorRebuildRequired(msg)
        if VERBOSE:
            print("Side sector {!s} link to side sector OK, {!s}".format(side_sector, next_side_sector))
        remember_used(side_sector)
        ss_from_links.append(side_sector)
        side_sector = next_side_sector

    ss_count_from_data = math.ceil(len(file_blocks)/SideSector.MAX_DATA_LINKS)
    if len(ss_from_links) != ss_count_from_data:
        msg = "File {!s}, mismatch in side sector count, {:d} & {:d} (data)".format(path.name, len(ss_from_links), ss_count_from_data)
        raise SideSectorRebuildRequired(msg)

    for ss_count, side_sector in enumerate(ss_from_links):
        if side_sector.number != ss_count:
            msg = "Side sector {:d}, mismatch in index, {:d}".format(ss_count, side_sector.number)
            errors += fix_error(msg, fix_ss_number, side_sector=side_sector, number=ss_count)
        elif VERBOSE:
            print("Side sector {:d} index OK".format(ss_count))
        if side_sector.record_len != path.entry.record_len:
            msg = "Side sector {:d}, mismatch in record length, {:d} & {:d} (directory)".format(ss_count, side_sector.record_len, path.entry.record_len)
            errors += fix_error(msg, fix_ss_rec_len, side_sector=side_sector, record_len=path.entry.record_len)
        elif VERBOSE:
            print("Side sector {:d}, side sector record length matches directory".format(ss_count))
        peer_ts_list = side_sector.all_side_sectors()
        links_ts_list = [(ss.track, ss.sector) for ss in ss_from_links]
        if peer_ts_list != links_ts_list:
            this_ss_str = ', '.join(["{:d}:{:d}".format(*ts) for ts in peer_ts_list])
            from_links_str = ', '.join([str(ss) for ss in ss_from_links])
            msg = "Side sector {:d}, mismatch in peer links, {} & {}".format(ss_count, this_ss_str, from_links_str)
            errors += fix_error(msg, fix_ss_list, side_sector=side_sector, ss_list=ss_from_links)
        elif VERBOSE:
            print("Side sector {:d} peer links OK".format(ss_count))
        data_slice = file_blocks[ss_count*SideSector.MAX_DATA_LINKS:(ss_count+1)*SideSector.MAX_DATA_LINKS]
        data_ts_list = side_sector.all_data_blocks()
        file_ts_list = [(d.track, d.sector) for d in data_slice]
        if data_ts_list != file_ts_list:
            ss_data_str = ', '.join("{:d}:{:d}".format(*ts) for ts in data_ts_list)
            file_str = ', '.join([str(d) for d in data_slice])
            msg = "Side sector {:d}, mismatch in data links, {} & {}".format(ss_count, ss_data_str, file_str)
            errors += fix_error(msg, fix_ss_data, side_sector=side_sector, data_list=data_slice)
        elif VERBOSE:
            print("Side sector {:d} contains {:d} data links".format(ss_count, len(data_ts_list)))
        size_from_links = len(data_ts_list)*2+0xe
        if side_sector.is_final:
            if side_sector.data_size != size_from_links:
                msg = "Side sector {:d}, mismatch in data size, {:d} & {:d}".format(ss_count, side_sector.data_size, size_from_links)
                errors += fix_error(msg, fix_data_size, block=side_sector, size=size_from_links)
            elif VERBOSE:
                print("Side sector {:d}, final side sector contains {:d} bytes".format(ss_count, size_from_links))
        elif ss_count+1 == SideSector.MAX_SIDE_SECTORS:
            # final size sector in group
            if next_group is None:
                # unexpected link to another side sector
                msg = "Side sector {:d}, final side sector links to {!s}".format(ss_count, side_sector.next_block())
                errors += fix_error(msg, fix_data_size, block=side_sector, size=size_from_links)
            else:
                if side_sector.next_block() != next_group:
                    msg = "Side sector {:d}, mismatch in final side sector, {!s} & {!s}".format(ss_count, side_sector.next_block(), next_group)
                    errors += fix_error(msg, fix_link, block=side_sector, link_to=next_group)
                elif VERBOSE:
                    print("Final side sector, links to next side sector group {!s}".format(next_group))
        sector_count += 1

    return errors, sector_count


def check_side_sectors(path, file_blocks):
    """Check the integrity of side sectors of a relative file."""
    errors = 0
    sector_count = 0

    if VERBOSE:
        print("Checking side sectors of relative file {!s}".format(path.name))
    if len(file_blocks) > SideSector.MAX_SIDE_SECTORS*SideSector.MAX_DATA_LINKS:
        msg = "File {!s}, data block count exceeds space in side sector group, {:d}".format(path.name, len(file_blocks))
        print(msg)
        return 1, 0
    try:
        try:
            side_sector = SideSector(IMAGE, *path.entry.side_sector_ts)
        except ValueError:
            msg = "File {!s}, invalid link to side sector, {:d}:{:d}".format(path.name, *path.entry.side_sector_ts)
            raise SideSectorRebuildRequired(msg)

        errors, sector_count = check_side_sector_group(path, side_sector, None, file_blocks)
    except SideSectorRebuildRequired as exc:
        ret = fix_error(str(exc), fix_rebuild_ss_group, file_blocks=file_blocks, record_len=path.entry.record_len, next_ssg=None)
        if isinstance(ret, int):
            return errors+ret, sector_count
        path.entry.side_sector_ts = (ret.track, ret.sector)

    return errors, sector_count


def check_path(path):
    """Check integrity of the contents of a file."""
    errors = 0
    file_blocks = []

    if path.entry.file_type == 'DEL':
        print("File {!s}, type DEL, skipping".format(path.name))
        return 0

    try:
        block = path.entry.first_block()
    except ValueError:
        print("File {!s}, invalid link to first data block (unfixed)".format(path.name))
        return 1
    if block is None:
        print("File {!s}, no first block, skipping".format(path.name))
        return 0
    if block.sector in USED_BLOCKS[block.track]:
        # linked to another file
        msg = "File {!s}, first block {!s} is in use".format(path.name, block)
        e = fix_error(msg, fix_entry_linked, entry=path.entry)
        if e:
            # not fixed, skip further processing of this file
            return 1
        block = path.entry.first_block()

    while block:
        # whole image block usage
        remember_used(block)
        # this file block usage
        file_blocks.append(block)
        if VERBOSE:
            print("File {!s}, link to block OK, {!s}".format(path.name, block))
        if not is_allocated(block):
            msg = "File {!s}, block {!s} not allocated".format(path.name, block)
            errors += fix_error(msg, fix_unalloc_block, block=block)
        elif VERBOSE:
            print("File {!s}, block {!s} allocated".format(path.name, block))

        try:
            next_block = block.next_block()
        except ValueError:
            # invalid track/sector
            ts = block.get(0, 2)
            msg = "File {!s}, invalid link to block, {:d}:{:d}".format(path.name, *ts)
            # truncate file
            errors += fix_error(msg, fix_data_size, block=block, size=0xfe)
            break
        if next_block:
            if next_block in file_blocks:
                msg = "File {!s}, block {!s} links to previous data block {!s}".format(path.name, block, next_block)
                # truncate file
                errors += fix_error(msg, fix_data_size, block=block, size=0xfe)
                break
            if next_block.sector in USED_BLOCKS[next_block.track]:
                # linked to another file
                msg = "File {!s}, block {!s} links to in use block {!s}".format(path.name, block, next_block)
                errors += fix_error(msg, fix_file_linked, block=block)
                next_block = block.next_block()
        else:
            try:
                block_size = block.data_size
                if VERBOSE:
                    print("File {!s}, final block contains {:d} bytes".format(path.name, block_size))
            except ValueError:
                msg = "File {!s}, final block has invalid size".format(path.name)
                errors += fix_error(msg, fix_data_size, block=block, size=0xfe)

        block = next_block

    blocks_used = len(file_blocks)
    if path.entry.file_type == 'REL':
        if isinstance(IMAGE, D81Image):
            ss_errors, ss_blocks_used = check_super_side_sector(path, file_blocks)
        else:
            ss_errors, ss_blocks_used = check_side_sectors(path, file_blocks)
        errors += ss_errors
        blocks_used += ss_blocks_used

    if blocks_used != path.size_blocks:
        msg = "File {!s}, mismatch in blocks used, {:d} & {:d} (actual)".format(path.name, path.size_blocks, blocks_used)
        errors += fix_error(msg, fix_block_count, entry=path.entry, count=blocks_used)
    elif VERBOSE:
        print("File {!s} uses {:d} blocks".format(path.name, blocks_used))

    return errors


def check_partition(path):
    """Check integrity of partition."""
    errors = 0

    try:
        block = path.entry.first_block()
    except ValueError:
        print("Partition {!s}, invalid link to first data block (unfixed)".format(path.name))
        return 1

    block_count = path.size_blocks
    while block_count:
        block_count -= 1

        if block.sector in USED_BLOCKS[block.track]:
            # linked to another file
            print("Partition {!s}, block {!s} is in use (unfixed)".format(path.name, block))
            return 1

        # whole image block usage
        remember_used(block)
        if not is_allocated(block):
            msg = "Partition {!s}, block {!s} not allocated".format(path.name, block)
            errors += fix_error(msg, fix_unalloc_block, block=block)
        elif VERBOSE:
            print("Partition {!s}, block {!s} allocated".format(path.name, block))

        if block_count:
            # blocks are allocated contiguously
            try:
                sector = block.sector+1
                if sector >= IMAGE.max_sectors(block.track):
                    track = block.track+1
                    sector = 0
                else:
                    track = block.track
                block = Block(IMAGE, track, sector)
            except ValueError:
                print("Partition {!s}, invalid block, {:d}:{:d}".format(path.name, track, sector))
                return 1

    if VERBOSE:
        print("Partition {!s} uses {:d} blocks".format(path.name, path.size_blocks))

    return errors


def check_files():
    """Check integrity of all files."""
    errors = 0

    if not QUIET:
        print("\nChecking files...")
    for path in IMAGE.iterdir():
        if path.entry.replacement:
            msg = "File {!s}, replacement in progress, replacement first block {:d}:{:d}".format(path.name, *path.entry.replacement_ts)
            new_block = None
            try:
                new_block = Block(IMAGE, *path.entry.replacement_ts)
            except ValueError:
                pass
            errors += fix_error(msg, fix_replacement, entry=path.entry, new_block=new_block)
        if not path.entry.closed:
            msg = "File {!s}, unclosed".format(path.name)
            errors += fix_error(msg, fix_unclosed, entry=path.entry)

        if path.entry.file_type == 'CBM':
            part_errors = check_partition(path)
            if part_errors == 0:
                try:
                    subdir = IMAGE.subdirectory(path.name)
                    IMAGES.append(subdir)
                except TypeError:
                    pass
            errors += part_errors
        else:
            errors += check_path(path)

    if errors == 0 and not QUIET:
        print("OK")

    return errors


def check_allocation():
    global USED_BLOCKS
    errors = 0

    if not QUIET:
        print("\nChecking block allocation...")
    for track in range(IMAGE.MIN_TRACK, IMAGE.MAX_TRACK+1):
        max_sectors = IMAGE.max_sectors(track)
        _, bits = IMAGE.bam.get_entry(track)
        bam_used = {i for i, b in enumerate(bits) if b == '0' and i < max_sectors}
        delta = bam_used-USED_BLOCKS[track]

        if delta:
            delta_s = ', '.join([str(b) for b in delta])
            msg = "Track {:d}, sectors {} marked allocated when unused".format(track, delta_s)
            # generate an updated bitmask for sectors actually used
            fixed_bits = ''.join(['1' if i in delta else b for i, b in enumerate(bits)])
            errors += fix_error(msg, fix_track_alloc, track=track, bits=fixed_bits)
        elif VERBOSE:
            print("Track {:2d} OK".format(track))

    if errors == 0 and not QUIET:
        print("OK")

    return errors


def check_image(image_path):
    """Check the integrity of an image, return the number of uncorrected errors."""
    global IMAGES
    global IMAGE
    global USED_BLOCKS

    mode = 'w' if FIX else 'r'
    with DiskImage(image_path, mode) as image:
        IMAGES = [image]
        while IMAGES:
            USED_BLOCKS = defaultdict(set)
            IMAGE = IMAGES.pop(0)
            errors = check_header()
            errors += check_bam()
            errors += check_directory()
            errors += check_files()
            errors += check_allocation()

            if VERBOSE:
                print()
                try:
                    for line in IMAGE.directory():
                        print(line)
                except Exception as exc:
                    print("ERROR: cannot list directory, {}".format(str(exc)))

    return errors


def fix_dos_version():
    """Fix DOS version field."""
    IMAGE.dos_version = IMAGE.DOS_VERSION
    if VERBOSE:
        print("Setting DOS version to "+chr(IMAGE.DOS_VERSION))
    return 0


def fix_dos_types():
    """Fix DOS format type fields."""
    IMAGE.dos_type = IMAGE.DOS_FORMAT
    if VERBOSE:
        print("Setting DOS format to "+chr(IMAGE.DOS_FORMAT))
    return 0


def fix_bam_id(block):
    """Fix disk id in BAM."""
    block.id = IMAGE.id
    if VERBOSE:
        print("Setting disk id to", IMAGE.id)


def fix_bam_dos_types(block):
    """Fix DOS format type fields in BAM."""
    block.set_dos_type()
    if VERBOSE:
        print("Setting DOS format to "+chr(IMAGE.DOS_FORMAT))
    return 0


def fix_bam_entry(track):
    """Fix track entry in BAM."""
    _, bits = IMAGE.bam.get_entry(track)
    counted = bits.count('1')
    IMAGE.bam.set_entry(track, counted, bits)
    if VERBOSE:
        print("Setting track {:d} to {:d} & {}".format(track, counted, bits))
    return 0


def fix_track_range(block, track_range):
    """Fix track range in BAM."""
    block.track_range = track_range
    if VERBOSE:
        print("Setting track range to {:d}-{:d}".format(*track_range))
    return 0


def fix_bam_dos_type(block):
    """Fix DOS format type field in BAM."""
    block.set_dos_type()
    if VERBOSE:
        print("Setting DOS format to "+chr(IMAGE.DOS_FORMAT))
    return 0


def fix_unalloc_block(block):
    """Allocate an in-use block."""
    IMAGE.bam.set_allocated(block.track, block.sector)
    if VERBOSE:
        print("Allocating block {!s}".format(block))
    return 0


def fix_link(block, link_to):
    """Fix link to next block."""
    block.set_next_block(link_to)
    if VERBOSE:
        print("Setting link to {!s}".format(link_to))
    return 0


def fix_data_size(block, size):
    """Fix data used in a block."""
    block.data_size = size
    if VERBOSE:
        print("Setting data size of {!s} to {:d}".format(block, size))
    return 0


def fix_ftype(entry, ftype):
    """Fix entry file type."""
    entry.file_type = ftype
    if VERBOSE:
        print("Setting entry file type to "+entry.file_type)
    return 0


def fix_rel_data(entry):
    """Clear relative file fields."""
    entry.side_sector_ts = (0, 0)
    entry.record_len = 0
    if VERBOSE:
        print("Clearing relative file data")
    return 0


def fix_ss_number(side_sector, number):
    """Fix side sector number."""
    side_sector.number = number
    if VERBOSE:
        print("Setting side sector index to {:d}".format(number))
    return 0


def fix_ss_rec_len(side_sector, record_len):
    """Fix side sector record length."""
    side_sector.record_len = record_len
    if VERBOSE:
        print("Setting side sector record length to {:d}".format(record_len))
    return 0


def fix_rebuild_ss_group(file_blocks, record_len, next_ssg):
    """Rebuild a side sector group from file data."""
    ss_list = []
    while file_blocks:
        block = IMAGE.alloc_next_block(file_blocks[0].track, file_blocks[0].sector)
        if block is None:
            # disk is full
            for ss in ss_list:
                IMAGE.free_block(ss)
            raise DiskFullError()
        side_sector = SideSector(IMAGE, block.track, block.sector)
        side_sector.record_len = record_len
        side_sector.set_data_blocks(file_blocks[:SideSector.MAX_DATA_LINKS])
        ss_list.append(side_sector)
        file_blocks = file_blocks[SideSector.MAX_DATA_LINKS:]
    peer_ts = [(s.track, s.sector) for s in ss_list]
    for ss_count, side_sector in enumerate(ss_list):
        side_sector.number = ss_count
        side_sector.set_peers(peer_ts)
        if ss_count+1 == len(ss_list):
            # final side sector
            next_ss = next_ssg if ss_count+1 == SideSector.MAX_SIDE_SECTORS else None
        else:
            next_ss = ss_list[ss_count+1]
        if next_ss:
            side_sector.set_next_block(next_ss)
        else:
            side_sector.data_size = len(side_sector.all_data_blocks())*2+0xe
        remember_used(side_sector)
    if VERBOSE:
        print("Rebuilding {:d} side sectors".format(len(ss_list)))
    return ss_list[0]


def fix_ss_list(side_sector, ss_list):
    """Fix list of peer side sectors."""
    side_sector.set_peers([(ss.track, ss.sector) for ss in ss_list])
    if VERBOSE:
        print("Setting peer links to", ', '.join([str(ss) for ss in ss_list]))
    return 0


def fix_ss_data(side_sector, data_list):
    """Fix list of data blocks in side sector."""
    side_sector.set_data_blocks(data_list)
    if VERBOSE:
        print("Setting data links to", ', '.join([str(d) for d in data_list]))
    return 0


def fix_super_id(super_side_sector):
    """Fix super side sector identifer."""
    super_side_sector.set_super_id()
    if VERBOSE:
        print("Setting super side sector marker")
    return 0


def fix_replacement(entry, new_block):
    """Fix an entry being replaced."""
    if new_block:
        entry.start_ts = (new_block.track, new_block.sector)
        if VERBOSE:
            print("Replacing file data, new first block {!s}".format(new_block))
    entry.replacement_ts = (0, 0)
    entry.replacement = False
    entry.closed = True
    return 0


def fix_unclosed(entry):
    """Mark an entry as closed."""
    entry.closed = True
    if VERBOSE:
        print("Setting entry file state as closed")
    return 0


def fix_entry_linked(entry):
    """Clone a file whose first block is linked to another."""
    new_block = IMAGE.clone_chain(entry.first_block())
    entry.start_ts = (new_block.track, new_block.sector)
    if VERBOSE:
        print("Duplicating blocks, new first block {!s}".format(new_block))
    return 0


def fix_file_linked(block):
    """Clone chain of blocks for file linked to another."""
    new_block = IMAGE.clone_chain(block.next_block())
    block.set_next_block(new_block)
    if VERBOSE:
        print("Duplicating blocks, new next block {!s}".format(new_block))
    return 0


def fix_block_count(entry, count):
    """Fix entry size in blocks."""
    entry.size = count
    if VERBOSE:
        print("Setting block count to {:d}".format(count))
    return 0


def fix_track_alloc(track, bits):
    """Fix BAM entry for a track."""
    IMAGE.bam.set_entry(track, bits.count('1'), bits)
    if VERBOSE:
        print("Setting track {:d} bits to {}".format(track, bits))
    return 0


def main():
    global FIX
    global YES
    global VERBOSE
    global QUIET

    parser = argparse.ArgumentParser(description='Check and fix Commodore disk images.')
    parser.add_argument('image', type=Path, help='image filename')
    parser.add_argument('--fix', '-f', action='store_true', help='fix errors detected')
    parser.add_argument('--yes', '-y', action='store_true', help='answer questions with "yes"')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='no output')

    args = parser.parse_args()
    FIX = args.fix
    YES = args.yes
    VERBOSE = args.verbose
    QUIET = args.quiet

    try:
        errors = check_image(args.image)
    except KeyboardInterrupt:
        sys.exit("\nAbort, discarding all changes")
    except Exception as e:
        sys.exit("\nException: %s" % str(e))

    if errors:
        sys.exit("\n{:d} unfixed errors".format(errors))
