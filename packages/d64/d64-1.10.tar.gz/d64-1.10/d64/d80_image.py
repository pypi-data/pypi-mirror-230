from .block import Block
from .d80_d82_bam import D80D82BAM
from .d80_d82_bam_block import D80D82BAMBlock
from .dos_image import DOSImage


class D80Image(DOSImage):

    DOS_VERSION = ord('2')
    DOS_FORMAT = ord('C')
    MAX_TRACK = 77
    BAM_TRACK = 38
    BAM_SECTORS = (0, 3)
    BAM_TRACK_RANGES = ((1, 50), (51, 77))
    DIR_TRACK = 39
    DIR_SECTOR = 1
    INTERLEAVE = 1
    TRACK_SECTOR_MAX = ((29, (1, 39)), (27, (40, 53)), (25, (54, 64)), (23, (65, 77)))
    IMAGE_SIZES = (533248, )

    def __init__(self, filename):
        super().__init__(filename)
        self.bam = D80D82BAM(self)

    def open(self, mode):
        super().open(mode)
        self.header_block = Block(self, self.DIR_TRACK, 0)
        self.bam_blocks = [D80D82BAMBlock(self, self.BAM_TRACK, s) for s in self.BAM_SECTORS]

    def alloc_next_block(self, track, sector, directory=False):
        return self._alloc_next_block(track, sector, self.INTERLEAVE)

    @property
    def dos_version(self):
        return self.header_block.get(0x1b)

    @property
    def name(self):
        name = self.header_block.get(0x06, 0x16)
        return name.rstrip(b'\xa0')

    @property
    def id(self):
        id = self.header_block.get(0x18, 0x1a)
        return id

    @property
    def dos_type(self):
        return self.header_block.get(2)

    @dos_version.setter
    def dos_version(self, version):
        self.header_block.set(0x1b, version)

    @name.setter
    def name(self, nam):
        self.header_block.set(6, nam[:16].ljust(16, b'\xa0'))

    @id.setter
    def id(self, did):
        if len(did) != 2:
            raise ValueError("Invalid disk id, "+str(did))
        self.header_block.set(0x18, did)

    @dos_type.setter
    def dos_type(self, dtype):
        self.header_block.set(2, dtype)
        self.header_block.set(0x1c, dtype)

    @classmethod
    def create(cls, filepath, disk_name, disk_id):
        """Create an empty disk image."""
        super().create(filepath)

        image = cls(filepath)
        try:
            image.open('r+b')

            # block 39/0 contains various identifying fields
            header_block = Block(image, cls.DIR_TRACK, 0)
            header_block.set(6, b'\xa0' * 0x1b)
            image.name = disk_name
            image.id = disk_id
            image.dos_type = cls.DOS_FORMAT
            image.dos_version = cls.DOS_VERSION

            # BAM spans multiple blocks on track 38
            prev_block = header_block
            bam_blocks = []
            for sector, track_range in zip(cls.BAM_SECTORS, cls.BAM_TRACK_RANGES):
                bam_block = D80D82BAMBlock(image, cls.BAM_TRACK, sector)
                bam_block.dos_type = cls.DOS_FORMAT
                bam_block.track_range = (track_range[0], track_range[1]+1)
                # link BAM blocks
                prev_block.set_next_block(bam_block)
                prev_block = bam_block
                bam_blocks.append(bam_block)

            # populate the BAM with all free blocks
            for sectors, range_ in cls.TRACK_SECTOR_MAX:
                for t in range(range_[0], range_[1]+1):
                    bits_free = '1' * sectors
                    image.bam.set_entry(t, sectors, bits_free)

            # block 39/1 contains 8 empty directory entries
            dir_block = Block(image, cls.DIR_TRACK, cls.DIR_SECTOR)
            dir_block.data_size = 0xfe

            # link final BAM block to directory block
            bam_blocks[-1].set_next_block(dir_block)

            # allocate all blocks
            for block in [header_block, dir_block]+bam_blocks:
                image.bam.set_allocated(block.track, block.sector)
        finally:
            image.close()
