from .bam import BAM


class D80D82BAM(BAM):

    BAM_OFFSET = 6
    BAM_ENTRY_SIZE = 5

    def get_entry(self, track):
        """Return a tuple of total free blocks and a string of free blocks for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        for block in self.image.bam_blocks:
            first_track, end = block.track_range
            if track <= end:
                break
        start = self.BAM_OFFSET+(track-first_track)*self.BAM_ENTRY_SIZE
        return self._get_entry(block, start)

    def set_entry(self, track, total, free_bits):
        """Update the block allocation entry for a track."""
        if track < self.image.MIN_TRACK or track > self.image.MAX_TRACK:
            raise ValueError("Invalid track, %d" % track)

        for block in self.image.bam_blocks:
            first_track, end = block.track_range
            if track < end:
                break
        start = self.BAM_OFFSET+(track-first_track)*self.BAM_ENTRY_SIZE
        self._set_entry(block, start, total, free_bits)
