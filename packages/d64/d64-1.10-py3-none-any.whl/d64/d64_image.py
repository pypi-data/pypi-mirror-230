from .block import Block
from .d64_bam import D64BAM, D64_40TrackBAM
from .dos_image import DOSImage


class D64Image(DOSImage):

    DOS_VERSION = ord('2')
    DOS_FORMAT = ord('A')
    MAX_TRACK = 35
    DIR_TRACK = 18
    DIR_SECTOR = 1
    INTERLEAVE = 10
    DIR_INTERLEAVE = 3
    TRACK_SECTOR_MAX = ((21, (1, 17)), (19, (18, 24)), (18, (25, 30)), (17, (31, 35)))
    IMAGE_SIZES = (174848, 175531)

    def __init__(self, filename):
        super().__init__(filename)
        self.bam = D64BAM(self)

    def open(self, mode):
        super().open(mode)
        self.bam_block = Block(self, self.DIR_TRACK, 0)

    def alloc_next_block(self, track, sector, directory=False):
        return self._alloc_next_block(track, sector, self.DIR_INTERLEAVE if directory else self.INTERLEAVE)

    @property
    def dos_version(self):
        return self.bam_block.get(0xa5)

    @property
    def name(self):
        name = self.bam_block.get(0x90, 0xa0)
        return name.rstrip(b'\xa0')

    @property
    def id(self):
        id = self.bam_block.get(0xa2, 0xa4)
        return id

    @property
    def dos_type(self):
        return self.bam_block.get(2)

    @dos_version.setter
    def dos_version(self, version):
        self.bam_block.set(0xa5, version)

    @name.setter
    def name(self, nam):
        self.bam_block.set(0x90, nam[:16].ljust(16, b'\xa0'))

    @id.setter
    def id(self, did):
        if len(did) != 2:
            raise ValueError("Invalid disk id, "+str(did))
        self.bam_block.set(0xa2, did)

    @dos_type.setter
    def dos_type(self, dtype):
        self.bam_block.set(2, dtype)
        self.bam_block.set(0xa6, dtype)

    def _create(self, disk_name, disk_id):
        # block 18/0 contains the BAM and various identifying fields
        bam_block = Block(self, self.DIR_TRACK, 0)
        bam_block.set(0x90, b'\xa0' * 0x1b)
        self.name = disk_name
        self.id = disk_id
        self.dos_type = self.DOS_FORMAT
        self.dos_version = self.DOS_VERSION

        # populate the BAM with all free blocks
        for sectors, range_ in self.TRACK_SECTOR_MAX:
            for t in range(range_[0], range_[1]+1):
                bits_free = '1' * sectors
                self.bam.set_entry(t, sectors, bits_free)

        # block 18/1 contains 8 empty directory entries
        dir_block = Block(self, self.DIR_TRACK, self.DIR_SECTOR)
        dir_block.data_size = 0xfe

        # link BAM block to directory block
        bam_block.set_next_block(dir_block)

        # allocate both blocks
        self.bam.set_allocated(self.DIR_TRACK, 0)
        self.bam.set_allocated(self.DIR_TRACK, 1)

    @classmethod
    def create(cls, filepath, disk_name, disk_id):
        """Create an empty disk image."""
        super().create(filepath)

        image = cls(filepath)
        try:
            image.open('r+b')
            image._create(disk_name, disk_id)
        finally:
            image.close()


class D64_40TrackImage(D64Image):
    MAX_TRACK = 40
    TRACK_SECTOR_MAX = ((21, (1, 17)), (19, (18, 24)), (18, (25, 30)), (17, (31, 40)))
    IMAGE_SIZES = (196608, 197376)
    DEFAULT_EXTENDED_BAM_OFFSET = 0xc0
    ALT_EXTENDED_BAM_OFFSET = 0xac
    EXTENDED_BAM_LEN = 0x14

    def __init__(self, filename):
        super().__init__(filename)
        self.bam = D64_40TrackBAM(self, self.DEFAULT_EXTENDED_BAM_OFFSET)

    def open(self, mode):
        super().open(mode)
        extended_bam = self.bam_block.get(self.DEFAULT_EXTENDED_BAM_OFFSET, self.DEFAULT_EXTENDED_BAM_OFFSET+self.EXTENDED_BAM_LEN)
        if sum(extended_bam) == 0:
            self.bam.extended_offset = self.ALT_EXTENDED_BAM_OFFSET

    @classmethod
    def create(cls, filepath, disk_name, disk_id):
        """Create an empty disk image."""
        super().create(filepath)

        image = cls(filepath)
        try:
            image.open('r+b')
            image._create(disk_name, disk_id)
        finally:
            image.close()
