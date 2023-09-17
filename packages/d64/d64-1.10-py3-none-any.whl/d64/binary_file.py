import io
import struct


class BinaryFile(object):
    """Manipulate binary program files."""
    def __init__(self, fileh, start_addr):
        self.start_addr = start_addr
        self.data = fileh.read()
        self.length = len(self.data)

    def dump(self):
        """Format file contents as hex data."""
        addr = self.start_addr
        fileh = io.BytesIO(self.data)

        data = fileh.read(16)
        while len(data):
            fmt = "${:04x}: "
            fmt += " {:02x}" * len(data)
            pack = "<{}B".format(len(data))
            yield fmt.format(addr, *struct.unpack(pack, data))
            addr += len(data)
            data = fileh.read(16)
