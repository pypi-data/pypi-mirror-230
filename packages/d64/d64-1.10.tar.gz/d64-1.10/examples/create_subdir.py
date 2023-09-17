import logging
import sys

from d64 import Block, DiskImage


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

part_name = sys.argv[2].encode()
subdir_id = sys.argv[3].encode()

part_start = 1
part_size = 120

with DiskImage(sys.argv[1], 'w') as i:
    p = i.partition(part_name)
    p.create(Block(i, part_start, 0), part_size)
    print(p.entry, p.entry.block)
    print(p.entry.file_type, p.name)
    p.format(part_name, subdir_id)

    s = i.subdirectory(part_name)
    print(s.id)
