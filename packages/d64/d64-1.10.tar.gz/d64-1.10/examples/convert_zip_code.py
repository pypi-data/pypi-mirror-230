import argparse
import struct
import sys

from pathlib import Path

from d64 import Block, DiskImage
from d64.d64_image import D64Image


def convert_zips(zip_dir, zip_base, image):
    for n in range(1, 5):
        zip_path = Path(zip_dir) / "{:d}!{}".format(n, zip_base)
        convert_zip(zip_path, image)


FINAL_TS = ((8, 10), (16, 10), (25, 17), (35, 8))

def convert_zip(zip_path, image):
    print("Reading", zip_path)
    with zip_path.open('rb') as zip_fp:
        (start_addr, ) = struct.unpack('<H', zip_fp.read(2))
        if start_addr == 0x03FE:
            # disk ID follows
            _ = zip_fp.read(2)

        while True:
            val = zip_fp.read(2)
            if len(val) == 0:
                break

            data = bytearray()
            track_flags, sector = struct.unpack('BB', val)
            flags = (track_flags & 0xC0) >> 6
            track = track_flags & 0x3F
            assert track <= 35

            if flags == 0:
                # no compression
                data = zip_fp.read(0x100)
            elif flags == 1:
                # fill byte
                data = zip_fp.read(1) * 0x100
            elif flags == 2:
                # run length encoding
                while len(data) < 0x100:
                    dlen, rep = struct.unpack('BB', zip_fp.read(2))
                    assert dlen >= 4
                    zdata = zip_fp.read(dlen)

                    while zdata:
                        b = zdata[0]
                        if b == rep:
                            data += bytearray([zdata[2]]) * zdata[1]
                            zdata = zdata[3:]
                        else:
                            data += bytearray([b])
                            zdata = zdata[1:]

            block = Block(image, track, sector)
            block.set(0, data)
            if (track, sector) in FINAL_TS:
                break


if __name__ == '__main__':
    D64Image.create(Path(sys.argv[3]), b'  ', b'  ')
    with DiskImage(sys.argv[3], 'w') as image:
        convert_zips(sys.argv[1], sys.argv[2], image)
