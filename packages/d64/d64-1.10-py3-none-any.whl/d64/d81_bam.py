from .bam import BAM


class D81BAM(BAM):

    BAM_OFFSET = 0x10
    BAM_ENTRY_SIZE = 6
    FIRST_TRACK_ON_REVERSE = 41

    def get_entry(self, track):
        """Return a tuple of total free blocks and a string of free blocks for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        block = self.image.side_a_bam_block if track < self.FIRST_TRACK_ON_REVERSE else self.image.side_b_bam_block

        start = self.BAM_OFFSET+(track-1) % (self.FIRST_TRACK_ON_REVERSE-1)*self.BAM_ENTRY_SIZE
        return self._get_entry(block, start)

    def set_entry(self, track, total, free_bits):
        """Update the block allocation entry for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        block = self.image.side_a_bam_block if track < self.FIRST_TRACK_ON_REVERSE else self.image.side_b_bam_block

        start = self.BAM_OFFSET+(track-1) % (self.FIRST_TRACK_ON_REVERSE-1)*self.BAM_ENTRY_SIZE
        self._set_entry(block, start, total, free_bits)
