from .block import Block


class D81BAMBlock(Block):

    @property
    def dos_type(self):
        return self.get(2)

    @property
    def id(self):
        return self.get(4, 6)

    @property
    def verify(self):
        return bool(self.get(6) & 0x80)

    @property
    def check_header_crc(self):
        return bool(self.get(6) & 0x40)

    @property
    def auto_start(self):
        return bool(self.get(7))

    @dos_type.setter
    def dos_type(self, dtype):
        self.set(2, dtype)
        self.set(3, dtype ^ 0xff)

    @id.setter
    def id(self, did):
        self.set(4, did)

    @verify.setter
    def verify(self, flag):
        val = 0x80 if flag else 0
        old = self.get(6)
        self.set(6, old & 0x7f | val)

    @check_header_crc.setter
    def check_header_crc(self, flag):
        val = 0x40 if flag else 0
        old = self.get(6)
        self.set(6, old & 0xbf | val)

    @auto_start.setter
    def auto_start(self, flag):
        self.set(7, 0xff if flag else 0)
