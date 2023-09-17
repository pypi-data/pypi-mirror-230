import argparse
import sys
import tempfile

import cmd2

from d64 import Block, DiskImage


class BlockRef:
    def __init__(self, ts):
        if ':' in ts:
            track_s, sector_s = ts.split(':', 1)
            self.track = int(track_s)
            self.sector = int(sector_s)
        else:
            raise ValueError("Invalid track/sector, "+ts)


def as_text(block, start=0, end=256):
    chunk = 16
    while start < end:
        span = chunk - (start % chunk)
        fmt = '{:02x} '*span
        yield fmt.format(*[b for b in block.get(start, start+span)])
        start += span


def update_from_file(block, fileh, start=0):
    for line in fileh:
        line = line.rstrip()
        new_data = bytes([int(b, 16) for b in line.split()])
        block.set(start, new_data)
        start += len(new_data)


class D64Edit(cmd2.Cmd):
    def __init__(self, image):
        super().__init__(allow_cli_args=False)
        self.prompt = '(edit) '
        self.image = image
        self.block = Block(image, image.DIR_TRACK, 0)

    def show_block(self):
        if self.block.is_final:
            try:
                data_size = self.block.data_size
            except ValueError:
                data_size = '-'
            self.poutput("Block: {}, data size: {}\n".format(self.block, data_size))
        else:
            try:
                next_block = str(self.block.next_block())
            except ValueError:
                next_block = '-'
            self.poutput("Block: {}, next block: {}, offset: {:08x}\n".format(self.block, next_block, self.block.start))
        for line in as_text(self.block):
            self.poutput(line)

    def do_directory(self, args):
        """Display all directory entries"""
        for path in self.image.iterdir(include_deleted=True):
            line = "name: {!s}, type: {:02x}, first block: {}".format(path.entry.name, path.entry._file_type(), path.entry.first_block())
            self.poutput(line)

    def do_bam(self, args):
        """Display Block Availability Map"""
        for track in range(1, self.image.MAX_TRACK+1):
            total, bits = self.image.bam.get_entry(track)
            self.poutput("Track {:2d}  {} {:2d}".format(track, bits, total))

    block_parser = argparse.ArgumentParser()
    block_parser.add_argument('block', type=BlockRef, nargs=(0, 1), metavar='TRACK:SECTOR', help="track and sector")

    @cmd2.with_argparser(block_parser)
    def do_block(self, args):
        """Display contents of a block"""
        if args.block:
            self.block = Block(self.image, args.block.track, args.block.sector)

        self.show_block()

    next_parser = argparse.ArgumentParser()
    next_parser.add_argument('block', type=BlockRef, nargs=(0, 1), metavar='TRACK:SECTOR', help="track and sector")

    @cmd2.with_argparser(next_parser)
    def do_next(self, args):
        """Follow link to next block"""
        if args.block:
            self.block = Block(self.image, args.block.track, args.block.sector)

        next_block = self.block.next_block()
        if next_block:
            self.block = next_block
            self.show_block()
        else:
            self.poutput("Final block")

    edit_block_parser = argparse.ArgumentParser()
    edit_block_parser.add_argument('block', type=BlockRef, nargs=(0, 1), metavar='TRACK:SECTOR', help="track and sector")

    @cmd2.with_argparser(edit_block_parser)
    def do_edit_block(self, args):
        """Edit contents of a block"""
        if args.block:
            self.block = Block(self.image, args.block.track, args.block.sector)

        with tempfile.NamedTemporaryFile(mode='w+', buffering=1, prefix="edit_block-{!s}-".format(self.block)) as fileh:
            for line in as_text(self.block):
                print(line, file=fileh)
            fileh.seek(0)
            if hasattr(self, 'run_editor'):
                self.run_editor(fileh.name)
            else:
                self._run_editor(fileh.name)
            update_from_file(self.block, fileh)

    edit_entry_parser = argparse.ArgumentParser()
    edit_entry_parser.add_argument('name', help="Directory entry name")

    @cmd2.with_argparser(edit_entry_parser)
    def do_edit_entry(self, args):
        """Edit contents of a directory entry"""
        entry = self.image.path(args.name.encode('ascii')).entry

        with tempfile.NamedTemporaryFile(mode='w+', buffering=1, prefix="edit_entry-") as fileh:
            for line in as_text(entry.block, start=entry.entry_offset, end=entry.entry_offset+entry.ENTRY_SIZE):
                print(line, file=fileh)
            fileh.seek(0)
            if hasattr(self, 'run_editor'):
                self.run_editor(fileh.name)
            else:
                self._run_editor(fileh.name)
            update_from_file(entry.block, fileh, start=entry.entry_offset)

    set_next_parser = argparse.ArgumentParser()
    set_next_parser.add_argument('block', type=BlockRef, metavar='TRACK:SECTOR', help="track and sector to link to")

    @cmd2.with_argparser(set_next_parser)
    def do_set_next(self, args):
        """Update link to next block"""
        next_block = Block(self.image, args.block.track, args.block.sector)
        self.block.set_next_block(next_block)

    set_size_parser = argparse.ArgumentParser()
    set_size_parser.add_argument('size', type=int, help="data size")

    @cmd2.with_argparser(set_size_parser)
    def do_set_size(self, args):
        """Update data size of final block"""
        self.block.data_size = args.size

    alloc_block_parser = argparse.ArgumentParser()
    alloc_block_parser.add_argument('block', type=BlockRef, metavar='TRACK:SECTOR', help="track and sector")

    @cmd2.with_argparser(alloc_block_parser)
    def do_alloc_block(self, args):
        """Allocate a block in the BAM"""
        self.image.bam.set_allocated(args.block.track, args.block.sector)

    free_block_parser = argparse.ArgumentParser()
    free_block_parser.add_argument('block', type=BlockRef, metavar='TRACK:SECTOR', help="track and sector")

    @cmd2.with_argparser(free_block_parser)
    def do_free_block(self, args):
        """Free a block in the BAM"""
        self.image.bam.set_free(args.block.track, args.block.sector)

    def do_alloc_first(self, args):
        """Allocate the first block in a file"""
        new_block = self.image.alloc_first_block()
        if new_block:
            self.poutput("New block: {}".format(new_block))
            self.block = new_block
        else:
            self.pwarning("Disk full")

    alloc_next_parser = argparse.ArgumentParser()
    alloc_next_parser.add_argument('block', type=BlockRef, nargs=(0, 1), metavar='TRACK:SECTOR', help="track and sector")
    alloc_next_parser.add_argument('--directory', action='store_true', help="allocate from directory track")

    @cmd2.with_argparser(alloc_next_parser)
    def do_alloc_next(self, args):
        """Allocate next block for a file"""
        if args.block:
            self.block = Block(self.image, args.block.track, args.block.sector)

        new_block = self.image.alloc_next_block(self.block.track, self.block.sector, directory=args.directory)
        if new_block:
            self.poutput("New block: {}".format(new_block))
            self.block = new_block
        else:
            self.pwarning("Disk full")


def main():
    parser = argparse.ArgumentParser(description="Edit Commodore disk images")
    parser.add_argument('image', help="image file name")
    args = parser.parse_args()

    with DiskImage(args.image, mode='w') as image:
        e = D64Edit(image)
        ret = e.cmdloop()

    sys.exit(ret)
