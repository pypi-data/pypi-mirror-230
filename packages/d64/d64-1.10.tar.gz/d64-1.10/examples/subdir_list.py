import logging
import sys

import petscii_codecs

from d64 import DiskImage


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

with DiskImage(sys.argv[1]) as image:
    for line in image.directory(encoding='petscii-c64en-uc'):
        print(line)

    print()
    subdir = image.subdirectory(sys.argv[2].encode('petscii-c64en-uc'))
    for line in subdir.directory(encoding='petscii-c64en-uc'):
        print(line)
