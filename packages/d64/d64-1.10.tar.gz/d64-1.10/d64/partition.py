import logging

from .exceptions import ConsistencyError, DiskFullError
from .path_base import PathBase

log = logging.getLogger(__name__)


class Partition(PathBase):
    """Partition, unstructured sequence of blocks (1581)."""
    def create(self, block_start, size_blocks):
        """Create a new partition."""
        if self.entry:
            raise FileExistsError("File exists: "+str(self.name))

        log.debug("Creating partition %s, start %d:%d, size %d blocks", self.name, block_start.track, block_start.sector, size_blocks)
        entry = self.image.get_free_entry()
        if entry is None:
            raise DiskFullError()

        entry.file_type = 'CBM'
        entry.name = self._name
        entry.size = size_blocks
        entry.set_first_block(block_start)

        # allocate all blocks
        alloc_blocks = []
        try:
            for block in entry.partition_blocks():
                self.image.bam.set_allocated(block.track, block.sector)
                alloc_blocks.append(block)
        except (ValueError, ConsistencyError):
            # free blocks that were allocated
            for block in alloc_blocks:
                self.image.free_block(block)
            entry.file_type = 0
            entry.reset()
            raise

        self.entry = entry
        self._name = None

    def format(self, disk_name, disk_id):
        from .subdirectory import Subdirectory

        log.debug("Format partition %s as %s:%s", self.entry.name, disk_name, disk_id)
        Subdirectory.create(self.image, self.entry, disk_name, disk_id)

    def blocks(self):
        """Generator to return each block of a partition."""
        self.assert_has_entry()

        yield from self.entry.partition_blocks()
