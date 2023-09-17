from .d80_image import D80Image


class D82Image(D80Image):
    MAX_TRACK = 154
    BAM_SECTORS = (0, 3, 6, 9)
    BAM_TRACK_RANGES = ((1, 50), (51, 100), (101, 150), (151, 154))
    TRACK_SECTOR_MAX = ((29, (1, 39)), (27, (40, 53)), (25, (54, 64)), (23, (65, 77)),
                        (29, (78, 116)), (27, (117, 130)), (25, (131, 141)), (23, (142, 154)))
    IMAGE_SIZES = (1066496, )
