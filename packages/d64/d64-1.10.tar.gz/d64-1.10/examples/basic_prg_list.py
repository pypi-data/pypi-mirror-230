import sys

import petscii_codecs

from cbm_files import ProgramFile
from d64 import DiskImage


with DiskImage(sys.argv[1]) as image:
    with image.path(sys.argv[2].encode('petscii-c64en-uc')).open() as f:
        p = ProgramFile(f)

for line in p.to_text():
    print(line)
