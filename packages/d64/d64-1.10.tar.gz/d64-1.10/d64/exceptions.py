class ConsistencyError(Exception):
    """Raised when an inconsistency in the image is detected."""
    pass


class DiskFullError(Exception):
    """Raised by a write operation when no blocks are free."""
    pass


class FileIndexError(Exception):
    """Raised when no more side sectors can added."""
    pass
