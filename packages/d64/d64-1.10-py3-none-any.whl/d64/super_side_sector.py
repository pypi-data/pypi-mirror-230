from .block import Block
from .side_sector import SideSector


class SuperSideSector(Block):
    """Relative file super side sector block (1581)."""
    MAX_SIDE_SECTORS = 126
    SUPER_ID = 0xfe

    @property
    def super_id(self):
        """Return super side sector identifier."""
        return self.get(2)

    def set_super_id(self):
        """Set super side sector identifier."""
        self.set(2, self.SUPER_ID)

    def all_side_sectors(self):
        """Return an array of all side sectors track & sector."""
        ss_bin = self.get(3, 0xff)
        return [(ss_bin[i], ss_bin[i+1]) for i in range(0, self.MAX_SIDE_SECTORS*2, 2) if ss_bin[i]]

    def side_sector(self, idx):
        """Return a given side sector."""
        if idx >= self.MAX_SIDE_SECTORS:
            raise ValueError("Invalid side sector index, %d" % idx)
        return SideSector(self.image, self.get(3+idx*2), self.get(4+idx*2))

    def set_side_sector(self, idx, side_sector):
        """Set side sector in side sector list."""
        if idx >= self.MAX_SIDE_SECTORS:
            raise ValueError("Invalid side sector index, %d" % idx)
        self.set(3+idx*2, bytes((side_sector.track, side_sector.sector)))

    def clear_side_sectors(self):
        """Zero out all side sector links."""
        self.set_super_id()
        self.set(3, bytes(0xfd))

    def add_side_sector(self, side_sector):
        """Append a new side sector to the side sector list."""
        for idx in range(0, self.MAX_SIDE_SECTORS*2, 2):
            if self.get(idx+3) == 0:
                self.set(idx+3, bytes((side_sector.track, side_sector.sector)))
                return idx

        return -1

    def next_block(self):
        """Return side sector linked from the super side sector."""
        if self.is_final:
            return None
        return SideSector(self.image, self.get(0), self.get(1))
