import logging

from .block import Block
from .exceptions import DiskFullError

log = logging.getLogger(__name__)


class File(object):
    """Read and write access to files."""
    def __init__(self, entry, mode):
        log.debug("Opening %s for %s", entry.name, mode)
        self.entry = entry
        self.mode = mode[0]
        if mode[0] == 'r':
            self.block = entry.first_block()
            self.read_pos = 2
        else:
            self.image = entry.block.image
            self.block = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, _, __):
        if exc_type is None:
            self.close()

    def get_first_block(self):
        """Return the first empty block for a file write."""
        next_block = self.image.alloc_first_block()
        if next_block is None:
            raise DiskFullError()
        next_block.data_size = 0
        self.entry.set_first_block(next_block)
        self.entry.size = 1
        log.debug("Allocated first data block %s", next_block)
        return next_block

    def get_new_block(self):
        """Get a new empty block for a file write."""
        next_block = self.image.alloc_next_block(self.block.track, self.block.sector)
        if next_block is None:
            raise DiskFullError()
        log.debug("Allocated data block %s", next_block)
        next_block.data_size = 0
        self.block.set_next_block(next_block)
        self.entry.size += 1
        return next_block

    def read(self, count=-1):
        """Read bytes from file."""
        ret = b''

        while count:
            remaining = self.block.data_size-(self.read_pos-2)
            if remaining == 0:
                break

            # read as much as is wanted from the current block
            length = remaining if count == -1 else min(count, remaining)
            ret += self.block.get(self.read_pos, self.read_pos+length)
            self.read_pos += length
            if count != -1:
                count -= length

            if self.block.is_final:
                # no more blocks, end of file
                break

            if self.read_pos == Block.SECTOR_SIZE:
                # end of block, move on to the next block
                self.block = self.block.next_block()
                self.read_pos = 2

        return ret

    def write(self, data):
        """Write data to a file."""
        written = 0

        if self.block is None:
            # allocate first block
            self.block = self.get_first_block()

        while data:
            remaining_space = Block.SECTOR_SIZE-(self.block.data_size+2)
            if remaining_space:
                length = min(remaining_space, len(data))
                self.block.set(self.block.data_size+2, data[:length])
                self.block.data_size += length
                written += length
                data = data[length:]
            else:
                # end of block, append a new one
                self.block = self.get_new_block()

        return written

    def seek(self, offset, whence=0):
        """Move position within file."""
        if self.mode != 'r':
            raise NotImplementedError("seek() within files open for write not implemented")

        if whence != 0:
            raise NotImplementedError("only seek() from start of file implemented")

        self.block = self.entry.first_block()
        self.read_pos = 2
        _ = self.read(offset)
        return offset

    def close(self):
        """Close file."""
        log.debug("Closing %s", self.entry.name)
        if self.block is None:
            # file open for write, no data written
            # DOS files cannot be empty, they must contain at least one byte
            self.write(b'\r')
