import logging

from .block import Block
from .exceptions import DiskFullError, FileIndexError
from .file import File
from .side_sector import SideSector

log = logging.getLogger(__name__)


class RelativeFile(File):
    """Read and write access to relative files."""
    def get_first_side_sector(self, data_block):
        """Allocate side sector and initialize it."""
        block = self.image.alloc_next_block(data_block.track, data_block.sector)
        if block is None:
            return None

        side_sector = SideSector(self.image, block.track, block.sector)
        log.debug("Allocated first side sector %s", side_sector)
        side_sector.number = 0
        side_sector.record_len = self.entry.record_len
        side_sector.clear_side_sectors()
        side_sector.add_side_sector(side_sector)
        side_sector.clear_data_blocks()
        return side_sector

    def get_next_side_sector(self, data_block):
        """Allocate the next side sector."""
        if self.side_sector.number+1 == SideSector.MAX_SIDE_SECTORS:
            raise FileIndexError()

        block = self.image.alloc_next_block(data_block.track, data_block.sector)
        if block is None:
            raise DiskFullError()

        side_sector = SideSector(self.image, block.track, block.sector)
        side_sector.number = self.side_sector.number+1
        log.debug("Allocated side sector %d %s", side_sector.number, side_sector)
        side_sector.record_len = self.entry.record_len
        side_sector.set_peers(self.side_sector.all_side_sectors())
        side_sector.clear_data_blocks()
        self.side_sector.add_side_sector(side_sector)
        self.side_sector.set_next_block(side_sector)

        # update the peer list of all side sectors (including the new one)
        all_peers = self.side_sector.all_side_sectors()
        for t, s in all_peers:
            ss = SideSector(self.image, t, s)
            ss.set_peers(all_peers)

        self.side_sector = side_sector
        self.entry.size += 1

    def get_first_block(self):
        """Return the first empty block for a file write."""
        data_block = super().get_first_block()
        side_sector = self.get_first_side_sector(data_block)
        if side_sector is None:
            self.image.free_block(data_block)
            raise DiskFullError()

        side_sector.add_data_block(data_block)
        self.entry.side_sector_ts = (side_sector.track, side_sector.sector)
        self.side_sector = side_sector
        self.entry.size += 1
        return data_block

    def get_new_block(self):
        """Get a new empty block for a file write."""
        data_block = super().get_new_block()
        if len(self.side_sector.all_data_blocks()) == SideSector.MAX_DATA_LINKS:
            # current side sector is full, allocate a new one
            self.get_next_side_sector(data_block)

        self.side_sector.add_data_block(data_block)
        return data_block

    def read_record(self):
        """Read a complete record from a file."""
        return self.read(self.entry.record_len)

    def write(self, data):
        """Write one or more records to a file."""
        ret = 0
        while data:
            chunk = data[:self.entry.record_len]
            ret += super().write(chunk.ljust(self.entry.record_len, b'\x00'))
            data = data[self.entry.record_len:]
        return ret

    def close(self):
        """Close file."""
        log.debug("Closing %s", self.entry.name)
        # pad rest of data block with empty records
        while self.block is None or Block.SECTOR_SIZE-(self.block.data_size+2) >= self.entry.record_len:
            self.write(b'\xff')
