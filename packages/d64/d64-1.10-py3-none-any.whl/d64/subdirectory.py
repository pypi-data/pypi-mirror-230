import math

from .block import Block
from .d81_bam import D81BAM
from .d81_bam_block import D81BAMBlock
from .d81_image import D81Image


class Subdirectory(D81Image):

    def __init__(self, parent, entry):
        self.parent = parent
        self.entry = entry
        self.map = parent.map
        self.writeable = parent.writeable
        self.MIN_TRACK = self.DIR_TRACK = entry.first_block().track
        self.MAX_TRACK = self.MIN_TRACK+math.ceil(entry.size/self.SECTORS_PER_TRACK)-1
        self.bam = D81BAM(self)
        self.header_block = Block(self, self.DIR_TRACK, 0)
        self.side_a_bam_block = D81BAMBlock(self, self.DIR_TRACK, 1)
        self.side_b_bam_block = D81BAMBlock(self, self.DIR_TRACK, 2)
        self.dir_block = Block(self, self.DIR_TRACK, self.DIR_SECTOR)

    def open(self, mode):
        return

    def close(self):
        return

    def is_formatted(self):
        """Return `True` if a subdirectory is valid."""
        return self.dos_type == self.DOS_FORMAT and self.dos_version == self.DOS_VERSION

    @classmethod
    def create(cls, parent, entry, disk_name, disk_id):
        """Format a partition to create an empty subdirectory."""
        if entry.start_ts[1] != 0:
            raise ValueError("Partition does not start at sector 0")
        if entry.size < 120:
            raise ValueError("Partition is less than 120 blocks")
        if entry.size % cls.SECTORS_PER_TRACK:
            raise ValueError("Partition is not a multiple of 40 blocks")

        for block in entry.partition_blocks():
            block.set(0, bytes(block.SECTOR_SIZE))
        subdir = cls(parent, entry)
        subdir._create(disk_name, disk_id)

    def __str__(self):
        return "Subdirectory({})".format(self.entry.name)
