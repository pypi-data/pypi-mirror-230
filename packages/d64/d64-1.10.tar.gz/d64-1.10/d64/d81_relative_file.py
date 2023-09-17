import logging

from .exceptions import DiskFullError, FileIndexError
from .file import File
from .relative_file import RelativeFile
from .side_sector import SideSector
from .super_side_sector import SuperSideSector

log = logging.getLogger(__name__)


class D81RelativeFile(RelativeFile):
    def get_first_block(self):
        """Allocate side sector and initialize it."""
        data_block = File.get_first_block(self)
        side_sector = self.get_first_side_sector(data_block)
        if side_sector is None:
            self.image.free_block(data_block)
            raise DiskFullError()

        block = self.image.alloc_next_block(side_sector.track, side_sector.sector)
        if block is None:
            self.image.free_block(data_block)
            self.image.free_block(side_sector)
            raise DiskFullError()

        side_sector.add_data_block(data_block)
        self.side_sector = side_sector
        super_side_sector = SuperSideSector(self.image, block.track, block.sector)
        log.debug("Allocated super side sector %s", super_side_sector)
        super_side_sector.clear_side_sectors()
        super_side_sector.set_next_block(side_sector)
        super_side_sector.add_side_sector(side_sector)
        self.entry.side_sector_ts = (super_side_sector.track, super_side_sector.sector)
        self.entry.size += 2
        return data_block

    def get_next_side_sector(self, data_block):
        """Allocate the next side sector."""
        if self.side_sector.number+1 == SideSector.MAX_SIDE_SECTORS:
            # current side sector group is full, create a new one
            side_sector = self.get_first_side_sector(data_block)
            if side_sector is None:
                raise DiskFullError()

            super_side_sector = SuperSideSector(self.image, *self.entry.side_sector_ts)
            if super_side_sector.add_side_sector(side_sector) == -1:
                # super side sector is full
                self.image.free_block(side_sector)
                raise FileIndexError()

            self.side_sector = side_sector
            self.entry.size += 1
            return

        super().get_next_side_sector(data_block)
