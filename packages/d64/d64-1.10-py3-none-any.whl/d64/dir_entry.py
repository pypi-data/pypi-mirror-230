import struct

from .block import Block
from .relative_file import RelativeFile


class DirEntry(object):
    ENTRY_SIZE = 0x20
    FTYPE_STR = ('DEL', 'SEQ', 'PRG', 'USR', 'REL', '???', '???', '???')

    def __init__(self, block, entry_offset):
        self.block = block
        self.entry_offset = entry_offset

    def _file_type(self):
        return self.block.get(self.entry_offset+2)

    def first_block(self):
        """Return the first block containing file data."""
        if self.start_ts[0] == 0:
            return None
        return Block(self.block.image, *self.start_ts)

    def set_first_block(self, block):
        """Set the first block containing file data."""
        self.start_ts = (block.track, block.sector)

    def reset(self):
        """Reset an entry for reuse."""
        self.size = 0
        self.start_ts = (0, 0)
        self.side_sector_ts = (0, 0)

    def free_blocks(self):
        """Free any data blocks and side sectors."""
        try:
            block = self.first_block()

            while block:
                # free all data blocks
                block.image.free_block(block)
                block = block.next_block()
        except ValueError:
            pass
        if self.file_type == 'REL':
            try:
                block = Block(self.block.image, *self.side_sector_ts)

                while block:
                    # free all side sectors
                    block.image.free_block(block)
                    block = block.next_block()
            except ValueError:
                pass

    def relative_file(self, mode):
        """Return relative file instance."""
        return RelativeFile(self, mode)

    @property
    def is_deleted(self):
        """Return `True` if this entry is no longer in use."""
        return self._file_type() == 0

    @property
    def file_type(self):
        return self.FTYPE_STR[self._file_type() & 7]

    @property
    def replacement(self):
        """Return `True` if file was being overwritten."""
        return bool(self._file_type() & 0x20)

    @property
    def protected(self):
        """Return `True` if file is locked from being deleted."""
        return bool(self._file_type() & 0x40)

    @property
    def closed(self):
        """Return `True` if file was closed after last write."""
        return bool(self._file_type() & 0x80)

    @property
    def start_ts(self):
        """Return track and sector of first data block."""
        return tuple(self.block.get(self.entry_offset+3, self.entry_offset+5))

    @property
    def name(self):
        """Return the name as PETSCII."""
        name = self.block.get(self.entry_offset+5, self.entry_offset+0x15)
        return name.rstrip(b'\xa0')

    @property
    def side_sector_ts(self):
        """Return track and sector of first side sector."""
        return tuple(self.block.get(self.entry_offset+0x15, self.entry_offset+0x17))

    @property
    def record_len(self):
        """Return relative file record length."""
        return self.block.get(self.entry_offset+0x17)

    @property
    def replacement_ts(self):
        """Return track and sector of new data during file replacement."""
        return tuple(self.block.get(self.entry_offset+0x1c, self.entry_offset+0x1e))

    @property
    def size(self):
        """Return file size in blocks."""
        size, = struct.unpack('<H', self.block.get(self.entry_offset+0x1e, self.entry_offset+0x20))
        return size

    @file_type.setter
    def file_type(self, ftype):
        if isinstance(ftype, str):
            if ftype.upper() not in self.FTYPE_STR:
                raise ValueError("Unknown file type, "+ftype)
            ftype = self.FTYPE_STR.index(ftype.upper()) | 0x80

        self.block.set(self.entry_offset+2, ftype)

    @replacement.setter
    def replacement(self, prot):
        val = 0x20 if prot else 0
        old = self._file_type()
        self.block.set(self.entry_offset+2, old & 0xdf | val)

    @protected.setter
    def protected(self, prot):
        val = 0x40 if prot else 0
        old = self._file_type()
        self.block.set(self.entry_offset+2, old & 0xbf | val)

    @closed.setter
    def closed(self, clsd):
        val = 0x80 if clsd else 0
        old = self._file_type()
        self.block.set(self.entry_offset+2, old & 0x7f | val)

    @start_ts.setter
    def start_ts(self, ts):
        """Modify track and sector of first data block."""
        self.block.set(self.entry_offset+3, bytes(ts))

    @name.setter
    def name(self, name):
        self.block.set(self.entry_offset+5, name[:16].ljust(16, b'\xa0'))

    @side_sector_ts.setter
    def side_sector_ts(self, ts):
        """Modify track and sector of first side sector."""
        self.block.set(self.entry_offset+0x15, bytes(ts))

    @record_len.setter
    def record_len(self, rec_len):
        """Modify relative file record length."""
        self.block.set(self.entry_offset+0x17, rec_len)

    @replacement_ts.setter
    def replacement_ts(self, ts):
        """Modify track and sector of new data during file replacement."""
        self.block.set(self.entry_offset+0x1c, bytes(ts))

    @size.setter
    def size(self, size):
        """Set file size in blocks."""
        self.block.set(self.entry_offset+0x1e, struct.pack('<H', size))

    @classmethod
    def max_file_type(cls):
        valid = [s for s in cls.FTYPE_STR if s != '???']
        return len(valid)-1
