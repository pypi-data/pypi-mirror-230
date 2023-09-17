from .block import Block


class D80D82BAMBlock(Block):
    """BAM block (8050/8250)."""

    @property
    def dos_type(self):
        return self.get(2)

    @dos_type.setter
    def dos_type(self, dtype):
        self.set(2, dtype)

    @property
    def track_range(self):
        tr = tuple(self.get(4, 6))
        return tr[0], tr[1]-1

    @track_range.setter
    def track_range(self, tr):
        start, end = tr
        self.set(4, bytes((start, end+1)))
