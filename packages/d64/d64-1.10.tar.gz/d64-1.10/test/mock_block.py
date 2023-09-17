class MockBlock(object):
    SECTOR_SIZE = 256
    BLOCK_FILL = bytes(64) * 4

    def __init__(self, image=None, track=1, sector=0):
        self.image = image
        self.track = track
        self.sector = sector
        self.data = bytearray(self.BLOCK_FILL)
        self._data_size = 0
        self.start = 0
        self.is_final = True
        self._next_block = None

    def get(self, start, end=None):
        if end is None:
            return self.data[start]
        return self.data[start:end]

    def set(self, start, new):
        if isinstance(new, int):
            self.data[start] = new
        else:
            self.data[start:start+len(new)] = new

    def _set_data(self, data):
        self.data = data
        self.data_size = len(data)-2
        self._next_block = None
        self.is_final = True

    def set_next_block(self, block):
        self.data_size = 254
        self._next_block = block
        self.is_final = False

    def next_block(self):
        return self._next_block

    @property
    def data_size(self):
        return self._data_size

    @data_size.setter
    def data_size(self, size):
        self._data_size = size
        self._next_block = None
        self.is_final = True

    def __repr__(self):
        if self._next_block:
            t = self._next_block.track
            s = self._next_block.sector
        else:
            t = 0
            s = self.data_size
        return "<MockBlock {}:{} ({}:{})>".format(self.track, self.sector, t, s)
