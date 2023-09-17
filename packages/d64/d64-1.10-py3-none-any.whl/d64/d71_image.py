from .block import Block
from .d64_image import D64Image
from .d71_bam import D71BAM


class D71Image(D64Image):

    DOS_VERSION = ord('2')
    DOS_FORMAT = ord('A')
    MAX_TRACK = 70
    EXTRA_BAM_TRACK = 53
    INTERLEAVE = 6
    DIR_INTERLEAVE = 3
    TRACK_SECTOR_MAX = ((21, (1, 17)), (19, (18, 24)), (18, (25, 30)), (17, (31, 35)),
                        (21, (36, 52)), (19, (53, 59)), (18, (60, 65)), (17, (66, 70)))
    IMAGE_SIZES = (349696, 351062)

    def __init__(self, filename):
        super().__init__(filename)
        self.bam = D71BAM(self)

    def open(self, mode):
        super().open(mode)
        self.extra_bam_block = Block(self, self.EXTRA_BAM_TRACK, 0)

    def alloc_next_block(self, track, sector, directory=False):
        return self._alloc_next_block(track, sector, self.DIR_INTERLEAVE if directory else self.INTERLEAVE)

    @classmethod
    def create(cls, filepath, disk_name, disk_id):
        """Create an empty disk image."""
        super().create(filepath, disk_name, disk_id)

        image = cls(filepath)
        try:
            image.open('r+b')
            image._format(disk_name, disk_id)

            # all of track 53 is allocated
            _, free_bits = image.bam.get_entry(cls.EXTRA_BAM_TRACK)
            free_bits = free_bits.replace('1', '0')
            image.bam.set_entry(cls.EXTRA_BAM_TRACK, 0, free_bits)
        finally:
            image.close()
