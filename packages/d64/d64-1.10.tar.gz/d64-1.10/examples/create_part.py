import sys

from d64 import Block, DiskImage

part_name = sys.argv[2].encode()
with DiskImage(sys.argv[1], 'w') as i:
    p = i.partition(part_name)
    p.create(Block(i, 1, 0), 10)
    print(p.entry, p.entry.block)
    print(p.entry.file_type, p.name)
