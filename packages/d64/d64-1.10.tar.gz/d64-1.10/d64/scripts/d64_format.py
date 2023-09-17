import argparse
import sys

from pathlib import Path

from d64 import DiskImage


def main():
    parser = argparse.ArgumentParser(description='Create empty Commodore disk images.')
    parser.add_argument('label', help='disk label')
    parser.add_argument('id', help='disk identifier')
    parser.add_argument('filename', type=Path, help='image filename')
    parser.add_argument('--type', default='d64', choices=DiskImage.supported_types(), help='image type')
    parser.add_argument('--force', action='store_true', help='overwrite existing image')
    args = parser.parse_args()

    if args.filename.exists():
        if args.force:
            args.filename.unlink()
        else:
            sys.exit("{!s} already exists".format(args.filename))
    print("Creating empty disk image as {!s}, {}:{}, type {}".format(args.filename, args.label, args.id, args.type))

    DiskImage.create(args.type, args.filename, args.label.encode(), args.id.encode())
