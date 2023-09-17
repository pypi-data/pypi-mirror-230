# Test reading D64 files using d64 library: https://pypi.org/project/d64/

from d64 import DiskImage, Block

# Parameters (D64 files only)
mediaFolder = "C:/Commodore/AppMedia/c64/"
#selectedFileName = "Empire Strikes Back.d64"
#selectedProgram = b"*"
selectedFileName = "Blue Max.d64"
selectedProgram = b"BLUE MAX"
read_contents = False

hostFile = DiskImage(mediaFolder + selectedFileName)
with hostFile as image:
    print("D64 Image properties and directory listing")
    print(f"hostFile size: {hostFile.filepath.stat().st_size}")
    print(f"Supported image sizes: {hostFile.image.IMAGE_SIZES}")
    print(f"hostFile is a valid D64 file: {hostFile.is_valid_image(hostFile.filepath)}")
    print(f"Image full path: {hostFile.image.filename}")
    print(f"Disk name: {hostFile.image.name}")
    mylist = list(image.directory())  #Directory including disk name and blocks free
    print(mylist)

    print("Directory listing with entry details")
    for path in image.iterdir():  #Directory with access to path entries
        print("name: {!s}, type: {}, size blocks: {}, first block: {}".format(path.entry.name, path.entry.file_type, path.size_blocks, path.entry.first_block()))

    print("Find specific program name on disk")
    for path in image.glob(selectedProgram):  #Directory matching given criteria
        print("name: {!s}, type: {}, size blocks: {}, first block: {}".format(path.entry.name, path.entry.file_type, path.size_blocks, path.entry.first_block()))

    print("Find wildcard name on disk, returning first match")
    for path in image.iterdir():  #Directory matching wildcard, returning first PRG entry
        if path.entry.name == selectedProgram and path.entry.file_type == 'PRG':
            print("name: {!s}, type: {}, size blocks: {}, first block: {}".format(path.entry.name, path.entry.file_type, path.size_blocks, path.entry.first_block()))

            block = path.entry.first_block()  #Navigate to the first block
            print(f"track/sector: {block.track}/{block.sector}, start: {block.start}, size: {block.data_size}")
            if read_contents: print(block.get(2,block.data_size+2))

            while not block.is_final:
                block = block.next_block() #Navigate to the next and all blocks until the final one is reached
                print(f"track/sector: {block.track}/{block.sector}, start: {block.start}, size: {block.data_size}")
                if read_contents: print(block.get(2,block.data_size+2))
            break

    print("Check if input program name matches directory entry name or *")
    currentLinkTrack = 0
    currentLinkSector = 0
    progEntry = None
    for path in image.iterdir():
        if path.entry.file_type in ('SEQ', 'PRG'):
            if selectedProgram in (path.entry.name, b"*"):
                progEntry = path
                break

    if progEntry:
        currentLinkTrack = progEntry.entry.start_ts[0]
        currentLinkSector = progEntry.entry.start_ts[1]
        print(f"Found {progEntry.entry.name} with start track/sector {currentLinkTrack}/{currentLinkSector}")

    print("Continuing from above - retrieve a block and chain to the next one (in a separate function if needed)")
    if progEntry:
        while True:
            block = Block(image, currentLinkTrack, currentLinkSector)
            print(f"Current track/sector and size {currentLinkTrack}/{currentLinkSector}   {block.data_size}")
            if read_contents: print(block.get(2,block.data_size+2))

            if block.is_final:
                print("End of program")
                break
            else:
                block = block.next_block()
                currentLinkTrack = block.track
                currentLinkSector = block.sector

    image.close
