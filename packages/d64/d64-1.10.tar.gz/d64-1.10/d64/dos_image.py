import codecs
import logging
import mmap

from itertools import zip_longest

import petscii_codecs  # noqa: F401

from .block import Block
from .dir_entry import DirEntry
from .dos_path import DOSPath
from .exceptions import DiskFullError

log = logging.getLogger(__name__)


class DOSImage(object):

    DIR_ENTRY = DirEntry
    MIN_TRACK = 1

    @classmethod
    def create(cls, filepath):
        """Create an empty disk image."""
        empty = bytes(cls.IMAGE_SIZES[0])
        with filepath.open('wb') as fh:
            fh.write(empty)

    @classmethod
    def valid_image(cls, filepath):
        """Return `True` if a file is an image supported by a derived class."""
        return filepath.stat().st_size in cls.IMAGE_SIZES

    def __init__(self, filename):
        self.filename = filename
        self.map = None
        self.fileh = None

    def directory(self, pattern=b'*', encoding='petscii-c64en-uc', drive=0):
        """Display entries in image."""
        try:
            _ = codecs.lookup(encoding)
        except LookupError:
            log.warning("PETSCII codecs not available, using ASCII")
            encoding = 'ascii'

        dos_info = bytes((self.dos_version, self.dos_type))
        yield '{} "{:16}" {} {}'.format(drive, self.name.decode(encoding), self.id.decode(encoding), dos_info.decode(encoding))
        for path in self.glob(pattern):
            # Entry names may contain control characters which would then be displayed as reverse
            # video in a directory listing (because they appear inside quotes).
            # Convert them to the equivalent PETSCII letter/symbol.
            def map_ctrl(c):
                if c < 0x20:
                    return c+0x40
                if c >= 0x80 and c < 0xa0:
                    return c-0x20
                return c

            name = bytes(map_ctrl(b) for b in path.name)
            closed_ch = ' ' if path.entry.closed else '*'
            file_type = path.entry.file_type.encode('ascii').decode(encoding)
            if path.entry.protected:
                file_type += '<'
            yield '{:5}{:18}{}{}'.format(str(path.size_blocks), '"'+name.decode(encoding)+'"', closed_ch, file_type)
        text = b'BLOCKS FREE.'.decode(encoding)
        yield '{} {}'.format(self.bam.total_free(), text)

    def open(self, mode):
        self.fileh = open(self.filename, mode)
        self.writeable = mode == 'r+b'
        access = mmap.ACCESS_WRITE if self.writeable else mmap.ACCESS_READ
        self.map = mmap.mmap(self.fileh.fileno(), 0, access=access)
        self.dir_block = Block(self, self.DIR_TRACK, self.DIR_SECTOR)

    def close(self):
        if self.map:
            self.map.close()
        if self.fileh:
            self.fileh.close()

    def iterdir(self, include_deleted=False):
        """Iterate over a directory."""
        block = self.dir_block

        while block:
            for offset in range(0, Block.SECTOR_SIZE, DirEntry.ENTRY_SIZE):
                entry = self.DIR_ENTRY(block, offset)
                if include_deleted or not entry.is_deleted:
                    yield DOSPath(self, entry=entry)

            block = block.next_block()

    def glob(self, pattern, include_deleted=False):
        """Return paths that match a wildcard pattern."""
        for path in self.iterdir(include_deleted):
            if DOSPath.wildcard_match(path.entry.name, path.entry.file_type, pattern):
                yield path

    def get_free_entry(self):
        """Return an unused entry for a new path."""
        block = Block(self, self.DIR_TRACK, self.DIR_SECTOR)
        entry = None

        # search directory for first free entry
        while block:
            for offset in range(0, Block.SECTOR_SIZE, DirEntry.ENTRY_SIZE):
                e = self.DIR_ENTRY(block, offset)
                if e.is_deleted:
                    entry = e
                    break

            last_block = block
            block = block.next_block()

        if entry is None:
            # no free entry, append a new block to the directory
            block = self.alloc_next_block(last_block.track, last_block.sector, directory=True)
            if block is None:
                return None

            block.data_size = Block.SECTOR_SIZE-2
            last_block.set_next_block(block)
            entry = self.DIR_ENTRY(block, 0)

        return entry

    def path(self, name):
        """Return a DOSPath instance for an entry."""
        paths = [e for e in self.glob(name)]
        if paths:
            # existing path
            return paths[0]
        return DOSPath(self, name=name)

    def alloc_first_block(self):
        """Allocate the first block for a new file."""
        track = None
        for low, high in zip_longest(range(self.DIR_TRACK-1, self.MIN_TRACK-1, -1), range(self.DIR_TRACK+1, self.MAX_TRACK+1)):
            if low is not None:
                total, free_bits = self.bam.get_entry(low)
                if total:
                    track = low
                    break
            if high is not None:
                total, free_bits = self.bam.get_entry(high)
                if total:
                    track = high
                    break

        if track is None:
            # tried either side of the directory, disk is full
            return None
        sector = self.bam.free_from(free_bits, 0)

        self.bam.set_allocated(track, sector)
        return Block(self, track, sector)

    def _alloc_next_block(self, track, sector, interleave):
        """Allocate a subsequent block for a file."""
        cur_track = track
        cur_sector = sector
        delta = -1 if track < self.DIR_TRACK else 1
        tries = 2  # either side of directory track

        while True:
            total, free_bits = self.bam.get_entry(cur_track)
            if total:
                # free sector in current track
                cur_sector += interleave
                if cur_sector >= self.max_sectors(cur_track):
                    cur_sector -= self.max_sectors(cur_track)
                    if cur_sector:
                        cur_sector -= 1

                cur_sector = self.bam.free_from(free_bits, cur_sector)
                self.bam.set_allocated(cur_track, cur_sector)
                return Block(self, cur_track, cur_sector)

            if cur_track == self.DIR_TRACK:
                # tried either side of the directory then the directory, disk is full
                return None

            cur_track += delta
            if cur_track < self.MIN_TRACK or cur_track > self.MAX_TRACK:
                # end of disk
                cur_sector = 0
                tries -= 1
                if tries:
                    # try other side of directory
                    delta = -delta
                    cur_track = self.DIR_TRACK + delta
                else:
                    # tried either side of the directory, try directory track
                    cur_track = self.DIR_TRACK

    def free_block(self, block):
        """Mark a block as free in the BAM."""
        self.bam.set_free(block.track, block.sector)

    def block_start(self, track, sector):
        """Return offset into image of a block."""
        if track < self.MIN_TRACK or track > self.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        sector_start = 0
        for sectors, track_range in self.TRACK_SECTOR_MAX:
            if track > track_range[1]:
                sector_start += (track_range[1]-track_range[0]+1) * sectors
            else:
                if sector >= sectors:
                    raise ValueError("Invalid sector, %d:%d" % (track, sector))
                sector_start += (track-track_range[0]) * sectors
                sector_start += sector
                break

        return sector_start*Block.SECTOR_SIZE

    def max_sectors(self, track):
        """Return the maximum sectors for a given track."""
        if track < self.MIN_TRACK:
            raise ValueError("Invalid track, %d" % track)

        for sectors, track_range in self.TRACK_SECTOR_MAX:
            if track <= track_range[1]:
                return sectors

        raise ValueError("Invalid track, %d" % track)

    def clone_chain(self, block):
        """Return a duplicate of a chain of blocks."""
        new_block = self.alloc_next_block(block.track, block.sector)
        if new_block is None:
            raise DiskFullError

        new_block.set(0, block.get(0, block.SECTOR_SIZE))

        if not block.is_final:
            # recurse for next block
            new_block.set_next_block(self.clone_chain(block.next_block()))

        return new_block

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.filename)
