from .bam import BAM


class D64BAM(BAM):

    BAM_OFFSET = 4
    BAM_ENTRY_SIZE = 4

    def get_entry(self, track):
        """Return a tuple of total free blocks and a string of free blocks for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        start = self.BAM_OFFSET+(track-1)*self.BAM_ENTRY_SIZE
        return self._get_entry(self.image.bam_block, start)

    def set_entry(self, track, total, free_bits):
        """Update the block allocation entry for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        start = self.BAM_OFFSET+(track-1)*self.BAM_ENTRY_SIZE
        self._set_entry(self.image.bam_block, start, total, free_bits)


class D64_40TrackBAM(D64BAM):

    FIRST_TRACK_IN_EXTENDED = 36

    def __init__(self, image, extended_offset):
        super().__init__(image)
        self.extended_offset = extended_offset

    def get_entry(self, track):
        """Return a tuple of total free blocks and a string of free blocks for a track."""
        if track < self.FIRST_TRACK_IN_EXTENDED:
            # tracks below 36 are as for a standard d64 image
            return super().get_entry(track)
        if track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        start = self.extended_offset+(track-self.FIRST_TRACK_IN_EXTENDED)*self.BAM_ENTRY_SIZE
        return self._get_entry(self.image.bam_block, start)

    def set_entry(self, track, total, free_bits):
        """Update the block allocation entry for a track."""
        if track < self.FIRST_TRACK_IN_EXTENDED:
            # tracks below 36 are as for a standard d64 image
            super().set_entry(track, total, free_bits)
            return
        if track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        start = self.extended_offset+(track-self.FIRST_TRACK_IN_EXTENDED)*self.BAM_ENTRY_SIZE
        self._set_entry(self.image.bam_block, start, total, free_bits)
