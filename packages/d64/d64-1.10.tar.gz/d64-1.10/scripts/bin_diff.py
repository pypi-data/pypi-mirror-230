import sys

import test.binary

from pathlib import Path


if __name__ == '__main__':
    bin1 = test.binary.load_binary(Path(sys.argv[1]))
    bin2 = test.binary.load_binary(Path(sys.argv[2]))

    print(test.binary.diff(bin1, bin2))
