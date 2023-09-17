# d64

This Python module enables access to disk image files (.d64, .d71, .d80, .d81, .d82) used by various Commodore microcomputer emulators and tools.

It provides familiar interfaces for developers to read and write program and data files within an image.

In addition it contains tools useful to inspect and modify images, for example a script to check the integrity of an image.


## Examples

Classes and functions reside in the `d64` module, the whole module may be imported or just those definitions referenced by the user.

### Displaying an image contents

To perform a directory list

```python
from d64 import DiskImage

with DiskImage('squadron.d64') as image:
    for line in image.directory():
        print(line)
```

This prints out

```
0 "SQUADRON        " Q9 2A
15   "SQUADRON PAL"     PRG
15   "SQUADRON NTSC"    PRG
634 BLOCKS FREE.
```

### Copying a file from an image

To extract, for example, a BASIC program and write it to a file

```python
from d64 import DiskImage

with DiskImage('test.d64') as image:
    with image.path(b'METEOR').open() as in_f:
        with open('meteor.prg', 'wb') as out_f:
	    out_f.write(in_f.read())
```


## TODO

- detailed documentation
- better docstrings
- more examples
