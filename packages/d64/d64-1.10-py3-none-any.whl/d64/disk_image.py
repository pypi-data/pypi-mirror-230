import shutil
import tempfile

from pathlib import Path

from .d64_image import D64Image, D64_40TrackImage
from .d71_image import D71Image
from .d80_image import D80Image
from .d81_image import D81Image
from .d82_image import D82Image

CREATE_METHODS = {
    'd64': D64Image.create,
    'd64_40': D64_40TrackImage.create,
    'd71': D71Image.create,
    'd80': D80Image.create,
    'd81': D81Image.create,
    'd82': D82Image.create
}


class DiskImage(object):

    all_image_classes = (D64Image, D64_40TrackImage, D71Image, D80Image, D81Image, D82Image)

    @staticmethod
    def supported_types():
        return CREATE_METHODS.keys()

    @staticmethod
    def create(type_name, filepath, disk_name, disk_id):
        CREATE_METHODS[type_name](filepath, disk_name, disk_id)

    @classmethod
    def is_valid_image(cls, filepath):
        return any([c.valid_image(filepath) for c in cls.all_image_classes])

    def __init__(self, filepath, mode='r'):
        self.filepath = Path(filepath) if isinstance(filepath, str) else filepath
        self.mode = mode

    def open(self, mode='r'):
        """Open and return a concrete instance of a disk image."""
        raw_modes = {'r': 'rb', 'w': 'r+b'}
        self.mode = mode

        for cls in self.all_image_classes:
            if cls.valid_image(self.filepath):
                self.image = cls(self.filepath)
                self.image.open(raw_modes.get(self.mode, 'rb'))
                return self.image

        raise NotImplementedError("Unsupported image format")

    def __enter__(self):
        if self.mode == 'w':
            self.org_filepath = self.filepath
            tempf = tempfile.NamedTemporaryFile(prefix='d64-', dir=self.filepath.parent,
                                                delete=False)
            # copy existing file to temporary
            with self.org_filepath.open('rb') as inh:
                shutil.copyfileobj(inh, tempf)
            tempf.close()
            self.filepath = Path(tempf.name)

        return self.open(self.mode)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.image.close()

        if self.mode == 'w':
            if exc_type is None:
                # update original with modified file
                self.filepath.replace(self.org_filepath)
            else:
                # discard changes
                self.filepath.unlink()
